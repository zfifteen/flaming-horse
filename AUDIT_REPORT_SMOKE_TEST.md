# Generator Audit Report: smoke-test Failure Analysis

**Auditor**: Flaming Horse Generator Auditor  
**Date**: 2026-02-17  
**Project**: examples/defective_output/smoke-test  
**Failure Phase**: build_scenes (repeated parse failure → syntax error loop)

---

## Executive Summary

**Root Cause**: Critical prompt ambiguity in `build_scenes_system.md` and `harness/prompts.py` user prompt causing agents to output complete scene files instead of body-only code, leading to parser rejection and empty scaffold injection.

**Impact**: 100% failure rate on build_scenes phase with infinite self-heal loops (4 retries × 4 heal attempts = 16 failed attempts).

**Primary Fix Target**: `harness/prompt_templates/build_scenes_system.md` lines 14-118 and `harness/prompts.py` lines 309-324.

---

## Findings (Severity-Ordered)

### 🔴 CRITICAL Finding 1: Prompt Instruction Contradiction

**Scope**: `harness/prompt_templates/build_scenes_system.md` and `harness/prompts.py`

**Origin**: Lines 14-16 and 70-71 of build_scenes_system.md state:
```markdown
Generate exactly ONE complete scene file that preserves the scaffold header and SLOT markers.
Edit ONLY inside the SLOT_START_SCENE_BODY region.
```

AND line 118 reinforces:
```markdown
**Output the complete scene file with SLOT markers preserved.**
```

User prompt (prompts.py:324) further states:
```markdown
Output ONLY the Python code. Start with the imports.
```

**Contradiction**: These instructions are contradictory:
- "complete scene file" + "Start with the imports" → Agent outputs full file with headers
- "Edit ONLY inside SLOT_START_SCENE_BODY" → Parser expects body-only code

**Causal Chain**:
1. Agent receives ambiguous instruction: "complete file" vs "ONLY inside SLOT"
2. Agent interprets "complete scene file" + "Start with imports" literally
3. Agent outputs full file with imports, config, class, SLOT markers (as seen in debug_response_build_scenes.txt)
4. Parser (parse_build_scenes_response) rejects output containing forbidden tokens: `from manim import`, `class Scene`, `SLOT_START:scene_body`
5. Parser returns None → scaffold unchanged (still contains empty SLOT with comments only)
6. Syntax check fails: IndentationError (empty with block at line 36)
7. Self-heal invokes scene_repair with same ambiguous instructions
8. Loop repeats 16 times until exhaustion

**Evidence**:
- `debug_response_build_scenes.txt`: Lines 1-73 show agent outputting complete file starting with imports
- `build.log`: Lines 56-61 show "❌ Failed to parse scene body from response" repeatedly
- `scene_01_intro.py`: Lines 37-44 show empty SLOT body (only PROMPT comments, no actual code)
- `errors.log`: "IndentationError: expected an indented block after 'with' statement on line 36"

**Primary Fix**:
1. **Remove contradictory language** from build_scenes_system.md:
   - Line 14: Change "Generate exactly ONE complete scene file" → "Generate body code only"
   - Line 70: Remove "Output only the current scene's complete Python code"
   - Line 118: Change "Output the complete scene file with SLOT markers preserved" → "Output ONLY the body code to inject between SLOT markers"

2. **Clarify user prompt** in prompts.py:
   - Line 309: Change "Generate the complete Python scene file" → "Generate the body code for the voiceover block"
   - Line 324: Change "Output ONLY the Python code. Start with the imports." → "Output ONLY the body code to be inserted between SLOT markers. Do NOT include imports, config, class definition, or SLOT markers themselves. Output should start with animation code (e.g., num_beats = ...)."

3. **Add explicit rejection example**:
```markdown
## ❌ WRONG (Will Be Rejected):
```python
from manim import *
class Scene01Intro(VoiceoverScene):
    def construct(self):
        with self.voiceover(...) as tracker:
            # SLOT_START:scene_body
            num_beats = ...
```

## ✅ CORRECT (Body Only):
```python
            num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
            beats = BeatPlan(tracker.duration, [1] * num_beats)
            
            blues = harmonious_color(BLUE, variations=3)
            title = Text("Awakening to Reality", font_size=48, weight=BOLD, color=blues[0])
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))
```
```

**Containment**: Parser already correctly rejects full files via forbidden_tokens check (lines 363-377, 403-410). This is working as designed but insufficient when prompt creates wrong output format.

---

### 🟠 HIGH Finding 2: Repair Prompt Inherits Same Ambiguity

**Scope**: `harness/prompt_templates/repair_system.md`

**Origin**: Lines 24-25 state:
```markdown
5. Output the corrected complete scene file with scaffold intact.
```

AND line 100 states:
```markdown
Output ONLY the corrected body code inside SLOT_START_SCENE_BODY. Do not include scaffold, headers, or markers.
```

**Contradiction**: "complete scene file with scaffold" contradicts "ONLY body code".

**Causal Chain**:
- Scene repair inherits same prompt structure confusion
- Agent outputs full file again (seen in debug_response_scene_repair.txt)
- Parser rejects again
- Self-heal loop cannot break out

**Evidence**:
- `debug_response_scene_repair.txt`: Lines 1-51 show agent outputting full file
- `build.log`: Lines 78-82, 164-169 show repeated "❌ Failed to parse repaired scene body"

**Primary Fix**:
1. **Remove line 24** from repair_system.md or change to: "Output ONLY the corrected body code for injection"
2. **Keep line 100 as-is** (already correct)
3. **Add prominent WARNING box**:
```markdown
## ⚠️ CRITICAL: Output Format
**You MUST output body code ONLY. NOT a complete file.**

The scaffold already exists. You are filling in the missing piece between SLOT markers.
```

---

### 🟡 MEDIUM Finding 3: Scaffold Template Contains Ambiguous PROMPT Comments

**Scope**: `scripts/scaffold_scene.py` lines 45-52

**Origin**: SLOT body contains multiple PROMPT comment lines:
```python
            # SLOT_START:scene_body
            # PROMPT: Design unique visual flow per scene...
            # PROMPT: Use structurally different patterns...
            # PROMPT: Position bullets at LEFT * 3.5...
            # PROMPT: Ensure layout contracts...
            # PROMPT: Use BeatPlan with num_beats = ...
            # PROMPT: Set max_text_seconds=999 in play_text_next...
            # SLOT_END:scene_body
```

**Issue**: These PROMPT comments make the SLOT body non-empty, but they're not executable code. Parser validation (inject_body_into_scaffold, lines 34-40) checks for "at least one non-comment statement" but empty SLOT passes through because comments are ignored.

**Result**: When agent fails to output valid body, scaffold is written with only comments → empty with block → IndentationError.

**Causal Chain**:
1. Agent parse fails (returns None)
2. Scaffold remains unchanged with PROMPT comments only
3. Python interpreter sees `with ... as tracker:` followed by only comments → expects indented statement
4. SyntaxError: "expected an indented block after 'with' statement"

**Primary Fix**:
1. **Add pass statement** to scaffold template after SLOT_START marker:
```python
            # SLOT_START:scene_body
            pass  # Placeholder - will be replaced by generated code
            # PROMPT: Design unique visual flow per scene...
```

2. **OR**: Remove PROMPT comments entirely and move to external guidance (less preferred as comments are useful for agent reference).

**Containment**: This is a last-resort safety issue. Primary fix (Finding 1) prevents reaching this state.

---

### 🟢 LOW Finding 4: Parser Forbidden Tokens Check is Comprehensive

**Scope**: `harness/parser.py` lines 363-377, 457-471

**Status**: WORKING AS DESIGNED ✓

**Observation**: Parser correctly rejects full files containing:
- `from manim import`
- `class Scene`
- `def construct`
- `SLOT_START:scene_body`
- etc.

This rejection is correct behavior. The issue is that the prompt creates wrong output, not that the parser fails to handle it.

**No Action Required**: Parser validation is functioning correctly.

---

### 🟢 LOW Finding 5: Self-Heal Loop Exhaustion is Correct Behavior

**Scope**: `scripts/build_video.sh` self-heal logic (lines visible in build.log)

**Status**: WORKING AS DESIGNED ✓

**Observation**: After 4 failed self-heal attempts, system correctly:
- Marks phase as failed
- Sets needs_human_review flag
- Stops build loop
- Preserves debug artifacts

**No Action Required**: Failure handling is correct. Issue is upstream in prompt ambiguity.

---

## Root-Cause Analysis Summary

### Failure Origin (First Bad Step)
**Location**: `harness/prompt_templates/build_scenes_system.md` lines 14-16, 70-71, 118

**Mechanism**: Contradictory instructions ("complete scene file" + "Edit ONLY inside SLOT") cause agent to misinterpret output format.

### Why Existing Logic Allowed Failure
The prompt system was designed with an assumption that "complete scene file" would be clear from context (scaffold example). However:
1. LLM agents interpret "complete" + "Start with imports" as a literal instruction
2. The example (lines 28-60) shows full file structure, reinforcing wrong interpretation
3. No explicit negative example ("DON'T output this format")
4. System prompt says "complete file", user prompt says "start with imports", but parser expects body-only

### Architecture Issue
The scaffold-based approach (deterministic scaffold + agent-generated body) is sound, but prompt documentation doesn't match parser expectations:
- **Scaffold layer**: Expects body injection
- **Parser layer**: Rejects full files (correct)
- **Prompt layer**: Requests "complete scene file" (incorrect for parser)

This is a **documentation/instruction mismatch**, not a code bug.

---

## Generator-Level Fixes (Priority Ordered)

### 1. HIGH PRIORITY: Clarify build_scenes Prompt

**File**: `harness/prompt_templates/build_scenes_system.md`

**Changes**:
- Line 14: "Generate body code only"
- Line 16: "Output body code for injection between SLOT markers"
- Line 70: Remove or change to "Output body-only code for current scene"
- Line 118: "Output ONLY the body code (no headers, imports, or markers)"
- Add WRONG/CORRECT examples showing rejected vs accepted formats

**File**: `harness/prompts.py`

**Changes**:
- Line 309: "Generate the body code for `{scene_id}` voiceover block"
- Line 324: "Output ONLY the body code to be inserted between SLOT markers. Do NOT include imports, config, class definition, or SLOT markers. Start with animation code (e.g., num_beats = ...)."

### 2. MEDIUM PRIORITY: Clarify repair_system Prompt

**File**: `harness/prompt_templates/repair_system.md`

**Changes**:
- Line 24: Remove or change to "Output ONLY corrected body code"
- Add WARNING box emphasizing body-only output
- Add WRONG/CORRECT examples

### 3. LOW PRIORITY: Add Scaffold Safety

**File**: `scripts/scaffold_scene.py`

**Changes**:
- Line 46: Add `pass  # Placeholder` after SLOT_START marker
- This prevents SyntaxError if injection fails

### 4. DOCUMENTATION: Update AGENTS.md Examples

**File**: `AGENTS.md`

**Changes**:
- Clarify that scene templates show "complete structure for understanding" but agents output "body code only"
- Add explicit note: "When generating scenes, output ONLY the code between SLOT markers"

---

## Residual Risks

### After Primary Fixes Applied

1. **Agent Interpretation Variability** (LOW)
   - Different LLMs may still interpret "body code" differently
   - Mitigation: Add explicit negative examples in prompt
   - Verification: Test with multiple model providers

2. **Backward Compatibility** (LOW)
   - Existing working projects may have been lucky with their agent outputs
   - Mitigation: Changes improve clarity without breaking correct behavior
   - Verification: Run integration tests on known-good projects

3. **Prompt Injection Attacks** (NEGLIGIBLE)
   - Malicious plan.json could include conflicting instructions
   - Mitigation: Parser forbidden_tokens check already rejects dangerous patterns
   - Verification: Already covered by existing parser tests

---

## Verification Checks

### Post-Fix Validation

1. **Prompt Consistency Audit**
   - [ ] Search all prompt templates for "complete scene file" → Replace with "body code"
   - [ ] Search for "Start with imports" in user prompts → Replace with "Start with animation code"
   - [ ] Verify no remaining contradictions between system/user prompts

2. **Parser Alignment Check**
   - [ ] Confirm parser forbidden_tokens list matches "what agents should NOT output"
   - [ ] Verify inject_body_into_scaffold handles empty/comment-only input gracefully
   - [ ] Test with example correct body code (from debug_response_build_scenes.txt lines 26-73 extracted as body only)

3. **Smoke Test Repair**
   - [ ] Apply fixes to prompt templates
   - [ ] Clear smoke-test project state
   - [ ] Re-run build_video.sh on smoke-test
   - [ ] Verify successful parse on first attempt (no self-heal needed)

4. **Integration Test Suite**
   - [ ] Create test case: "Agent outputs full file" → Parser rejects
   - [ ] Create test case: "Agent outputs body only" → Parser accepts and injects correctly
   - [ ] Add to tests/test_scaffold_and_parser.py

5. **Multi-Model Validation**
   - [ ] Test with grok-code-fast-1 (current)
   - [ ] Test with alternative models (gpt-4, claude) if available
   - [ ] Verify consistent body-only output across models

---

## Appendix: Evidence Files

### A. Defective Project Artifacts
- `examples/defective_output/smoke-test/project_state.json` - Phase stall at build_scenes
- `examples/defective_output/smoke-test/build.log` - 16 failed parse attempts
- `examples/defective_output/smoke-test/errors.log` - IndentationError repeated 4x
- `examples/defective_output/smoke-test/debug_response_build_scenes.txt` - Agent outputting full file
- `examples/defective_output/smoke-test/debug_response_scene_repair.txt` - Repair also outputting full file
- `examples/defective_output/smoke-test/scene_01_intro.py` - Empty SLOT body (only comments)

### B. Generator Components
- `harness/prompt_templates/build_scenes_system.md` - Ambiguous instructions (Finding 1)
- `harness/prompt_templates/repair_system.md` - Inherited ambiguity (Finding 2)
- `harness/prompts.py` lines 289-327 - User prompt reinforces wrong format
- `harness/parser.py` lines 353-411 - Parser correctly rejects full files
- `scripts/scaffold_scene.py` lines 45-52 - SLOT template with PROMPT comments (Finding 3)

### C. Contract Documentation
- `AGENTS.md` - Scene templates show full structure (may need clarification note)
- `docs/reference_docs/phase_scenes.md` - Build scenes phase documentation
- `docs/SCAFFOLD_FIX_SUMMARY.md` - Previous scaffold fixes (issue #50)

---

## Conclusion

The smoke-test failure is caused by **prompt instruction ambiguity**, not a code defect. The parser, scaffold, and self-heal mechanisms are working correctly. The agent is following contradictory instructions and outputting the wrong format.

**Primary Fix**: Update prompt templates to explicitly request "body code only" and remove all references to "complete scene file" or "start with imports". Add explicit negative examples.

**Secondary Fix**: Add safety pass statement to scaffold template to prevent empty with block syntax errors.

**Verification**: Re-run smoke-test after fixes and validate with integration tests.

**Impact**: Fixes will prevent 100% of build_scenes parse failures caused by format mismatch. No code changes required to harness or parser.

---

**Report Status**: COMPLETE  
**Next Steps**: Apply generator-level fixes to prompt templates and scaffold  
**Owner**: Development team (prompt engineering focus)
