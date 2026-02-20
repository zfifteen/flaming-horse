# Issue #70 / PR #73 - Smoke Test 2 Root Cause Analysis

## Scope
Analyze why the smoke run at `/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2` failed after Copilot fixes in PR #73.

## Inputs Reviewed
- Issue: `https://github.com/zfifteen/flaming-horse/issues/70`
- PR: `https://github.com/zfifteen/flaming-horse/pull/73`
- Commits on PR branch:
  - `f34ff5c` - Initial plan
  - `aa79418` - prompt/parser updates for helper usage and boilerplate detection
  - `7e4b795` - tighter boilerplate regex + false-positive test
- Artifacts:
  - `/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/log/build.log`
  - `/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/log/conversation.log`
  - `/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/log/error.log`
  - `/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/project_state.json`
  - `/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/scene_06_resistance_and_training.py`
  - `/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/scene_07_beyond_the_matrix.py`
- Runtime scripts and prompts:
  - `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/build_video.sh`
  - `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/qc_final_video.sh`
  - `/Users/velocityworks/IdeaProjects/flaming-horse/harness/prompts/04_build_scenes/user.md`
  - `/Users/velocityworks/IdeaProjects/flaming-horse/harness/prompts/06_scene_repair/system.md`

## Executive Summary
- PR #73 fixed parts of Issue #70 (helper docs, repair prompt clarity, boilerplate rejection), but the observed smoke failure is a different failure mode.
- This run reaches `assemble` and fails final QC due per-scene audio/video ratio failure, not due `harmonious_color`.
- First divergence is scene generation timing oversubscription in `scene_06_resistance_and_training`.
- Timing desync is only warned during scene validation and is only enforced at the final QC gate, causing late failure.

## Findings

### Finding 1 (Primary): Scene timing budget oversubscription causes final QC failure
Scope: `build_scenes -> scene_06_resistance_and_training -> assemble QC`

Failure origin:
- The generated scene body for scene 06 (conversation artifact) contains cumulative `tracker.duration` allocations greater than 1.0 (`/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/log/conversation.log:5206`).
- Estimated duration for this scene was explicitly provided as `22s` (`/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/log/conversation.log:5133`).

Causal chain:
- Scene 06 code schedules approximately `0.97 * tracker.duration` in `run_time` plus `0.26 * tracker.duration` in waits (`/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/scene_06_resistance_and_training.py:45` to `/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/scene_06_resistance_and_training.py:101`).
- This yields about `1.23 * narration_duration`, producing long tail time.
- Final QC enforces scene-level ratio `audio/video >= 0.90` (`/Users/velocityworks/IdeaProjects/flaming-horse/scripts/qc_final_video.sh:114` to `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/qc_final_video.sh:116`).
- Manual rerun of QC confirms scene 06 ratio `0.814` and fails with `SYNC ISSUE`.
- Build exits in error phase (`/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/project_state.json:183`).

Primary fix:
- Add deterministic pre-assemble timing-budget validation in scene validation flow (not only final QC).

Containment status:
- Contained only at terminal QC (`assemble`), which is late and expensive.

### Finding 2: Validation gap allows timing-desynced scenes to pass earlier phases
Scope: scene validation and scene QC policy

Failure origin:
- Voiceover sync check only warns on missing `tracker.duration`; it does not enforce budget compliance (`/Users/velocityworks/IdeaProjects/flaming-horse/scripts/build_video.sh:641` to `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/build_video.sh:646`).
- Build log shows repeated warnings but pass-through behavior (`/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/log/build.log:366` to `/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/log/build.log:369`).

Causal chain:
- Timing drift is not treated as a failure in `build_scenes`, repair, or `scene_qc`.
- `scene_qc` is intentionally render-blocking only (`/Users/velocityworks/IdeaProjects/flaming-horse/harness/prompts/05_scene_qc/system.md`).
- Final QC in `assemble` becomes the first strict desync gate, where the run fails.

Primary fix:
- Promote timing-sync from warning to deterministic gate before final render/assemble.

Containment status:
- No early containment.

### Finding 3: PR #73 scope does not cover the failure mode in this smoke run
Scope: Issue assumptions vs observed run behavior

Failure origin:
- Issue #70 and PR #73 primarily target `harmonious_color` misuse and boilerplate contamination.
- In this run, runtime failure during `build_scenes` is `NameError: BROWN`, then repaired successfully (`/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/log/build.log:413` to `/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/log/build.log:507`).
- Final failure is audio/video sync at `assemble`, unrelated to `harmonious_color`.

Causal chain:
- PR adds helper docs and parser defenses, which are valid improvements.
- However, there is no deterministic guard for cumulative timing oversubscription.
- Smoke test still fails in a different path.

Primary fix:
- Retarget follow-up fix scope to timing budget enforcement and early sync gating.

Containment status:
- Current PR mitigates some prior classes of errors but not this one.

### Finding 4: Debug observability is insufficient at the failure point
Scope: QC diagnostics and retry reporting

Failure origin:
- `qc_final_video.sh` output is not piped into `build.log` in `handle_assemble`, so detailed fail reason is missing from primary artifact (`/Users/velocityworks/IdeaProjects/flaming-horse/scripts/build_video.sh:2393` to `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/build_video.sh:2396`).
- `error.log` shows `attempt=1/4` while build output says failed after 4 attempts (`/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/log/error.log:75`).
- QC scene loop currently scans two overlapping globs, producing duplicate scene checks (`/Users/velocityworks/IdeaProjects/flaming-horse/scripts/qc_final_video.sh:95`).

Causal chain:
- Operators cannot see ratio/silence details in standard build log.
- Retry messaging is misleading for triage.

Primary fix:
- Tee QC output to build log, align retry messaging with actual attempt count, and deduplicate scene-glob iteration.

Containment status:
- Manual rerun of QC script is required to diagnose root cause.

## Issue #70 Hypotheses vs Current Code/Run
- Prompt deficiency for helper signatures: addressed in PR #73.
- Repair prompt missing helper guidance: addressed in PR #73.
- Claimed scaffold reset regression: not supported by current code; reset reinserts prior slot body (`/Users/velocityworks/IdeaProjects/flaming-horse/scripts/build_video.sh:1043` to `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/build_video.sh:1068`).
- Boilerplate contamination risk: addressed by new parser checks and tests in PR #73.
- Missing validation: still true for timing budget/sync enforcement.

## First Divergence Point
- First divergence relevant to this smoke failure is the scene 06 generated timing plan in `build_scenes` (`/Users/velocityworks/IdeaProjects/flaming-horse/generated/smoke-test-2/log/conversation.log:5206`), not the earlier scene 07 `BROWN` runtime error (which self-heal fixed).
