# Root Cause Analysis: Blank Video Generation

**Date**: 2026-02-17  
**Issue**: Videos rendered with audio but no visible text or animations (black screen)  
**Status**: ✅ FIXED

---

## Executive Summary

The video generation pipeline was producing videos with audio but no visual content. The root cause was a multi-layered failure:

1. **Parser mismatch** - The parser couldn't understand the LLM's output format
2. **Python version** - Wrong Python version caused import failures  
3. **Indentation handling** - Incorrect dedenting caused syntax validation failures
4. **Color types** - LLM generated numpy values that Manim v0.19+ rejects

---

## Problem Description

When running the smoke test (`./tests/smoke_test.sh`), the pipeline completed but produced videos where:
- ✅ Audio was present (voiceover worked)
- ❌ No text or animations were visible
- ❌ Videos showed black screen with audio

The Manim render logs showed: `Played 1 animations` - indicating the scene body code (with actual animations) was never executed.

---

## Root Cause Analysis

### Finding 1: Parser Could Not Extract LLM Output

**Scope**: `harness/parser.py` - `parse_build_scenes_response()`

**Failure Origin**: The system prompt (`build_scenes_system.md` lines 18-24) explicitly instructed the LLM to output XML tags:

```xml
<scene_body>
[CODE HERE]
</scene_body>
```

However, the parser only looked for ```python code blocks, completely ignoring the XML format that the prompt requested.

**Causal Chain**:
1. LLM followed prompt instructions → output `<scene_body>` tags
2. Parser searched for ```python blocks → found nothing
3. Parser returned `None` → scene file remained with `pass` scaffold stub
4. Videos rendered with empty scene body → black screen

**Evidence**: The debug response files showed:
```
<scene_body>
num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
beats = BeatPlan(...)
# Title
title = Text("Free Your Mind", ...)
...
</scene_body>
```

But the parser reported: `❌ Failed to parse scene body from response`

---

### Finding 2: Python Version Mismatch

**Scope**: `.env`, `scripts/build_video.sh`

**Failure Origin**: The build script was using the system Python 3.9, which doesn't have `datetime.UTC` (added in Python 3.11).

**Error**:
```
ImportError: cannot import name 'UTC' from 'datetime'
```

This caused the pipeline to fail immediately after the plan phase.

---

### Finding 3: Indentation Handling Issues

**Scope**: `harness/parser.py` - `extract_scene_body_xml()`, `validate_scene_body_syntax()`

**Failure Origin**: Two related issues:

1. **Extra indentation**: The LLM output already had 12-space indentation (matching the `with` block context). The parser's `inject_body_into_scaffold()` added ANOTHER 12 spaces, resulting in 24-space indentation and broken Python code.

2. **Syntax validation**: The `validate_scene_body_syntax()` function tested the body without adding proper indentation first:
   ```python
   # WRONG:
   test_code = f"def test():\n{body_code}\n    pass"
   # body_code had no indentation, so this was invalid Python
   ```

---

### Finding 4: Invalid Color Values

**Scope**: `harness/prompt_templates/build_scenes_system.md`

**Failure Origin**: The system prompt instructed the LLM to "Use harmonious_color for palettes" but didn't explain:

1. What `harmonious_color()` returns (a list of RGB lists `[r,g,b,1.0]`)
2. What valid color types Manim v0.19+ accepts
3. What NOT to do (index into palette results, do math on colors)

**Error**:
```
TypeError: ManimColor only accepts int, str, list[int, int, int], ..., not <class 'numpy.float64'>
```

The LLM generated code like:
```python
# WRONG - what LLM generated:
colors = harmonious_color(BLUE, variations=4)
title = Text("Hello", color=colors[0])  # colors[0] is [r,g,b,1.0] - a list!
```

---

## Fixes Applied

### Fix 1: Parser XML Extraction

**File**: `harness/parser.py`

Added `extract_scene_body_xml()` function to parse `<scene_body>` tags:

```python
def extract_scene_body_xml(text: str) -> Optional[str]:
    pattern = r"<scene_body>(.*?)</scene_body>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        raw_body = match.group(1)
        # Dedent to remove common leading whitespace
        dedented = textwrap.dedent(raw_body)
        return dedented.strip()
    return None
```

Updated `parse_build_scenes_response()` to try XML extraction first before falling back to code blocks.

---

### Fix 2: Full File Fallback

**File**: `harness/parser.py`

Added `extract_scene_body_from_full_file()` to handle cases where the LLM outputs a complete Python file instead of just the body content. This handles the retry case where the parser fails the first time and the LLM re-generates with full file output.

---

### Fix 3: Indentation Correction

**File**: `harness/parser.py`

Updated syntax validation to properly indent before testing:

```python
def validate_scene_body_syntax(body_code: str) -> bool:
    # Add indentation to make it valid inside a function
    indented_body = "\n".join("    " + line for line in body_code.split("\n"))
    test_code = f"def test():\n{indented_body}\n    pass"
    try:
        compile(test_code, "<string>", "exec")
        return True
    except (SyntaxError, ValueError):
        return False
```

---

### Fix 4: Python Version Configuration

**File**: `.env`

Added Python version configuration:
```bash
# Python version - must be 3.11+ for datetime.UTC
export PYTHON=/Users/velocityworks/IdeaProjects/flaming-horse/.venv/bin/python
export PYTHON3=/Users/velocityworks/IdeaProjects/flaming-horse/.venv/bin/python3
export PATH="/Users/velocityworks/IdeaProjects/flaming-horse/.venv/bin:$PATH"
```

**File**: `scripts/build_video.sh`

Updated to use the configured Python:
```bash
# After sourcing .env
PYTHON_BIN="${PYTHON:-${PYTHON3:-python3}}"
# Then replaced all 'python3' calls with "$PYTHON_BIN"
```

---

### Fix 5: Color Value Instructions

**File**: `harness/prompt_templates/build_scenes_system.md`

Added detailed color instructions:

```markdown
### Color Values (CRITICAL - READ THIS)
Manim v0.19+ has strict color type requirements. You MUST use valid color values:

**VALID color options:**
- Built-in colors: BLUE, RED, GREEN, YELLOW, WHITE, BLACK, GRAY, ORANGE, PURPLE, etc.
- Hex strings: "#FF5500" (use string quotes!)
- RGB tuples: (0.5, 0.3, 0.8) or (0.5, 0.3, 0.8, 1.0) (float 0-1 range, tuple NOT list)

**INVALID (will cause runtime errors):**
- colors[0] where colors comes from harmonious_color() - returns a list!
- Numpy arrays or numpy scalars: np.array([...]), some_value * 0.5
- Integer RGB values: (255, 0, 0) - must be float 0-1 range

**How to use harmonious_color():**
# CORRECT - use as entire color argument:
title = Text("Hello", color=harmonious_color(BLUE, variations=3))

# SAFEST - use built-in Manim colors directly:
title = Text("Hello", color=BLUE)
```

---

## Files Modified

| File | Change |
|------|--------|
| `harness/parser.py` | Added XML extraction, full-file fallback, fixed indentation handling |
| `.env` | Added PYTHON, PYTHON3 exports |
| `scripts/build_video.sh` | Use configured Python version |
| `harness/prompt_templates/build_scenes_system.md` | Added detailed color value instructions |

---

## Verification

After fixes, the smoke test produces:

```
✅ Injected body into ...scene_01_intro.py
✅ Phase build_scenes completed successfully
✓ Generated scene_01_intro (18.88s) in 23.5s
✓ Generated scene_02_content (23.36s) in 23.0s
✓ Generated scene_03_conclusion (21.76s) in 21.5s
✅ Video build complete!
Final video: ...final_video.mp4
```

The rendered videos now contain visible text and animations synced to voiceover.

---

## Lessons Learned

1. **Parser must match prompt format**: When instructing LLMs to output in a specific format, the parser MUST understand that format. This seems obvious in retrospect but was the core issue.

2. **Indentation is critical**: Python is indentation-sensitive. Any automated code injection must carefully handle indentation at multiple levels.

3. **Provide concrete examples**: Instructions like "use harmonious_color" without concrete usage examples led the LLM to make incorrect assumptions.

4. **Test both success and failure paths**: The parser worked for one format but failed for another (XML vs code blocks). Both need testing.

5. **Version compatibility matters**: Using Python 3.9 when the code expects 3.11+ features caused complete pipeline failure.

---

## Related Documentation

- `harness/prompt_templates/build_scenes_system.md` - System prompt for scene generation
- `harness/parser.py` - Output parser for LLM responses  
- `scripts/build_video.sh` - Main build orchestration script
- `docs/reference_docs/visual_helpers.md` - Color helper documentation
