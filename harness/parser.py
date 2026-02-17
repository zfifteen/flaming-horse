"""
Output parser for the Flaming Horse agent harness.

Extracts artifacts from model responses and writes them to disk.
"""

import json
import ast
import re
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


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
    min_indent = float('inf')
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, indent)
    
    if min_indent == float('inf'):
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
    if start_marker not in full_code or end_marker not in full_code:
        raise ValueError("Injection corrupted markers")

    return full_code


def validate_scene_body_syntax(body_code: str) -> bool:
    """Check if body code compiles as indented statements."""
    # Try to compile as part of a function
    test_code = f"def test():\n{body_code}\n    pass"
    try:
        compile(test_code, "<string>", "exec")
        return True
    except (SyntaxError, ValueError):
        return False


def extract_json_block(text: str) -> Optional[str]:
    """
    Extract JSON from model response.

    Handles both:
    - Raw JSON starting with {
    - JSON in markdown code blocks

    Returns:
        JSON string or None if not found
    """
    decoder = json.JSONDecoder()

    # First, try to find JSON in fenced code blocks.
    # Allow optional language and tolerate extra prose around JSON.
    code_block_pattern = r"```(?:json)?\s*(.*?)```"
    matches = re.findall(code_block_pattern, text, re.DOTALL)

    if matches:
        for match in matches:
            # Try to parse it to verify it's valid JSON
            cleaned = match.strip()
            try:
                json.loads(cleaned)
                return cleaned
            except json.JSONDecodeError:
                # Try extracting first valid JSON value if extra text exists.
                try:
                    obj, _ = decoder.raw_decode(cleaned)
                    return json.dumps(obj)
                except json.JSONDecodeError:
                    continue

    # If no code block, try regex-based raw JSON slices.
    json_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
    matches = re.findall(json_pattern, text, re.DOTALL)

    for match in matches:
        try:
            json.loads(match)
            return match
        except json.JSONDecodeError:
            continue

    # Last resort: scan for first decodable object from any '{'.
    for idx, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(text[idx:])
            if isinstance(obj, (dict, list)):
                return json.dumps(obj)
        except json.JSONDecodeError:
            continue

    # Final fallback: try to parse the whole text
    try:
        json.loads(text.strip())
        return text.strip()
    except json.JSONDecodeError:
        pass

    return None


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

    Returns:
        Python code string or None if not found
    """
    # Try to find code in markdown blocks
    code_blocks = extract_python_code_blocks(text)

    if code_blocks:
        # Return the first (or longest) code block
        return max(code_blocks, key=lambda x: len(x[1]))[1]

    # If no code blocks found, check if the whole text looks like Python
    if "import" in text or "def " in text or "class " in text:
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
    json_text = extract_json_block(response_text)
    if not json_text:
        return None

    try:
        try:
            plan = json.loads(json_text)
        except json.JSONDecodeError:
            # Fallback for near-JSON payloads with single quotes/trailing commas.
            plan = ast.literal_eval(json_text)

        # Basic validation, with support for wrapped payloads.
        if "title" not in plan or "scenes" not in plan:
            for wrapper_key in ("plan", "video_plan", "result"):
                wrapped = plan.get(wrapper_key)
                if (
                    isinstance(wrapped, dict)
                    and "title" in wrapped
                    and "scenes" in wrapped
                ):
                    plan = wrapped
                    break
            else:
                return None

        if not isinstance(plan.get("scenes"), list):
            return None

        return plan
    except (json.JSONDecodeError, SyntaxError, ValueError):
        return None


def parse_narration_response(response_text: str) -> Optional[str]:
    """
    Parse narration phase response to extract narration_script.py.

    Args:
        response_text: Model response

    Returns:
        Python code string or None if parsing failed
    """
    code = extract_single_python_code(response_text)
    if not code:
        return None

    code = sanitize_code(code)

    # Verify it's valid Python
    if not verify_python_syntax(code):
        return None

    # Verify it has SCRIPT dict
    if "SCRIPT = {" not in code and "SCRIPT = {" not in code:
        return None

    return code


def parse_build_scenes_response(response_text: str) -> Optional[str]:
    """
    Parse build_scenes phase response to extract scene body code only.

    Args:
        response_text: Model response

    Returns:
        Python body code string or None if parsing failed
    """
    forbidden_tokens = [
        "from manim import",
        "from pathlib import",
        "import numpy",
        "config.frame",
        "class Scene",
        "def construct",
        "SLOT_START:scene_body",
        "SLOT_END:scene_body",
        "def BeatPlan",
        "def play_in_slot",
        "def play_text_in_slot",
        "def play_next",
        "def play_text_next",
    ]

    # Extract Python blocks
    for _filename_hint, block_code in extract_python_code_blocks(response_text):
        candidate = sanitize_code(block_code)
        if not verify_python_syntax(candidate):
            continue
        # Reject if contains forbidden header tokens
        if any(token in candidate for token in forbidden_tokens):
            continue
        # Should be body code: indented statements, no class/def at top level
        if candidate.strip().startswith(("class ", "def ", "import ", "from ")):
            continue
        # Reject if has scaffold placeholders
        if has_scaffold_artifacts(candidate):
            continue
        return candidate

    # Fallback: try raw/single-block extraction.
    code = extract_single_python_code(response_text)
    if not code:
        return None
    code = sanitize_code(code)
    if not verify_python_syntax(code):
        return None
    # Reject forbidden tokens
    if any(token in code for token in forbidden_tokens):
        return None
    # Ensure it's body code
    if code.strip().startswith(("class ", "def ", "import ", "from ")):
        return None
    # Reject if has scaffold placeholders
    if has_scaffold_artifacts(code):
        return None
    return code


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
    scene_files = []
    report = None

    # Extract all Python code blocks (these are the modified scenes)
    code_blocks = extract_python_code_blocks(response_text)

    for filename_hint, code in code_blocks:
        code = sanitize_code(code)
        if verify_python_syntax(code):
            scene_files.append((filename_hint, code))

    # Extract markdown report
    # Look for "# Scene QC Report" or similar
    report_pattern = r"(?:```markdown\s*)?(#\s*Scene\s*QC\s*Report.*?)(?:```|\Z)"
    match = re.search(report_pattern, response_text, re.DOTALL | re.IGNORECASE)
    if match:
        report = match.group(1).strip()

    return scene_files, report


def parse_scene_repair_response(response_text: str) -> Optional[str]:
    """
    Parse scene_repair phase response to extract fixed scene body.

    Args:
        response_text: Model response

    Returns:
        Python body code string or None if parsing failed
    """
    forbidden_tokens = [
        "from manim import",
        "from pathlib import",
        "import numpy",
        "config.frame",
        "class Scene",
        "def construct",
        "SLOT_START:scene_body",
        "SLOT_END:scene_body",
        "def BeatPlan",
        "def play_in_slot",
        "def play_text_in_slot",
        "def play_next",
        "def play_text_next",
    ]

    for _filename_hint, block_code in extract_python_code_blocks(response_text):
        candidate = sanitize_code(block_code)
        if not verify_python_syntax(candidate):
            continue
        # Reject if contains forbidden header tokens
        if any(token in candidate for token in forbidden_tokens):
            continue
        # Should be body code: no class/def/import at top level
        if candidate.strip().startswith(("class ", "def ", "import ", "from ")):
            continue
        # Reject if has scaffold placeholders
        if has_scaffold_artifacts(candidate):
            continue
        return candidate

    # Fallback
    code = extract_single_python_code(response_text)
    if not code:
        return None
    code = sanitize_code(code)
    if not verify_python_syntax(code):
        return None
    # Reject forbidden
    if any(token in code for token in forbidden_tokens):
        return None
    # Ensure body
    if code.strip().startswith(("class ", "def ", "import ", "from ")):
        return None
    # Reject repaired code that still has scaffold placeholders
    if has_scaffold_artifacts(code):
        return None
    return code


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

            # Write modified scene files
            for filename, code in scene_files:
                if filename:
                    scene_file = project_dir / filename
                else:
                    # Try to infer filename from class name in code
                    class_match = re.search(r"class\s+(\w+)\(", code)
                    if class_match:
                        # Convert class name to filename (e.g., Scene01Intro -> scene_01_intro.py)
                        class_name = class_match.group(1)
                        filename = (
                            re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower() + ".py"
                        )
                        scene_file = project_dir / filename
                    else:
                        print(f"⚠️  Could not determine filename for scene, skipping")
                        continue

                scene_file.write_text(code)
                print(f"✅ Wrote {scene_file}")

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

    except Exception as e:
        print(f"❌ Error writing artifacts: {e}")
        import traceback

        traceback.print_exc()
        return False
