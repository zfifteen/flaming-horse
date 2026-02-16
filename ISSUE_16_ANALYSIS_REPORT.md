# Issue #16 Analysis & Update Report

## Executive Summary

Performed comprehensive analysis of ElevenLabs references in the flaming-horse repository to update issue #16. The original issue description contained several inaccuracies - notably stating that AGENTS.md and manim_voiceover.md needed updates when they were already correctly cleaned up.

## Findings

### Original Issue Claims vs. Reality

| Original Claim | Reality | Status |
|---|---|---|
| AGENTS.md has ElevenLabs integration docs | Only has prohibition policy | ✅ Already correct |
| manim_voiceover.md has ElevenLabs patterns | Fully updated to Qwen-only | ✅ Already correct |
| MOCK_VOICE_RECOVERY.md needs update | File doesn't exist | ✅ Not applicable |
| README/repo description needs update | Already says "cached Qwen voice clones" | ✅ Already correct |
| 12 files have stale references | 7 files have references (excl. issues/) | ⚠️ Count was off |

### Actual State

**Total References:** 55 hits for "elevenlabs" (case-insensitive)
- **45 references** in `issues/*.md` (historical records - should be preserved)
- **10 references** in active documentation and code

**Files Requiring Updates (High Priority):**
1. `reference_docs/phase_scenes.md` - Line 48
2. `docs/VOICE_POLICY.md` - Lines 71, 89  
3. `docs/scaffold_instructions.md` - Lines 11, 77, 136-137, 229

**Files Requiring Decision (Medium/Low Priority):**
4. `scripts/migrate_voiceover_to_qwen.py` - Migration script (archive or keep?)
5. `projects/matrix-multiplication/voice_config.py` - Legacy project example
6. `projects/matrix-multiplication/project_state.json` - Legacy project history

## Detailed Analysis

### High Priority Documentation Updates Needed

#### 1. reference_docs/phase_scenes.md (Line 48)
**Current:** `**Goal:** Render all scenes with ElevenLabs voice (production quality) and verify output`
**Should be:** `**Goal:** Render all scenes with cached Qwen voice (production quality) and verify output`
**Or:** `**Goal:** Render all scenes at production quality and verify output`

#### 2. docs/VOICE_POLICY.md

**Line 71:**
- Current: `4. **Fail Fast:** If ElevenLabs fails, we want to know immediately, not get a gTTS video`
- Should be: `4. **Fail Fast:** If Qwen voice cache fails, we want to know immediately, not get a gTTS video`

**Line 89:**
- Current: `A: Don't. Test with ElevenLabs voice. That's what production will use.`
- Should be: `A: Don't. Test with cached Qwen voice. That's what production will use.`

#### 3. docs/scaffold_instructions.md

**Line 11:**
- Current: `3. **Use my ElevenLabs voice configuration**: Voice ID \`rBgRd5IfS6iqrGfuhlKR\`, model \`eleven_multilingual_v2\``
- Should be: `3. **Use Qwen voice clone configuration**: Reference assets in \`assets/voice_ref/\``

**Line 77:**
- Current: `- Prerequisites (manim, manim-voiceover-plus, sox, ffmpeg, ElevenLabs API key)`
- Should be: `- Prerequisites (manim, manim-voiceover-plus, sox, ffmpeg, Qwen model and voice reference assets)`

**Lines 136-137:**
```bash
# Current:
# ElevenLabs config
export ELEVENLABS_API_KEY="${ELEVENLABS_API_KEY:?ERROR: Set ELEVENLABS_API_KEY}"
VOICE_ID="rBgRd5IfS6iqrGfuhlKR"
MODEL_ID="eleven_multilingual_v2"

# Should be:
# Qwen voice config
export MANIM_VOICE_PROD=1
export FLAMING_HORSE_TTS_BACKEND=qwen
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
```

**Line 229:**
- Current: `Re-render all scenes with \`MANIM_VOICE_PROD=1\` (ElevenLabs)`
- Should be: `Re-render all scenes with \`MANIM_VOICE_PROD=1\` (cached Qwen voice)`

### Medium Priority: Migration Script

`scripts/migrate_voiceover_to_qwen.py` contains ElevenLabs references by design (it's a migration tool). Options:
- **Option A:** Keep as-is (references are expected in migration code)
- **Option B:** Move to `archive/` if migration is complete and won't be used again
- **Option C:** Add header comment: "Historical migration script - references to ElevenLabs are expected"

### Low Priority: Legacy Project

`projects/matrix-multiplication/` appears to be a legacy example from before the Qwen migration:
- `voice_config.py` imports from `elevenlabs` package
- `project_state.json` has history entries mentioning ElevenLabs

Options:
- **Option A:** Update to use Qwen services (if it should remain a working example)
- **Option B:** Add a README noting it predates the migration (for reference only)
- **Option C:** Leave as-is (historical artifact)

### No Changes Needed

- `issues/*.md` - Historical records, should be preserved
- `AGENTS.md` - Already correct (only has prohibition)
- `reference_docs/manim_voiceover.md` - Already fully Qwen-based
- README.md - Already accurate

## Updated Issue Body

The accurate, updated issue description has been created in:
```
/home/runner/work/flaming-horse/flaming-horse/ISSUE_16_UPDATED_BODY.md
```

## How to Apply the Update

### Automated (requires appropriate GitHub token):
```bash
cd /home/runner/work/flaming-horse/flaming-horse
gh issue edit 16 --body-file ISSUE_16_UPDATED_BODY.md
```

### Manual:
1. Go to https://github.com/zfifteen/flaming-horse/issues/16
2. Click "Edit" on the issue description
3. Replace entire body with contents of `ISSUE_16_UPDATED_BODY.md`
4. Save

## Why Direct Update Failed

Attempted to update the issue via:
- `gh issue edit` CLI command
- GitHub REST API (PATCH /repos/{owner}/{repo}/issues/{number})
- GitHub GraphQL API (updateIssue mutation)

All attempts returned: `"Resource not accessible by integration"` (HTTP 403)

The GitHub Actions token (`GITHUB_TOKEN`) used by this agent does not have the `issues:write` scope required to modify issue descriptions. It only has permissions for repository content (code, commits, PRs).

## Verification Commands

To verify the current state yourself:

```bash
# Count total ElevenLabs references
grep -ri "elevenlabs" . --include="*.md" --include="*.py" --include="*.sh" --include="*.json" 2>/dev/null | wc -l

# List files with references (excluding issues/)
grep -ri "elevenlabs" . --include="*.md" --include="*.py" --include="*.sh" --include="*.json" 2>/dev/null | \
  grep -v "issues/" | grep -v "NEVER call ElevenLabs" | cut -d: -f1 | sort -u

# Check specific high-priority files
grep -n "elevenlabs" reference_docs/phase_scenes.md -i
grep -n "elevenlabs" docs/VOICE_POLICY.md -i
grep -n "elevenlabs" docs/scaffold_instructions.md -i
```

## Conclusion

The original issue #16 overstated the problem. The main work (AGENTS.md, manim_voiceover.md, README) was already complete. Only 3 high-priority documentation files need updates, plus decisions on 2 medium/low priority items (migration script and legacy project).

The updated issue body accurately reflects this current state and provides a clear, prioritized action plan.
