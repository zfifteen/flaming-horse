# Deterministic Scene Validation Plan

Date: 2026-02-13
Owner: Build pipeline

## Problem Statement

Agent-generated scene code can pass basic syntax checks but still fail at render time with deterministic runtime errors (example: `self.wait(0)`). This causes expensive render retries and makes builds unreliable.

## Goal

Move critical scene validation from agent judgment to deterministic scripts so invalid scenes fail fast before render, with actionable errors and optional safe autofixes.

## Scope

In scope:

- Deterministic pre-render validation for every generated scene.
- Hard checks for timing/run-time constraints that Manim enforces.
- Integration into `scripts/build_video.sh` phase flow.
- Optional constrained autofix mode for obviously safe rewrites.

Out of scope:

- Creative animation quality scoring.
- Full semantic correctness of narration-to-visual alignment.
- Rewriting scene layout or content strategy.

## Design Overview

Implement a new script:

- `scripts/validate_scene_deterministic.py`

Primary approach:

1. Parse scene files with Python AST.
2. Detect high-confidence violations.
3. Emit machine-readable diagnostics and human-readable summaries.
4. Return non-zero exit code on hard failures.

Optional follow-up script:

- `scripts/autofix_scene_deterministic.py` for minimal safe rewrites.

## Deterministic Rules (Phase 1: Must-Have)

1. **No non-positive waits**
   - Flag `self.wait(0)`, `self.wait(-x)`, and constant-foldable expressions `<= 0`.
   - Detect simple zero forms like `a - a` for identical AST subtrees.

2. **No sub-minimum run times**
   - Flag `run_time` literals `< 0.3`.
   - Flag negative/zero `run_time` expressions where constant-foldable.

3. **Voiceover timing budget sanity per block**
   - For each `with self.voiceover(...) as tracker:` block, collect direct `tracker.duration * fraction` usages in `run_time` and slot helpers.
   - Fail when summed constant fractions are `> 1.0 + epsilon`.
   - Warn when no explicit timing allocation is detected.

4. **Narration source policy**
   - Require `SCRIPT["..."]` style usage in voiceover text.
   - Reject hardcoded narration strings in `self.voiceover(text=...)`.

5. **Import/service policy**
   - Require `from manim_voiceover_plus import VoiceoverScene`.
   - Require `get_speech_service(...)` usage in `construct`.

## Deterministic Rules (Phase 2: Strongly Recommended)

1. **Title placement policy**
   - Require title objects to use `.move_to(UP * 3.8)`.
   - Reject `.to_edge(UP)` for titles.

2. **`next_to` safety policy**
   - After `.next_to(...)`, require a nearby `safe_position(...)` call on the same object.

3. **Sibling layout safety policy**
   - For manually positioned sibling groups (2+ similar objects), require `safe_layout(...)` usage or explicit spacing helper.

4. **Math rendering policy**
   - Warn on `Tex` usage that appears to contain equations.
   - Encourage/require `MathTex` for equations.

## Pipeline Integration Plan

1. Add deterministic validator invocation after scene generation and before state advancement in `build_scenes`.
2. If validator fails:
   - Keep phase at `build_scenes`.
   - Add structured error to `project_state.json.errors`.
   - Mark `needs_human_review` only after configurable retry threshold.
3. Add deterministic validator invocation before each render in `final_render` as defense-in-depth.

## Error Output Contract

Validator should output JSON lines or single JSON payload:

- `file`
- `rule_id`
- `severity` (`error` or `warning`)
- `line`
- `message`
- `suggested_fix`

This enables future UI and automated repair tooling.

## Optional Autofix Strategy (Safe Subset Only)

Autofix only high-confidence edits:

- Remove `self.wait(0)` and `self.wait(0.0)`.
- Clamp tiny literal run times to `0.3`.
- Replace identical subtraction zero forms with removed waits when used only in wait duration.

Autofix must:

- Produce a patch preview in logs.
- Re-run validator immediately.
- Never rewrite creative animation structure.

## Test Plan

1. Unit tests for AST rules using fixture scenes:
   - valid scenes
   - `wait(0)` failures
   - `run_time=0.1` failures
   - timing budget overflow failures
2. Integration test with `build_video.sh` on a sample project.
3. Regression test reproducing `scene_02_countable.py` failure pattern.

## Rollout Plan

1. Phase A: validator in warning mode (logs only) for 1-2 runs.
2. Phase B: enforce hard-fail on must-have rules.
3. Phase C: enable optional safe autofix behind flag (`--autofix-deterministic`).

## Acceptance Criteria

- Build never reaches Manim render with `wait <= 0` in scene code.
- Deterministic checks catch known bad timing patterns before render.
- Error messages point to exact file/line/rule with a fix hint.
- Existing successful projects continue to pass without manual intervention.

## Implementation Checklist

- [ ] Create `scripts/validate_scene_deterministic.py`
- [ ] Add rule engine + diagnostics format
- [ ] Add tests for all Phase 1 rules
- [ ] Integrate into `build_scenes`
- [ ] Integrate into `final_render` preflight
- [ ] Add optional `--autofix-deterministic` pathway
- [ ] Document usage in `README.md` and `docs/scaffold_instructions.md`
