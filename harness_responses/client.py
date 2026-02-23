"""
xAI Responses API client for harness_responses.

Uses xai_sdk (gRPC) with response_format JSON mode.
No dependencies on harness/.

Design:
  Layer 1 (API JSON mode): response_format=json_object constrains output to JSON.
  Layer 2 (semantic):     caller validates field-level business rules before artifact write.
"""

import os
import time
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Tuple, Type, TypeVar

import requests
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

# Default model for harness_responses (override via XAI_MODEL or AGENT_MODEL env vars)
_DEFAULT_MODEL = "grok-4-1-fast"
_DEFAULT_XAI_BASE_URL = "https://api.x.ai/v1"
_BUILD_SCENES_TEMPLATE_PATH = (
    Path(__file__).parent / "prompts" / "build_scenes" / "user.md"
)

# How many times to retry transient API failures
_MAX_RETRIES = 3
_RETRY_DELAY = 2.0


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_session_payload(session_state_path: Path) -> dict[str, Any]:
    if not session_state_path.exists():
        return {}
    try:
        raw = json.loads(session_state_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(raw, dict):
        return {}
    return raw


def _write_session_payload(session_state_path: Path, payload: dict[str, Any]) -> None:
    session_state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = session_state_path.with_suffix(session_state_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp_path.replace(session_state_path)


def _read_session_state_pointer(
    session_state_path: Path,
    *,
    expected_model: str,
) -> tuple[Optional[str], Optional[str]]:
    raw = _read_session_payload(session_state_path)
    if not raw:
        return None, None
    stored_model = raw.get("model")
    if isinstance(stored_model, str) and stored_model.strip() and stored_model != expected_model:
        return None, f"model mismatch ({stored_model} != {expected_model})"
    response_id = raw.get("last_response_id")
    if not isinstance(response_id, str) or not response_id.strip():
        return None, None
    return response_id.strip(), None


def _write_session_state(
    session_state_path: Path,
    *,
    model: str,
    last_response_id: str,
    phase: Optional[str] = None,
) -> None:
    payload = _read_session_payload(session_state_path)
    payload.update({
        "model": model,
        "updated_at": _utc_now(),
        "last_response_id": last_response_id,
    })
    if phase:
        payload["phase"] = phase
    _write_session_payload(session_state_path, payload)


def _clear_session_state(session_state_path: Path) -> None:
    payload = _read_session_payload(session_state_path)
    if not payload:
        return
    payload.pop("last_response_id", None)
    payload.pop("model", None)
    payload.pop("phase", None)
    payload["updated_at"] = _utc_now()
    _write_session_payload(session_state_path, payload)


def _resolve_base_url() -> str:
    base = (os.getenv("XAI_BASE_URL") or _DEFAULT_XAI_BASE_URL).strip()
    if not base:
        return _DEFAULT_XAI_BASE_URL
    return base.rstrip("/")


def _upload_file_to_xai(*, api_key: str, filename: str, content: str) -> str:
    url = f"{_resolve_base_url()}/files"
    headers = {"Authorization": f"Bearer {api_key}"}
    attempts = (
        {"purpose": "content-extract"},
        {},
    )
    last_error: Optional[Exception] = None
    for data in attempts:
        try:
            response = requests.post(
                url,
                headers=headers,
                files={"file": (filename, content.encode("utf-8"), "text/markdown")},
                data=data,
                timeout=60,
            )
            response.raise_for_status()
            body = response.json()
            file_id = body.get("id")
            if isinstance(file_id, str) and file_id.strip():
                return file_id.strip()
            raise RuntimeError(f"xAI files upload returned no id: {body}")
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Failed to upload file to xAI Files: {last_error}") from last_error


def ensure_build_scenes_template_file(
    *,
    session_state_path: Path,
) -> dict[str, Any]:
    """
    Ensure build_scenes template is uploaded once and tracked in session state.

    Returns:
        {
            "template_file_id": str,
            "template_hash": str,
            "uploaded": bool,
        }
    """
    template_content = _BUILD_SCENES_TEMPLATE_PATH.read_text(encoding="utf-8")
    template_hash = hashlib.sha256(template_content.encode("utf-8")).hexdigest()
    session = _read_session_payload(session_state_path)
    existing_id = session.get("template_file_id")
    existing_hash = session.get("template_hash")

    if (
        isinstance(existing_id, str)
        and existing_id.strip()
        and isinstance(existing_hash, str)
        and existing_hash == template_hash
    ):
        return {
            "template_file_id": existing_id.strip(),
            "template_hash": template_hash,
            "uploaded": False,
        }

    api_key = _resolve_api_key()
    file_id = _upload_file_to_xai(
        api_key=api_key,
        filename="build_scenes_template.md",
        content=template_content,
    )
    session.update(
        {
            "template_file_id": file_id,
            "template_hash": template_hash,
            "template_uploaded_at": _utc_now(),
        }
    )
    _write_session_payload(session_state_path, session)
    return {
        "template_file_id": file_id,
        "template_hash": template_hash,
        "uploaded": True,
    }


def _extract_response_text(raw_response: Any) -> str:
    """
    Extract text payload from xai_sdk Response.content.

    Handles common shapes:
      - plain string
      - list[str]
      - list[dict] with "text"/"content"
      - list[objects] with .text/.content
    """
    content = getattr(raw_response, "content", None)
    if isinstance(content, str):
        text = content.strip()
        if text:
            return text
        raise ValueError("Response content is empty")

    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, str):
                if item.strip():
                    chunks.append(item)
                continue

            if isinstance(item, dict):
                text_val = item.get("text")
                if isinstance(text_val, str) and text_val.strip():
                    chunks.append(text_val)
                    continue
                content_val = item.get("content")
                if isinstance(content_val, str) and content_val.strip():
                    chunks.append(content_val)
                    continue
                continue

            text_attr = getattr(item, "text", None)
            if isinstance(text_attr, str) and text_attr.strip():
                chunks.append(text_attr)
                continue
            content_attr = getattr(item, "content", None)
            if isinstance(content_attr, str) and content_attr.strip():
                chunks.append(content_attr)
                continue

        joined = "".join(chunks).strip()
        if joined:
            return joined
        raise ValueError("Response content has no text payload")

    if content is None:
        raise ValueError("Response content is missing")
    return str(content)


def _resolve_model() -> str:
    """Resolve model name from environment variables."""
    raw = (
        os.getenv("XAI_MODEL")
        or os.getenv("AGENT_MODEL")
        or _DEFAULT_MODEL
    )
    # Strip provider prefix if present (e.g. "xai/grok-..." → "grok-...")
    return raw.removeprefix("xai/").removeprefix("minimax/")


def _resolve_api_key() -> str:
    """Resolve xAI API key; fail with actionable error if missing."""
    key = os.getenv("XAI_API_KEY")
    if not key:
        raise EnvironmentError(
            "XAI_API_KEY environment variable is not set. "
            "Set it with: export XAI_API_KEY=<your-key>"
        )
    return key


def call_responses_api(
    system_prompt: str,
    user_prompt: str,
    schema: Type[T],
    *,
    temperature: float = 0.7,
    max_tokens: int = 16000,
    store: bool = True,
    enable_web_search: bool = False,
    model: Optional[str] = None,
    session_state_path: Optional[Path] = None,
    phase: Optional[str] = None,
) -> Tuple[Any, T]:
    """
    Call xAI Responses API using response_format JSON mode and Pydantic validation.

    Args:
        system_prompt: System role prompt.
        user_prompt: User role prompt.
        schema: Pydantic BaseModel class defining the expected output shape.
        temperature: Sampling temperature (0.0–2.0).
        max_tokens: Maximum output tokens.
        store: When True, enables stateful message storage. Defaults to True.
        enable_web_search: When True, enables web_search tool. Defaults to False.
        model: Model override; if None, resolved from env vars.

    Returns:
        (raw_response, parsed_instance) where raw_response is the xai_sdk Response
        object and parsed_instance is a validated Pydantic model instance.
    """
    # Import here to isolate xai_sdk from the rest of the codebase
    from xai_sdk.search import SearchParameters, web_source
    from xai_sdk.sync.client import Client
    from xai_sdk.chat import (
        system as sdk_system,
        user as sdk_user,
    )

    api_key = _resolve_api_key()
    resolved_model = model or _resolve_model()

    print(f"🤖 harness_responses using:")
    print(f"   Model: {resolved_model}")
    effective_store = bool(store)

    print(f"   Store: {effective_store}")
    print(f"   Web search: {enable_web_search}")

    client = Client(api_key=api_key)
    previous_response_id: Optional[str] = None
    reset_reason: Optional[str] = None
    if session_state_path is not None:
        previous_response_id, reset_reason = _read_session_state_pointer(
            session_state_path,
            expected_model=resolved_model,
        )
        if previous_response_id:
            print(f"   Previous response ID: {previous_response_id}")
        if reset_reason:
            print(f"   Session pointer reset: {reset_reason}")

    last_exc: Optional[Exception] = None
    attempted_reset_from_invalid_previous = False
    for attempt in range(_MAX_RETRIES):
        try:
            create_kwargs = {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "store_messages": effective_store,
                "response_format": "json_object",
            }
            if previous_response_id:
                create_kwargs["previous_response_id"] = previous_response_id
            if enable_web_search:
                create_kwargs["search_parameters"] = SearchParameters(
                    sources=[web_source()],
                    mode="on",
                )

            chat = client.chat.create(
                resolved_model,
                **create_kwargs,
            )
            chat.append(sdk_system(system_prompt))
            chat.append(sdk_user(user_prompt))

            raw_response = chat.sample()
            setattr(raw_response, "previous_response_id_used", previous_response_id)
            payload_text = _extract_response_text(raw_response)
            try:
                parsed = schema.model_validate_json(payload_text)
            except ValidationError as exc:
                raise ValueError(
                    f"Structured JSON validation failed for schema {schema.__name__}: {exc}"
                ) from exc
            response_id: Optional[str] = getattr(raw_response, "id", None)
            if session_state_path is not None and isinstance(response_id, str) and response_id.strip():
                _write_session_state(
                    session_state_path,
                    model=resolved_model,
                    last_response_id=response_id.strip(),
                    phase=phase,
                )
            return raw_response, parsed

        except Exception as exc:
            last_exc = exc
            # If pointer is stale/invalid, clear and retry once as a fresh root request.
            if previous_response_id and not attempted_reset_from_invalid_previous:
                err_str = str(exc).lower()
                pointer_invalid = any(
                    kw in err_str for kw in ("previous_response_id", "not found", "invalid")
                )
                if pointer_invalid:
                    print("⚠️  previous_response_id invalid; retrying without conversation pointer")
                    previous_response_id = None
                    attempted_reset_from_invalid_previous = True
                    if session_state_path is not None:
                        _clear_session_state(session_state_path)
                    continue
            # Retry transient errors; re-raise deterministic failures immediately
            err_str = str(exc).lower()
            is_transient = any(
                kw in err_str
                for kw in ("timeout", "unavailable", "rate", "429", "503", "502")
            )
            if not is_transient or attempt == _MAX_RETRIES - 1:
                raise
            wait = _RETRY_DELAY * (2 ** attempt)
            print(f"⚠️  Transient error (attempt {attempt + 1}/{_MAX_RETRIES}): {exc}")
            print(f"⚠️  Retrying in {wait}s...")
            time.sleep(wait)

    # Should never reach here, but satisfies type checker
    raise RuntimeError(
        f"Failed after {_MAX_RETRIES} attempts"
    ) from last_exc
