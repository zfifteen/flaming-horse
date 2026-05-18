"""Local Grok CLI client for harness_responses.

The live backend is the local Grok Build CLI. Grok may read the repository and
project files, but it must write exactly one staged JSON response. The harness
then validates that JSON against the phase schema and promotes artifacts through
the deterministic parser.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

_DEFAULT_MODEL = "grok-build"
_DEFAULT_TIMEOUT_SECONDS = 900


class GrokCliTimeoutError(EnvironmentError):
    """Raised when the local Grok CLI exceeds the configured phase timeout."""


@dataclass
class GrokCliResponse:
    """Minimal raw response object consumed by harness_responses.cli/parser."""

    content: str
    id: str
    stdout: str
    stderr: str
    prompt_file: str
    staged_response_file: str
    previous_response_id_used: Optional[str] = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_session_payload(session_state_path: Path) -> dict[str, Any]:
    if not session_state_path.exists():
        return {}
    try:
        raw = json.loads(session_state_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def _write_session_payload(session_state_path: Path, payload: dict[str, Any]) -> None:
    session_state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = session_state_path.with_suffix(session_state_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(session_state_path)


def _clear_session_state(session_state_path: Path) -> None:
    payload = _read_session_payload(session_state_path)
    if not payload:
        return
    payload.pop("last_response_id", None)
    payload.pop("model", None)
    payload.pop("phase", None)
    payload["updated_at"] = _utc_now()
    _write_session_payload(session_state_path, payload)


def clear_response_pointer(*, session_state_path: Path) -> None:
    """Clear conversation pointer metadata while preserving other session fields."""

    _clear_session_state(session_state_path)


def _resolve_grok_cli() -> str:
    configured = os.getenv("GROK_CLI", "").strip()
    if configured:
        path = Path(os.path.expanduser(configured))
        if not path.exists():
            raise EnvironmentError(f"GROK_CLI path does not exist: {configured}")
        if not path.is_file():
            raise EnvironmentError(f"GROK_CLI is not a file: {configured}")
        if not os.access(path, os.X_OK):
            raise EnvironmentError(f"GROK_CLI is not executable: {configured}")
        return str(path)

    discovered = shutil.which("grok")
    if discovered:
        return discovered
    raise EnvironmentError(
        "grok CLI not found. Install/login to Grok Build and ensure `grok` is on PATH, "
        "or set GROK_CLI=/absolute/path/to/grok."
    )


def _resolve_model(model: Optional[str]) -> str:
    raw = model or os.getenv("GROK_MODEL") or _DEFAULT_MODEL
    value = raw.strip()
    if not value:
        return _DEFAULT_MODEL
    if "/" in value:
        raise EnvironmentError(
            "GROK_MODEL must be a Grok CLI model id without provider prefix "
            f"(got {value!r})"
        )
    return value


def _resolve_timeout_seconds() -> int:
    raw = os.getenv("GROK_CLI_TIMEOUT_SECONDS", "").strip()
    if not raw:
        return _DEFAULT_TIMEOUT_SECONDS
    try:
        value = int(raw)
    except ValueError as exc:
        raise EnvironmentError("GROK_CLI_TIMEOUT_SECONDS must be an integer") from exc
    if value <= 0:
        raise EnvironmentError("GROK_CLI_TIMEOUT_SECONDS must be positive")
    return value


def _response_paths(
    *,
    session_state_path: Optional[Path],
    phase: Optional[str],
) -> tuple[Path, Path]:
    log_dir = (
        session_state_path.parent
        if session_state_path is not None
        else Path.cwd() / "log"
    )
    log_dir.mkdir(parents=True, exist_ok=True)
    phase_name = phase or "unknown"
    stamp = _safe_timestamp()
    prompt_path = log_dir / f"grok_prompt_{phase_name}_{stamp}.md"
    staged_path = log_dir / f"grok_response_{phase_name}_{stamp}.json"
    return prompt_path, staged_path


def _compact_schema_contract(schema: Type[BaseModel]) -> str:
    contracts = {
        "PlanResponse": "\n".join(
            [
                "Return one JSON object with:",
                "- title: string",
                "- description: string",
                "- target_duration_seconds: positive integer",
                "- scenes: non-empty ordered array of objects",
                "Each scene object has title, description, estimated_duration_seconds, and visual_ideas.",
            ]
        ),
        "NarrationResponse": "Return one JSON object with script: an object mapping narration keys to narration text strings.",
        "BuildScenesResponse": "Return one JSON object with scene_body: a string containing only scaffold-slot Python statements.",
        "SceneQcResponse": "Return one JSON object with report_markdown: a string.",
        "SceneRepairResponse": "Return one JSON object with scene_body: a string containing the repaired scaffold-slot Python statements.",
    }
    known = contracts.get(schema.__name__)
    if known:
        return known

    fields = []
    for field_name in schema.model_fields:
        fields.append(f"- {field_name}")
    return "Return one JSON object with these top-level fields:\n" + "\n".join(fields)


def _build_prompt(
    *,
    system_prompt: str,
    user_prompt: str,
    schema: Type[BaseModel],
    staged_response_path: Path,
    project_dir: Optional[Path],
    phase: Optional[str],
) -> str:
    project_text = str(project_dir.resolve()) if project_dir is not None else ""
    return "\n".join(
        [
            "# Flaming Horse Grok CLI Harness Task",
            "",
            "You are the local backend model for Flaming Horse.",
            "You may read repository and project files directly.",
            "Do not edit canonical project artifacts such as plan.json, narration_script.py, scene_*.py, project_state.json, or rendered media.",
            f"Write exactly one JSON object to this staged response file: {staged_response_path}",
            "The harness will validate that file and deterministically promote artifacts.",
            "Do not write markdown, code fences, XML, explanations, or prose to the staged response file.",
            "Do not create or edit any other files.",
            "",
            f"Phase: {phase or 'unknown'}",
            f"Repository root: {_repo_root()}",
            f"Project directory: {project_text}",
            "",
            "## Required JSON Contract",
            _compact_schema_contract(schema),
            "",
            "## System Prompt",
            system_prompt,
            "",
            "## User Prompt",
            user_prompt,
            "",
            "When finished, print only the staged response file path.",
            "",
        ]
    )


def _parse_stdout_payload(stdout: str) -> dict[str, Any]:
    stripped = stdout.strip()
    if not stripped:
        return {}
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def call_grok_cli(
    system_prompt: str,
    user_prompt: str,
    schema: Type[T],
    *,
    model: Optional[str] = None,
    session_state_path: Optional[Path] = None,
    phase: Optional[str] = None,
    project_dir: Optional[Path] = None,
) -> Tuple[GrokCliResponse, T]:
    """Call local Grok CLI and validate its staged JSON response."""

    grok_cli = _resolve_grok_cli()
    resolved_model = _resolve_model(model)
    timeout_seconds = _resolve_timeout_seconds()
    prompt_path, staged_response_path = _response_paths(
        session_state_path=session_state_path,
        phase=phase,
    )
    prompt_text = _build_prompt(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        schema=schema,
        staged_response_path=staged_response_path,
        project_dir=project_dir,
        phase=phase,
    )
    prompt_path.write_text(prompt_text, encoding="utf-8")
    if staged_response_path.exists():
        staged_response_path.unlink()
    execution_dir = prompt_path.parent

    cmd = [
        grok_cli,
        "--cwd",
        str(execution_dir),
        "--sandbox",
        "workspace",
        "--prompt-file",
        str(prompt_path),
        "--output-format",
        "json",
        "--no-subagents",
        "--disable-web-search",
        "--max-turns",
        "1",
        "--permission-mode",
        "bypassPermissions",
        "--always-approve",
        "--no-memory",
        "--model",
        resolved_model,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=str(execution_dir),
        )
    except subprocess.TimeoutExpired as exc:
        staged_response_path.unlink(missing_ok=True)
        raise GrokCliTimeoutError(
            "Grok CLI timed out after "
            f"{timeout_seconds} seconds for phase {phase or 'unknown'}. "
            "Increase GROK_CLI_TIMEOUT_SECONDS if this phase is expected to run longer."
        ) from exc
    if result.returncode != 0:
        raise RuntimeError(
            "Grok CLI failed with exit code "
            f"{result.returncode}.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    if not staged_response_path.exists():
        raise ValueError(
            f"Grok CLI exited successfully but did not write {staged_response_path}"
        )

    staged_text = staged_response_path.read_text(encoding="utf-8").strip()
    if not staged_text:
        raise ValueError(f"Grok CLI wrote empty staged response: {staged_response_path}")
    try:
        parsed = schema.model_validate_json(staged_text)
    except ValidationError as exc:
        raise ValueError(
            f"Structured JSON validation failed for schema {schema.__name__}: {exc}"
        ) from exc

    stdout_payload = _parse_stdout_payload(result.stdout)
    response_id = (
        str(stdout_payload.get("requestId") or "").strip()
        or str(stdout_payload.get("sessionId") or "").strip()
        or f"grok-cli-{_safe_timestamp()}"
    )
    raw = GrokCliResponse(
        content=staged_text,
        id=response_id,
        stdout=result.stdout,
        stderr=result.stderr,
        prompt_file=str(prompt_path),
        staged_response_file=str(staged_response_path),
    )

    if session_state_path is not None:
        session = _read_session_payload(session_state_path)
        session.update(
            {
                "backend": "grok_cli",
                "model": resolved_model,
                "last_response_id": response_id,
                "updated_at": _utc_now(),
                "prompt_file": str(prompt_path),
                "staged_response_file": str(staged_response_path),
            }
        )
        if phase:
            session["phase"] = phase
        else:
            session.pop("phase", None)
        _write_session_payload(session_state_path, session)

    return raw, parsed
