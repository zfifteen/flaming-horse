# Issue #70 / Smoke Test 2 - Fix Implementation Plan

## Goal
Prevent audio/video desync failures from reaching `assemble` by enforcing scene timing budget compliance during scene generation/validation.

## Success Criteria
- `build_scenes` (and repair) fail fast when projected scene timing violates sync threshold.
- `final_render` and `assemble` do not fail for deterministic timing-overrun scenes.
- Smoke test topic used in `/Users/velocityworks/IdeaProjects/flaming-horse/tests/smoke_test.sh` completes without `phase=error`.
- Diagnostics in `build.log` clearly show why a timing gate failed.

## Non-Goals
- Do not patch generated project artifacts as a permanent fix.
- Do not relax final QC thresholds.
- Do not redesign the phase state machine.

## Workstream 1 - Add deterministic timing-budget gate
Scope files:
- `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/build_video.sh`
- `/Users/velocityworks/IdeaProjects/flaming-horse/scripts` (new helper script for timing analysis)

Plan:
1. Add a deterministic validator that computes projected scene runtime from scene body timing expressions.
2. Use cached narration audio duration from `media/voiceovers/qwen/cache.json` when available.
3. Compute projected ratio `audio_duration / projected_scene_duration`.
4. Fail validation when projected ratio is below the same threshold used in final QC (`0.90`).
5. Print actionable diagnostics:
- scene id
- detected timing terms
- projected duration
- projected ratio
- offending lines

Integration points:
- Call this validator inside `validate_voiceover_sync()` after existing checks.
- Re-run it after scene repair output before accepting repaired scene.

Acceptance checks:
- A scene like `scene_06_resistance_and_training.py` fails before final render.
- A compliant scene passes without changing final QC behavior.

## Workstream 2 - Tighten prompt-level timing contract
Scope files:
- `/Users/velocityworks/IdeaProjects/flaming-horse/harness/prompts/04_build_scenes/user.md`
- `/Users/velocityworks/IdeaProjects/flaming-horse/harness/templates/kitchen_sink.md`
- `/Users/velocityworks/IdeaProjects/flaming-horse/harness/prompts/06_scene_repair/system.md`

Plan:
1. Add explicit arithmetic guardrails in build prompt:
- Sum of `tracker.duration` multipliers for `run_time` plus waits must stay within budget.
- Fixed waits must be minimal and justified.
2. Add one compliant timing budget example and one violating example.
3. Add repair guidance for over-budget timing errors with direct before/after pattern.

Acceptance checks:
- Prompt text explicitly encodes budget math, not just qualitative pacing.
- Retry context can communicate timing budget violations clearly.

## Workstream 3 - Improve failure observability
Scope files:
- `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/build_video.sh`
- `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/qc_final_video.sh`

Plan:
1. Pipe `qc_final_video.sh` stdout/stderr through `tee -a "$LOG_FILE"` so detailed QC evidence is persisted.
2. Fix retry exhaustion message to report actual attempts when `needs_human_review` aborts early.
3. Remove duplicate per-scene QC iteration caused by overlapping globs in `qc_final_video.sh`.

Acceptance checks:
- `build.log` includes per-scene ratio outputs from QC.
- No duplicate scene rows in QC output.
- Attempt reporting is consistent between `build.log` and `error.log`.

## Workstream 4 - Add regression tests
Scope files:
- `/Users/velocityworks/IdeaProjects/flaming-horse/tests` (new/updated tests)

Plan:
1. Unit tests for timing validator:
- pass case: budget-compliant scene
- fail case: ratio < 0.90
- edge case: fixed waits push scene over threshold
2. Integration test to verify build validation fails before `assemble` on over-budget scene.
3. Regression assertion that final QC diagnostics appear in `build.log`.

Acceptance checks:
- New tests fail on current behavior and pass with fixes.
- Existing parser/scaffold tests remain green.

## Execution Order
1. Workstream 1 (deterministic gate)
2. Workstream 2 (prompt constraints)
3. Workstream 3 (observability cleanup)
4. Workstream 4 (tests)
5. Re-run smoke test and confirm completion

## Verification Runbook
1. Run targeted tests for timing validator and build integration.
2. Run smoke test:
`/Users/velocityworks/IdeaProjects/flaming-horse/tests/smoke_test.sh`
3. Confirm:
- `project_state.json` phase is `complete`
- no `Final video failed quality control - check audio/video sync`
- per-scene ratios in logged QC output are all `>= 0.90`

## Risk Notes
- Overly strict static timing analysis may false-positive on complex expressions.
- Use conservative parser behavior: fail closed on clearly over-budget scenes; warn on non-parsable expressions until coverage improves.
