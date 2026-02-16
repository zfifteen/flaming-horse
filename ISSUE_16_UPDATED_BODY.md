## Summary

The project migrated from ElevenLabs to local Qwen voice clone, and AGENTS.md explicitly forbids ElevenLabs (`NEVER call ElevenLabs in this repo`). However, **several files still reference ElevenLabs**, creating contradictions that confuse both human contributors and automated agents.

## Current State (Updated 2026-02-16)

### ✅ Already Cleaned Up

- **AGENTS.md**: Only contains policy prohibition ("NEVER call ElevenLabs") - correct state
- **reference_docs/manim_voiceover.md**: Fully updated to Qwen-only patterns, no ElevenLabs references
- **README.md**: Already describes "cached Qwen voice clones" - correct state
- **docs/MOCK_VOICE_RECOVERY.md**: Does not exist (was removed or never created)

### ❌ Files Still Requiring Updates

A code search for `ElevenLabs` across the repo returns **55 total hits**, distributed as follows:

| File | Nature of Reference | Priority |
|---|---|---|
| `reference_docs/phase_scenes.md` | Line 48: "Render all scenes with ElevenLabs voice (production quality)" | **HIGH** |
| `docs/VOICE_POLICY.md` | Lines 71, 89 reference ElevenLabs in Q&A section | **HIGH** |
| `docs/scaffold_instructions.md` | Lines 11, 77, 136-137, 229 reference ElevenLabs config and API key | **HIGH** |
| `scripts/migrate_voiceover_to_qwen.py` | Migration script with ElevenLabs replacement logic | **MEDIUM** (historical/archive) |
| `projects/matrix-multiplication/voice_config.py` | Legacy project config importing from `elevenlabs` package | **LOW** (legacy example) |
| `projects/matrix-multiplication/project_state.json` | Legacy project history mentioning ElevenLabs in `history` array | **LOW** (historical record) |
| `issues/*.md` | 5 files with historical references | **KEEP** (historical records) |

### 📊 Reference Count
- Total: 55 references
- In `issues/` (historical): ~45 references
- In active documentation/code: ~10 references

## What Needs to Happen

### Priority 1: Core Documentation (HIGH)

1. **reference_docs/phase_scenes.md** (line 48):
   - Change: "Render all scenes with ElevenLabs voice (production quality)"
   - To: "Render all scenes with cached Qwen voice (production quality)" or "Render all scenes at production quality"

2. **docs/VOICE_POLICY.md** (lines 71, 89):
   - Line 71: Update "If ElevenLabs fails" → "If Qwen voice cache fails"
   - Line 89: Update "Test with ElevenLabs voice" → "Test with cached Qwen voice"

3. **docs/scaffold_instructions.md** (lines 11, 77, 136-137, 229):
   - Line 11: Update voice configuration reference from ElevenLabs to Qwen
   - Line 77: Update prerequisites from "ElevenLabs API key" to "Qwen model and voice reference assets"
   - Lines 136-137: Remove `ELEVENLABS_API_KEY` export, replace with Qwen env vars
   - Line 229: Update "Re-render all scenes with `MANIM_VOICE_PROD=1` (ElevenLabs)" to reflect Qwen

### Priority 2: Migration Script (MEDIUM)

4. **scripts/migrate_voiceover_to_qwen.py**: 
   - Evaluate if still needed for active use
   - If migration is complete, consider moving to `archive/` or adding a header comment indicating it's for reference only
   - Alternative: Keep as-is since references are expected in a migration script

### Priority 3: Legacy Project (LOW)

5. **projects/matrix-multiplication/**: 
   - These are historical artifacts from pre-migration
   - Option A: Update `voice_config.py` to import Qwen services (if project should remain runnable)
   - Option B: Add README note that this predates the Qwen migration
   - Option C: Leave as-is (historical example)
   - `project_state.json` history array should remain unchanged (historical record)

### No Changes Needed

6. **issues/*.md**: Historical records - no changes needed, but will continue to appear in code search
7. **AGENTS.md**: Already correct (only contains prohibition policy)
8. **reference_docs/manim_voiceover.md**: Already fully updated
9. **GitHub repo description**: README already accurate

## Acceptance Criteria

- [ ] `grep -ri "elevenlabs" reference_docs/ docs/ --include="*.md" | grep -v "NEVER call ElevenLabs"` returns zero hits
- [ ] All active documentation (reference_docs/, docs/) reflects Qwen-only voice pipeline
- [ ] Decision made on migration script (archive, keep as-is, or remove)
- [ ] Decision made on matrix-multiplication project (update, note, or leave as-is)
- [ ] `issues/` directory acknowledged as historical record (no cleanup needed)

## Notes

- This issue description was updated on 2026-02-16 to reflect actual repository state
- AGENTS.md and manim_voiceover.md were already correctly updated
- Main cleanup needed: 3 active documentation files (phase_scenes.md, VOICE_POLICY.md, scaffold_instructions.md)
