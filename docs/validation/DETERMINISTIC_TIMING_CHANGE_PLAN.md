# Deterministic Timing Change Plan

Date: 2026-02-13
Status: Planned
Scope: Single enhancement focused on timing reliability

## Goal

Eliminate render-time timing failures (especially `wait <= 0`) by moving timing safety checks from agent-authored code to deterministic scripts.

## Why This Change

Recent failure mode:

- Scene compiled but failed at render with `Scene.wait() has a duration of 0 <= 0`.

This class of issue is mechanical and should be caught before rendering.

## Design

Implement a deterministic validator script:

- `scripts/validate_scene_deterministic.py`

Run it in pipeline gates:

1. After scene generation in `build_scenes`
2. Before each render in `final_render` (defense in depth)

## Rules for This Change (PR-1 only)

Hard-fail checks:

1. `wait` duration must be positive
   - Reject obvious forms like `self.wait(0)`, `self.wait(0.0)`, negative constants
   - Reject simple foldable zero forms where possible

2. `run_time` must be valid
   - Reject `run_time <= 0`
   - Reject literal `run_time < 0.3` (repo visual minimum)

This first PR does **not** include broader timing-budget or positioning linting.

## Output Contract

Validator emits deterministic diagnostics including:

- `file`
- `line`
- `rule_id`
- `severity`
- `message`
- `suggested_fix`

Non-zero exit code on any error.

## Implementation Steps

1. Build AST-based checker in `scripts/validate_scene_deterministic.py`
2. Add fixture tests for pass/fail cases
3. Integrate validator call into `build_video.sh` flow
4. Ensure build fails fast with actionable message
5. Add short usage note to docs

## Test Plan

Must pass:

- Valid scene with positive waits and run times

Must fail:

- `self.wait(0)`
- `self.wait(-1)`
- `self.play(..., run_time=0)`
- `self.play(..., run_time=0.1)`

Regression test:

- Reproduce the exact `scene_02_countable.py`-style `wait(0)` failure pattern and confirm pre-render detection.

## Acceptance Criteria

- No scene reaches Manim render with non-positive `wait`.
- Build stops in deterministic validation phase with clear file/line diagnostics.
- Change is isolated to timing safety only (one-change-per-PR).

## Follow-ups (separate PRs)

- Timing budget validator (`tracker.duration * fraction` sums)
- Narration scaffolding
- Cross-file contract validation
- Positioning linting
- Entrypoint preflight checks
