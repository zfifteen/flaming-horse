# Unresolved Issues - Agent Interactions Troubleshooting Guide

This document catalogs issues encountered while troubleshooting the Flaming Horse video generation pipeline. Each issue includes sufficient detail for another LLM to reproduce and diagnose.

---

## Issue 1: Model Outputs Full Python File Instead of Scene Body

### Description
When generating scene code, the model outputs a complete Python file (with imports, class definition, config) instead of just the scene body code that should be injected between `# SLOT_START:scene_body` and `# SLOT_END:scene_body` markers.

### Symptom
- Parser fails with: `❌ Failed to parse scene body from response`
- Debug file shows full file output starting with `from manim import *`
- Scene file ends up with empty body (`pass` only)

### Example Debug File
Location: `generated/smoke-test-8/debug_response_build_scenes.txt`

```
2: Let me analyze the requirements:
...
42: ```python
43: """
44: Manim Community Edition VoiceoverScene Template
45: Optimized for cached Qwen integration
46: 
47: Scene 03 Conclusion: The Choice
48: """
49: 
50: from manim import *
```

### Root Cause
The system prompt was not explicit enough about output format. Even with `<scene_body>` XML tags in the prompt, the model ignores them and outputs full files.

### Attempts to Fix
1. Added explicit "NO full file" warnings to prompts
2. Added examples showing correct vs incorrect output
3. Rewrote prompts to be extremely explicit
4. Still fails intermittently

---

## Issue 2: Model Uses Undefined Variables

### Description
The model generates code that references variables that are never defined in the scene body.

### Symptom
- Runtime error: `NameError: name 'code_group' is not defined`
- Or: `NameError: name 'choice' is not defined`
- Or: `NameError: name 'x' is not defined`

### Example
Generated code (from `generated/smoke-test-1/scene_01_intro.py`):
```python
# Model generated this - error on line using code_group:
play_next(self, beats, FadeIn(code_group))  # code_group never defined!
```

### Root Cause
1. The model doesn't understand variable scoping - it assumes variables from its "imagination" exist
2. When trying to use loops, it references loop variables outside the loop
3. When using "code rain" effects, it references a `code_group` that was never created

### Attempts to Fix
1. Added "NO LOOPS" rule to prompts
2. Added explicit examples of correct variable usage
3. Added common error patterns with fixes to repair_system.md
4. Still fails because model can generate any Python

---

## Issue 3: Model Uses random.choice() Without Import

### Description
Scene body code uses `choice()` or `random.choice()` without importing the random module.

### Symptom
- Runtime error: `NameError: name 'choice' is not defined`

### Example Generated Code
```python
char = choice(code_chars)  # WRONG - choice not defined
# OR
import random
char = random.choice(code_chars)  # Still wrong - random not imported in scaffold
```

### Root Cause
The scaffold only imports `numpy as np`, not `random`. The model assumes random is available.

### Attempts to Fix
1. Added explicit rule: "NO random functions - use deterministic values"
2. Added to repair_system.md error patterns
3. Still fails - model forgets this rule

---

## Issue 4: Model Uses Loops in Scene Body

### Description
The model generates `for` loops in scene body code, but loops don't work inside the `with voiceover()` block properly.

### Symptom
- Code passes syntax check but fails at runtime
- Or: undefined variable errors from loop

### Example Generated Code
```python
# WRONG - loop doesn't work in voiceover block
for x in np.linspace(-8, 8, 20):
    line = Line(np.array([x, -5, 0]), np.array([x, 5, 0]))
```

### Root Cause
The scene body runs inside a `with voiceover()` context. Loops may not execute as expected.

### Attempts to Fix
1. Added very explicit "NO LOOPS" rule with examples
2. Added rule to repair_system.md
3. Still fails - model defaults to generating loops for "multiple elements"

---

## Issue 5: JSON Parsing Failures - Various Formats

### Description
When model outputs JSON (for plan or narration), parsing frequently fails due to:
- Extra closing braces `}`
- Parentheses instead of quotes: `"key": (value)` instead of `"key": "value"`
- Trailing commas
- Single quotes instead of double quotes
- Explanatory text before/after JSON

### Symptom
- `❌ Failed to parse narration_script.py from response`
- `❌ Failed to parse artifacts from response`

### Example Failed Output
Location: `generated/smoke-test-5/debug_response_narration.txt`

```
49: ```python
50: # Narration Script for "The Matrix: A Digital Reality"
...
69: }
70: }  <-- EXTRA BRACE!
```

### Another Example
```
{
  "scene_01_intro": (
      "Welcome to a world beyond what you see."
  ),
}
```

### Root Cause
MINIMAX model (and others) don't consistently output valid JSON.

### What Fixed It (Partially)
1. Added preprocessing in `harness/parser.py` `extract_json_block()`:
   - Remove parentheses: `: (value)` → `: "value"`
   - Remove trailing commas
2. Added JSON schema to prompts with examples
3. Added to narration_system.md: "Use double quotes, NOT parentheses"

---

## Issue 6: Plan Uses Wrong Key Name

### Description
The plan.json uses `narrative_key` instead of `narration_key`.

### Symptom
- Validation warning: `scene[0] missing narration_key`
- But the field exists as `narrative_key`

### Example
Location: `generated/smoke-test-5/plan.json`
```json
{
  "id": "scene_01_intro",
  "title": "Enter the Matrix",
  "narrative_key": "scene_01_intro",  // WRONG - should be narration_key
}
```

### Root Cause
The model confuses "narrative" vs "narration" keys.

### What Fixed It
Added to `harness/parser.py` `parse_plan_response()`:
```python
# Normalize narration_key: some models output "narrative_key" instead
for scene in plan.get("scenes", []):
    if "narrative_key" in scene and "narration_key" not in scene:
        scene["narration_key"] = scene.pop("narrative_key")
```

---

## Issue 7: Scene Files Not Built for All Scenes

### Description
The build_scenes phase only generates content for scene 1. Scenes 2 and 3 end up with empty bodies.

### Symptom
- Scene files `scene_02_content.py` and `scene_03_conclusion.py` only have:
  ```python
  with self.voiceover(text=SCRIPT["scene_02_content"]) as tracker:
      # SLOT_START:scene_body
      pass  # TEMP scaffold stub
      # SLOT_END:scene_body
  ```
- Video shows black screen for scenes 2 and 3
- Frames extracted show empty content (14KB vs 200KB+ for valid frames)

### Root Cause
The build loop should iterate through all scenes, but either:
1. The model keeps outputting full files and fails to parse
2. The loop terminates early due to some condition

### Debug Evidence
Location: `generated/smoke-test-8/build.log`
```
Line 60: [Run 3] Phase: build_scenes — invoking agent...
Line 69: ✅ Phase build_scenes completed successfully  <-- Only once!

Line 10391: [Run 4] Phase: build_scenes — invoking agent...  
Line 10401: ❌ Failed to parse scene body from response
Line 10440: [Run 5] Phase: build_scenes — invoking agent...
```

### Location of Scene Files
- `generated/smoke-test-8/scene_01_intro.py` - 154 lines (has content)
- `generated/smoke-test-8/scene_02_content.py` - 45 lines (empty body)
- `generated/smoke-test-8/scene_03_conclusion.py` - 45 lines (empty body)

---

## Issue 8: MINIMAX Provider Not Being Used

### Description
Even though `.env` has `LLM_PROVIDER=MINIMAX`, the logs show "Using Python harness (direct xAI API)".

### Symptom
```
Using Python harness (direct xAI API)
🤖 Harness using:
   Provider: XAI
   Model: grok-code-fast-1
```

### Root Cause
The build_video.sh script doesn't export MINIMAX variables to the harness:

```bash
# Old code (line 768):
export XAI_API_KEY="$XAI_API_KEY"
# Missing: MINIMAX_API_KEY and LLM_PROVIDER
```

### What Fixed It
Added to `scripts/build_video.sh`:
```bash
export XAI_API_KEY="$XAI_API_KEY"
export MINIMAX_API_KEY="$MINIMAX_API_KEY"
export LLM_PROVIDER="$LLM_PROVIDER"
```

Also fixed hardcoded log message at line 751:
```bash
echo "Using Python harness (${LLM_PROVIDER:-XAI} API)"
```

---

## Issue 9: Font Warning - Courier vs Courier New

### Description
The model uses `font="Courier"` but macOS only has `font="Courier New"`.

### Symptom
```
WARNING: Font Courier not in ['AppleSystemUIFont', 'Arial', 'Courier New', ...]
```

### Root Cause
The model uses "Courier" as font name but Manim translates this to system font lookup which fails on macOS.

### Attempted Fix
Added to AGENTS.md and build_scenes_system.md:
- Use `font="Courier New"` not `font="Courier"`

Still happens - model forgets the rule.

---

## Issue 10: Empty Scene Body Passes Validation

### Description
A scene with only `pass` in the body passes validation but renders as black screen.

### Symptom
- Template structure: passes
- Import validation: passes
- Python syntax: passes
- Voiceover sync: passes
- Runtime: renders black (no animations)

### Root Cause
Validation doesn't check if the scene body is actually implemented or just has `pass`.

### Location
`generated/smoke-test-8/scene_02_content.py` - has `pass` but passes validation.

---

## Issue 11: Video Frames Show Black for Some Scenes

### Description
Extracted frames from video show black screen for scenes 2 and 3 while scene 1 has content.

### Evidence
Command: `ffmpeg -i final_video.mp4 -vf "fps=1" frames/frame_%04d.png`

Results:
- Frames 1-17: Have content (~200KB each)
- Frames 18-58: Black (~14KB each)

### Root Cause
Same as Issue 7 - scenes 2 and 3 have empty bodies.

---

## Issue 12: ManimColor TypeError with numpy

### Description
Passing numpy values directly to color parameter causes TypeError.

### Symptom
```
TypeError: ManimColor only accepts int, str, list[int, int, int]... not <class 'numpy.float64'>
```

### Example Generated Code
```python
# WRONG
grid_line.set_stroke(color=greens[0])  # greens[0] might be numpy array!
```

### What Should Work
```python
# RIGHT - use built-in colors
color=GREEN
# OR use harmonious_color directly
title = Text("Hello", color=harmonious_color(GREEN, variations=3))
```

### Attempts to Fix
Added to repair_system.md error patterns.

---

## Summary of Files Modified During Troubleshooting

### Prompts
- `harness/prompt_templates/narration_system.md` - Added JSON schema, fixed format
- `harness/prompt_templates/plan_system.md` - Added JSON schema
- `harness/prompt_templates/build_scenes_system.md` - Rewrote for clarity, added NO LOOPS rules
- `harness/prompt_templates/repair_system.md` - Added common errors with fixes
- `harness/prompt_templates/core_rules.md` - Added base rules

### Parser
- `harness/parser.py` - Multiple fixes:
  - JSON extraction with preprocessing for parentheses/trailing commas
  - Plan parser handles narrative_key → narration_key
  - Build scenes parser handles full file output extraction
  - Validation warnings for random/choice usage

### Scripts
- `scripts/build_video.sh` - Fixed MINIMAX environment variables
- `scripts/scaffold_scene.py` - No changes needed

### AGENTS.md
- Added EXTERNAL ASSETS - FORBIDDEN section
- Added LaTeX and Code Text rules
- Added validation checklist items

---

## Key Insight

The fundamental problem is that the LLM can generate arbitrary Python code, and we can't anticipate all possible errors through prompts alone. Possible solutions:

1. **Pre-built Visual Components** - Create a library of pre-built visual elements (title, bullets, simple shapes) that the model can compose without writing custom code
2. **Stricter Validation** - Add more pre-runtime checks to catch undefined variables
3. **Simplified DSL** - Create a domain-specific language that the model outputs instead of Python
4. **Template with Validators** - The scaffold could include runtime checks that fail fast with clear errors
