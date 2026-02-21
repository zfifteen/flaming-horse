"""
Semantic validator and artifact writer for harness_responses.

Responsibilities:
  - Layer 2 semantic validation (business rules beyond schema structure).
  - Convert validated Pydantic models to on-disk artifact format.
  - Write failure diagnostics to log/responses_last_response.json on error.

No dependencies on harness/.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from harness_responses.schemas.plan import PlanResponse

# Semantic validation bounds (from plan manifest)
_PLAN_MIN_SCENES = 8
_PLAN_MAX_SCENES = 12
_PLAN_MIN_SCENE_DURATION = 20
_PLAN_MAX_SCENE_DURATION = 45
_PLAN_MIN_TOTAL_DURATION = 240
_PLAN_MAX_TOTAL_DURATION = 480


class SemanticValidationError(ValueError):
    """Raised when a phase response passes schema validation but fails semantic rules."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_failure_diagnostic(
    log_dir: Path,
    raw_response: Any,
    extracted_content: Any,
    validation_error: str,
) -> None:
    """Write raw response + validation error to log/responses_last_response.json."""
    log_dir.mkdir(parents=True, exist_ok=True)
    diag_path = log_dir / "responses_last_response.json"

    # Serialize raw_response safely (xai_sdk Response objects may not be JSON-serializable)
    try:
        raw_serializable = {
            "id": getattr(raw_response, "id", None) if raw_response is not None else None,
            "content": getattr(raw_response, "content", None) if raw_response is not None else None,
        }
    except Exception:
        raw_serializable = {"error": "could not serialize raw response"}

    diagnostic = {
        "timestamp_utc": _utc_now(),
        "raw_response": raw_serializable,
        "extracted_content": extracted_content,
        "validation_error": validation_error,
    }
    try:
        diag_path.write_text(json.dumps(diagnostic, indent=2, default=str), encoding="utf-8")
    except Exception:
        pass  # Best-effort; don't mask the original error


def validate_and_write_plan(
    parsed: PlanResponse,
    project_dir: Path,
    raw_response: Any = None,
) -> bool:
    """
    Semantic-validate a PlanResponse and write plan.json.

    Args:
        parsed: Validated Pydantic PlanResponse instance.
        project_dir: Project directory for artifact output.
        raw_response: Raw xai_sdk Response object for diagnostics (optional).

    Returns:
        True on success.

    Raises:
        SemanticValidationError: When semantic rules are violated.
    """
    log_dir = project_dir / "log"
    content_repr = parsed.model_dump()

    def _fail(msg: str) -> None:
        _write_failure_diagnostic(log_dir, raw_response, content_repr, msg)
        raise SemanticValidationError(msg)

    # Title and description non-empty
    if not parsed.title.strip():
        _fail("plan.title must not be empty")
    if not parsed.description.strip():
        _fail("plan.description must not be empty")

    # Scene count
    scene_count = len(parsed.scenes)
    if not (_PLAN_MIN_SCENES <= scene_count <= _PLAN_MAX_SCENES):
        _fail(
            f"plan.scenes must have {_PLAN_MIN_SCENES}-{_PLAN_MAX_SCENES} scenes, "
            f"got {scene_count}"
        )

    # Total duration
    if not (_PLAN_MIN_TOTAL_DURATION <= parsed.target_duration_seconds <= _PLAN_MAX_TOTAL_DURATION):
        _fail(
            f"plan.target_duration_seconds must be {_PLAN_MIN_TOTAL_DURATION}-"
            f"{_PLAN_MAX_TOTAL_DURATION}, got {parsed.target_duration_seconds}"
        )

    # Per-scene validation
    for idx, scene in enumerate(parsed.scenes):
        if not scene.title.strip():
            _fail(f"plan.scenes[{idx}].title must not be empty")
        if not scene.description.strip():
            _fail(f"plan.scenes[{idx}].description must not be empty")
        dur = scene.estimated_duration_seconds
        if not (_PLAN_MIN_SCENE_DURATION <= dur <= _PLAN_MAX_SCENE_DURATION):
            _fail(
                f"plan.scenes[{idx}].estimated_duration_seconds must be "
                f"{_PLAN_MIN_SCENE_DURATION}-{_PLAN_MAX_SCENE_DURATION}, got {dur}"
            )
        if not scene.visual_ideas:
            _fail(f"plan.scenes[{idx}].visual_ideas must not be empty")
        for vi_idx, idea in enumerate(scene.visual_ideas):
            if not isinstance(idea, str) or not idea.strip():
                _fail(
                    f"plan.scenes[{idx}].visual_ideas[{vi_idx}] must be a non-empty string"
                )

    # Build plan dict with harness-assigned IDs (matching legacy format)
    scenes_out = []
    for idx, scene in enumerate(parsed.scenes):
        scene_number = idx + 1
        scene_id = f"scene_{scene_number:02d}"
        scenes_out.append(
            {
                "id": scene_id,
                "narration_key": scene_id,
                "title": scene.title,
                "description": scene.description,
                "estimated_duration_seconds": scene.estimated_duration_seconds,
                "visual_ideas": scene.visual_ideas,
            }
        )

    plan_dict = {
        "title": parsed.title,
        "description": parsed.description,
        "target_duration_seconds": parsed.target_duration_seconds,
        "scenes": scenes_out,
    }

    plan_path = project_dir / "plan.json"
    plan_path.write_text(json.dumps(plan_dict, indent=2), encoding="utf-8")
    print(f"✅ Wrote plan.json ({scene_count} scenes)")
    return True


def write_phase_artifacts(
    phase: str,
    parsed: Any,
    project_dir: Path,
    raw_response: Any = None,
) -> bool:
    """
    Dispatch to phase-specific artifact writer.

    Args:
        phase: Phase name.
        parsed: Pydantic model instance from chat.parse().
        project_dir: Project directory.
        raw_response: Raw API response for diagnostics.

    Returns:
        True on success.
    """
    if phase == "plan":
        return validate_and_write_plan(parsed, project_dir, raw_response)

    raise NotImplementedError(
        f"Phase '{phase}' artifact writing is not yet implemented in harness_responses"
    )
