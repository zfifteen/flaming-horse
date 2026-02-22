# Prompt Improvements – 2026-02-22

## Summary

This improvement pass audited all files in `harness/prompts/**` against the evaluation criteria: token efficiency, constraint completeness, ownership alignment, structure, consistency, and redundancy elimination. The main changes were: (1) adding a 6-part structure (Purpose → Inputs → Outputs → Hard Rules → Self-Check → Failure Behavior) to every agent-facing prompt; (2) removing ~6,000 characters of duplicate layout examples from `04_build_scenes/user.md` by consolidating them into `system.md` (the canonical location); (3) deduplicating the voice policy in `core_rules.md` which previously appeared twice; (4) eliminating emoji decorations from `core_rules.md` to reduce tokens without weakening any rule; (5) fixing a scene-count inconsistency between `00_plan/manifest.yaml` (8–12) and `00_plan/user.md` (12–24) by aligning both to 12–24 per the `phase_plan.md` reference doc; and (6) adding explicit Voice Policy reminders to phases that generate scene code (`build_scenes`, `scene_repair`). All hard rules are preserved; no hard rule was weakened or made optional.

---

## Per-File Changes

### `harness/prompts/00_plan/manifest.yaml`
**Changes:**
- Updated `scene_count: 8-12` → `scene_count: 12-24`
- Updated `total_duration_seconds: 240-480` → `total_duration_seconds: 480-960`
- Updated input constraint comment to match

**Rationale:** The manifest validation values conflicted with the user prompt (12–24 scenes, 480–960s) and `docs/reference_docs/phase_plan.md`. Mismatched constraints create ambiguity for the agent and can cause schema validation failures. Aligned to the authoritative reference doc. (Constraint completeness, consistency)

**Token impact:** Negligible (2 lines changed in YAML metadata).

---

### `harness/prompts/_shared/core_rules.md`
**Changes:**
- Removed all emoji decorations (`🚨`, `✅`, `❌`) — replaced with plain text equivalents
- Merged two duplicate Voice Policy sections into one: the top "CRITICAL: VOICE POLICY - READ THIS FIRST" section and the "1. Voice Configuration" sub-section under CRITICAL RULES both stated the same rules; these are now a single section
- Removed emoji-decorated bullet separators in Visual Quality Rules

**Rationale:** Emoji decorations add tokens without adding semantic value for LLM processing. The duplicate Voice Policy section was 9 lines of redundant text. No rule was removed or weakened. (Token efficiency, redundancy elimination)

**Token impact:** ~150 characters saved (~25–30 tokens at typical tokenization).

---

### `harness/prompts/00_plan/system.md`
**Changes:**
- Added explicit `## Purpose` section
- Added `## Role` label for the agent role statement
- Added `## Behavior` label for the behavior bullet list
- Added "Always include a final recap scene summarizing the video's key points" to Behavior

**Rationale:** Adds the Purpose section required by the 6-part structure. The recap scene rule was in `user.md` but not in `system.md`; adding it to system ensures it is present regardless of user prompt variation. (Structure, constraint completeness)

**Token impact:** +131 characters (adds clarity, minimal cost).

---

### `harness/prompts/00_plan/user.md`
**Changes:**
- Added 6-part structure headings (Purpose, Inputs, Required Output, Hard Rules, Self-Check, Failure Behavior)
- Replaced the 40-line WRONG/RIGHT `visual_ideas` example block with a concise 2-line inline example
- Aligned constraint values to 12–24 scenes, 20–45s per scene, 480–960s total
- Added Self-Check checklist
- Added Failure Behavior section

**Rationale:** The long WRONG/RIGHT example was ~600 characters of illustrative content that the new concise inline examples replace with equivalent specificity at a fraction of the tokens. The 6-part structure makes the agent's task unambiguous. (Token efficiency: −654 characters; structure; constraint completeness)

**Token impact:** −654 characters (~130–160 tokens saved).

---

### `harness/prompts/02_narration/user.md`
**Changes:**
- Added 6-part structure headings (Purpose, Inputs, Required Output, Hard Rules, Soft Guidelines, Self-Check, Failure Behavior)
- Moved content-quality guidelines (concrete phrasing, no stage directions, continuity) to a dedicated `## Soft Guidelines` section
- Added Self-Check checklist
- Added Failure Behavior section

**Rationale:** The original prompt lacked failure behavior (what to do when a scene description is ambiguous) and a self-check step. Adding these reduces the probability of incomplete outputs. The Soft Guidelines section clearly separates flexible best-practice guidance from hard constraints. (Structure, constraint completeness)

**Token impact:** +572 characters (quality improvement accepted).

---

### `harness/prompts/04_build_scenes/system.md`
**Changes:**
- Added `## Purpose` and `## Role` sections
- Moved 3 "Layout and Overlap Examples" from `user.md` into `system.md` (Examples 1–3)
- Moved 2 "Known Failure Patterns" from `user.md` into `system.md` (Patterns A–B)
- Restructured headers: `## Hard Rules`, `## Hard Layout Contract`, `## Layout Examples`, `## Required Structural Pattern`

**Rationale:** The layout examples and failure patterns were duplicated across both `system.md` and `user.md`. Consolidating them into `system.md` (which is loaded once per session) eliminates ~2,000 characters of duplication from the per-invocation `user.md`. `system.md` is the canonical location for authoritative guidance; `user.md` provides run-specific context. (Redundancy elimination, token efficiency, ownership alignment)

**Token impact:** +1,502 characters in system (one-time cost); enables −6,000 in user.md.

---

### `harness/prompts/04_build_scenes/user.md`
**Changes:**
- Added 6-part structure headings
- Removed the "Layout and Overlap Examples" section (~500 characters) — moved to `system.md`
- Removed the "Known Failure Patterns" section (~600 characters) — moved to `system.md`
- Removed the second full "Mandatory Readability Self-Check" block (~400 characters) — now a single consolidated Self-Check
- Added explicit Voice Policy reminder (`SCRIPT["{{narration_key}}"]` only, no TTS imports)
- Added explicit Timing rule: "NEVER use raw literal timing values (e.g., `run_time=2`) — always scale to `tracker.duration`"
- Added Failure Behavior section

**Rationale:** The `user.md` was 256 lines (11,616 characters) with extensive duplication of content from `system.md`. The user prompt is sent on every scene generation call; the system prompt is sent once per session context. Moving stable reference content to `system.md` reduces per-call token cost by ~53%. The Voice Policy reminder was absent from `user.md` and is now explicit. (Token efficiency: −6,187 characters; constraint completeness; ownership alignment)

**Token impact:** −6,187 characters (~1,500–1,800 tokens saved per scene generation call).

---

### `harness/prompts/05_scene_qc/user.md`
**Changes:**
- Added 6-part structure headings (Purpose, Inputs, Required Output, Hard Rules, Self-Check)

**Rationale:** The original 13-line `user.md` lacked explicit structure. The added sections make the agent's output contract unambiguous. (Structure)

**Token impact:** +334 characters (quality improvement accepted).

---

### `harness/prompts/06_scene_repair/user.md`
**Changes:**
- Added 6-part structure headings (Purpose, Inputs, Required Output, Hard Rules, Failure Behavior)
- Added explicit Voice Policy section ("NEVER import or configure any TTS service")
- Added explicit Timing rule ("NEVER use `run_time=<literal>`")
- Consolidated the validation checklist into the new Self-Check / Repair Validation Checklist section
- Added Failure Behavior section

**Rationale:** The original `user.md` lacked an explicit Voice Policy reminder; a repair agent could generate scene code that references TTS services without this constraint. The added Timing rule reinforces the `tracker.duration` pattern as the only acceptable approach. (Constraint completeness: voice policy, timing)

**Token impact:** +760 characters (quality improvement accepted; voice policy is non-negotiable).

---

## Validation Results

### Dry-run Composition (all phases passed)

```
bash tests/test_harness_dry_run.sh

✅ Plan phase dry-run passed
✅ Narration phase dry-run passed
✅ Build scenes phase dry-run passed
✅ Scene QC phase dry-run passed
✅ Scene repair phase dry-run passed
✅ All harness dry-run tests passed!
```

### Prompt Size Before/After

| Phase | Before (sys+user) | After (sys+user) | Delta |
|-------|-------------------|------------------|-------|
| plan | 3,412 characters | 2,889 characters | **−15%** |
| narration | 1,883 characters | 2,455 characters | +30% (structure added) |
| build_scenes | 42,760 characters | 38,075 characters | **−11%** |
| scene_qc | 8,937 characters | 9,271 characters | +4% (structure added) |
| scene_repair | 34,286 characters | 35,046 characters | +2% (voice policy added) |

The build_scenes user prompt alone went from 11,616 to 5,429 characters (**−53%** per-call savings).

### Forbidden Pattern Check

```
grep -r "gTTS\|Azure.*TTS\|OpenAI.*TTS\|\.to_edge(UP)\|run_time=" harness/prompts/ harness/templates/
```

**Matches found and explanation:**

All matches in `harness/prompts/` are in documentation context — they appear in rule statements ("NEVER use X") or illustrative wrong/right examples. Zero instances recommend or enable a forbidden pattern.

Matches in `harness/templates/` (kitchen_sink.md, manim_template.py.txt, manim_config_guide.md, visual_helpers.md, manim_content_pipeline.md) are in reference code examples for the Manim CE API. These files were not modified (outside scope). The `run_time=` appearances in kitchen_sink.md are in API-demonstration code patterns where tracker context is not always applicable (e.g., 3D camera animations). The `FORBIDDEN_FOR_BUILD_SCENES` markers in kitchen_sink.md correctly label `.to_edge(UP)` as prohibited in agent-generated output.

### Placeholder Preservation

All `{{PLACEHOLDER}}` variables present before edits remain present after:

```
{{all_scenes}}, {{broken_file_content}}, {{broken_file_name}},
{{estimated_duration_seconds}}, {{estimated_duration_text}},
{{kitchen_sink}}, {{narration_key}}, {{narration_word_count}},
{{plan_json}}, {{reference_section}}, {{retry_context}},
{{retry_section}}, {{scene_class_name}}, {{scene_details}},
{{scene_id}}, {{scene_narration}}, {{scene_title}}, {{scenes_doc}},
{{speech_wpm}}, {{title}}, {{topic}}
```

No placeholder variables were renamed, removed, or added.

---

## Risks & Rollback

**Changes that could affect downstream agent behavior:**

1. **build_scenes/user.md** — Removing the detailed layout examples from user.md means agents rely on system.md for layout guidance. If the kitchen sink or system.md layout section is insufficient, the agent may produce more layout violations. Mitigation: layout examples are now in system.md and remain authoritative there.

2. **plan/user.md** — Replacing the 40-line WRONG/RIGHT `visual_ideas` example with a concise inline example reduces illustration depth. If agents produce lower-quality visual_ideas, restore the longer example to user.md.

3. **plan/manifest.yaml** — Scene count change (8–12 → 12–24) aligns with the user prompt and reference doc but tightens validation. If the harness validation was intentionally set to 8–12 for a different reason not reflected in docs, this could cause unexpected validation failures.

**Rollback:**
```bash
# Revert all prompt changes
git checkout HEAD -- harness/prompts/
# Revert manifest
git checkout HEAD -- harness/prompts/00_plan/manifest.yaml
```

Or revert a specific file:
```bash
git checkout HEAD -- harness/prompts/04_build_scenes/user.md
```

---

## Deferred Recommendations

These improvements require changes outside `harness/prompts/` and `harness/templates/`:

1. **Template partials / include mechanism** — The voice policy, timing rules, and positioning rules appear in `core_rules.md` AND are re-stated in phase-specific prompts for emphasis. A template partial system (e.g., `{{> voice_policy}}`) would allow a single source of truth with deduplication. Requires harness template engine enhancement.

2. **`run_time=<literal>` in manim_template.py.txt** — The scaffold template contains `run_time=0.8`, `run_time=1.2`, etc. in example scene code. Updating these to tracker-based patterns (`run_time=min(0.8, tracker.duration * 0.10)`) would strengthen the timing contract in actual rendered code. Requires `harness/templates/manim_template.py.txt` change.

3. **`run_time=2` in kitchen_sink.md 3D camera examples** — Camera animation examples use `run_time=2` (literal). While these are outside the scene-body narration context, replacing with tracker-based patterns would remove ambiguity. Requires `harness/templates/kitchen_sink.md` change.

4. **Narration phase system.md** — The narration system prompt (`02_narration/system.md`) currently contains only role and behavior but no explicit output format requirement. Adding the output format constraint to system.md would reduce redundancy with user.md. Requires review of harness prompt loading order.

5. **Training phase** — `03_training/` is a stub handshake phase. If the training phase is ever expanded to actually condition the model, the current prompts should be redesigned with a proper 6-part structure. Currently kept as stub.
