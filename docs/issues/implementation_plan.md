# Implementation Plan for Flaming Horse Generator Issues

## Overview
This document outlines the implementation plan to address the high-severity issues identified in the Flaming Horse generator and orchestration system. The issues stem from ambiguities in AGENTS.md prompts, template rigidness, scaffold script patterns, and missing validation logic, leading to poor scene composition (planning text as content, off-screen elements, dead air, and monotony).

**Goal:** Deploy fixes to generator prompts/templates/scaffold before the next build, ensuring valid outputs align with project contracts.

**Scope:** Core fixes to AGENTS.md, scene template, scaffold script, and QC prompts. No project-level patching; focus on root-cause generator changes.

**Timeline:** Target completion in ~5-6 focused hours for prompt/template updates; verification via test builds.

## Issues Summary
1. **Planning Text as Content:** Agents copy `narrative_beats` from `plan.json` verbatim into `Text()` calls, rendering stage directions as viewer text.
2. **Off-Screen Positioning:** `safe_position()` lacks horizontal clamping; bullets at `LEFT * 4.8` overflow frame bounds.
3. **Dead Air in Timing:** Uniform `BeatPlan` weights create 3s slots with 50% idle waits; double-slot consumption exhausts beats; `self.wait(remaining)` causes micro-stuttering.
4. **Structural Monotony:** Rigid template enforces identical scene patterns; ignores `topic_visual_patterns.md`.
5. **QC Misses:** Scene QC prompt lacks quantitative checks for content validity and positioning.

## Implementation Steps
**Note:** Create the shared helpers module (Task 2.3) as the very first commit to enable references in templates/scaffold.

### Phase 1: Update AGENTS.md Template and Rules (Priority: High)
- **Task 1.1:** Add "Bullet Content Rule" section under CRITICAL RULES.
  - Insert after "Narration Text" rule.
  - Content: Prohibit using `narrative_beats` or `visual_ideas` as on-screen text; mandate derivation from `narration_script.py`; cap bullets at 30 characters or 6 words as readability guideline (enforced by `set_max_width(6.0)`); forbid stage directions. Add examples (e.g., "For math: derive 'a² + b² = c²' from narration, not 'Explain the theorem.'").
- **Task 1.2:** Expand "Positioning" rules.
  - Add "Horizontal Bounds" subsection with frame calculations, positioning guidelines (e.g., `LEFT * 3.5`), and requirement for horizontal-safe helpers. Include `Text.set_max_width(6.0)` as primary constraint.
- **Task 1.3:** Revise "Timing Budget" rules.
  - Update beat formula to `num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))`.
  - Add prohibition on double-consuming slots and on passing `run_time=` to slot helpers. Remove 1.5s text cap entirely (`max_text_seconds=999`) to eliminate `self.wait()` micro-pauses.
- **Task 1.4:** Update "Complete Scene Template".
  - Replace single rigid template with 2 structurally different examples (e.g., progressive bullets + timeline/staged reveal). Mandate unique flows, inline key patterns from `topic_visual_patterns.md` into AGENTS.md, require ≥1 unique visual per scene.
  - Adjust positions to `LEFT * 3.5`; use `set_max_width(6.0)`.
- **Task 1.5:** Audit and update `scripts/scaffold_scene.py`.
  - Confirm it does not emit hardcoded bullet patterns at `LEFT * 4.8` or `{{KEY_POINT_1}}` placeholders; update to emit comment-only directives (e.g., `# PROMPT: Design unique visual flow...`) to force creative composition.
- **Dependencies:** None.
- **Estimated Time:** 2 hours (30-45 min per template example).

### Phase 2: Enhance Positioning Helpers and Centralization (Priority: High)
- **Task 2.1:** Extend `safe_position()` function in template.
  - Add parameters: `max_x=7.5, min_x=-7.5`.
  - Implement horizontal clamping logic (bounding-box edges).
- **Task 2.2:** Update template examples to call extended `safe_position()` and `Text.set_max_width(6.0)` on all positioned elements (e.g., bullets, diagrams).
- **Task 2.3:** Centralize helper functions into a shared module (e.g., `flaming_horse/scene_helpers.py` under existing package, on PYTHONPATH) to prevent inter-scene divergence. Create module first; reference from templates/scaffold as written.
- **Dependencies:** Parallel to Phase 1 (consume from Phase 1 tasks).
- **Estimated Time:** 1 hour (including dependency resolution).

### Phase 3: Strengthen Scene QC Prompt (Priority: Medium)
- **Task 3.1:** Locate and update `SCENE_QC_AGENT_PROMPT.md` (assumed in docs/reference_docs/).
  - Add "Content Validation" checks: reject planning text matches, horizontal overflow (with width estimation), structural duplication.
- **Task 3.2:** If not existing, create the file with the suggested content.
- **Dependencies:** None (parallel to Phase 1).
- **Estimated Time:** 45 minutes.

### Phase 4: Add Regression Tests and Containment (Priority: Medium)
- **Task 4.1:** Create `tests/test_scene_content.py` with functions: `test_no_planning_text_in_scenes`, `test_horizontal_bounds`, `test_stage_direction_blacklist`, `test_no_runtime_passed_to_play_next`, `test_no_long_waits`.
  - Implement logic as per analysis (JSON parsing, regex scanning). Add `test_stage_direction_blacklist` for leading patterns like `^Deliver\b`, `^Pause for\b`, `^Transition to\b` (scoped to bullet text). Add `test_no_runtime_passed_to_play_next` (fails on `run_time=` in slot helpers); `test_no_long_waits` (fails on `self.wait(x)` > 1.0s).
- **Task 4.2:** Merge containment into Phase 4: Create standalone script `scripts/validate_scene_content.py` that runs pytest as a build gate (insert after `build_scenes`/`scene_qc`, before `final_render`).
- **Task 4.3:** Update `tests/README.md` to reference new tests and gate script.
- **Dependencies:** Phases 1-2 (to ensure tests align with fixes).
- **Estimated Time:** 1.5 hours.

## Verification and Testing
- **Post-Implementation:** Run two test builds: one dense-text topic (e.g., Matrix simulation explainer for overflow stress), one math topic (e.g., "Pythagorean Theorem"). Verify generated scenes: 0 planning text matches, 0 bound violations, no `self.wait()` > 1.0s (no micro-stuttering), ≥1 unique visual per scene.
- **Regression Runs:** Execute new tests and gate script on existing/future projects.
- **Metrics:** Check build.log for no overflow warnings; scene_qc_report.md should flag issues pre-render; pytest passes as gate (all tests 0 failures).
- **Fallback:** If issues persist, review agent execution logs for prompt adherence and context injection.

## Risks and Mitigations
- **Risk:** Agents misinterpret new directives.
  - Mitigation: Add explicit examples in AGENTS.md (e.g., "Example: For math topic, derive 'a² + b² = c²' from narration, not 'Explain the theorem.'"); inline key patterns from `topic_visual_patterns.md` into AGENTS.md.
- **Risk:** Horizontal clamping affects layout.
  - Mitigation: Test with varying text lengths in dry runs; use `Text.set_max_width(6.0)` as primary defense.
- **Risk:** QC additions increase false positives.
  - Mitigation: Tune thresholds (e.g., width estimation formula) based on initial tests.
- **Risk:** Scaffold script overrides prose fixes.
  - Mitigation: Audit and update scaffold to align with new templates.

## Responsible Parties
- **Core Dev:** Implement all phases (as solo operator).
- **Verification:** Run tests and inspect outputs.

## Next Steps
1. Create shared helpers module first (as Task 2.3).
2. Begin Phase 1 immediately.
3. Commit changes incrementally with descriptive messages (e.g., "Fix bullet content rule in AGENTS.md").
4. Schedule test build after Phase 4 completion.
5. Future: Implement scaffold-level `topic_visual_patterns.md` injection as follow-up.</content>
<parameter name="filePath">docs/issues/implementation_plan.md