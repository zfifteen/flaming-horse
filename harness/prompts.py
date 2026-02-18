"""
Prompt composer for the Flaming Horse agent harness.

Assembles phase-specific prompts from modular prompt files.
"""

import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

PROMPTS_DIR = Path(__file__).parent / "prompts"
TEMPLATES_DIR = Path(__file__).parent / "templates"

PHASE_DIRS = {
    "plan": "00_plan",
    "review": "01_review",
    "narration": "02_narration",
    "training": "03_training",
    "build_scenes": "04_build_scenes",
    "scene_qc": "05_scene_qc",
    "scene_repair": "06_scene_repair",
}

PLACEHOLDER_RE = re.compile(r"{{\s*([A-Za-z0-9_]+)\s*}}")


def read_file(path: Path) -> str:
    """Read a file and return contents. Fail fast if missing."""
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path.read_text(encoding="utf-8")


def render_template(template_text: str, values: Dict[str, Any]) -> str:
    """Render {{placeholders}} with strict unresolved placeholder failures."""
    # Protect literal braces represented as {{{{...}}}} in prompt text.
    left_escape = "__FH_LBRACE_ESCAPE__"
    right_escape = "__FH_RBRACE_ESCAPE__"
    working = template_text.replace("{{{{", left_escape).replace("}}}}", right_escape)

    placeholders = {m.group(1) for m in PLACEHOLDER_RE.finditer(working)}
    missing = {key for key in placeholders if key not in values}
    if missing:
        joined = ", ".join(sorted(missing))
        raise ValueError(f"Unresolved template placeholders: {joined}")

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        value = values[key]
        return "" if value is None else str(value)

    rendered = PLACEHOLDER_RE.sub(replace, working)
    rendered = rendered.replace(left_escape, "{{").replace(right_escape, "}}")

    return rendered


def load_prompt_template(phase: str, filename: str, values: Dict[str, Any]) -> str:
    if phase not in PHASE_DIRS:
        raise ValueError(f"Unknown phase: {phase}")
    path = PROMPTS_DIR / PHASE_DIRS[phase] / filename
    return render_template(read_file(path), values)


def resolve_project_file(
    project_dir: Path, configured_name: Any, default_name: str
) -> Path:
    if isinstance(configured_name, str) and configured_name.strip():
        return project_dir / configured_name
    return project_dir / default_name


def scene_id_to_class_name(scene_id: str) -> str:
    parts = [part for part in str(scene_id).split("_") if part]
    return "".join(part.capitalize() for part in parts)


def extract_scene_narration(
    narration_content: str, narration_key: str
) -> Optional[str]:
    """Extract SCRIPT[narration_key] from narration_script.py content."""
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

    narration = script_dict.get(narration_key)
    if isinstance(narration, str):
        stripped = narration.strip()
        return stripped if stripped else None
    return None


def compose_plan_prompt(state: Dict[str, Any], topic: Optional[str]) -> Tuple[str, str]:
    system_prompt = load_prompt_template(
        "plan",
        "system.md",
        {
            "core_rules": read_file(PROMPTS_DIR / "_shared" / "core_rules.md"),
            "pipeline_doc": read_file(TEMPLATES_DIR / "manim_content_pipeline.md"),
        },
    )
    user_prompt = load_prompt_template("plan", "user.md", {"topic": topic or ""})
    return system_prompt, user_prompt


def compose_review_prompt(state: Dict[str, Any], project_dir: Path) -> Tuple[str, str]:
    _ = (state, project_dir)
    return (
        load_prompt_template("review", "system.md", {}),
        load_prompt_template("review", "user.md", {}),
    )


def compose_narration_prompt(
    state: Dict[str, Any], project_dir: Path
) -> Tuple[str, str]:
    plan_file = resolve_project_file(project_dir, state.get("plan_file"), "plan.json")
    plan_data = json.loads(read_file(plan_file))

    system_prompt = load_prompt_template(
        "narration",
        "system.md",
        {
            "core_rules": read_file(PROMPTS_DIR / "_shared" / "core_rules.md"),
            "narration_system": read_file(
                PROMPTS_DIR / "02_narration" / "narration_system.md"
            ),
            "pipeline_doc": read_file(TEMPLATES_DIR / "manim_content_pipeline.md"),
        },
    )
    user_prompt = load_prompt_template(
        "narration",
        "user.md",
        {
            "title": plan_data.get("title", "Unknown"),
            "plan_json": json.dumps(plan_data, indent=2),
        },
    )
    return system_prompt, user_prompt


def compose_build_scenes_prompt(
    state: Dict[str, Any], project_dir: Path, retry_context: Optional[str] = None
) -> Tuple[str, str]:
    plan_file = resolve_project_file(project_dir, state.get("plan_file"), "plan.json")
    plan_data = json.loads(read_file(plan_file))

    narration_file = resolve_project_file(
        project_dir,
        state.get("narration_file"),
        "narration_script.py",
    )
    narration_content = read_file(narration_file)

    scenes = state.get("scenes", [])
    current_index = state.get("current_scene_index", 0)

    if current_index < len(scenes):
        current_scene = scenes[current_index]
        scene_id = current_scene.get("id", f"scene_{current_index + 1:02d}")
        scene_title = current_scene.get("title", "Unknown")
        narration_key = current_scene.get("narration_key", scene_id)
        scene_file_name = current_scene.get("file", f"{scene_id}.py")
        scene_class_name = current_scene.get(
            "class_name", scene_id_to_class_name(scene_id)
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
        scene_class_name = scene_id_to_class_name(scene_id)
        scene_details = "N/A"

    scene_narration = extract_scene_narration(narration_content, narration_key)
    if not scene_narration:
        raise ValueError(
            f"Could not extract SCRIPT[{narration_key!r}] from {narration_file.name}"
        )

    reference_section = ""
    if current_index == 0:
        reference_section = (
            "## Manim CE Reference Documentation\n\n"
            "Use ONLY syntax documented in the official Manim CE reference:\n"
            "https://docs.manim.community/en/stable/reference.html\n\n"
            "This is your authoritative source for valid Manim classes, methods, and parameters."
        )

    retry_section = ""
    if retry_context:
        retry_section = (
            "## RETRY CONTEXT\n\n"
            "This scene previously failed with the following error:\n\n"
            "```\n"
            f"{retry_context}\n"
            "```\n\n"
            "Please fix the issue and generate a corrected version."
        )

    rendered_build_scenes_system = render_template(
        read_file(PROMPTS_DIR / "04_build_scenes" / "build_scenes_system.md"),
        {
            "TITLE": "{{TITLE}}",
            "SUBTITLE": "{{SUBTITLE}}",
            "KEY_POINT_1": "{{KEY_POINT_1}}",
            "KEY_POINT_2": "{{KEY_POINT_2}}",
            "KEY_POINT_3": "{{KEY_POINT_3}}",
        },
    )

    system_prompt = load_prompt_template(
        "build_scenes",
        "system.md",
        {
            "core_rules": read_file(PROMPTS_DIR / "_shared" / "core_rules.md"),
            "build_scenes_system": rendered_build_scenes_system,
            "template_doc": read_file(TEMPLATES_DIR / "manim_template.py.txt"),
            "config_guide": read_file(TEMPLATES_DIR / "manim_config_guide.md"),
            "visual_helpers": read_file(TEMPLATES_DIR / "visual_helpers.md"),
        },
    )
    user_prompt = load_prompt_template(
        "build_scenes",
        "user.md",
        {
            "scene_id": scene_id,
            "scene_file_name": scene_file_name,
            "scene_class_name": scene_class_name,
            "narration_key": narration_key,
            "scene_title": scene_title,
            "scene_details": scene_details,
            "scene_narration": scene_narration,
            "reference_section": reference_section,
            "retry_section": retry_section,
        },
    )
    return system_prompt, user_prompt


def compose_scene_qc_prompt(
    state: Dict[str, Any], project_dir: Path
) -> Tuple[str, str]:
    scenes = state.get("scenes", [])
    scene_files_content = []

    for scene in scenes:
        scene_file_path = project_dir / scene.get("file", "")
        if scene_file_path.exists():
            content = read_file(scene_file_path)
            scene_files_content.append(
                f"\n### {scene.get('file')}\n\n```python\n{content}\n```\n"
            )

    all_scenes = "\n".join(scene_files_content)

    system_prompt = load_prompt_template(
        "scene_qc",
        "system.md",
        {
            "core_rules": read_file(PROMPTS_DIR / "_shared" / "core_rules.md"),
            "qc_system": read_file(PROMPTS_DIR / "05_scene_qc" / "scene_qc_system.md"),
            "scenes_doc": read_file(TEMPLATES_DIR / "phase_scenes.md"),
        },
    )
    user_prompt = load_prompt_template("scene_qc", "user.md", {"all_scenes": all_scenes})
    return system_prompt, user_prompt


def compose_scene_repair_prompt(
    state: Dict[str, Any],
    project_dir: Path,
    scene_file: Path,
    retry_context: Optional[str],
) -> Tuple[str, str]:
    broken_file_content = read_file(scene_file)

    plan_file = resolve_project_file(project_dir, state.get("plan_file"), "plan.json")
    plan_data = json.loads(read_file(plan_file))

    narration_file = resolve_project_file(
        project_dir,
        state.get("narration_file"),
        "narration_script.py",
    )
    narration_content = read_file(narration_file)

    scenes = state.get("scenes", [])
    current_index = state.get("current_scene_index", 0)

    scene_id = scene_file.stem
    scene_title = "Unknown"
    narration_key = scene_id
    scene_class_name = scene_id_to_class_name(scene_id)
    scene_file_name = scene_file.name

    if current_index < len(scenes):
        current_scene = scenes[current_index]
        scene_id = current_scene.get("id", scene_id)
        scene_title = current_scene.get("title", scene_title)
        narration_key = current_scene.get("narration_key", narration_key)
        scene_class_name = current_scene.get(
            "class_name", scene_id_to_class_name(scene_id)
        )
        scene_file_name = current_scene.get("file", scene_file_name)

    plan_scene = None
    for ps in plan_data.get("scenes", []):
        if ps.get("id") == scene_id:
            plan_scene = ps
            break

    scene_details = json.dumps(plan_scene, indent=2) if plan_scene else "N/A"
    scene_narration = extract_scene_narration(narration_content, narration_key) or "N/A"

    system_prompt = load_prompt_template(
        "scene_repair",
        "system.md",
        {
            "core_rules": read_file(PROMPTS_DIR / "_shared" / "core_rules.md"),
            "repair_system": read_file(
                PROMPTS_DIR / "06_scene_repair" / "repair_system.md"
            ),
        },
    )
    user_prompt = load_prompt_template(
        "scene_repair",
        "user.md",
        {
            "scene_id": scene_id,
            "scene_file_name": scene_file_name,
            "scene_class_name": scene_class_name,
            "narration_key": narration_key,
            "scene_title": scene_title,
            "scene_details": scene_details,
            "scene_narration": scene_narration,
            "broken_file_name": scene_file.name,
            "broken_file_content": broken_file_content,
            "retry_context": retry_context or "Unknown error",
        },
    )
    return system_prompt, user_prompt


def compose_training_prompt(
    state: Dict[str, Any],
    project_dir: Path,
) -> Tuple[str, str]:
    _ = (state, project_dir)
    system_prompt = load_prompt_template(
        "training",
        "system.md",
        {"manim_training": read_file(PROMPTS_DIR / "03_training" / "manim_training.md")},
    )
    user_prompt = load_prompt_template("training", "user.md", {})
    return system_prompt, user_prompt


def compose_prompt(
    phase: str,
    state: Dict[str, Any],
    topic: Optional[str] = None,
    retry_context: Optional[str] = None,
    scene_file: Optional[Path] = None,
    project_dir: Optional[Path] = None,
) -> Tuple[str, str]:
    """Compose phase-specific prompts."""
    if not project_dir:
        raise ValueError("project_dir is required")

    if phase == "plan":
        return compose_plan_prompt(state, topic)
    if phase == "review":
        return compose_review_prompt(state, project_dir)
    if phase == "narration":
        return compose_narration_prompt(state, project_dir)
    if phase == "training":
        return compose_training_prompt(state, project_dir)
    if phase == "build_scenes":
        return compose_build_scenes_prompt(state, project_dir, retry_context)
    if phase == "scene_qc":
        return compose_scene_qc_prompt(state, project_dir)
    if phase == "scene_repair":
        if not scene_file:
            raise ValueError("scene_file is required for scene_repair phase")
        return compose_scene_repair_prompt(state, project_dir, scene_file, retry_context)

    raise ValueError(f"Unknown phase: {phase}")
