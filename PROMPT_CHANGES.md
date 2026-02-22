# Prompt Changes

This document describes improvements made to harness prompt content and template structure.

## Summary

Changes are limited to `harness/prompts/**` and `harness/templates/**` (plus this document).
No orchestration logic, validation code, or script behavior was modified.

---

## Changes by Phase

### 00_plan (plan)

- **Added `## Purpose` section to `system.md`** — gives the model a clear, concise role statement at the start of the system turn. Replaces the sparse 5-line role description with a structured format matching other phases.
- **Fixed scene count inconsistency** — `manifest.yaml` previously declared `scene_count(8-12)` while `user.md` required 12–24 scenes. Updated manifest to reflect the actual validated range (12–24 / 480–960 s).
- **Added `### Self-Check Before Output`** to `user.md` — forces the model to verify scene count, duration, visual_ideas quality, and JSON format before emitting a response. Reduces malformed plan output.

### 02_narration (narration)

- **Improved `system.md`** — added `## Purpose` and `## Voice Policy` sections. Explicitly states that narration feeds local cached Qwen TTS and must be speakable (no code syntax, no formatting symbols). This reinforces the hard voice policy at the system-turn level.
- **Added `### Self-Check Before Output`** to `user.md` — forces the model to verify all narration_keys are present, values are non-empty strings, and output matches `{"script": {...}}` shape.

### 04_build_scenes (build_scenes)

- **Added `## Purpose` header to `system.md`** — replaces the plain title line with a structured role definition matching other phases.
- **Removed color rule duplication from `user.md`** — the color rule (`use hex strings`) and geometry rule (Polygon vertex unpacking) appeared in both `system.md` and `user.md`. Removed them from `user.md` to reduce token overhead. The authoritative versions remain in `system.md`.

### 05_scene_qc (scene_qc)

- **Added `## Purpose` header to `system.md`** — gives the model a clear role before the detailed review protocol.
- **Added `### Self-Check Before Output`** to `user.md` — forces verification that every scene is covered, rewrite_required is used only for render-blocking errors, and output is valid JSON with `report_markdown`.
- **Fixed `manifest.yaml` output format** — changed `format: markdown_only` to `format: json_object` with the correct payload declaration. The phase has always returned JSON with a `report_markdown` field; the manifest was wrong.

### 06_scene_repair (scene_repair)

- **Added `## Purpose` header to `system.md`** — gives the model a clear, focused role statement at the start of the system turn.

---

## Shared Template Changes

No changes were made to `harness/templates/` or `harness/prompts/_shared/core_rules.md`. These files were reviewed and found to be accurate and non-redundant with the phase-level improvements above.

---

## What Was Preserved

All of the following hard rules were preserved unchanged:

- Voice policy: local cached Qwen only, no network TTS, no fallback patterns.
- Timing contract: `tracker.duration`, run_time budgets, max timing constraints.
- Layout contract: `safe_position`, `safe_layout`, `set_max_width`, no `arrange` on Text/MathTex.
- Color rule: hex strings only, no named Manim color constants.
- Narration key contract: `SCRIPT["narration_key"]` pattern.
- JSON output formats for all phases.
- Deterministic values only (no `random` module).
- No imports, class defs, or function defs in scene_body.

---

## How to Validate

### Dry-run prompt composition

```bash
cd /home/runner/work/flaming-horse/flaming-horse
mkdir -p /tmp/testvideo
echo '{"phase": "plan", "topic": "Test", "scenes": []}' > /tmp/testvideo/project_state.json
python3 -m harness --phase plan --project-dir /tmp/testvideo --topic Test --dry-run
python3 -m harness --phase narration --project-dir /tmp/testvideo --dry-run
```

Expected: Both commands print composed prompt and exit 0 (no API call).

### Unit tests

```bash
python3 -m pytest tests/test_harness_mock_e2e.py tests/test_scaffold_and_parser.py tests/test_phase_vocabulary.py -q
```

Expected: All tests pass.

---

## Known Risks / Follow-up

1. The manifest scene count (12–24) is now aligned with user.md but the harness does not enforce this via schema validation at runtime; plan.json scene count validation is script-owned (build_video.sh). No regression.
2. The `05_scene_qc` manifest format fix is a doc-only fix; the harness parser for scene_qc already handles the JSON `report_markdown` field correctly.
3. If future phases are added, they should follow the same structured format: Purpose → Role Behavior → Hard Rules → Self-Check → Output.
