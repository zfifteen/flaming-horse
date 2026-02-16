"""
Output parser for the Flaming Horse agent harness.

Extracts artifacts from model responses and writes them to disk.
"""

import json
import ast
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


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
    Parse build_scenes phase response to extract scene file.

    Args:
        response_text: Model response

    Returns:
        Python code string or None if parsing failed
    """
    required_imports = [
        "from manim import",
        "VoiceoverScene",
        "from narration_script import SCRIPT",
    ]

    # Prefer fenced Python blocks that pass all checks.
    for _filename_hint, block_code in extract_python_code_blocks(response_text):
        candidate = sanitize_code(block_code)
        if not verify_python_syntax(candidate):
            continue
        if not all(imp in candidate for imp in required_imports):
            continue
        # NEW: Reject code with scaffold placeholders
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
    if not all(imp in code for imp in required_imports):
        return None
    # NEW: Reject code with scaffold placeholders
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
    Parse scene_repair phase response to extract fixed scene file.

    Args:
        response_text: Model response

    Returns:
        Python code string or None if parsing failed
    """
    # Same as build_scenes parsing
    code = extract_single_python_code(response_text)
    if not code:
        return None

    code = sanitize_code(code)

    if not verify_python_syntax(code):
        return None

    # NEW: Reject repaired code that still has scaffold placeholders
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
                return False

            current_scene = scenes[current_index]
            scene_id = current_scene.get("id", f"scene_{current_index + 1:02d}")
            scene_file_name = current_scene.get("file", f"{scene_id}.py")

            code = parse_build_scenes_response(response_text)
            if not code:
                print(f"❌ Failed to parse {scene_file_name} from response")
                return False

            scene_file = project_dir / scene_file_name
            scene_file.write_text(code)

            print(f"✅ Wrote {scene_file}")
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
            code = parse_scene_repair_response(response_text)
            if not code:
                print("❌ Failed to parse repaired scene from response")
                return False

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
                    return False

                current_scene = scenes[current_index]
                scene_file_name = current_scene.get(
                    "file", f"scene_{current_index + 1:02d}.py"
                )
                scene_file = project_dir / scene_file_name

            scene_file.write_text(code)
            print(f"✅ Wrote repaired {scene_file}")
            return True

        else:
            print(f"❌ Unknown phase: {phase}")
            return False

    except Exception as e:
        print(f"❌ Error writing artifacts: {e}")
        import traceback

        traceback.print_exc()
        return False
