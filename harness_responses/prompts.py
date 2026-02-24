"""
Prompt composer for harness_responses.

Loads phase-specific prompts from harness_responses/prompts/<phase>/.
No dependencies on harness/.
"""

import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from harness_responses.collections import CollectionSearchResult, search_manim_collection

PROMPTS_DIR = Path(__file__).parent / "prompts"
TEMPLATES_DIR = Path(__file__).parent / "templates"

PHASE_DIRS: Dict[str, str] = {
    "plan": "plan",
    "narration": "narration",
    "build_scenes": "build_scenes",
    "scene_qc": "scene_qc",
    "scene_repair": "scene_repair",
}

PLACEHOLDER_RE = re.compile(r"{{\s*([A-Za-z0-9_]+)\s*}}")
DEFAULT_SPEECH_WPM = 150
_LAST_RETRIEVAL_INFO: Dict[str, Any] = {}


def consume_last_retrieval_info() -> Dict[str, Any]:
    """Return and clear retrieval metadata from the latest prompt composition."""
    global _LAST_RETRIEVAL_INFO
    out = dict(_LAST_RETRIEVAL_INFO)
    _LAST_RETRIEVAL_INFO = {}
    return out


def _record_retrieval_info(phase: str, result: Optional[CollectionSearchResult]) -> None:
    global _LAST_RETRIEVAL_INFO
    if result is None:
        _LAST_RETRIEVAL_INFO = {}
        return
    _LAST_RETRIEVAL_INFO = {
        "phase": phase,
        "query": result.query,
        "collection_id": result.collection_id,
        "limit": result.limit,
        "hit_count": result.hit_count,
        "error": result.error,
        "chunks": result.chunks,
        "reference_section": result.formatted_reference,
    }


def _extract_error_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    if not text:
        return tokens

    patterns = [
        r"NameError:\s*name\s*'([^']+)'",
        r"AttributeError:\s*'[^']+'\s*object has no attribute\s*'([^']+)'",
        r"unexpected keyword argument\s*'([^']+)'",
        r"TypeError:\s*([A-Za-z_][A-Za-z0-9_\.]*)",
        r"ImportError:\s*cannot import name\s*'([^']+)'",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, text):
            candidate = match.strip()
            if candidate:
                tokens.append(candidate)

    seen = set()
    unique: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique[:12]


def _build_reference_query(
    *,
    phase: str,
    scene_id: str,
    narration_key: str,
    scene_title: str,
    scene_source: str,
    scene_details: str,
    scene_narration: str,
    retry_context: str,
) -> str:
    query_parts: list[str] = []
    query_parts.append(f"Phase: {phase}")
    if scene_id:
        query_parts.append(f"Scene ID: {scene_id}")
    if narration_key:
        query_parts.append(f"Narration key: {narration_key}")
    if scene_title and scene_title != "Unknown":
        query_parts.append(f"Scene title: {scene_title}")
    if scene_source:
        query_parts.append("Current scene source:\n```python\n" + scene_source + "\n```")
    if scene_details and scene_details != "N/A":
        query_parts.append(f"Scene details: {scene_details}")

    retry = (retry_context or "").strip()
    if retry:
        query_parts.append("Full error stacktrace/context:\n```text\n" + retry + "\n```")
        tokens = _extract_error_tokens(retry)
        if tokens:
            query_parts.append("Failing API symbols/tokens: " + ", ".join(tokens))

    narration = (scene_narration or "").strip()
    if narration:
        query_parts.append("Narration intent:\n" + narration[:800])

    query_parts.append(
        "Find official Manim CE usage patterns and correct API signatures for this failure."
    )
    return "\n\n".join(query_parts)


def _read_file(path: Path) -> str:
    """Read a file; fail fast if missing."""
    if not path.exists():
        raise FileNotFoundError(f"Required prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def _render(template_text: str, values: Dict[str, Any]) -> str:
    """Render {{placeholders}}; missing keys become empty strings."""
    left_esc = "__FHR_LBRACE__"
    right_esc = "__FHR_RBRACE__"
    working = template_text.replace("{{{{", left_esc).replace("}}}}", right_esc)

    def replace(match: re.Match) -> str:
        key = match.group(1)
        val = values.get(key, "")
        return "" if val is None else str(val)

    rendered = PLACEHOLDER_RE.sub(replace, working)
    return rendered.replace(left_esc, "{{").replace(right_esc, "}}")


def _resolve_project_file(project_dir: Path, configured_name: Any, default_name: str) -> Path:
    if isinstance(configured_name, str) and configured_name.strip():
        return project_dir / configured_name
    return project_dir / default_name


def _scene_id_to_class_name(scene_id: str) -> str:
    parts = [part for part in str(scene_id).split("_") if part]
    return "".join(part.capitalize() for part in parts)


def _load_project_state(project_dir: Path) -> Dict[str, Any]:
    state_file = project_dir / "project_state.json"
    if not state_file.exists():
        raise FileNotFoundError(f"Project state file not found: {state_file}")
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_script_dict(narration_content: str) -> Optional[Dict[str, str]]:
    try:
        tree = ast.parse(narration_content)
    except SyntaxError:
        return None

    script_value = None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "SCRIPT"
            for target in node.targets
        ):
            continue
        script_value = node.value
        break

    if script_value is None:
        return None

    try:
        script_dict = ast.literal_eval(script_value)
    except (ValueError, SyntaxError):
        return None

    if not isinstance(script_dict, dict):
        return None

    normalized: Dict[str, str] = {}
    for key, value in script_dict.items():
        if not isinstance(key, str) or not isinstance(value, str):
            continue
        stripped = value.strip()
        if stripped:
            normalized[key] = stripped
    return normalized


def _resolve_narration_binding(
    narration_content: str, preferred_key: str, fallback_key: str
) -> Tuple[Optional[str], Optional[str]]:
    script_dict = _extract_script_dict(narration_content)
    if not script_dict:
        return None, None

    if preferred_key and preferred_key in script_dict:
        return preferred_key, script_dict[preferred_key]
    if fallback_key and fallback_key in script_dict:
        return fallback_key, script_dict[fallback_key]
    return None, None


def _count_words(text: str) -> int:
    if not text:
        return 0
    return len(re.findall(r"[A-Za-z0-9']+", text))


def _estimate_duration_seconds(word_count: int, wpm: int = DEFAULT_SPEECH_WPM) -> int:
    if word_count <= 0 or wpm <= 0:
        return 0
    return int(round(word_count / (wpm / 60.0)))


def _format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0s"
    mins = seconds // 60
    secs = seconds % 60
    if mins > 0:
        return f"{mins}m {secs:02d}s"
    return f"{secs}s"


def _truncate_retry_context(text: str) -> str:
    return (text or "").strip()


def _compose_plan_prompt(topic: str, retry_context: str) -> Tuple[str, str]:
    phase_dir = PROMPTS_DIR / PHASE_DIRS["plan"]
    values: Dict[str, Any] = {"topic": topic}
    system_prompt = _render(_read_file(phase_dir / "system.md"), values)
    user_prompt = _render(_read_file(phase_dir / "user.md"), values)
    retry_context = _truncate_retry_context(retry_context)
    if retry_context:
        user_prompt = (
            user_prompt.rstrip()
            + f"\n\nRetry context (previous attempt failed):\n{retry_context}\n"
        )
    retrieval = search_manim_collection(user_prompt)
    _record_retrieval_info("plan", retrieval)
    return system_prompt, user_prompt


def _build_scene_prompt_values(
    state: Dict[str, Any], project_dir: Path
) -> Dict[str, Any]:
    plan_file = _resolve_project_file(project_dir, state.get("plan_file"), "plan.json")
    plan_data = json.loads(_read_file(plan_file))

    narration_file = _resolve_project_file(
        project_dir,
        state.get("narration_file"),
        "narration_script.py",
    )
    narration_content = _read_file(narration_file)

    scenes = state.get("scenes", [])
    current_index = state.get("current_scene_index", 0)

    if current_index < len(scenes):
        current_scene = scenes[current_index]
        scene_id = current_scene.get("id", f"scene_{current_index + 1:02d}")
        scene_title = current_scene.get("title", "Unknown")
        narration_key = current_scene.get("narration_key", scene_id)
        scene_file_name = current_scene.get("file", f"{scene_id}.py")
        scene_class_name = current_scene.get(
            "class_name", _scene_id_to_class_name(scene_id)
        )
        plan_scene = None
        for ps in plan_data.get("scenes", []):
            if ps.get("id") == scene_id:
                plan_scene = ps
                break
        scene_details = json.dumps(plan_scene, indent=2) if plan_scene else "N/A"
    else:
        scene_id = f"scene_{current_index + 1:02d}"
        scene_title = "Unknown"
        narration_key = scene_id
        scene_file_name = f"{scene_id}.py"
        scene_class_name = _scene_id_to_class_name(scene_id)
        scene_details = "N/A"

    resolved_key, scene_narration = _resolve_narration_binding(
        narration_content, narration_key, scene_id
    )
    if not scene_narration or not resolved_key:
        raise ValueError(
            f"Could not extract SCRIPT[{narration_key!r}] or SCRIPT[{scene_id!r}] from "
            f"{narration_file.name}"
        )

    narration_word_count = _count_words(scene_narration)
    estimated_duration_seconds = _estimate_duration_seconds(
        narration_word_count, DEFAULT_SPEECH_WPM
    )
    estimated_duration_text = _format_duration(estimated_duration_seconds)

    return {
        "scene_id": scene_id,
        "scene_file_name": scene_file_name,
        "scene_class_name": scene_class_name,
        "narration_key": resolved_key,
        "scene_title": scene_title,
        "scene_details": scene_details,
        "scene_narration": scene_narration,
        "narration_word_count": narration_word_count,
        "speech_wpm": DEFAULT_SPEECH_WPM,
        "estimated_duration_seconds": estimated_duration_seconds,
        "estimated_duration_text": estimated_duration_text,
    }


def _compose_build_scenes_prompt(
    state: Dict[str, Any],
    project_dir: Path,
    retry_context: str,
    template_file_reference: str = "",
) -> Tuple[str, str]:
    phase_dir = PROMPTS_DIR / PHASE_DIRS["build_scenes"]
    values = _build_scene_prompt_values(state, project_dir)
    values["template_file_reference"] = template_file_reference
    retry_context = _truncate_retry_context(retry_context)
    values["retry_section"] = (
        (
            "## RETRY CONTEXT\n\n"
            "This scene previously failed with the following error:\n\n"
            "```\n"
            f"{retry_context}\n"
            "```\n\n"
            "Please fix the issue and generate a corrected version."
        )
        if retry_context
        else ""
    )
    system_prompt = _render(_read_file(phase_dir / "system.md"), values)
    ref_query = _build_reference_query(
        phase="build_scenes",
        scene_id="",
        narration_key="",
        scene_title="",
        scene_source=_read_file(project_dir / str(values.get("scene_file_name", ""))),
        scene_details=str(values.get("scene_details", "")),
        scene_narration=str(values.get("scene_narration", "")),
        retry_context=retry_context,
    )
    ref_query = (
        f"{ref_query}\n\nSystem prompt:\n{system_prompt}"
    )
    current_scene_index = int(state.get("current_scene_index") or 0)
    if current_scene_index == 0:
        retrieval = search_manim_collection(ref_query)
    else:
        retrieval = CollectionSearchResult(
            query=ref_query,
            collection_id="",
            limit=10,
            chunks=[],
            error="skipped_not_first_scene",
        )
    _record_retrieval_info("build_scenes", retrieval)
    values["reference_section"] = retrieval.formatted_reference

    user_prompt = _render(_read_file(phase_dir / "user.md"), values)
    return system_prompt, user_prompt


def _compose_narration_prompt(
    state: Dict[str, Any],
    project_dir: Path,
    retry_context: str,
) -> Tuple[str, str]:
    phase_dir = PROMPTS_DIR / PHASE_DIRS["narration"]
    plan_file = _resolve_project_file(project_dir, state.get("plan_file"), "plan.json")
    plan_data = json.loads(_read_file(plan_file))

    retry_context = _truncate_retry_context(retry_context)
    retry_block = ""
    if retry_context:
        retry_block = (
            "## RETRY CONTEXT\n\n"
            "The previous narration attempt failed with the following error details:\n\n"
            "```\n"
            f"{retry_context}\n"
            "```\n\n"
            "Fix this failure and return only the required top-level JSON object.\n"
        )

    values: Dict[str, Any] = {
        "title": plan_data.get("title", "Unknown"),
        "plan_json": json.dumps(plan_data, indent=2),
        "retry_context_block": retry_block,
    }
    system_prompt = _render(_read_file(phase_dir / "system.md"), values)
    user_prompt = _render(_read_file(phase_dir / "user.md"), values)
    retrieval = search_manim_collection(user_prompt)
    _record_retrieval_info("narration", retrieval)
    return system_prompt, user_prompt


def _compose_scene_qc_prompt(
    state: Dict[str, Any],
    project_dir: Path,
) -> Tuple[str, str]:
    _record_retrieval_info("scene_qc", None)
    phase_dir = PROMPTS_DIR / PHASE_DIRS["scene_qc"]
    scenes = state.get("scenes", [])
    scene_files_content = []
    for scene in scenes:
        scene_file_path = project_dir / scene.get("file", "")
        if scene_file_path.exists():
            content = _read_file(scene_file_path)
            scene_files_content.append(
                f"\n### {scene.get('file')}\n\n```python\n{content}\n```\n"
            )
    all_scenes = "\n".join(scene_files_content)
    scenes_doc = ""
    scenes_doc_path = TEMPLATES_DIR / "phase_scenes.md"
    if scenes_doc_path.exists():
        scenes_doc = _read_file(scenes_doc_path)

    values: Dict[str, Any] = {
        "all_scenes": all_scenes,
        "scenes_doc": scenes_doc,
    }
    system_prompt = _render(_read_file(phase_dir / "system.md"), values)
    user_prompt = _render(_read_file(phase_dir / "user.md"), values)
    return system_prompt, user_prompt


def _compose_scene_repair_prompt(
    state: Dict[str, Any],
    project_dir: Path,
    scene_file: Path,
    retry_context: str,
) -> Tuple[str, str]:
    phase_dir = PROMPTS_DIR / PHASE_DIRS["scene_repair"]
    broken_file_content = _read_file(scene_file)
    values = _build_scene_prompt_values(state, project_dir)
    retry_context = _truncate_retry_context(retry_context)
    ref_query = _build_reference_query(
        phase="scene_repair",
        scene_id=str(values.get("scene_id", "")),
        narration_key=str(values.get("narration_key", "")),
        scene_title=str(values.get("scene_title", "")),
        scene_source=broken_file_content,
        scene_details=str(values.get("scene_details", "")),
        scene_narration=str(values.get("scene_narration", "")),
        retry_context=retry_context,
    )
    retrieval = search_manim_collection(ref_query)
    _record_retrieval_info("scene_repair", retrieval)

    values.update(
        {
            "broken_file_name": scene_file.name,
            "broken_file_content": broken_file_content,
            "retry_context": retry_context or "Unknown error",
            "reference_section": retrieval.formatted_reference,
        }
    )
    system_prompt = _render(_read_file(phase_dir / "system.md"), values)
    user_prompt = _render(_read_file(phase_dir / "user.md"), values)
    return system_prompt, user_prompt


def compose_prompt(
    phase: str,
    project_dir: Path,
    topic: str = "",
    retry_context: str = "",
    scene_file: Optional[Path] = None,
    template_file_reference: str = "",
) -> Tuple[str, str]:
    """
    Compose system and user prompts for a phase.

    Args:
        phase: Phase name (must be in PHASE_DIRS)
        project_dir: Project directory containing project_state.json and artifacts
        topic: Topic string for plan phase
        retry_context: Optional retry context for failed prior attempts
        scene_file: Required for scene_repair phase

    Returns:
        (system_prompt, user_prompt) tuple
    """
    if phase not in PHASE_DIRS:
        raise ValueError(
            f"Phase '{phase}' is not implemented in harness_responses. "
            f"Implemented phases: {', '.join(PHASE_DIRS)}"
        )

    _record_retrieval_info(phase, None)

    if phase == "plan":
        return _compose_plan_prompt(topic, retry_context)

    state = _load_project_state(project_dir)

    if phase == "build_scenes":
        return _compose_build_scenes_prompt(
            state,
            project_dir,
            retry_context,
            template_file_reference,
        )

    if phase == "narration":
        return _compose_narration_prompt(state, project_dir, retry_context)

    if phase == "scene_qc":
        return _compose_scene_qc_prompt(state, project_dir)

    if phase == "scene_repair":
        if scene_file is None:
            raise ValueError("scene_file is required for scene_repair phase")
        return _compose_scene_repair_prompt(
            state, project_dir, scene_file, retry_context
        )

    raise ValueError(f"Unknown phase: {phase}")
