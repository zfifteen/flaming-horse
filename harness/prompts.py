"""
Prompt composer for the Flaming Horse agent harness.

Assembles phase-specific prompts from modular documentation,
reducing context window waste compared to OpenCode.
"""

import json
import ast
from pathlib import Path
from typing import Tuple, Optional, Dict, Any


# Get the repository root
REPO_ROOT = Path(__file__).parent.parent
PROMPT_TEMPLATES_DIR = Path(__file__).parent / "prompt_templates"
REFERENCE_DOCS_DIR = REPO_ROOT / "reference_docs"


def read_file(path: Path) -> str:
    """Read a file and return its contents."""
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path.read_text()


def resolve_project_file(
    project_dir: Path, configured_name: Any, default_name: str
) -> Path:
    """Resolve a project file path with fallback for null/empty state values."""
    if isinstance(configured_name, str) and configured_name.strip():
        return project_dir / configured_name
    return project_dir / default_name


def scene_id_to_class_name(scene_id: str) -> str:
    """Convert scene id like scene_01_intro to Scene01Intro."""
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
    """
    Compose prompts for the plan phase.

    Returns:
        (system_prompt, user_prompt)
    """
    # System prompt: core rules + plan system + pipeline overview
    core_rules = read_file(PROMPT_TEMPLATES_DIR / "core_rules.md")
    plan_system = read_file(PROMPT_TEMPLATES_DIR / "plan_system.md")
    pipeline_doc = read_file(REFERENCE_DOCS_DIR / "manim_content_pipeline.md")

    system_prompt = f"""# Flaming Horse Video Production Agent - Plan Phase

{core_rules}

---

{plan_system}

---

## Pipeline Overview

{pipeline_doc}
"""

    # User prompt: topic + instructions
    user_prompt = f"""You are creating a video plan for the following topic:

**Topic**: {topic}

Please create a detailed video plan following the JSON format specified in your instructions.

Think about:
1. What are the key concepts that need to be explained?
2. What is the logical sequence for explaining them?
3. What visual elements will make each concept clear?
4. How can we build understanding progressively?

Output ONLY the JSON plan. Begin your response with the opening brace.
"""

    return system_prompt, user_prompt


def compose_narration_prompt(
    state: Dict[str, Any], project_dir: Path
) -> Tuple[str, str]:
    """
    Compose prompts for the narration phase.

    Returns:
        (system_prompt, user_prompt)
    """
    # System prompt: core rules + narration system + pipeline overview
    core_rules = read_file(PROMPT_TEMPLATES_DIR / "core_rules.md")
    narration_system = read_file(PROMPT_TEMPLATES_DIR / "narration_system.md")
    pipeline_doc = read_file(REFERENCE_DOCS_DIR / "manim_content_pipeline.md")

    system_prompt = f"""# Flaming Horse Video Production Agent - Narration Phase

{core_rules}

---

{narration_system}

---

## Pipeline Overview

{pipeline_doc}
"""

    # User prompt: plan contents + instructions
    plan_file = resolve_project_file(project_dir, state.get("plan_file"), "plan.json")
    plan_content = read_file(plan_file)
    plan_data = json.loads(plan_content)

    user_prompt = f"""You are writing the voiceover script for this video:

**Title**: {plan_data.get("title", "Unknown")}

**Plan**:
```json
{json.dumps(plan_data, indent=2)}
```

Please write the complete narration script following the Python format specified in your instructions.

Create engaging, conversational narration for each scene that:
1. Matches the planned duration
2. Covers the narrative beats
3. Flows naturally from scene to scene
4. Maintains audience engagement

Output ONLY the Python code (narration_script.py). Start with the comment line.
"""

    return system_prompt, user_prompt


def compose_build_scenes_prompt(
    state: Dict[str, Any], project_dir: Path, retry_context: Optional[str] = None
) -> Tuple[str, str]:
    """
    Compose prompts for the build_scenes phase.

    Returns:
        (system_prompt, user_prompt)
    """
    # System prompt: core rules + build scenes system + template + config + visual helpers
    core_rules = read_file(PROMPT_TEMPLATES_DIR / "core_rules.md")
    build_scenes_system = read_file(PROMPT_TEMPLATES_DIR / "build_scenes_system.md")
    template = read_file(REFERENCE_DOCS_DIR / "manim_template.py.txt")
    config_guide = read_file(REFERENCE_DOCS_DIR / "manim_config_guide.md")
    visual_helpers = read_file(REFERENCE_DOCS_DIR / "visual_helpers.md")

    system_prompt = f"""# Video Production Agent - Build Scenes Phase

{core_rules}

---

{build_scenes_system}

---

## Complete Scene Template

{template}

---

## Configuration and Positioning Guide

{config_guide}

---

## Visual Helpers and Aesthetics

{visual_helpers}
"""

    # User prompt: plan + current scene narration + retry context
    plan_file = resolve_project_file(project_dir, state.get("plan_file"), "plan.json")
    plan_content = read_file(plan_file)
    plan_data = json.loads(plan_content)

    narration_file = resolve_project_file(
        project_dir,
        state.get("narration_file"),
        "narration_script.py",
    )
    narration_content = read_file(narration_file)

    # Get current scene to build
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

        # Find the corresponding scene in the plan
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

    retry_section = ""
    if retry_context:
        retry_section = f"""

## RETRY CONTEXT

This scene previously failed with the following error:

```
{retry_context}
```

Please fix the issue and generate a corrected version.
"""

    user_prompt = f"""You are generating exactly ONE scene file for this run.

**Current Scene ID**: {scene_id}
**Expected File Name**: {scene_file_name}
**Expected Class Name**: {scene_class_name}
**Expected Narration Key**: {narration_key}
**Expected Title (Exact Match Required)**: {scene_title}

**Scene Details from Plan**:
```json
{scene_details}
```

**Current Scene Narration** (`SCRIPT["{narration_key}"]`):
```text
{scene_narration}
```

{retry_section}

Generate the complete Python scene file for `{scene_id}`.

Hard requirements:
1. Use the exact SCRIPT key: `SCRIPT["{narration_key}"]`.
2. The title text in code must exactly match: `{scene_title}` (no paraphrase).
3. Use subtitle and bullets grounded in this scene's plan details; do not use placeholders.
4. Keep semantics strictly scene-specific: use only this scene's plan details + narration text.
5. Do not introduce unrelated branding/topics/project names unless they appear in this scene's provided inputs.
6. Use class name `{scene_class_name}` and output code for file `{scene_file_name}` only.
7. Implement visuals tied to this scene's `narrative_beats` and `visual_ideas`.
8. Follow positioning rules (title at `UP * 3.8`, `safe_position` after `.next_to`, etc.).
9. Keep timing budget ≤ 1.0 and keep text animations ≤ 1.5s.
10. Forbidden placeholder strings/tokens: `{{{{TITLE}}}}`, `{{{{SUBTITLE}}}}`, `{{{{KEY_POINT_1}}}}`, `{{{{KEY_POINT_2}}}}`, `{{{{KEY_POINT_3}}}}` (and any `{{{{...}}}}` left in scaffold strings).
11. Do not reuse scaffold demo animations (default box/shape demo) unless explicitly required by this scene's plan.

Output ONLY the Python code. Start with the imports.
"""

    return system_prompt, user_prompt


def compose_scene_qc_prompt(
    state: Dict[str, Any], project_dir: Path
) -> Tuple[str, str]:
    """
    Compose prompts for the scene_qc phase.

    Returns:
        (system_prompt, user_prompt)
    """
    # System prompt: core rules + QC system + scenes phase doc
    core_rules = read_file(PROMPT_TEMPLATES_DIR / "core_rules.md")
    qc_system = read_file(PROMPT_TEMPLATES_DIR / "scene_qc_system.md")
    scenes_doc = read_file(REFERENCE_DOCS_DIR / "phase_scenes.md")

    system_prompt = f"""# Flaming Horse Video Production Agent - Scene QC Phase

{core_rules}

---

{qc_system}

---

## Build Scenes Reference

{scenes_doc}
"""

    # User prompt: all scene files
    scenes = state.get("scenes", [])
    scene_files_content = []

    for scene in scenes:
        scene_file_path = project_dir / scene.get("file", "")
        if scene_file_path.exists():
            content = read_file(scene_file_path)
            scene_files_content.append(f"""
### {scene.get("file")}

```python
{content}
```
""")

    all_scenes = "\n".join(scene_files_content)

    user_prompt = f"""Please review all scene files for consistency and quality.

**Scene Files**:

{all_scenes}

Review each file against the QC checklist and:
1. Fix any issues found
2. Write corrected versions of modified files
3. Generate scene_qc_report.md

Output the modified scene files (with clear markers showing which file) and the QC report.
"""

    return system_prompt, user_prompt


def compose_scene_repair_prompt(
    state: Dict[str, Any],
    project_dir: Path,
    scene_file: Path,
    retry_context: Optional[str],
) -> Tuple[str, str]:
    """
    Compose prompts for the scene_repair phase.

    Returns:
        (system_prompt, user_prompt)
    """
    # System prompt: core rules + repair system (minimal)
    core_rules = read_file(PROMPT_TEMPLATES_DIR / "core_rules.md")
    repair_system = read_file(PROMPT_TEMPLATES_DIR / "repair_system.md")

    system_prompt = f"""# Video Production Agent - Scene Repair Phase

{core_rules}

---

{repair_system}
"""

    # User prompt: broken file + error + scene-specific context
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

    user_prompt = f"""Please repair this scene file that failed to render.

**Current Scene ID**: {scene_id}
**Expected File Name**: {scene_file_name}
**Expected Class Name**: {scene_class_name}
**Expected Narration Key**: {narration_key}
**Expected Title (Exact Match Required)**: {scene_title}

**Scene Details from Plan**:
```json
{scene_details}
```

**Current Scene Narration** (`SCRIPT["{narration_key}"]`):
```text
{scene_narration}
```

**File**: {scene_file.name}

**Current Content**:
```python
{broken_file_content}
```

**Error**:
```
{retry_context or "Unknown error"}
```

Repair intent is strict:
1. Patch only what is needed to fix the reported failure.
2. Preserve this scene's topic and planned meaning.
3. Keep title text exactly `{scene_title}`.
4. Keep SCRIPT key exactly `SCRIPT["{narration_key}"]`.
5. Do not inject unrelated branding/topics/project names.

Output ONLY the corrected Python code. No explanations.
"""

    return system_prompt, user_prompt


def compose_prompt(
    phase: str,
    state: Dict[str, Any],
    topic: Optional[str] = None,
    retry_context: Optional[str] = None,
    scene_file: Optional[Path] = None,
    project_dir: Optional[Path] = None,
) -> Tuple[str, str]:
    """
    Compose phase-specific prompts.

    Args:
        phase: Phase name (plan, narration, build_scenes, scene_qc, scene_repair)
        state: Project state dict
        topic: Topic for plan phase
        retry_context: Error context for retry attempts
        scene_file: Scene file path for repair phase
        project_dir: Project directory path

    Returns:
        (system_prompt, user_prompt)
    """
    if not project_dir:
        raise ValueError("project_dir is required")

    if phase == "plan":
        return compose_plan_prompt(state, topic)
    elif phase == "narration":
        return compose_narration_prompt(state, project_dir)
    elif phase == "build_scenes":
        return compose_build_scenes_prompt(state, project_dir, retry_context)
    elif phase == "scene_qc":
        return compose_scene_qc_prompt(state, project_dir)
    elif phase == "scene_repair":
        if not scene_file:
            raise ValueError("scene_file is required for scene_repair phase")
        return compose_scene_repair_prompt(
            state, project_dir, scene_file, retry_context
        )
    else:
        raise ValueError(f"Unknown phase: {phase}")
