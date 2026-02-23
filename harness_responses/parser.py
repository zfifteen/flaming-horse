"""
Semantic validator and artifact writer for harness_responses.

Responsibilities:
  - Layer 2 semantic validation (business rules beyond schema structure).
  - Convert validated Pydantic models to on-disk artifact format.
  - Write failure diagnostics to log/responses_last_response.json on error.

No dependencies on harness/.
"""

import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness_responses.schemas.build_scenes import BuildScenesResponse
from harness_responses.schemas.plan import PlanResponse
from harness_responses.schemas.scene_repair import SceneRepairResponse

# Semantic validation bounds (from plan manifest)
_PLAN_MIN_SCENES = 8
_PLAN_MAX_SCENES = 12
_PLAN_MIN_SCENE_DURATION = 20
_PLAN_MAX_SCENE_DURATION = 45
_PLAN_MIN_TOTAL_DURATION = 240
_PLAN_MAX_TOTAL_DURATION = 480

_FORBIDDEN_SCENE_BODY_TOKENS = (
    "from manim import",
    "from pathlib import",
    "import numpy",
    "config.frame",
    "class Scene",
    "def construct",
    "SLOT_START:scene_body",
    "SLOT_END:scene_body",
)


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
    except Exception as write_exc:
        print(f"⚠️  Could not write failure diagnostic to {diag_path}: {write_exc}")


def _fail_with_diag(
    project_dir: Path,
    raw_response: Any,
    extracted_content: Any,
    msg: str,
) -> None:
    _write_failure_diagnostic(project_dir / "log", raw_response, extracted_content, msg)
    raise SemanticValidationError(msg)


def _sanitize_code(code: str) -> str:
    code = re.sub(r"</?[A-Za-z][^>\n]*>", "", code)
    code = re.sub(r"^\s*</?[A-Za-z][^>]*>\s*$", "", code, flags=re.MULTILINE)
    code = re.sub(r"^```python\s*", "", code, flags=re.MULTILINE)
    code = re.sub(r"^```\s*$", "", code, flags=re.MULTILINE)
    return code.strip()


def _verify_python_syntax(code: str) -> bool:
    try:
        compile(code, "<string>", "exec")
        return True
    except SyntaxError:
        return False


def _has_executable_self_play_call(body_code: str) -> bool:
    try:
        tree = ast.parse(body_code)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "play":
            continue
        owner = func.value
        if not isinstance(owner, ast.Name) or owner.id != "self":
            continue
        if len(node.args) >= 1:
            return True
    return False


def _validate_scene_body_syntax(body_code: str) -> bool:
    indented_body = "\n".join("    " + line for line in body_code.split("\n"))
    test_code = f"def test():\n{indented_body}\n    pass"
    try:
        compile(test_code, "<string>", "exec")
        return True
    except (SyntaxError, ValueError):
        return False


def _inject_body_into_scaffold(scaffold_path: Path, body_code: str) -> str:
    scaffold_text = scaffold_path.read_text(encoding="utf-8")
    start_marker = "# SLOT_START:scene_body"
    end_marker = "# SLOT_END:scene_body"

    start_idx = scaffold_text.find(start_marker)
    if start_idx == -1:
        raise ValueError(f"SLOT_START marker not found in scaffold {scaffold_path}")

    end_idx = scaffold_text.find(end_marker, start_idx)
    if end_idx == -1:
        raise ValueError(f"SLOT_END marker not found in scaffold {scaffold_path}")

    body_lines = [
        line.strip()
        for line in body_code.strip().split("\n")
        if line.strip() and not line.strip().startswith("#")
    ]
    if not body_lines:
        raise ValueError("Body code must contain at least one non-comment statement")

    lines = body_code.strip().split("\n")
    min_indent = None
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            min_indent = indent if min_indent is None else min(min_indent, indent)
    if min_indent is None:
        min_indent = 0

    indented_lines = []
    for line in lines:
        if line.strip():
            dedented = line[min_indent:] if min_indent < len(line) else line.lstrip()
            indented_lines.append("            " + dedented)
        else:
            indented_lines.append("")

    indented_body = "\n".join(indented_lines)
    header = scaffold_text[: start_idx + len(start_marker)]
    footer = scaffold_text[end_idx:]
    full_code = header + "\n" + indented_body.rstrip() + "\n            " + footer

    if start_marker not in full_code or end_marker not in full_code:
        raise ValueError("Injection corrupted scaffold markers")
    return full_code


def validate_and_write_plan(
    parsed: PlanResponse,
    project_dir: Path,
    raw_response: Any = None,
) -> bool:
    """Semantic-validate a PlanResponse and write plan.json."""
    content_repr = parsed.model_dump()

    def _fail(msg: str) -> None:
        _fail_with_diag(project_dir, raw_response, content_repr, msg)

    if not parsed.title.strip():
        _fail("plan.title must not be empty")
    if not parsed.description.strip():
        _fail("plan.description must not be empty")

    scene_count = len(parsed.scenes)
    if not (_PLAN_MIN_SCENES <= scene_count <= _PLAN_MAX_SCENES):
        _fail(
            f"plan.scenes must have {_PLAN_MIN_SCENES}-{_PLAN_MAX_SCENES} scenes, "
            f"got {scene_count}"
        )

    if not (_PLAN_MIN_TOTAL_DURATION <= parsed.target_duration_seconds <= _PLAN_MAX_TOTAL_DURATION):
        _fail(
            f"plan.target_duration_seconds must be {_PLAN_MIN_TOTAL_DURATION}-"
            f"{_PLAN_MAX_TOTAL_DURATION}, got {parsed.target_duration_seconds}"
        )

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
                _fail(f"plan.scenes[{idx}].visual_ideas[{vi_idx}] must be a non-empty string")

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


def _normalize_and_validate_scene_body(
    phase: str,
    scene_body: str,
    project_dir: Path,
    raw_response: Any,
    extracted_content: Any,
) -> str:
    candidate = _sanitize_code(scene_body)
    if not candidate:
        _fail_with_diag(
            project_dir,
            raw_response,
            extracted_content,
            f"{phase}.scene_body cannot be empty after sanitization",
        )
    if not _verify_python_syntax(candidate):
        _fail_with_diag(
            project_dir,
            raw_response,
            extracted_content,
            f"{phase}.scene_body must be valid Python",
        )
    if any(token in candidate for token in _FORBIDDEN_SCENE_BODY_TOKENS):
        _fail_with_diag(
            project_dir,
            raw_response,
            extracted_content,
            f"{phase}.scene_body must contain body statements only (no imports/class/config/scaffold markers)",
        )
    if re.search(r"with\s+self\.voiceover\(", candidate):
        _fail_with_diag(
            project_dir,
            raw_response,
            extracted_content,
            f"{phase}.scene_body must not include self.voiceover wrapper",
        )
    if candidate.strip().startswith(("class ", "def ", "import ", "from ")):
        _fail_with_diag(
            project_dir,
            raw_response,
            extracted_content,
            f"{phase}.scene_body must not start with class/def/import statements",
        )
    if not _has_executable_self_play_call(candidate):
        _fail_with_diag(
            project_dir,
            raw_response,
            extracted_content,
            f"{phase}.scene_body must contain at least one executable self.play(...) call",
        )
    if not _validate_scene_body_syntax(candidate):
        _fail_with_diag(
            project_dir,
            raw_response,
            extracted_content,
            f"{phase}.scene_body must compile as method-body statements",
        )
    return candidate


def _resolve_scene_file_for_build(project_dir: Path) -> Path:
    state_file = project_dir / "project_state.json"
    if not state_file.exists():
        raise ValueError(f"Project state file not found: {state_file}")
    state = json.loads(state_file.read_text(encoding="utf-8"))
    scenes = state.get("scenes", [])
    current_index = state.get("current_scene_index", 0)
    if current_index >= len(scenes):
        raise ValueError("No more scenes to build")
    current_scene = scenes[current_index]
    scene_id = current_scene.get("id", f"scene_{current_index + 1:02d}")
    scene_file_name = current_scene.get("file", f"{scene_id}.py")
    return project_dir / scene_file_name


def _resolve_scene_file_for_repair(project_dir: Path) -> Path:
    state_file = project_dir / "project_state.json"
    if not state_file.exists():
        raise ValueError(f"Project state file not found: {state_file}")
    state = json.loads(state_file.read_text(encoding="utf-8"))
    explicit_scene_file = state.get("scene_file")
    if isinstance(explicit_scene_file, str) and explicit_scene_file:
        explicit_path = Path(explicit_scene_file)
        return explicit_path if explicit_path.is_absolute() else project_dir / explicit_path

    scenes = state.get("scenes", [])
    current_index = state.get("current_scene_index", 0)
    if current_index >= len(scenes):
        raise ValueError("No scene to repair")
    current_scene = scenes[current_index]
    scene_file_name = current_scene.get("file", f"scene_{current_index + 1:02d}.py")
    return project_dir / scene_file_name


def validate_and_write_build_scenes(
    parsed: BuildScenesResponse,
    project_dir: Path,
    raw_response: Any = None,
) -> bool:
    content_repr = parsed.model_dump()
    scene_file = _resolve_scene_file_for_build(project_dir)
    if not scene_file.exists():
        _fail_with_diag(
            project_dir,
            raw_response,
            content_repr,
            f"Scaffold not found for build_scenes: {scene_file}",
        )

    body = _normalize_and_validate_scene_body(
        "build_scenes", parsed.scene_body, project_dir, raw_response, content_repr
    )
    try:
        full_code = _inject_body_into_scaffold(scene_file, body)
    except ValueError as exc:
        _fail_with_diag(project_dir, raw_response, content_repr, f"Injection failed: {exc}")

    scene_file.write_text(full_code, encoding="utf-8")
    print(f"✅ Injected body into {scene_file}")
    return True


def validate_and_write_scene_repair(
    parsed: SceneRepairResponse,
    project_dir: Path,
    raw_response: Any = None,
) -> bool:
    content_repr = parsed.model_dump()
    scene_file = _resolve_scene_file_for_repair(project_dir)
    if not scene_file.exists():
        _fail_with_diag(
            project_dir,
            raw_response,
            content_repr,
            f"Scene file not found for scene_repair: {scene_file}",
        )

    body = _normalize_and_validate_scene_body(
        "scene_repair", parsed.scene_body, project_dir, raw_response, content_repr
    )
    try:
        full_code = _inject_body_into_scaffold(scene_file, body)
    except ValueError as exc:
        _fail_with_diag(project_dir, raw_response, content_repr, f"Injection failed: {exc}")

    scene_file.write_text(full_code, encoding="utf-8")
    print(f"✅ Injected repaired body into {scene_file}")
    return True


def write_phase_artifacts(
    phase: str,
    parsed: Any,
    project_dir: Path,
    raw_response: Any = None,
) -> bool:
    """Dispatch to phase-specific artifact writer."""
    if phase == "plan":
        return validate_and_write_plan(parsed, project_dir, raw_response)
    if phase == "build_scenes":
        return validate_and_write_build_scenes(parsed, project_dir, raw_response)
    if phase == "scene_repair":
        return validate_and_write_scene_repair(parsed, project_dir, raw_response)

    raise NotImplementedError(
        f"Phase '{phase}' artifact writing is not yet implemented in harness_responses"
    )
