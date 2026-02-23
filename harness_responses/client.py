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
from typing import Any, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

# Default model for harness_responses (override via XAI_MODEL or AGENT_MODEL env vars)
_DEFAULT_MODEL = "grok-4-1-fast"

# How many times to retry transient API failures
_MAX_RETRIES = 3
_RETRY_DELAY = 2.0


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
    store: bool = False,
    enable_web_search: bool = False,
    model: Optional[str] = None,
) -> Tuple[Any, T]:
    """
    Call xAI Responses API using response_format JSON mode and Pydantic validation.

    Args:
        system_prompt: System role prompt.
        user_prompt: User role prompt.
        schema: Pydantic BaseModel class defining the expected output shape.
        temperature: Sampling temperature (0.0–2.0).
        max_tokens: Maximum output tokens.
        store: When True, enables stateful message storage. Defaults to False.
        enable_web_search: When True, enables web_search tool. Defaults to False.
        model: Model override; if None, resolved from env vars.

    Returns:
        (raw_response, parsed_instance) where raw_response is the xai_sdk Response
        object and parsed_instance is a validated Pydantic model instance.
    """
    # Import here to isolate xai_sdk from the rest of the codebase
    from xai_sdk.search import SearchParameters, web_source
    from xai_sdk.sync.client import Client
    from xai_sdk.chat import system as sdk_system, user as sdk_user

    api_key = _resolve_api_key()
    resolved_model = model or _resolve_model()

    print(f"🤖 harness_responses using:")
    print(f"   Model: {resolved_model}")
    print(f"   Store: {store}")
    print(f"   Web search: {enable_web_search}")

    client = Client(api_key=api_key)

    last_exc: Optional[Exception] = None
    for attempt in range(_MAX_RETRIES):
        try:
            create_kwargs = {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "store_messages": store,
                "response_format": "json_object",
            }
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
            payload_text = _extract_response_text(raw_response)
            try:
                parsed = schema.model_validate_json(payload_text)
            except ValidationError as exc:
                raise ValueError(
                    f"Structured JSON validation failed for schema {schema.__name__}: {exc}"
                ) from exc
            return raw_response, parsed

        except Exception as exc:
            last_exc = exc
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
