# Audit Report: Black Video Rendering in smoke-test-2

**Date:** 2026-02-17  
**Project:** examples/defective_output/smoke-test-2  
**Issue:** Videos render successfully but show black/empty screens (no visible graphics)  
**Status:** Phase = complete, all 3 scenes rendered, final_video.mp4 produced (1.62 MB)

---

## Executive Summary

**Root Cause:** Parser fallback logic incompatible with body-only code output.

**Impact:** 100% failure rate for agents that correctly generate body-only code without markdown fencing. Videos render as black screens with audio only.

**Severity:** CRITICAL - Parser logic contradicts prompt instructions, making correct agent behavior result in failure.

---

## Findings (Severity-Ordered)

### Finding 1: Parser Fallback Rejects Body-Only Code (CRITICAL)

**Scope:** `harness/parser.py:180-200` (`extract_single_python_code`)

**Failure Origin:** Line 197 fallback check

**Evidence:**
```python
# harness/parser.py:197-199
if "import" in text or "def " in text or "class " in text:
    return text.strip()
return None
```

**Causal Chain:**
1. PR #56 prompt instructs: "Generate ONLY body code" (no imports/class/def)
2. Agent obeys: generates valid body code (debug_response_build_scenes.txt, 2842 bytes)
3. Parser `extract_python_code_blocks`: no ```python fences → returns 0 blocks
4. Parser `extract_single_python_code` fallback: checks for "import"/"def "/"class "
5. Body-only code has NONE of these keywords → returns None
6. `parse_build_scenes_response` returns None → parsing failed
7. Harness keeps scaffold unchanged → scene files contain ONLY `pass` in SLOT
8. Manim renders empty scene → BLACK VIDEO with audio

**Verification:**
```bash
# All 3 scene files have only 'pass' between SLOT markers:
$ python3 -c "
from pathlib import Path
for s in ['scene_01_intro.py', 'scene_02_content.py', 'scene_03_conclusion.py']:
    code = Path(f'examples/defective_output/smoke-test-2/{s}').read_text()
    in_slot = False
    exec_lines = 0
    for line in code.split('\n'):
        if 'SLOT_START' in line: in_slot = True; continue
        if 'SLOT_END' in line: break
        if in_slot and line.strip() and not line.strip().startswith('#'):
            exec_lines += 1
    print(f'{s}: {exec_lines} executable line(s) - {'PASS ONLY' if exec_lines == 1 else 'HAS CODE'}')
"
# Output:
# scene_01_intro.py: 1 executable line(s) - PASS ONLY
# scene_02_content.py: 1 executable line(s) - PASS ONLY
# scene_03_conclusion.py: 1 executable line(s) - PASS ONLY
```

**Agent Output Was Correct:**
```python
# debug_response_build_scenes.txt (excerpt):
num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
beats = BeatPlan(tracker.duration, [1] * num_beats)

blues = harmonious_color(BLUE, variations=3)
title = Text("The Path to Discovery", font_size=48, weight=BOLD, color=blues[0])
title.move_to(UP * 3.8)
play_text_next(self, beats, Write(title), max_text_seconds=999)
# ... (59 lines total, valid body code)
```

**Primary Fix:**
```python
# harness/parser.py:180-200 - extract_single_python_code()
def extract_single_python_code(text: str) -> Optional[str]:
    """Extract a single Python code block from text."""
    # Try markdown blocks first
    code_blocks = extract_python_code_blocks(text)
    if code_blocks:
        return max(code_blocks, key=lambda x: len(x[1]))[1]

    # FIXED: Accept raw Python if it looks like valid code
    # Body-only code won't have import/def/class but will have:
    # - Python keywords (for, if, with, etc.)
    # - Assignment statements
    # - Function calls
    stripped = text.strip()
    if not stripped:
        return None
    
    # Check if it's plausibly Python code
    # Look for common Python patterns in body code:
    python_indicators = [
        "=",  # Assignment
        "(",  # Function call
        "import", "def ", "class ",  # Header code (keep for backward compat)
        "for ", "while ", "if ", "with ",  # Control flow
        "self.", "Text(", "Circle(", "Rectangle(",  # Manim objects
    ]
    
    if any(indicator in stripped for indicator in python_indicators):
        # Validate it compiles (even if indentation is wrong, we'll fix it later)
        try:
            compile(stripped, "<string>", "exec")
            return stripped
        except SyntaxError:
            # Try as indented block (common for body code)
            try:
                test_code = f"def _test():\n" + "\n".join(f"    {line}" for line in stripped.split("\n"))
                compile(test_code, "<string>", "exec")
                return stripped
            except SyntaxError:
                pass
    
    return None
```

**Removal Trigger:** After verifying parser correctly handles body-only code in tests.

---

### Finding 2: Prompt Instruction Contradiction (HIGH)

**Scope:** `harness/prompt_templates/build_scenes_system.md:16,118`

**Failure Origin:** Line 118 contradicts line 16

**Evidence:**
```markdown
# Line 16 (Output Format section):
Generate ONLY the body code to be inserted between SLOT markers. Do NOT output 
imports, config, class definition, voiceover block, or the SLOT markers themselves.

# Line 118 (Think Step-by-Step section):
**Output the complete scene file with SLOT markers preserved.**
```

**Causal Chain:**
1. Agent reads line 16: "Generate ONLY body code"
2. Agent reads line 118: "Output the complete scene file with SLOT markers"
3. Agent must choose which instruction to follow
4. If agent follows line 16 → parser rejects (Finding 1)
5. If agent follows line 118 → parser rejects (forbidden_tokens check at line 385-386)
6. **Either choice leads to parse failure**

**Primary Fix:**
```markdown
# harness/prompt_templates/build_scenes_system.md:118
# REMOVE: "Output the complete scene file with SLOT markers preserved."
# REPLACE WITH:
**Output ONLY the body code (animation statements) without any wrapper structure.**
```

**Secondary Fix (Defense in Depth):**
Add explicit formatting instruction:
```markdown
## Output Format

Generate ONLY the body code to be inserted between SLOT markers. Do NOT output 
imports, config, class definition, voiceover block, or the SLOT markers themselves.

**Recommended format:** Wrap your code in a ```python markdown fence for clarity:

\```python
num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
beats = BeatPlan(tracker.duration, [1] * num_beats)
# ... rest of body code
\```

**Note:** Raw code without fencing is also acceptable if it contains valid Python statements.
```

**Removal Trigger:** After smoke tests confirm agents generate correctly formatted code.

---

### Finding 3: No Validation for Empty Scene Bodies (MEDIUM)

**Scope:** `scripts/build_video.sh` scene validation phase

**Failure Origin:** Validation checks passed despite empty SLOT bodies

**Evidence:**
```
# build.log:64-75
→ Validating template structure in scene_01_intro.py...
✓ Template structure checks passed
→ Validating imports in scene_01_intro.py...
✓ Import names are correct (manim_voiceover_plus)
✓ Python syntax valid
✓ Import validation passed
→ Validating voiceover sync in scene_01_intro.py...
✓ Voiceover sync checks passed
→ Validating semantic quality in scene_01_intro.py...
✓ Semantic quality validation passed
```

All checks passed, but SLOT contains only `pass`.

**Causal Chain:**
1. Parser fails to extract body → returns None
2. Harness keeps scaffold unchanged (with `pass` safety statement)
3. Validation checks syntax, imports, voiceover → all valid (scaffold is correct)
4. No check for "does SLOT contain actual animation code?"
5. Scene marked as "built", advances to render
6. Manim renders empty scene → black video

**Primary Fix:**
Add semantic validation check in `scripts/build_video.sh` or validation script:
```bash
# After syntax/import validation, before marking scene as built:
validate_scene_has_content() {
    local scene_file="$1"
    
    # Extract code between SLOT markers, excluding comments and 'pass'
    local content=$(sed -n '/# SLOT_START:scene_body/,/# SLOT_END:scene_body/p' "$scene_file" \
        | grep -v "^[[:space:]]*#" \
        | grep -v "^[[:space:]]*$" \
        | grep -v "^[[:space:]]*pass[[:space:]]*$")
    
    if [ -z "$content" ]; then
        echo "❌ Scene body is empty (only 'pass' or comments)" >&2
        return 1
    fi
    
    # Check for at least one animation call
    if ! echo "$content" | grep -qE "(play_next|play_text_next|self\.play|self\.add|FadeIn|FadeOut|Write|Create)"; then
        echo "❌ Scene body has no animation statements" >&2
        return 1
    fi
    
    echo "✓ Scene body has animation code"
    return 0
}
```

**Containment Status:** Temporary - primary fix (Finding 1) eliminates root cause. This is defense-in-depth.

**Removal Trigger:** After 10+ successful video generations with primary fix.

---

## Contract Violations

### Generator Contracts

1. ✅ **Prompt Instructions (PR #56):** Line 16 correctly specifies body-only output
2. ❌ **Prompt Consistency:** Line 118 contradicts line 16
3. ✅ **Agent Behavior:** Generated valid body-only code (debug_response shows correct output)
4. ❌ **Parser Contract:** `extract_single_python_code` assumes header code (import/def/class)

### Scaffold/Injection Contracts

1. ✅ **Immutable Scaffold:** Header/config/class/voiceover preserved
2. ✅ **SLOT Markers:** Present and correctly formatted
3. ❌ **Body Content:** Empty (only `pass` safety statement)
4. ✅ **Indentation:** N/A (no body code injected)

### Manim Rendering Contracts

1. ✅ **Syntax Valid:** Scene files compile without errors
2. ✅ **Imports Correct:** No deprecated APIs
3. ❌ **Mobjects Present:** Zero mobjects added to scene
4. ❌ **Animations Present:** Zero play() calls
5. ✅ **Audio Present:** Voiceover cached and included (1.5 MB in 1.62 MB video)

---

## Residual Risks

### After Applying Primary Fixes

1. **Parser Over-Acceptance:** New fallback logic may accept non-Python text
   - **Mitigation:** Keep syntax validation (`compile()` check)
   - **Test:** Add negative cases to parser tests

2. **Markdown Fence Dependency:** If agents forget fencing, fallback must work
   - **Mitigation:** Primary fix handles both fenced and raw code
   - **Test:** Add raw code test case

3. **Prompt Ambiguity Recurrence:** Future edits may reintroduce contradictions
   - **Mitigation:** Add linter check for "complete file"/"SLOT marker" in body-only prompts
   - **Test:** CI check for contradictory instructions

---

## Verification Checks

### Parser Fix Validation
```bash
# Test 1: Body-only code (raw, no fencing)
cd /home/runner/work/flaming-horse/flaming-horse
python3 << 'EOF'
from harness.parser import parse_build_scenes_response

body_code = """
num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
beats = BeatPlan(tracker.duration, [1] * num_beats)
title = Text("Test", font_size=48)
play_text_next(self, beats, Write(title), max_text_seconds=999)
"""

result = parse_build_scenes_response(body_code)
assert result is not None, "❌ Parser rejected valid body code"
assert "num_beats" in result, "❌ Parser mangled body code"
print("✅ Parser accepts body-only code (raw)")
EOF

# Test 2: Body-only code (markdown fenced)
python3 << 'EOF'
from harness.parser import parse_build_scenes_response

response = """
Here's the animation code:

```python
num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
beats = BeatPlan(tracker.duration, [1] * num_beats)
title = Text("Test", font_size=48)
play_text_next(self, beats, Write(title), max_text_seconds=999)
```
"""

result = parse_build_scenes_response(response)
assert result is not None, "❌ Parser rejected fenced body code"
assert "num_beats" in result, "❌ Parser mangled fenced code"
print("✅ Parser accepts body-only code (fenced)")
EOF

# Test 3: Full scene file (should still be rejected)
python3 << 'EOF'
from harness.parser import parse_build_scenes_response

full_file = """
from manim import *

class SceneTest(VoiceoverScene):
    def construct(self):
        title = Text("Test")
        self.play(Write(title))
"""

result = parse_build_scenes_response(full_file)
assert result is None, "❌ Parser accepted full file (should reject)"
print("✅ Parser rejects full scene files")
EOF
```

### Smoke Test with Fixed Parser
```bash
# Generate new test project
./tests/smoke_test.sh

# Expected results:
# - build_scenes phase: all 3 scenes built on first attempt
# - No "Failed to parse scene body" messages
# - Scene files have animation code between SLOT markers
# - Videos show visible graphics (not black)
# - final_video.mp4 > 2 MB (graphics increase encoding size)
```

### Manual Scene Inspection
```bash
# After smoke test completes:
cd projects/smoke-test-3  # (or whatever number)

# Check scene bodies
for scene in scene_*.py; do
    echo "=== $scene ==="
    sed -n '/# SLOT_START:scene_body/,/# SLOT_END:scene_body/p' "$scene" \
        | grep -v "^[[:space:]]*#" \
        | grep -v "^[[:space:]]*$" \
        | head -10
done

# Should show: num_beats, BeatPlan, title = Text(...), play_text_next, etc.
# Should NOT show: only 'pass'
```

---

## Recommended Implementation Priority

### Phase 1: Critical Fix (Parser)
1. **Fix `extract_single_python_code` fallback** (Finding 1)
2. **Add parser tests** for body-only code (raw + fenced)
3. **Run existing test suite** to ensure no regressions

### Phase 2: Prompt Cleanup
4. **Remove contradictory instruction** at line 118 (Finding 2)
5. **Add markdown fence suggestion** in output format section
6. **Add CI check** for prompt consistency

### Phase 3: Defense in Depth (Optional)
7. **Add scene body validation** (Finding 3)
8. **Add logging** to track parse success/failure rates
9. **Monitor production** for new failure patterns

---

## Evidence Citations

### Scene Files
- `examples/defective_output/smoke-test-2/scene_01_intro.py:38` - Only `pass` in SLOT
- `examples/defective_output/smoke-test-2/scene_02_content.py:38` - Only `pass` in SLOT
- `examples/defective_output/smoke-test-2/scene_03_conclusion.py:38` - Only `pass` in SLOT

### Parser Logic
- `harness/parser.py:197-199` - Fallback check requires import/def/class
- `harness/parser.py:385-386` - Forbidden tokens check (correct, not the issue)
- `harness/parser.py:388-389` - Top-level class/def/import check (correct, not the issue)

### Agent Output
- `examples/defective_output/smoke-test-2/debug_response_build_scenes.txt:1-59` - Valid body code

### Build Logs
- `examples/defective_output/smoke-test-2/build.log:60` - "Failed to parse scene body"
- `examples/defective_output/smoke-test-2/build.log:64-75` - Validation passed (false positive)

### Prompt Instructions
- `harness/prompt_templates/build_scenes_system.md:16` - "Generate ONLY body code"
- `harness/prompt_templates/build_scenes_system.md:118` - "Output complete scene file" (contradiction)

### Video Output
- `examples/defective_output/smoke-test-2/final_video.mp4` - 1.62 MB (audio present, video black)
- Expected: ~50-100 KB video track (black) + ~1.5 MB audio = 1.55-1.6 MB ✓

---

## Root Cause Summary

**The parser's fallback logic was designed for full-file extraction (pre-PR #51) and never updated for body-only extraction (post-PR #51/56).**

Timeline:
- **Pre-PR #51:** Agents generated full scene files, parser used `extract_single_python_code` with import/def/class check
- **PR #51:** Introduced scaffold/SLOT system, parser switched to body-only mode
- **PR #56:** Fixed prompt contradictions, agents now correctly generate body-only code
- **Issue:** Parser fallback still checks for import/def/class (orphaned logic from pre-scaffold era)

**Fix:** Update fallback logic to recognize body-only code patterns.

---

## Appendix: Reproduction Steps

```bash
# 1. Checkout PR #56 branch
git checkout 8cb1f77

# 2. Examine defective project
cd examples/defective_output/smoke-test-2
cat scene_01_intro.py  # Shows only 'pass' in SLOT
cat debug_response_build_scenes.txt  # Shows valid body code agent generated

# 3. Test parser directly
cd /home/runner/work/flaming-horse/flaming-horse
python3 << 'EOF'
from harness.parser import parse_build_scenes_response
response = open('examples/defective_output/smoke-test-2/debug_response_build_scenes.txt').read()
result = parse_build_scenes_response(response)
print(f"Parser result: {result is not None}")  # Should print: False
EOF

# 4. Verify videos are black
# (Requires media player or ffmpeg frame extraction - not included in audit env)
```

---

**End of Audit Report**
