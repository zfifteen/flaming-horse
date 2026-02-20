"""
Output parser for the Flaming Horse agent harness.

Extracts artifacts from model responses and writes them to disk.
"""

import json
import ast
import re
import textwrap
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


class SchemaValidationError(ValueError):
    """Raised when a phase response fails strict JSON schema validation."""


def _looks_like_placeholder_narration(text: str) -> bool:
    """Return True when narration text is punctuation-only placeholder content."""
    stripped = text.strip()
    if not stripped:
        return True
    # Reject degenerate filler like "...", "…", or repeated punctuation/symbols.
    if re.fullmatch(r"[\.\u2026,\-_=~`'\"*#\s]+", stripped):
        return True
    return False


def class_name_to_scene_filename(class_name: str) -> str:
    """Convert a scene class name to canonical scene_XX_slug.py filename."""
    m = re.match(r"^Scene(\d+)([A-Za-z0-9_]*)$", class_name)
    if m:
        num = m.group(1)
        suffix = m.group(2)
        if suffix:
            slug = re.sub(r"(?<!^)(?=[A-Z])", "_", suffix).lower().strip("_")
            return f"scene_{num}_{slug}.py" if slug else f"scene_{num}.py"
        return f"scene_{num}.py"
    return re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower() + ".py"


def strip_harness_preamble(text: str) -> str:
    """
    Remove non-model preamble lines printed by harness client logging.

    Example removed block:
      🤖 Harness using:
      Provider: XAI
      Base URL: ...
      Model: ...
    """
    lines = text.splitlines()
    idx = 0

    # Skip leading blank lines
    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    if idx >= len(lines):
        return text

    first = lines[idx].strip()
    if first.startswith("🤖 Harness using"):
        idx += 1
        prefixes = ("Provider:", "Base URL:", "Model:")
        while idx < len(lines):
            line = lines[idx].strip()
            if not line:
                idx += 1
                continue
            if line.startswith(prefixes):
                idx += 1
                continue
            break
        return "\n".join(lines[idx:]).lstrip()

    return text


def inject_body_into_scaffold(scaffold_path: Path, body_code: str) -> str:
    """
    Inject body code into scaffold between SLOT markers.

    Returns the full code string, or raises if invalid.
    """
    scaffold_text = scaffold_path.read_text(encoding="utf-8")
    start_marker = "# SLOT_START:scene_body"
    end_marker = "# SLOT_END:scene_body"

    start_idx = scaffold_text.find(start_marker)
    if start_idx == -1:
        raise ValueError(f"SLOT_START marker not found in scaffold {scaffold_path}")

    end_idx = scaffold_text.find(end_marker, start_idx)
    if end_idx == -1:
        raise ValueError(f"SLOT_END marker not found in scaffold {scaffold_path}")

    # Validate body has meaningful content (not just comments/whitespace)
    body_lines = [
        line.strip()
        for line in body_code.strip().split("\n")
        if line.strip() and not line.strip().startswith("#")
    ]
    if not body_lines:
        raise ValueError("Body code must contain at least one non-comment statement")

    # Ensure body code is properly indented for the with block (12 spaces)
    # First, strip any existing indentation from body
    lines = body_code.strip().split("\n")
    # Find minimum indentation (ignoring empty lines)
    min_indent = None
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            min_indent = indent if min_indent is None else min(min_indent, indent)

    if min_indent is None:  # pragma: no cover
        min_indent = 0

    # Re-indent all lines to 12 spaces (3 levels: class, def, with)
    indented_lines = []
    for line in lines:
        if line.strip():
            # Remove existing indent and add 12 spaces
            dedented = line[min_indent:] if min_indent < len(line) else line.lstrip()
            indented_lines.append("            " + dedented)
        else:
            indented_lines.append("")

    indented_body = "\n".join(indented_lines)

    # Header is everything up to and including the start marker
    header = scaffold_text[: start_idx + len(start_marker)]

    # Footer is everything from the end marker onwards
    footer = scaffold_text[end_idx:]

    # Inject body - ensure proper spacing
    full_code = header + "\n" + indented_body.rstrip() + "\n            " + footer

    # Verify markers are still present
    if start_marker not in full_code or end_marker not in full_code:  # pragma: no cover
        raise ValueError("Injection corrupted markers")

    return full_code


def validate_scene_body_syntax(body_code: str) -> bool:
    """Check if body code compiles as indented statements and has no undefined names."""
    # Add indentation to make it valid inside a function
    indented_body = "\n".join("    " + line for line in body_code.split("\n"))
    # Try to compile as part of a function
    test_code = f"def test():\n{indented_body}\n    pass"
    try:
        compile(test_code, "<string>", "exec")
    except (SyntaxError, ValueError):
        return False

    # Check for common undefined name issues
    # These are not available in the scaffold
    forbidden_patterns = [
        (
            r"\bchoice\(",
            "choice() requires 'random' module - not available in scaffold",
        ),
        (
            r"\brandom\.",
            "random module not available in scaffold - use deterministic values",
        ),
        (r"\brandint\(", "random.randint() not available - use deterministic values"),
        (r"\brandrandom\(", "random not available - use deterministic values"),
    ]

    for pattern, msg in forbidden_patterns:
        if re.search(pattern, body_code):
            print(f"⚠ Validation warning: {msg}")
            # Don't fail - let runtime handle it, but warn

    return True


def _is_non_empty(value: Any) -> bool:
    """Check if a value is present and non-empty."""
    if value is None:
        return False
    # Treat empty strings and empty collections as empty
    if isinstance(value, (str, list, dict, tuple, set)):
        return len(value) > 0
    return True


def extract_json_block(
    text: str, required_keys: Optional[List[str]] = None
) -> Optional[str]:
    """
    Extract the first top-level JSON object from model response text.

    Args:
        text: Raw model response
        required_keys: If provided, only return JSON objects containing these keys

    Returns:
        Canonical JSON string or None if no valid top-level JSON object exists
    """
    decoder = json.JSONDecoder()

    # Collect all valid dicts
    # Then return the one with the most keys (likely the complete one)
    candidates = []

    for idx, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(text[idx:])
            if isinstance(obj, dict):
                if required_keys:
                    if all(k in obj for k in required_keys):
                        candidates.append((len(obj), obj))
                else:
                    candidates.append((len(obj), obj))
        except json.JSONDecodeError:
            continue

    if not candidates:
        return None

    # When required_keys are provided, prefer objects where those keys
    # have non-empty values, not just presence.
    if required_keys:
        valid_candidates = []
        for size, obj in candidates:
            if all(_is_non_empty(obj.get(k)) for k in required_keys):
                valid_candidates.append((size, obj))

        # If we have any fully valid candidates, choose among them.
        if valid_candidates:
            selected_obj = max(valid_candidates, key=lambda x: x[0])[1]
        else:
            # Fall back to the original behavior: choose largest by key count
            selected_obj = max(candidates, key=lambda x: x[0])[1]
    else:
        selected_obj = max(candidates, key=lambda x: x[0])[1]

    return json.dumps(selected_obj)


def extract_python_code_blocks(text: str) -> List[Tuple[str, str]]:
    """
    Extract Python code blocks from model response.

    Returns:
        List of (filename_hint, code) tuples
    """
    # Pattern for code blocks with optional filename hints
    # More flexible - allows optional whitespace and newline
    pattern = r"```python\s*(?:#\s*(.+?\.py)\s*)?(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    results = []
    for filename_hint, code in matches:
        # Clean up the code
        code = code.strip()
        results.append((filename_hint.strip() if filename_hint else "", code))

    return results


def extract_single_python_code(text: str) -> Optional[str]:
    """
    Extract a single Python code block from text.

    Handles both markdown fences and raw Python code.
    Also handles cases where model outputs explanatory text before code.

    Returns:
        Python code string or None if not found
    """
    # Try to find code in markdown blocks
    code_blocks = extract_python_code_blocks(text)

    if code_blocks:
        # Return the first (or longest) code block
        return max(code_blocks, key=lambda x: len(x[1]))[1]

    # If no code blocks found, look for SCRIPT = { as a strong indicator of Python code
    # This is more reliable than checking for "import" which appears in English
    if "SCRIPT = {" in text:
        # Find where SCRIPT = { starts and extract from there
        start_idx = text.find("SCRIPT = {")
        if start_idx != -1:
            code_candidate = text[start_idx:]
            # Try to find the proper end (closing brace at appropriate indentation)
            # Look for a line that's just "}" followed by optional whitespace at end
            lines = code_candidate.split("\n")
            brace_count = 0
            end_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                brace_count += stripped.count("{") - stripped.count("}")
                if brace_count == 0 and stripped == "}":
                    # Find the end of this line
                    end_idx = sum(len(l) + 1 for l in lines[: i + 1])
                    break
            if end_idx > 0:
                return code_candidate[:end_idx].strip()
            return code_candidate.strip()

    # Check if the text looks more like Python than English
    # Look for Python-specific patterns (def, class, import at start of lines)
    python_patterns = [
        re.search(r"^import\s+\w+", text, re.MULTILINE),
        re.search(r"^from\s+\w+\s+import", text, re.MULTILINE),
        re.search(r"^class\s+\w+", text, re.MULTILINE),
        re.search(r"^def\s+\w+", text, re.MULTILINE),
    ]
    if any(python_patterns):
        return text.strip()

    return None


def sanitize_code(code: str) -> str:
    """
    Remove stray markup artifacts from code.

    Args:
        code: Python code string

    Returns:
        Cleaned code
    """
    # Remove HTML/XML-like tags emitted by models while preserving Python
    # comparison operators. We only strip tokens that look like real tags
    # (<tag ...> / </tag>) and never span across newlines.
    code = re.sub(r"</?[A-Za-z][^>\n]*>", "", code)

    # Remove standalone tag-only lines that can remain after stripping.
    code = re.sub(r"^\s*</?[A-Za-z][^>]*>\s*$", "", code, flags=re.MULTILINE)

    # Remove markdown artifacts that might have slipped through
    code = re.sub(r"^```python\s*", "", code, flags=re.MULTILINE)
    code = re.sub(r"^```\s*$", "", code, flags=re.MULTILINE)

    return code.strip()


def has_scaffold_artifacts(code: str) -> bool:
    """
    Check if code contains scaffold placeholders or demo code.

    Args:
        code: Python code string

    Returns:
        True if scaffold artifacts are found
    """
    # Forbidden placeholder tokens
    forbidden_literals = [
        '"{{TITLE}}"',
        "'{{TITLE}}'",
        '"{{SUBTITLE}}"',
        "'{{SUBTITLE}}'",
        '"{{KEY_POINT_1}}"',
        "'{{KEY_POINT_1}}'",
        '"{{KEY_POINT_2}}"',
        "'{{KEY_POINT_2}}'",
        '"{{KEY_POINT_3}}"',
        "'{{KEY_POINT_3}}'",
    ]

    for literal in forbidden_literals:
        if literal in code:
            return True

    # Check for demo Rectangle from scaffold template
    # Pattern: box = Rectangle(width=4.0, height=2.4, ...
    if re.search(
        r"box\s*=\s*Rectangle\(\s*width\s*=\s*4(?:\.0)?,\s*height\s*=\s*2\.4", code
    ):
        return True

    return False


def has_kitchen_sink_boilerplate(code: str) -> bool:
    """
    Check if code contains Kitchen Sink example class definitions.

    These should never appear in scene body output.

    Args:
        code: Python code string

    Returns:
        True if boilerplate is found
    """
    forbidden_classes = [
        "SceneLifecycleBaseline",
        "GeometryGallery2D",
        "LayoutAndLabelAnchoring2D",
        "TextHierarchyAndCallouts",
        "MathTexDerivationPattern",
        "TransitionPatternsCore",
        "GroupedTimingPatterns",
        "AxesAndFunctionPlot",
        "DataNarrativeGraphing",
        "ThreeDOrientationBaseline",
        "CameraMotionAndFocus3D",
        "ValueTrackerDrivenMotion",
        "ColorSemanticPalette",
        "FillStrokeStyleTransitions",
    ]

    for class_name in forbidden_classes:
        if re.search(rf"\bclass\s+{class_name}\b", code):
            return True

    if re.search(r'"""[^"]*Pattern Family [A-H]:', code):
        return True
    if "Source: https://docs.manim.community" in code:
        return True

    return False


def verify_python_syntax(code: str) -> bool:
    """
    Verify that code is syntactically valid Python.

    Args:
        code: Python code string

    Returns:
        True if valid, False otherwise
    """
    try:
        compile(code, "<string>", "exec")
        return True
    except SyntaxError:
        return False


def parse_plan_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Parse plan phase response to extract plan.json.

    Args:
        response_text: Model response

    Returns:
        Plan dict or None if parsing failed
    """
    cleaned_response = strip_harness_preamble(response_text)
    json_text = extract_json_block(cleaned_response, required_keys=["title", "scenes"])
    if not json_text:
        raise SchemaValidationError("no valid top-level JSON object found")

    try:
        plan = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(f"invalid JSON object: {exc}") from exc

    title = plan.get("title")
    if not isinstance(title, str) or not title.strip():
        raise SchemaValidationError(
            "plan.title is required and must be a non-empty string"
        )

    scenes = plan.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise SchemaValidationError(
            "plan.scenes is required and must be a non-empty array"
        )

    for idx, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            raise SchemaValidationError(f"plan.scenes[{idx}] must be an object")

        # Deterministic ID assignment by array index (harness responsibility)
        # The LLM should NOT provide id or narration_key - harness generates these
        scene_number = idx + 1
        scene_id = f"scene_{scene_number:02d}"  # scene_01, scene_02, etc.
        scene["id"] = scene_id
        scene["narration_key"] = scene_id

        # Validate required fields
        if (
            not scene.get("title")
            or not isinstance(scene.get("title"), str)
            or not scene["title"].strip()
        ):
            raise SchemaValidationError(
                f"plan.scenes[{idx}].title is required and must be a non-empty string"
            )

    return plan


def parse_narration_response(response_text: str) -> Optional[str]:
    """
    Parse narration phase response to extract narration_script.py.

    The model now outputs JSON, which we convert to Python code.

    Args:
        response_text: Model response

    Returns:
        Python code string or None if parsing failed
    """
    cleaned_response = strip_harness_preamble(response_text)
    json_data = extract_json_block(cleaned_response, required_keys=["script"])
    if not json_data:
        raise SchemaValidationError("no valid top-level JSON object found")

    try:
        payload = json.loads(json_data)
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(f"invalid JSON object: {exc}") from exc

    script_dict = payload.get("script")
    if not isinstance(script_dict, dict) or not script_dict:
        raise SchemaValidationError(
            "narration.script is required and must be a non-empty object"
        )
    for key, value in script_dict.items():
        if not isinstance(key, str) or not key.strip():
            raise SchemaValidationError(
                "narration.script keys must be non-empty strings"
            )
        if not isinstance(value, str) or not value.strip():
            raise SchemaValidationError(
                f"narration.script[{key!r}] must be a non-empty string"
            )
        if _looks_like_placeholder_narration(value):
            raise SchemaValidationError(
                f"narration.script[{key!r}] must contain real narration text (not placeholder punctuation)"
            )

    # Convert to Python code
    code = """# Voiceover script
# This file is imported by scene files as: from narration_script import SCRIPT

SCRIPT = {
"""

    for key, value in script_dict.items():
        # Use json.dumps to safely serialize both keys and values.
        # This handles all edge cases: quotes, backslashes, unicode, newlines,
        # and prevents injection attacks from malicious narration content.
        code += f"    {json.dumps(key)}: {json.dumps(value)},\n"

    code += "}\n"

    return code


def extract_scene_body_xml(text: str) -> Optional[str]:
    """
    Extract scene body from <scene_body> XML tags.

    This matches the output format specified in build_scenes_system.md

    Returns:
        Body code string or None if not found
    """
    # Match <scene_body>...</scene_body> tags
    pattern = r"<scene_body>(.*?)</scene_body>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        raw_body = match.group(1)
        # Dedent to remove common leading whitespace
        # The LLM may output already-indented code (12 spaces for with block context)
        dedented = textwrap.dedent(raw_body)
        return dedented.strip()
    return None


def extract_scene_body_from_full_file(code: str) -> Optional[str]:
    """
    Extract scene body from a full Python file response.

    This handles the case where the LLM outputs a complete scene file
    instead of just the <scene_body> content.

    Returns:
        Body code (indented for with block) or None if not found
    """
    import re

    # Find the with self.voiceover block
    # Pattern: with self.voiceover(text=SCRIPT["..."]) as tracker:\n<indented body>
    pattern = r"with\s+self\.voiceover\([^)]+\)\s+as\s+tracker:\s*\n((?:[ \t]+.+\n*)*)"
    match = re.search(pattern, code)
    if not match:
        return None

    body_indented = match.group(1)
    # Remove one level of indentation (12 spaces) to dedent for injection
    lines = body_indented.split("\n")
    dedented_lines = []
    for line in lines:
        if line.strip():
            # Remove up to 12 spaces of leading whitespace
            if line.startswith("            "):  # 12 spaces
                dedented_lines.append(line[12:])
            elif line.startswith("        "):  # 8 spaces
                dedented_lines.append(line[8:])
            else:
                dedented_lines.append(line.lstrip())
        else:
            dedented_lines.append("")

    return "\n".join(dedented_lines).strip()


def _extract_scene_body_from_json_response(response_text: str, phase: str) -> str:
    """Extract and validate `scene_body` from strict JSON phase payload."""
    cleaned_response = strip_harness_preamble(response_text)
    json_text = extract_json_block(cleaned_response)
    if not json_text:
        raise SchemaValidationError("no valid top-level JSON object found")

    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(f"invalid JSON object: {exc}") from exc

    scene_body = payload.get("scene_body")
    if not isinstance(scene_body, str) or not scene_body.strip():
        raise SchemaValidationError(
            f"{phase}.scene_body is required and must be a non-empty string"
        )

    candidate = sanitize_code(scene_body)
    if not candidate:
        raise SchemaValidationError(
            f"{phase}.scene_body cannot be empty after sanitization"
        )
    if not verify_python_syntax(candidate):
        raise SchemaValidationError(f"{phase}.scene_body must be valid Python")

    forbidden_tokens = [
        "from manim import",
        "from pathlib import",
        "import numpy",
        "config.frame",
        "class Scene",
        "def construct",
        "SLOT_START:scene_body",
        "SLOT_END:scene_body",
    ]
    if any(token in candidate for token in forbidden_tokens):
        raise SchemaValidationError(
            f"{phase}.scene_body must contain scene-body statements only (no imports/class/config/scaffold markers)"
        )
    if re.search(r"with\s+self\.voiceover\(", candidate):
        raise SchemaValidationError(
            f"{phase}.scene_body must not include nested self.voiceover wrapper"
        )
    if candidate.strip().startswith(("class ", "def ", "import ", "from ")):
        raise SchemaValidationError(
            f"{phase}.scene_body must not start with class/def/import statements"
        )
    if has_scaffold_artifacts(candidate):
        raise SchemaValidationError(
            f"{phase}.scene_body contains unresolved scaffold placeholders"
        )
    if has_kitchen_sink_boilerplate(candidate):
        raise SchemaValidationError(
            f"{phase}.scene_body contains Kitchen Sink boilerplate class definitions"
        )

    return candidate


def _has_executable_self_play_call(body_code: str) -> bool:
    """Return True when body has at least one executable self.play(...) with >=1 arg."""
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


def parse_build_scenes_response(response_text: str) -> Optional[str]:
    """
    Parse build_scenes phase response to extract scene body code.

    Strict contract:
    - Exactly one fenced ```python ... ``` code block
    - Scene body code only (no imports/class/config/helpers)

    Args:
        response_text: Model response

    Returns:
        Python body code string or None if parsing failed
    """
    candidate = _extract_scene_body_from_json_response(response_text, "build_scenes")
    if not _has_executable_self_play_call(candidate):
        raise SchemaValidationError(
            "build_scenes.scene_body must contain at least one executable self.play(...) call with >=1 argument"
        )
    return candidate


def parse_scene_qc_response(
    response_text: str,
) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    """
    Parse scene_qc phase response to extract modified scenes and report.

    Args:
        response_text: Model response

    Returns:
        (list of (filename, code) tuples, report markdown or None)
    """
    cleaned_response = strip_harness_preamble(response_text)
    json_text = extract_json_block(cleaned_response)
    if not json_text:
        raise SchemaValidationError("no valid top-level JSON object found")
    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(f"invalid JSON object: {exc}") from exc

    report = payload.get("report_markdown")
    if not isinstance(report, str) or not report.strip():
        raise SchemaValidationError(
            "scene_qc.report_markdown is required and must be a non-empty string"
        )

    return [], report.strip()


def parse_scene_repair_response(response_text: str) -> Optional[str]:
    """
    Parse scene_repair phase response to extract fixed scene body.

    Args:
        response_text: Model response

    Returns:
        Python body code string or None if parsing failed
    """
    candidate = _extract_scene_body_from_json_response(response_text, "scene_repair")
    if not _has_executable_self_play_call(candidate):
        raise SchemaValidationError(
            "scene_repair.scene_body must contain at least one executable self.play(...) call with >=1 argument"
        )
    return candidate


def parse_and_write_artifacts(
    phase: str, response_text: str, project_dir: Path, state: Dict[str, Any]
) -> bool:
    """
    Parse model response and write artifacts to disk.

    Args:
        phase: Phase name
        response_text: Model response
        project_dir: Project directory
        state: Project state

    Returns:
        True if successful, False otherwise
    """
    try:
        if phase == "plan":
            plan = parse_plan_response(response_text)
            if not plan:
                print("❌ Failed to parse plan.json from response")
                return False

            plan_file = project_dir / "plan.json"
            with open(plan_file, "w") as f:
                json.dump(plan, f, indent=2)

            print(f"✅ Wrote {plan_file}")
            return True

        elif phase == "narration":
            code = parse_narration_response(response_text)
            if not code:
                print("❌ Failed to parse narration_script.py from response")
                return False

            narration_file = project_dir / "narration_script.py"
            narration_file.write_text(code)

            print(f"✅ Wrote {narration_file}")
            return True

        elif phase == "build_scenes":
            scenes = state.get("scenes", [])
            current_index = state.get("current_scene_index", 0)

            if current_index >= len(scenes):
                print("❌ No more scenes to build")
                return

            current_scene = scenes[current_index]
            scene_id = current_scene.get("id", f"scene_{current_index + 1:02d}")
            scene_file_name = current_scene.get("file", f"{scene_id}.py")

            body_code = parse_build_scenes_response(response_text)

            if not body_code:
                print(f"❌ Failed to parse scene body from response")
                return

            # Validate body syntax
            if not validate_scene_body_syntax(body_code):
                print(f"❌ Body code has syntax errors")
                return

            scene_file = project_dir / scene_file_name

            # If scaffold doesn't exist, create it (but it should)
            if not scene_file.exists():
                print(f"⚠️  Scaffold not found, skipping injection")
                return

            try:
                full_code = inject_body_into_scaffold(scene_file, body_code)
                scene_file.write_text(full_code)
                print(f"✅ Injected body into {scene_file}")
            except ValueError as e:
                print(f"❌ Injection failed: {e}")
                return
            return True

        elif phase == "scene_qc":
            scene_files, report = parse_scene_qc_response(response_text)

            if not scene_files and not report:
                print("❌ Failed to parse any artifacts from QC response")
                return False

            # Scene QC is report-only: no scene file rewrites in this phase.
            if scene_files:
                print(
                    f"ℹ️  Ignored {len(scene_files)} scene code block(s) from scene_qc response "
                    "(report-only policy)"
                )

            # Write QC report
            if report:
                report_file = project_dir / "scene_qc_report.md"
                report_file.write_text(report)
                print(f"✅ Wrote {report_file}")

            return True

        elif phase == "scene_repair":
            body_code = parse_scene_repair_response(response_text)

            if not body_code:
                print("❌ Failed to parse repaired scene body from response")
                return

            # Validate body syntax
            if not validate_scene_body_syntax(body_code):
                print(f"❌ Body code has syntax errors")
                return

            scene_file = None
            explicit_scene_file = state.get("scene_file")
            if isinstance(explicit_scene_file, str) and explicit_scene_file:
                explicit_path = Path(explicit_scene_file)
                scene_file = (
                    explicit_path
                    if explicit_path.is_absolute()
                    else project_dir / explicit_path
                )
            else:
                scenes = state.get("scenes", [])
                current_index = state.get("current_scene_index", 0)

                if current_index >= len(scenes):
                    print("❌ No scene to repair")
                    return

                current_scene = scenes[current_index]
                scene_file_name = current_scene.get(
                    "file", f"scene_{current_index + 1:02d}.py"
                )
                scene_file = project_dir / scene_file_name

            try:
                full_code = inject_body_into_scaffold(scene_file, body_code)
                scene_file.write_text(full_code)
                print(f"✅ Injected repaired body into {scene_file}")
            except ValueError as e:
                print(f"❌ Injection failed: {e}")
                return
            return True

        else:
            print(f"❌ Unknown phase: {phase}")
            return False

    except SchemaValidationError:
        raise
    except Exception as e:
        print(f"❌ Error writing artifacts: {e}")
        import traceback

        traceback.print_exc()
        return False
