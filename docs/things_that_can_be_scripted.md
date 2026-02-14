# Determinism Opportunities in Flaming Horse (Updated Analysis)

**Analysis Date:** 2026-02-13  
**Primary Entrypoint:** `scripts/create_video.sh`  
**Scope:** Re-evaluate what is already deterministic vs. what can still be scripted so implementing agents do less boilerplate work.

---

## Executive Summary

The pipeline is already strongly scripted from project creation through final assembly:

- `create_video.sh` standardizes CLI input and delegates reliably.
- `new_project.sh` seeds deterministic project state and Qwen voice clone config/assets.
- `build_video.sh` enforces a phased state machine, lock file protection, state validation/sanitization, and render/assembly/QC gates.
- `scaffold_scene.py` and `generate_scenes_txt.py` remove major repetitive agent work.

The remaining high-value determinism gains are now mostly **validator/scaffolding additions**, not orchestration rewrites.

---

## Current Deterministic Baseline (What is already scripted well)

## 1) Entrypoint and argument normalization

### `scripts/create_video.sh`
- Deterministically parses:
  - `<project_name>`
  - `--topic`
  - `--projects-dir`
  - `--build-args` (via Python `shlex.split`)
- Enforces topic presence (`--topic` or `VIDEO_TOPIC`).
- Always executes:
  1. `scripts/new_project.sh`
  2. `scripts/build_video.sh`

**Result:** user gets one consistent command path into the system.

## 2) Project bootstrap and voice prerequisites

### `scripts/new_project.sh`
- Creates deterministic `project_state.json` skeleton.
- Writes `voice_clone_config.json` with locked Qwen defaults (CPU/float32).
- Ensures voice reference assets exist (`assets/voice_ref/ref.wav` + `ref.txt`), seeding from template if needed.
- Fails fast if required voice assets are unavailable.

**Result:** avoids ad-hoc setup and missing-file drift across projects.

## 3) Build orchestration and state safety

### `scripts/build_video.sh`
- Lock file prevents concurrent builders.
- Validates required state schema/phase values each loop.
- Attempts JSON repair for malformed/trailing output in `project_state.json`.
- Backs up state and restores on invalid transitions.
- Enforces max iterations and human-review pausing.

**Result:** robust, repeatable state machine behavior.

## 4) Agent guardrails already in place

- `validate_scene_imports()` catches common module naming/syntax mistakes.
- `validate_voiceover_sync()` blocks hardcoded narration text and requires scripted voice service usage.
- Narration post-step sanitizes known markup artifacts in `narration_script.py`.

**Result:** fewer invalid scene/narration outputs pass downstream.

## 5) Rendering, assembly, and quality gates are script-owned

- `handle_final_render()` renders scenes from `project_state.json` metadata (not freeform agent output), verifies audio stream presence, updates per-scene verification.
- `handle_assemble()` generates `scenes.txt` via script, verifies inputs, and assembles with deterministic ffmpeg filter graph.
- `qc_final_video.sh` enforces final media checks (audio coverage, silence detection, per-scene checks).

**Result:** final output path is already mostly deterministic and script-driven.

---

## Re-analysis of Prior Document (what changed)

The previous analysis correctly identified major opportunities, but status has shifted:

- ✅ **Implemented and integrated:**
  - Scene scaffolding (`scaffold_scene.py`)
  - `scenes.txt` generation (`generate_scenes_txt.py`)
- ✅ **Implemented (script exists) + used in build flow:**
  - Qwen precache (`precache_voiceovers_qwen.py`) via `build_video.sh` before render when cache is missing; also available as explicit phase.
- ⏳ **Still pending:**
  - Timing budget validator
  - Narration skeleton generator
  - Positioning linter
  - Additional schema/contract validators around plan/narration/scene metadata

---

## Additional Opportunities for Determinism (Updated Priorities)

## Priority 1 (High): Deterministic scene runtime safety + timing validator

### Problem
Agent scenes can be syntactically valid but still fail at render time due to deterministic runtime errors (for example `self.wait(0)`). Timing over-allocation also causes dead air or desync.

### Script opportunity
Add `scripts/validate_scene_deterministic.py` that parses scene AST and enforces runtime safety and timing constraints before render.

### Suggested checks
- Reject non-positive waits: `self.wait(0)`, negative constants, simple foldable zero expressions.
- Reject invalid run times: `run_time <= 0` and literal `run_time < 0.3`.
- Enforce timing budget: sum of explicit `tracker.duration * X` allocations per voiceover block must be `<= 1.0` (with small epsilon).
- Warn when no explicit budgeting is detected in a voiceover block.
- Emit deterministic diagnostics with file + line + rule id + fix hint.

### Integration point
- Run in `handle_build_scenes()` immediately after existing import/sync validators.
- Re-run in `final_render` preflight as defense in depth.

### Enforcement mode
- Hard-fail immediately for runtime safety rules (`wait <= 0`, invalid `run_time`).
- Warning-first for advisory checks if needed.

---

## Priority 2 (High): Deterministic narration skeleton generation from `plan.json`

### Problem
Agent currently writes `narration_script.py` structure manually.

### Script opportunity
Add `scripts/scaffold_narration.py`:
- Reads `plan.json` scene entries.
- Creates/updates `narration_script.py` with exact SCRIPT keys, placeholders, and optional target word counts.

### Integration point
- Run immediately after plan/review success or at start of narration phase.

**Benefit:** agent fills content only; scripts own structure and key matching.

---

## Priority 3 (Medium): Plan/state contract validator before narration/build

### Problem
`build_video.sh` validates top-level state shape, but not deep contracts between files.

### Script opportunity
Add `scripts/validate_project_contract.py` checking:
- `plan.json` scene IDs are unique.
- `project_state.json.scenes[*].id` matches plan scenes.
- Narration SCRIPT keys exist for all required scene narration keys.
- Scene metadata (`id/file/class_name`) completeness before final render.

### Integration point
- Gate at start of `narration`, `build_scenes`, and `final_render`.

**Benefit:** catches structural mismatches earlier than render time.

---

## Priority 4 (Medium): Positioning/style linter for common Manim anti-patterns

### Problem
Visual clipping/overlap rules remain mostly convention-based.

### Script opportunity
Add `scripts/lint_positioning.py` with static checks, e.g.:
- `.to_edge(UP)` usage where fixed safe coordinates are preferred.
- `.next_to(...)` patterns missing `safe_position(...)` usage nearby.
- suspicious repeated `.move_to(ORIGIN)` overlaps.

### Integration point
- Optional warning gate in `handle_build_scenes()`; can be elevated to fail-on-error later.

---

## Priority 5 (Medium): Preflight environment checker from entrypoint

### Problem
Some failures (missing `manim`, `ffmpeg`, `ffprobe`, `opencode`, invalid qwen python path) surface late.

### Script opportunity
Add `scripts/preflight_check.py` (or `.sh`) and call it from `create_video.sh` before project creation/build.

### Checks
- Required binaries in PATH.
- Qwen python executable from voice config exists (or guidance to regenerate config).
- Writable project directory.

**Benefit:** fast, deterministic failure with actionable diagnostics.

---

## Priority 6 (Low): Narrower scripted state mutation helpers

### Problem
State updates are currently done inline in multiple embedded Python snippets.

### Script opportunity
Add helper scripts for common mutations (append error/history, phase advance, scene rendered update).

### Note
Current inline approach works today; this is maintainability/consistency optimization, not urgent reliability work.

---

## What Should Remain Agent-Owned (not worth scripting)

- Creative plan content and narrative flow decisions.
- Narration prose writing quality.
- Visual pedagogy/animation design choices.

The best deterministic split is:
- **Scripts own structure, validation, contracts, and repetitive glue.**
- **Agents own creative content within those rails.**

---

## Recommended Implementation Sequence

1. **Scene runtime safety + timing validator** (`validate_scene_deterministic.py`) + gate in `handle_build_scenes()`.
2. **Narration scaffold generator** (`scaffold_narration.py`) from `plan.json`.
3. **Project contract validator** (`validate_project_contract.py`) across state/plan/narration.
4. **Positioning linter** (`lint_positioning.py`) as warning-first.
5. **Entrypoint preflight check** from `create_video.sh`.
6. Optional state-helper refactor.

---

## One Change Per PR Rollout Protocol

To reduce risk, each enhancement should ship in a separate PR with tight scope:

1. **PR-1: Validator skeleton + hard rule for `wait <= 0` and invalid `run_time`**
   - Add script + tests + `build_video.sh` integration.
   - No narration, contract, or positioning changes.

2. **PR-2: Timing budget checks (`tracker.duration * fraction`)**
   - Extend validator only.

3. **PR-3: Narration scaffolding from `plan.json`**
   - Add `scaffold_narration.py` + phase integration.

4. **PR-4: Cross-file project contract validator**
   - Validate state/plan/narration consistency.

5. **PR-5: Positioning linter (warning mode first)**
   - Keep non-blocking until signal quality is proven.

6. **PR-6: Entrypoint preflight checks**
   - Environment and dependency checks before project/build.

### PR Acceptance Checklist

- Includes targeted tests for the new rule(s)
- Includes one short docs update
- Keeps unrelated behavior unchanged
- Demonstrates pass/fail examples in CI or local test output

---

## Bottom Line

Compared to the previous analysis, the system is now more deterministic than the old document implied. The biggest remaining wins are **adding scripted validators and scaffolds around timing, narration structure, and cross-file contracts** so agents spend less time on mechanical correctness and more on actual educational content.
