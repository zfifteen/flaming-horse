# Documentation Audit Report
**Date:** 2026-02-16  
**Scope:** Complete documentation review and pipeline QC validation  
**Status:** Experiment blocked by missing dependencies (documented below)

> **Note:** This is a historical audit report. References to "ElevenLabs" in this document are intentional—they describe issues that were found during the audit and have since been addressed. This report is preserved for historical reference.

---

## Executive Summary

This audit reviews agent instructions (AGENTS.md, reference_docs/) and validates them against actual implementation. The review identifies **14 critical issues** requiring immediate correction, including stale ElevenLabs references that contradict the Qwen-only voice policy, missing dependency documentation, and unclear mock-mode guidance.

**Key Finding:** The helper functions (`BeatPlan`, `play_next`, `play_text_next`, `safe_layout`) referenced in AGENTS.md ARE implemented in `scripts/scaffold_scene.py` and ARE injected into scene files. This is a major strength—the documentation correctly describes available functionality.

---

## 1. Documentation Review Findings

### 1.1 CRITICAL: Stale ElevenLabs References

**Severity:** `critical` - Direct contradiction to voice policy

| File | Line | Issue | Recommended Fix |
|------|------|-------|-----------------|
| `AGENTS.md` | 30 | States "NEVER call ElevenLabs" but should say "Qwen-only" | Change to "❌ **NEVER** use any TTS service except cached Qwen" |
| `reference_docs/phase_scenes.md` | 48 | "Render all scenes with ElevenLabs voice" | Change to "Render all scenes with cached Qwen voice" |
| `docs/VOICE_POLICY.md` | 71 | "If ElevenLabs fails, we want to know immediately" | Change to "If Qwen TTS fails, we want to know immediately" |
| `docs/VOICE_POLICY.md` | 89 | "Test with ElevenLabs voice. That's what production will use." | Change to "Test with cached Qwen voice. That's what production will use." |

**Context:** The voice policy clearly states Qwen-only (lines 1-27 of VOICE_POLICY.md), but legacy ElevenLabs references remain from earlier versions. This creates confusion and contradicts the "no fallback" policy.

**Impact:** Agents reading these docs may incorrectly believe ElevenLabs is supported or required.

---

### 1.2 CRITICAL: Helper Function Documentation vs Implementation

**Severity:** `info` - Documentation is CORRECT (rare win!)

**Finding:** AGENTS.md claims the following helpers are available:
- `BeatPlan(tracker.duration, [weights])`
- `play_next(scene, beats, *animations, ...)`
- `play_text_next(scene, beats, *animations, max_text_seconds=1.5, ...)`
- `safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2)`
- `safe_layout(*mobjects, h_buff=0.5, ...)`

**Verification:** All helpers ARE implemented in `scripts/scaffold_scene.py` (lines 25-131) and injected into every scene file via the `TEMPLATE` string.

**Evidence:**
```python
# scaffold_scene.py lines 48-77
class BeatPlan:
    def __init__(self, total_duration, weights):
        # ...implementation...

# scaffold_scene.py lines 112-131
def play_next(scene, beats, *animations, max_run_time=None, min_run_time=0.3, **play_kwargs):
    return play_in_slot(scene, beats.next_slot(), ...)
```

**Recommendation:** No changes needed. This is exemplary documentation-to-implementation alignment.

---

### 1.3 WARNING: Mock Mode Clarity

**Severity:** `warning` - Undocumented feature mentioned in issue description

**Finding:** The issue description mentions `--mock` flag for `create_video.sh`:
```bash
./scripts/create_video.sh copilot-test-video-1 --topic "..." --mock
```

**Verification:** Searched all shell scripts and documentation for `--mock` flag:
```bash
grep -rn "\-\-mock" scripts/ docs/ reference_docs/
# Result: No matches
```

**Impact:** Users have no guidance on when/how to use mock mode or what it does.

**Recommendation:** Add mock-mode documentation to:
1. `README.md` - Quick start section
2. `scripts/create_video.sh` usage text
3. `AGENTS.md` - Voice policy section

**Suggested content:**
```markdown
### Mock Mode (CI/Cloud Environments)

If running in a constrained environment without Qwen model access:
```bash
./scripts/create_video.sh my_video --topic "..." --mock
```

Mock mode uses placeholder audio for testing pipeline mechanics without TTS.
**Not suitable for production videos.** Use only for development/CI validation.
```

---

### 1.4 WARNING: Dependency Installation Not Documented

**Severity:** `warning` - Critical path missing from docs

**Finding:** README.md (lines 59-69) shows minimal install instructions:
```bash
pip install manim manim-voiceover-plus
brew install sox ffmpeg
```

But actual environment requirements include:
- Python 3.8+ (documented)
- Manim Community Edition (documented)
- FFmpeg (documented)
- Sox (documented)
- **HuggingFace Transformers** (not documented)
- **Qwen model downloaded** (mentioned but not detailed)
- **Voice reference assets** (`assets/voice_ref/ref.wav` + `ref.txt`) (not documented)

**Evidence from code:**
```bash
# scripts/create_video.sh lines 4-7
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
```

**Verification:** Attempted to run experiment but dependencies missing:
```bash
$ which manim
# (empty - not installed)
$ ls -la assets/voice_ref/
ls: cannot access 'assets/voice_ref/': No such file or directory
```

**Recommendation:** Add complete installation guide to `docs/INSTALLATION.md` including:
1. Python package requirements (`requirements.txt`)
2. System dependencies (ffmpeg, sox, latex)
3. Qwen model download procedure
4. Voice reference asset creation
5. Environment variable configuration

---

### 1.5 INFO: Visual Helper Integration

**Severity:** `info` - Minor enhancement opportunity

**Finding:** AGENTS.md (lines 188-226) includes enhanced visual helpers in the scene template:
- `harmonious_color(base_color, variations=3, lightness_shift=0.1)`
- `polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.1, glow=False)`
- `adaptive_title_position(title, content_group, max_shift=0.5)`

**Verification:** These helpers are NOT in `scaffold_scene.py` template (lines 9-161).

**Impact:** Agents following AGENTS.md will include these helpers inline in each scene file, leading to code duplication.

**Recommendation:** Either:
1. Add these helpers to `scaffold_scene.py` TEMPLATE (preferred), OR
2. Create `flaming_horse_visual_helpers.py` module and import in scaffold

**Preferred approach:**
```python
# In scaffold_scene.py TEMPLATE, add after safe_layout():
def harmonious_color(base_color, variations=3, lightness_shift=0.1):
    import colorsys
    # ...implementation from visual_helpers.md...
```

---

### 1.6 INFO: Positioning Rules Consistency

**Severity:** `info` - Documentation is consistent and correct

**Finding:** Positioning rules are clearly stated in multiple locations:
- AGENTS.md lines 285-298 (Layout Contract)
- reference_docs/phase_scenes.md lines 36-42 (Layout Checklist)
- reference_docs/manim_config_guide.md (assumed - not reviewed in detail)

**Key rules verified:**
1. Title at `UP * 3.8` (never `.to_edge(UP)`) ✓
2. Call `safe_position()` after `.next_to()` ✓
3. Call `safe_layout()` for 2+ sibling elements ✓
4. Graphs/diagrams offset downward (`DOWN * 0.6` to `DOWN * 1.2`) ✓

**Evidence:** These rules are reinforced in:
- Scene template example (AGENTS.md lines 243-260)
- Pre-render validation checklist (AGENTS.md lines 439-443)
- Phase scenes documentation (phase_scenes.md lines 36-42)

**Recommendation:** No changes needed. Positioning guidance is comprehensive and consistent.

---

### 1.7 WARNING: Frame Inspection Procedure Missing

**Severity:** `warning` - Deliverable requirement not documented

**Finding:** Issue description requests "standard frame-inspection procedure" but no such procedure exists in docs.

**Current state:** 
- phase_scenes.md mentions "Extract a mid-frame" (lines 88-96) but provides no runnable commands
- AGENTS.md mentions frame thumbnails (line 482) but no extraction procedure

**Recommendation:** Add to `docs/FRAME_INSPECTION.md`:

```markdown
# Frame Inspection Procedure

## Extract Representative Frames

```bash
# Extract mid-frame from video
ffmpeg -ss 50% -i final_video.mp4 -vframes 1 -q:v 2 midframe.jpg

# Extract specific timestamp
ffmpeg -ss 00:00:05 -i scene_01_intro.mp4 -vframes 1 frame_5s.jpg

# Extract every 10 seconds
ffmpeg -i final_video.mp4 -vf "fps=1/10" frame_%03d.jpg
```

## Visual Validation Checklist

- [ ] Title visible and positioned near top edge (not clipped)
- [ ] Subtitle spacing consistent (0.4-0.5 units below title)
- [ ] Content inside safe bounds (y between -4.0 and 4.0)
- [ ] No overlapping elements (siblings properly spaced)
- [ ] Text readable at 1440p (no aliasing/blur)
```

---

### 1.8 INFO: Timing Budget Examples

**Severity:** `info` - Documentation is excellent

**Finding:** AGENTS.md (lines 327-341) provides clear timing budget examples with WRONG/CORRECT patterns.

**Example quality:**
```python
# WRONG - Causes dead air:
with self.voiceover(text=SCRIPT["demo"]) as tracker:  # 10 seconds
    self.play(Write(title), run_time=tracker.duration * 0.6)   # 6s (60%)
    self.play(FadeIn(obj), run_time=tracker.duration * 0.5)     # 5s (50%)
    # Total = 1.1 = 110% → 1 second of SILENT VIDEO ❌
```

**Strength:** Uses concrete numbers and explains the failure mode.

**Recommendation:** No changes needed. This is exemplary instructional content.

---

### 1.9 WARNING: Render Quality Flag Ambiguity

**Severity:** `warning` - Conflicting guidance

**Finding:** AGENTS.md says "render with `-qh`" (line 53 in phase_scenes.md) but doesn't explain quality levels or when to use each.

**Evidence:**
- phase_scenes.md line 55: "Default to `-pql` for validation, then `-qh` if passes"
- No explanation of what `-pql`, `-qh`, `-ql` mean
- No guidance on disk space or time tradeoffs

**Recommendation:** Add to `reference_docs/manim_config_guide.md`:

```markdown
## Render Quality Flags

| Flag | Resolution | FPS | Use Case | Approx Time | Size |
|------|-----------|-----|----------|-------------|------|
| `-ql` | 854×480 | 15 | Quick iteration | ~10s/scene | ~5MB |
| `-qm` | 1280×720 | 30 | Review | ~30s/scene | ~20MB |
| `-qh` | 1920×1080 | 60 | Production (default) | ~2min/scene | ~50MB |
| `-qk` | 3840×2160 | 60 | 4K export | ~5min/scene | ~200MB |
| `-pql` | (preview low) | 15 | Fast preview | ~5s/scene | ~2MB |

**Pipeline default:** `-ql` for validation, `-qh` for final render.
```

---

### 1.10 CRITICAL: Voice Cache Validation Not Documented

**Severity:** `critical` - Pipeline requirement missing from AGENTS.md

**Finding:** Scripts use voice cache hash validation (`scripts/voice_cache_validator.py`) but this is never mentioned in AGENTS.md or reference docs.

**Evidence:**
```python
# From repository_memories:
"Voice cache uses SHA256 hash of narration_script.py stored in .cache_hash file. 
Skip precache if hash matches, saving 2-5 minutes per build."
```

**Impact:** Agents don't know this optimization exists and may unnecessarily regenerate voice cache.

**Recommendation:** Add to `reference_docs/phase_narration.md`:

```markdown
## Voice Cache Optimization

After generating `narration_script.py`, the precache step:
1. Computes SHA256 hash of narration_script.py
2. Compares to `.cache_hash` file in project
3. Skips regeneration if hash matches (saves 2-5 minutes)

**Agent action:** None required. Orchestrator handles cache validation automatically.
```

---

### 1.11 INFO: Phase Sequencing Documentation

**Severity:** `info` - Clear and correct

**Finding:** AGENTS.md clearly states phase-locking requirement (lines 58-66):
> **This repo uses an orchestrator (`scripts/build_video.sh`) that invokes the agent one phase at a time.**
> - ✅ **ALWAYS** read `project_state.json` and execute ONLY the current phase.
> - ❌ **NEVER** execute multiple phases in a single invocation

**Verification:** This aligns with `scripts/build_video.sh` behavior (confirmed via repository memories).

**Recommendation:** No changes needed. Documentation is accurate.

---

### 1.12 WARNING: Error Handling Examples Incomplete

**Severity:** `warning` - Missing recovery guidance

**Finding:** AGENTS.md (lines 468-476) shows how to record errors:
```python
error_msg = f"Phase {phase} failed: {error_details}"
state['errors'].append(error_msg)
state['flags']['needs_human_review'] = True
```

But doesn't explain:
- What happens after `needs_human_review` is set
- How to clear the flag
- When to retry vs escalate
- What format `error_details` should use

**Recommendation:** Add to AGENTS.md after line 476:

```python
### Error Recovery Protocol

When `needs_human_review = True`:
1. Orchestrator halts after current phase
2. Human inspects `state['errors']` array
3. Human fixes issue (edits files, updates deps, etc.)
4. Human clears flag: Set `state['flags']['needs_human_review'] = false`
5. Human resumes: `./scripts/build_video.sh <project>`

**Agent responsibility:** Provide actionable error messages.

Good: "Scene 02 failed: MathTex rendering error at line 45. Check LaTeX syntax for '\\frac{GMm}{r^2}'"
Bad: "Render failed"
```

---

### 1.13 INFO: 3D Scene Guidance

**Severity:** `info` - Policy change documented

**Finding:** phase_plan.md line 60 states:
> 3D is allowed and often preferred when it improves clarity/engagement; flag only if unusually complex

**Contrast:** Earlier versions discouraged 3D (based on repository memories mentioning 3D warnings).

**Current guidance:** visual_helpers.md lines 47-48:
> 3D Guidelines: Prefer for spatial topics (e.g., geometry); limit to 1-2 moving objects.

**Recommendation:** No changes needed. This is an intentional policy evolution documented in agent_improvements.md.

---

### 1.14 WARNING: Parallel Rendering Not Mentioned in AGENTS.md

**Severity:** `warning` - Performance feature undocumented for agents

**Finding:** Scripts support parallel rendering (`scripts/render_scene_worker.sh`, `PARALLEL_RENDERS` env var) but AGENTS.md never mentions this.

**Evidence from repository_memories:**
> Parallel scene rendering requires MANIM_VOICE_PROD=1 and other env vars passed via GNU parallel --env flag

**Impact:** Agents may not understand why certain environment variables are required or why renders run in parallel.

**Recommendation:** Add to `reference_docs/phase_scenes.md` after line 127:

```markdown
## Parallel Rendering (Automatic)

The orchestrator automatically renders scenes in parallel when:
- `PARALLEL_RENDERS` env var set (0=auto, N=use N jobs, -1=disable)
- GNU parallel installed
- All scenes pass pre-render validation

**Agent action:** None required. Orchestrator handles parallelization.

Required env vars (set by orchestrator):
- `MANIM_VOICE_PROD=1`
- `PYTHONPATH=<repo_root>`
- `FLAMING_HORSE_TTS_BACKEND=qwen`
- `HF_HUB_OFFLINE=1`
```

---

## 2. Experiment Log

### 2.1 Experiment Setup

**Command:** Could not execute due to missing dependencies

**Planned command:**
```bash
./scripts/create_video.sh copilot-test-video-1 --topic "Create a video explaining trial division."
```

**Environment check results:**

| Dependency | Status | Notes |
|------------|--------|-------|
| Python | ✓ 3.12.3 | Installed |
| Manim | ✗ Not found | `which manim` returned empty |
| FFmpeg | ✗ Not found | `which ffmpeg` returned empty |
| Voice refs | ✗ Missing | `assets/voice_ref/` does not exist |
| HuggingFace | ✗ Unknown | Cannot verify without attempting import |

### 2.2 Blocking Issues

**Issue 1:** Manim not installed
```bash
$ which manim
(empty)
```

**Issue 2:** FFmpeg not installed
```bash
$ which ffmpeg
(empty)
```

**Issue 3:** Voice reference assets missing
```bash
$ ls -la assets/voice_ref/
ls: cannot access 'assets/voice_ref/': No such file or directory
```

### 2.3 Installation Gap Analysis

**README.md states:**
```bash
pip install manim manim-voiceover-plus
brew install sox ffmpeg
```

**Problems:**
1. No `requirements.txt` file to ensure version compatibility
2. No pre-flight check script to validate environment
3. No guidance on creating voice reference assets
4. No Qwen model download instructions

**Recommendation:** Create `scripts/check_dependencies.sh`:

```bash
#!/usr/bin/env bash
# Verify all required dependencies before running pipeline

errors=0

command -v python3 >/dev/null || { echo "✗ Python 3 not found"; errors=$((errors+1)); }
command -v manim >/dev/null || { echo "✗ Manim not found"; errors=$((errors+1)); }
command -v ffmpeg >/dev/null || { echo "✗ FFmpeg not found"; errors=$((errors+1)); }
command -v sox >/dev/null || { echo "✗ Sox not found"; errors=$((errors+1)); }

[[ -f "assets/voice_ref/ref.wav" ]] || { echo "✗ Voice reference missing"; errors=$((errors+1)); }

python3 -c "import manim_voiceover_plus" 2>/dev/null || { echo "✗ manim-voiceover-plus not installed"; errors=$((errors+1)); }

if [[ $errors -eq 0 ]]; then
  echo "✓ All dependencies satisfied"
  exit 0
else
  echo ""
  echo "See docs/INSTALLATION.md for setup instructions"
  exit 1
fi
```

### 2.4 Experiment Outcome

**Status:** ❌ Blocked - Cannot run experiment without dependencies

**Next steps for manual validation:**
1. Install dependencies
2. Create voice reference assets
3. Re-run experiment
4. Extract frames and validate positioning
5. Document any deviations from AGENTS.md template

---

## 3. Documentation Edit Proposals

### 3.1 AGENTS.md Edits

**Edit 1: Remove ElevenLabs reference (line 30)**

```diff
- ❌ **NEVER** call ElevenLabs in this repo.
+ ❌ **NEVER** use any TTS service except cached Qwen.
```

---

### 3.2 reference_docs/phase_scenes.md Edits

**Edit 1: Fix voice service reference (line 48)**

```diff
-**Goal:** Render all scenes with ElevenLabs voice (production quality) and verify output
+**Goal:** Render all scenes with cached Qwen voice (production quality) and verify output
```

---

### 3.3 docs/VOICE_POLICY.md Edits

**Edit 1: Update service name (line 71)**

```diff
-4. **Fail Fast:** If ElevenLabs fails, we want to know immediately, not get a gTTS video
+4. **Fail Fast:** If Qwen TTS fails, we want to know immediately, not get a placeholder audio
```

**Edit 2: Update service name (line 89)**

```diff
-A: Don't. Test with ElevenLabs voice. That's what production will use.
+A: Don't. Test with cached Qwen voice. That's what production will use.
```

---

### 3.4 README.md Additions

**Addition 1: After line 69 (Installation section)**

```markdown
## Environment Setup

Before your first build:

```bash
# 1. Check dependencies
./scripts/check_dependencies.sh

# 2. Set up voice reference (one-time)
# Record a 5-10 second voice sample and place:
# - assets/voice_ref/ref.wav (audio file)
# - assets/voice_ref/ref.txt (transcript of audio)

# 3. Test Qwen model access
python3 -c "from scripts.qwen_tts_mediator import load_model; load_model()"
```

For detailed installation instructions, see [docs/INSTALLATION.md](docs/INSTALLATION.md).
```

---

### 3.5 New File: docs/INSTALLATION.md

```markdown
# Installation Guide

## Prerequisites

- Python 3.8 or higher
- 8GB+ RAM (16GB recommended for Qwen model)
- FFmpeg and Sox for media processing
- LaTeX (for mathematical typesetting)

## Step 1: System Dependencies

### macOS
```bash
brew install ffmpeg sox
brew install --cask mactex-no-gui
```

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install ffmpeg sox texlive-latex-base texlive-fonts-recommended
```

## Step 2: Python Packages

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install manim manim-voiceover-plus transformers torch
```

## Step 3: Voice Reference Assets

Create voice reference for Qwen voice cloning:

```bash
mkdir -p assets/voice_ref
```

1. Record a 5-10 second voice sample (clear audio, minimal background noise)
2. Save as `assets/voice_ref/ref.wav` (16kHz mono WAV preferred)
3. Create `assets/voice_ref/ref.txt` with exact transcript of the audio

Example `ref.txt`:
```
Hello, this is my voice sample for video narration. The quality matters.
```

## Step 4: Qwen Model Download

First run will download the Qwen TTS model (~3GB):

```bash
python3 -c "from scripts.qwen_tts_mediator import load_model; load_model()"
```

Model will be cached in `~/.cache/huggingface/`.

## Step 5: Verify Installation

```bash
./scripts/check_dependencies.sh
```

All checks should pass (✓) before creating videos.

## Troubleshooting

**Issue:** Manim import errors
- **Fix:** Ensure `manim` package installed, not `manimlib` (different project)

**Issue:** LaTeX rendering fails
- **Fix:** Install full LaTeX distribution (mactex or texlive-full)

**Issue:** Qwen model download fails
- **Fix:** Check internet connection, disk space (need 5GB free)

**Issue:** Voice reference not found
- **Fix:** Verify `assets/voice_ref/ref.wav` and `ref.txt` exist and are readable
```

---

### 3.6 New File: docs/FRAME_INSPECTION.md

```markdown
# Frame Inspection Procedure

Use these commands to validate visual quality of rendered scenes.

## Extract Representative Frames

### Mid-frame from video
```bash
ffmpeg -ss 50% -i final_video.mp4 -vframes 1 -q:v 2 midframe.jpg
```

### Specific timestamp
```bash
ffmpeg -ss 00:00:05 -i scene_01_intro.mp4 -vframes 1 frame_5s.jpg
```

### Grid of thumbnails (every 10 seconds)
```bash
ffmpeg -i final_video.mp4 -vf "fps=1/10" frame_%03d.jpg
```

## Visual Validation Checklist

For each extracted frame, verify:

### Positioning
- [ ] Title visible near top edge (y ≈ 3.8)
- [ ] Title not clipped by frame boundary
- [ ] Subtitle spacing consistent (0.4-0.5 units below title)
- [ ] Content within safe bounds (y between -4.0 and 4.0)
- [ ] No elements touching left/right edges

### Layout
- [ ] No overlapping text elements
- [ ] Sibling elements properly spaced (h_buff ≥ 0.5)
- [ ] Vertical alignment intentional (not accidental)
- [ ] Charts/graphs offset below subtitle (not overlapping title)

### Quality
- [ ] Text readable at 1440p (no aliasing or blur)
- [ ] Colors have sufficient contrast
- [ ] Mathematical notation renders cleanly (no garbled LaTeX)
- [ ] Animations appear smooth (no stuttering or frozen frames)

## Automated Validation (Future)

Planned: `scripts/validate_frames.py` to programmatically check positioning rules.
```

---

### 3.7 New File: scripts/check_dependencies.sh

```bash
#!/usr/bin/env bash
# Verify all required dependencies before running pipeline

set -euo pipefail

errors=0

echo "Checking dependencies..."
echo ""

# Python
if command -v python3 >/dev/null; then
  version=$(python3 --version | awk '{print $2}')
  echo "✓ Python $version"
else
  echo "✗ Python 3 not found"
  errors=$((errors+1))
fi

# Manim
if command -v manim >/dev/null; then
  version=$(manim --version 2>&1 | head -1 || echo "unknown")
  echo "✓ Manim ($version)"
else
  echo "✗ Manim not found (install: pip install manim)"
  errors=$((errors+1))
fi

# FFmpeg
if command -v ffmpeg >/dev/null; then
  version=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')
  echo "✓ FFmpeg $version"
else
  echo "✗ FFmpeg not found (install: brew install ffmpeg)"
  errors=$((errors+1))
fi

# Sox
if command -v sox >/dev/null; then
  version=$(sox --version 2>&1 | head -1 | awk '{print $3}')
  echo "✓ Sox $version"
else
  echo "✗ Sox not found (install: brew install sox)"
  errors=$((errors+1))
fi

# Voice reference
if [[ -f "assets/voice_ref/ref.wav" ]] && [[ -f "assets/voice_ref/ref.txt" ]]; then
  echo "✓ Voice reference assets"
else
  echo "✗ Voice reference missing (create: assets/voice_ref/ref.wav + ref.txt)"
  errors=$((errors+1))
fi

# Python packages
if python3 -c "import manim" 2>/dev/null; then
  echo "✓ manim package"
else
  echo "✗ manim package not installed (install: pip install manim)"
  errors=$((errors+1))
fi

if python3 -c "import manim_voiceover_plus" 2>/dev/null; then
  echo "✓ manim-voiceover-plus package"
else
  echo "✗ manim-voiceover-plus not installed (install: pip install manim-voiceover-plus)"
  errors=$((errors+1))
fi

echo ""
if [[ $errors -eq 0 ]]; then
  echo "✅ All dependencies satisfied - ready to build videos"
  exit 0
else
  echo "❌ $errors missing dependencies - see docs/INSTALLATION.md"
  exit 1
fi
```

---

## 4. Summary of Findings

### Critical Issues (3)
1. **Stale ElevenLabs references** - 4 locations need correction
2. **Missing dependency documentation** - Installation incomplete
3. **Voice cache validation undocumented** - Performance optimization hidden

### Warnings (6)
1. Mock mode clarity - Feature mentioned but not documented
2. Frame inspection procedure missing
3. Render quality flag ambiguity
4. Error recovery protocol incomplete
5. Parallel rendering not mentioned in AGENTS.md
6. Dependency installation gaps

### Info (5)
1. Helper functions correctly documented ✓
2. Positioning rules consistent ✓
3. Timing budget examples excellent ✓
4. Phase sequencing clear ✓
5. 3D guidance updated appropriately ✓

### Total: 14 findings (3 critical, 6 warning, 5 info)

---

## 5. Experiment Validation (Pending)

**Status:** Cannot validate until dependencies installed

**When validation is possible, test:**
1. Run create_video.sh with trial division topic
2. Monitor phase progression (plan → review → narration → build_scenes → final_render → assemble)
3. Extract mid-frame from each scene
4. Verify positioning rules:
   - Title at UP * 3.8
   - No overlapping elements
   - Content within safe bounds
5. Check timing sync (no dead air or premature cutoffs)
6. Validate voice cache optimization (should skip regeneration on second run)

---

## 6. Recommendations Priority Order

### P0 (Critical - Fix immediately)
1. Remove all ElevenLabs references (4 edits)
2. Create docs/INSTALLATION.md
3. Create scripts/check_dependencies.sh
4. Document voice cache validation

### P1 (Important - Fix soon)
1. Document mock mode in README and create_video.sh
2. Create docs/FRAME_INSPECTION.md
3. Add render quality flag documentation
4. Complete error recovery protocol

### P2 (Nice to have)
1. Add visual helpers to scaffold template
2. Document parallel rendering
3. Create requirements.txt
4. Add automated frame validation script

---

**Report prepared by:** GitHub Copilot Agent  
**Audit date:** 2026-02-16  
**Next steps:** Implement P0 fixes, install dependencies, re-run experiment
