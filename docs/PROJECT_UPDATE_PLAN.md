# Project Update Plan: Incremental Manim Video Builder

**Date**: February 11, 2026  
**Based On**: LESSONS_LEARNED.md from coffee_mathematics build  
**Objective**: Implement fixes to prevent voiceover sync issues, module import errors, and quality control failures

---

## Table of Contents

1. [Overview](#overview)
2. [Priority Matrix](#priority-matrix)
3. [File-by-File Changes](#file-by-file-changes)
4. [New Files to Create](#new-files-to-create)
5. [Testing Strategy](#testing-strategy)
6. [Rollout Plan](#rollout-plan)
7. [Success Criteria](#success-criteria)

---

## Overview

### What Went Wrong (Summary)

The first production build succeeded architecturally but failed on execution quality:
- **Module imports**: Scene 4 used `manimvoiceoverplus` instead of `manim_voiceover_plus`
- **Voiceover sync**: ~30% of video had no audio (animations longer than narration)
- **Quality control**: Declared success without verifying output quality

### Root Causes

1. **System prompt lacked enforcement detail** - Rules stated but not explained with consequences
2. **Build script had no validation gates** - Scenes marked "built" without import/sync checks
3. **No mandatory QC before completion** - Process success ≠ output quality

### Fix Strategy

**Three-tier approach**:
1. **Prevention** (system prompt improvements) - Make it hard to generate bad code
2. **Detection** (build script validation) - Catch errors before rendering
3. **Verification** (mandatory QC) - Never declare success without proof

---

## Priority Matrix

| Priority | Component | Impact | Effort | Risk if Skipped |
|----------|-----------|--------|--------|-----------------|
| **P0** | QC Script | High | Medium | 🔴 Will ship broken videos |
| **P0** | System Prompt - Sync Section | High | Low | 🔴 Sync issues will recur |
| **P0** | System Prompt - Import Section | High | Low | 🔴 Import errors will recur |
| **P1** | Build Script - Import Validation | High | Medium | 🟡 Errors caught late |
| **P1** | Build Script - Sync Validation | Medium | Low | 🟡 Warnings missed |
| **P1** | Scene Template (strict) | Medium | Medium | 🟡 Reference missing |
| **P2** | Anti-patterns Section | Medium | Low | 🟢 Agent may still make mistakes |
| **P2** | Audio Duration Checks | Medium | Medium | 🟢 QC script covers this |
| **P3** | Silence Detection | Low | High | 🟢 Nice to have |

**P0 = Must have before next build**  
**P1 = Should have within this session**  
**P2 = Can defer to future**  
**P3 = Optional enhancement**

---

## File-by-File Changes

### 1. system_prompt.md

**Current Status**: 454 lines, basic templates, high-level rules  
**Target Status**: ~600 lines, detailed explanations, anti-patterns, worked examples

#### Change 1.1: Add Import Name Emphasis (After Line 18)

**Location**: Right after "You are an AI agent..." introduction  
**Size**: ~25 lines  
**Why**: Prevent `manimvoiceoverplus` import errors

```markdown
## ⚠️  CRITICAL: Python Module Naming Convention

**The manim-voiceover-plus package uses DIFFERENT names for pip vs Python imports:**

| Context | Name | Example |
|---------|------|---------|
| pip install | `manim-voiceover-plus` | `pip install manim-voiceover-plus` |
| Python import | `manim_voiceover_plus` | `from manim_voiceover_plus import VoiceoverScene` |

### Common Mistakes (DO NOT MAKE THESE):

❌ **WRONG** - No separators:
```python
import manimvoiceoverplus  # ModuleNotFoundError!
from manimvoiceoverplus import VoiceoverScene
```

❌ **WRONG** - Hyphens (invalid Python syntax):
```python
from manim-voiceover-plus import VoiceoverScene  # SyntaxError!
```

✅ **CORRECT** - Underscores:
```python
import manim_voiceover_plus.services.base as base
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from manim_voiceover_plus.services.gtts import GTTSService
```

**If you generate incorrect import names, the scene will fail with:**
```
ModuleNotFoundError: No module named 'manimvoiceoverplus'
```
```

#### Change 1.2: Expand Tracker Duration Section (Replace Lines 180-195)

**Location**: In the "Phase: build_scenes" section  
**Size**: Replace ~15 lines with ~80 lines  
**Why**: Explain voiceover sync in detail with consequences

```markdown
## Voiceover-Animation Synchronization (CRITICAL FOR QUALITY)

### The Problem

If animations run longer than the voiceover audio, the video will have **silent dead air** - 
this is the #1 quality issue that causes user complaints.

### The Solution: tracker.duration

The `tracker` object from `with self.voiceover(text=...) as tracker:` provides:
- `tracker.duration`: Exact length of the voiceover audio in seconds

**RULE**: ALL animations inside the voiceover block MUST complete within `tracker.duration`

### ✅ CORRECT Pattern - Time Budget Approach

```python
with self.voiceover(text=SCRIPT["intro"]) as tracker:
    # Example: tracker.duration = 14.5 seconds
    
    # Allocate percentages (must sum to ≤ 100%)
    title = Text("Coffee Science", font_size=48)
    title.move_to(UP * 3.8)
    self.play(Write(title), run_time=tracker.duration * 0.30)  # 30% = 4.35s
    
    circle = Circle(radius=1.5, color=BLUE)
    self.play(FadeIn(circle), run_time=tracker.duration * 0.40)  # 40% = 5.80s
    
    # Reserve buffer for natural pacing
    self.wait(tracker.duration * 0.30)  # 30% = 4.35s
    
    # Total: 30% + 40% + 30% = 100% = 14.5s ✅ Perfect sync!
```

### ❌ WRONG Pattern - Fixed Times (CAUSES DEAD AIR)

```python
with self.voiceover(text=SCRIPT["intro"]) as tracker:
    # tracker.duration = 14.5 seconds
    
    title = Text("Coffee Science", font_size=48)
    self.play(Write(title), run_time=5)  # Fixed! ❌
    
    circle = Circle(radius=1.5)
    self.play(FadeIn(circle), run_time=8)  # Fixed! ❌
    
    self.wait(2)  # Fixed! ❌
    
    # Total: 5 + 8 + 2 = 15 seconds
    # Voiceover ends at 14.5s, but video continues to 15s
    # Result: 0.5 seconds of SILENT VIDEO ❌
```

### What Happens When Timing is Wrong

**Scenario**: Voiceover is 20 seconds, animations total 25 seconds

```
Time:     0s -------- 10s -------- 20s -------- 25s
          |           |            |            |
Audio:    [========== VOICEOVER ===========]
Video:    [============ ANIMATIONS ================]
                                   ^^^^ SILENT ^^^^
```

**User experience**: Video plays normally for 20s, then continues in awkward silence for 5s. 
This looks broken and unprofessional.

### Safety Pattern: Use min() to Cap Times

If you want animations to have a minimum aesthetic quality but still respect tracker.duration:

```python
with self.voiceover(text=SCRIPT["intro"]) as tracker:
    # This ensures animations look good even if narration is very short
    title_time = min(3.0, tracker.duration * 0.35)
    self.play(Write(title), run_time=title_time)
    
    # If tracker.duration = 20s: min(3.0, 7.0) = 3.0s (use full 3s)
    # If tracker.duration = 5s:  min(3.0, 1.75) = 1.75s (speed up to fit)
```

### Time Tracking Pattern (RECOMMENDED)

For complex scenes with many animations:

```python
with self.voiceover(text=SCRIPT["scene_key"]) as tracker:
    time_used = 0
    
    # Animation 1
    anim_time = min(2.5, tracker.duration * 0.25)
    self.play(Write(title), run_time=anim_time)
    time_used += anim_time
    
    # Animation 2
    anim_time = min(3.0, tracker.duration * 0.30)
    self.play(FadeIn(content), run_time=anim_time)
    time_used += anim_time
    
    # Animation 3
    anim_time = min(2.0, tracker.duration * 0.20)
    self.play(Transform(obj1, obj2), run_time=anim_time)
    time_used += anim_time
    
    # Fill remaining time (CRITICAL - prevents early exit)
    remaining = max(0, tracker.duration - time_used)
    if remaining > 0:
        self.wait(remaining)
    
    # This guarantees total time exactly matches tracker.duration ✅
```

### Validation (What the Build System Checks)

After you generate a scene, the build system will:
1. Extract audio from rendered video
2. Compare audio duration to video duration
3. **Fail the build** if audio < 90% of video duration

This catches sync violations automatically.
```

#### Change 1.3: Add Anti-Patterns Section (After line 420, before "Example Outputs")

**Location**: New section before example outputs  
**Size**: ~60 lines  
**Why**: Show what NOT to do with explanations

```markdown
## ❌ ANTI-PATTERNS - Things You Must NEVER Do

These are common mistakes that WILL cause build failures. Learn them to avoid them.

### Anti-Pattern #1: Hardcoded Narration Text

❌ **WRONG**:
```python
with self.voiceover(text="This is my narration text here...") as tracker:
    # animations...
```

✅ **CORRECT**:
```python
with self.voiceover(text=SCRIPT["scene_key"]) as tracker:
    # animations...
```

**Why this matters**: 
- Narration belongs in `narration_script.py` for centralized editing
- If narration is hardcoded, the client can't update it without regenerating scenes
- The build system will REJECT scenes with hardcoded narration

**How to avoid**: ALWAYS use `SCRIPT["key"]`, never write narration text directly

---

### Anti-Pattern #2: Fixed Animation Times Inside Voiceover

❌ **WRONG**:
```python
with self.voiceover(text=SCRIPT["intro"]) as tracker:
    self.play(Write(title), run_time=3)  # Fixed time!
    self.play(FadeIn(obj), run_time=5)   # Fixed time!
```

✅ **CORRECT**:
```python
with self.voiceover(text=SCRIPT["intro"]) as tracker:
    self.play(Write(title), run_time=tracker.duration * 0.30)
    self.play(FadeIn(obj), run_time=tracker.duration * 0.50)
```

**Why this matters**:
- Fixed times cause desync when narration duration changes
- Creates silent gaps or cuts off narration
- Build QC will flag audio/video duration mismatches

**How to avoid**: ALWAYS use `tracker.duration * fraction` or `min(max_val, tracker.duration * fraction)`

---

### Anti-Pattern #3: Wrong Module Import Name

❌ **WRONG**:
```python
from manimvoiceoverplus import VoiceoverScene  # No separators
from manim-voiceover-plus import VoiceoverScene  # Hyphens (syntax error)
```

✅ **CORRECT**:
```python
from manim_voiceover_plus import VoiceoverScene  # Underscores
```

**Why this matters**:
- Python module names MUST use underscores (or no separators)
- Hyphens are invalid Python syntax
- Will cause `ModuleNotFoundError` and build failure

**How to avoid**: Copy imports from the template EXACTLY - use underscores

---

### Anti-Pattern #4: Skipping safe_position() After .next_to()

❌ **WRONG**:
```python
label = Text("Label")
label.next_to(equation, DOWN, buff=1.0)
self.play(FadeIn(label))  # May be off-screen!
```

✅ **CORRECT**:
```python
label = Text("Label")
label.next_to(equation, DOWN, buff=1.0)
safe_position(label)  # Ensures it's visible
self.play(FadeIn(label))
```

**Why this matters**:
- `.next_to()` can place objects outside the visible frame
- Users won't see the text/object
- Looks like a rendering bug

**How to avoid**: ALWAYS call `safe_position()` after using `.next_to()`

---

### Anti-Pattern #5: Using .to_edge(UP) for Titles

❌ **WRONG**:
```python
title = Text("My Title", font_size=48)
title.to_edge(UP)  # Places at y=5.0, text top may be at y=5.5
```

✅ **CORRECT**:
```python
title = Text("My Title", font_size=48)
title.move_to(UP * 3.8)  # Safe positioning, top will be at ~y=4.3
```

**Why this matters**:
- `.to_edge(UP)` positions the CENTER at the edge
- With large font sizes, the TOP extends beyond the frame
- Text gets clipped/cut off at the top

**How to avoid**: NEVER use `.to_edge(UP)` - always use `.move_to(UP * 3.8)` or similar

---

**Remember**: The build system validates against these patterns. If detected, your scene 
will be rejected and you'll need to regenerate it.
```

#### Change 1.4: Add Validation Notice (After line 450, before completion)

**Location**: End of build_scenes section  
**Size**: ~15 lines

```markdown
## Post-Generation Validation

After you generate each scene file, the build system will automatically verify:

1. **Import validation**: `python3 -c "import scene_XX"` must succeed
   - Catches module naming errors
   - Catches syntax errors
   - Catches missing imports

2. **Narration validation**: Scene must NOT contain `voiceover(text="...hardcoded...")`
   - Ensures SCRIPT dictionary is used
   - Prevents narration divergence

3. **Sync validation**: Scene should use `tracker.duration` in run_time parameters
   - Warning if not found (doesn't fail, but flags for review)

4. **Audio validation**: After rendering, audio duration must be ≥90% of video duration
   - Catches timing desync
   - Prevents silent gaps

**If validation fails**: The build system will request regeneration with error details.
You'll see the specific issue and can fix it in the next iteration.
```

**Total system_prompt.md changes**: +~250 lines (454 → ~700 lines)

---

### 2. build_video.sh

**Current Status**: ~350 lines, basic flow, minimal validation  
**Target Status**: ~500 lines, comprehensive validation at each gate

#### Change 2.1: Add Validation Functions (After line 115, after helper functions)

**Location**: After `backup_state()` function, before phase handlers  
**Size**: ~80 lines

```bash
# ══════════════════════════════════════════════════════════════════
# Validation Functions
# ══════════════════════════════════════════════════════════════════

validate_scene_imports() {
    local scene_file="$1"
    
    echo "Validating imports in $scene_file..." | tee -a "$LOG_FILE"
    
    cd "$PROJECT_DIR"
    python3 -c "
import sys
sys.path.insert(0, '.')
try:
    module_name = '${scene_file%.py}'
    __import__(module_name)
    print('✅ Imports valid')
    exit(0)
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
except SyntaxError as e:
    print(f'❌ Syntax error: {e}')
    exit(1)
except Exception as e:
    print(f'❌ Other error: {e}')
    exit(1)
" 2>&1 | tee -a "$LOG_FILE"
    
    local result=${PIPESTATUS[0]}
    if [[ $result -ne 0 ]]; then
        echo "ERROR: Scene has import/syntax errors" | tee -a "$LOG_FILE"
        return 1
    fi
    
    return 0
}

validate_voiceover_sync() {
    local scene_file="$1"
    
    echo "Validating voiceover sync in $scene_file..." | tee -a "$LOG_FILE"
    
    # Check for hardcoded narration text
    if grep -q 'voiceover(text="' "$scene_file"; then
        echo "❌ ERROR: Scene uses hardcoded narration text instead of SCRIPT dictionary" | tee -a "$LOG_FILE"
        echo "   Found at:" | tee -a "$LOG_FILE"
        grep -n 'voiceover(text="' "$scene_file" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # Check for voiceover(text=f"...") pattern (f-strings)
    if grep -q 'voiceover(text=f"' "$scene_file"; then
        echo "❌ ERROR: Scene uses f-string narration instead of SCRIPT dictionary" | tee -a "$LOG_FILE"
        echo "   Found at:" | tee -a "$LOG_FILE"
        grep -n 'voiceover(text=f"' "$scene_file" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # Check for tracker.duration usage in run_time
    if ! grep -q 'tracker\.duration' "$scene_file"; then
        echo "⚠️  WARNING: Scene may not use tracker.duration for synchronization" | tee -a "$LOG_FILE"
        echo "   This can cause voiceover/animation desync" | tee -a "$LOG_FILE"
        # Don't fail, but warn
    fi
    
    echo "✅ Voiceover sync checks passed" | tee -a "$LOG_FILE"
    return 0
}
```

#### Change 2.2: Update build_scenes Handler (Replace lines ~180-220)

**Location**: The `handle_build_scenes()` function  
**Size**: Modify existing function, add ~30 lines

**Current structure**:
```bash
handle_build_scenes() {
    # Get current scene
    # Invoke agent
    # Render with manim
    # Update state
}
```

**New structure**:
```bash
handle_build_scenes() {
    # Get current scene
    scene_id=$(python3 -c "...")
    scene_file="scene_${scene_id}.py"
    
    # Invoke agent to generate scene
    invoke_agent "build_scenes" "$run"
    
    # VALIDATION GATE 1: Check imports
    if ! validate_scene_imports "$scene_file"; then
        echo "Import validation failed. Logging error for agent to fix..." | tee -a "$LOG_FILE"
        python3 <<PYEOF
import json
with open('$STATE_FILE', 'r') as f:
    state = json.load(f)
state['errors'].append('Scene $scene_id failed import validation. Check module names (use manim_voiceover_plus with underscores).')
state['flags']['needs_human_review'] = False  # Allow auto-retry
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
PYEOF
        return 1
    fi
    
    # VALIDATION GATE 2: Check voiceover sync patterns
    if ! validate_voiceover_sync "$scene_file"; then
        echo "Sync validation failed. Logging error for agent to fix..." | tee -a "$LOG_FILE"
        python3 <<PYEOF
import json
with open('$STATE_FILE', 'r') as f:
    state = json.load(f)
state['errors'].append('Scene $scene_id uses hardcoded narration text. Must use SCRIPT dictionary.')
state['flags']['needs_human_review'] = False  # Allow auto-retry
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
PYEOF
        return 1
    fi
    
    # Render with gTTS for testing (existing code continues here)
    # ...rest of existing handler...
}
```

#### Change 2.3: Add Audio Verification to final_render Handler (Modify lines ~250-280)

**Location**: In `handle_final_render()` function, after each scene renders  
**Size**: Add ~15 lines per scene render loop

```bash
handle_final_render() {
    # ...existing ElevenLabs setup...
    
    for scene in scene_01_intro scene_02_extraction scene_03_factors scene_04_optimization; do
        scene_file="${scene}.py"
        scene_class=$(# ...existing class extraction...)
        
        # Render with ElevenLabs
        manim render "$scene_file" "$scene_class" -qh || {
            # ...existing error handling...
        }
        
        # NEW: Verify audio in rendered output
        rendered_video="media/videos/${scene}/1440p60/${scene_class}.mp4"
        if [[ -f "$rendered_video" ]]; then
            echo "Checking audio in $rendered_video..." | tee -a "$LOG_FILE"
            
            video_dur=$(ffprobe "$rendered_video" 2>&1 | grep "Duration:" | head -1 | awk '{print $2}' | tr -d ',')
            audio_check=$(ffprobe "$rendered_video" 2>&1 | grep "Stream.*Audio")
            
            if [[ -z "$audio_check" ]]; then
                echo "⚠️  WARNING: No audio stream found in $scene" | tee -a "$LOG_FILE"
            else
                echo "✅ Audio present: $video_dur" | tee -a "$LOG_FILE"
            fi
        fi
    done
    
    # ...rest of existing handler...
}
```

#### Change 2.4: Add QC to assemble Handler (Modify lines ~290-310)

**Location**: In `handle_assemble()`, after final assembly (FFmpeg concat *filter* + re-encode)  
**Size**: Add ~20 lines

```bash
handle_assemble() {
    # ...existing assembly code (concat filter + re-encode)...
    
    # NEW: Run quality control
    echo "Running quality control on final video..." | tee -a "$LOG_FILE"
    
    if [[ -x "${SCRIPT_DIR}/qc_final_video.sh" ]]; then
        "${SCRIPT_DIR}/qc_final_video.sh" "$PROJECT_DIR/final_video.mp4" "$PROJECT_DIR" || {
            echo "❌ QC FAILED! Video has quality issues." | tee -a "$LOG_FILE"
            python3 <<PYEOF
import json
with open('$STATE_FILE', 'r') as f:
    state = json.load(f)
state['phase'] = 'error'
state['errors'].append('Final video failed quality control - check audio/video sync')
state['flags']['needs_human_review'] = True
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
PYEOF
            return 1
        }
    else
        echo "⚠️  WARNING: qc_final_video.sh not found or not executable. Skipping QC." | tee -a "$LOG_FILE"
        echo "   This is DANGEROUS - video may have quality issues!" | tee -a "$LOG_FILE"
    fi
    
    # Only advance to complete if QC passes
    echo "✅ QC passed! Advancing to complete phase." | tee -a "$LOG_FILE"
    # ...existing state update to complete...
}
```

**Total build_video.sh changes**: +~150 lines (350 → ~500 lines)

---

### 3. README.md

**Current Status**: Basic usage instructions  
**Target Status**: Includes QC requirements and validation info

#### Change 3.1: Add Quality Control Section (After "Usage" section)

**Location**: After build instructions, before "Project Structure"  
**Size**: ~40 lines

```markdown
## Quality Control

The build system includes **mandatory quality control** checks before declaring a video complete.

### Automatic Validation

Each scene is validated for:

1. **Import correctness** - No `ModuleNotFoundError` or syntax errors
2. **Narration source** - Must use `SCRIPT` dictionary, not hardcoded text  
3. **Sync patterns** - Should use `tracker.duration` for animation timing
4. **Audio presence** - Rendered videos must have audio tracks

### Final Video QC

Before marking a project as complete, the system runs `qc_final_video.sh` which checks:

- ✅ Video file exists and has non-zero size
- ✅ Audio track is present and covers ≥95% of video duration
- ✅ No silent gaps longer than 3 seconds
- ✅ Each scene has audio (per-scene validation)

**If QC fails**, the build is marked as `error` and requires human review.

### Manual Verification (Recommended)

Even with automatic QC, you should:

1. **Play the first 10 seconds** - Verify voiceover is audible
2. **Play the last 10 seconds** - Verify voiceover continues to end
3. **Scrub to 3 random points** - Verify continuous narration

**Never trust "process completed" = "quality achieved"**
```

---

## New Files to Create

### File 1: qc_final_video.sh

**Location**: `/Users/velocityworks/IdeaProjects/flaming-horse/incremental_builder/qc_final_video.sh`  
**Size**: ~200 lines  
**Priority**: P0 (must have before next build)  
**Purpose**: Mandatory quality control before declaring video complete

**Features**:
- Extracts audio track from final video
- Compares audio duration to video duration
- Checks for silent gaps using ffmpeg's silencedetect filter
- Validates audio codec
- Per-scene audio verification
- Exit code 0 = pass, 1 = fail

**Source**: Full implementation in LESSONS_LEARNED.md, "Quality Control Failures" section

**Permissions**: `chmod +x qc_final_video.sh`

---

### File 2: scene_template_strict.py

**Location**: `/Users/velocityworks/IdeaProjects/flaming-horse/incremental_builder/scene_template_strict.py`  
**Size**: ~150 lines  
**Priority**: P1 (should have this session)  
**Purpose**: Reference template with ALL best practices for agent to reference

**Features**:
- Complete Python 3.13 compatibility patch
- Correct module imports (with emphasis on underscores)
- Safe positioning helper function
- TTS backend selection (gTTS/ElevenLabs toggle)
- Complete voiceover sync pattern with time tracking
- Extensive comments explaining each section

**Source**: Full implementation in LESSONS_LEARNED.md, "Required System Updates" section

**Usage**: Referenced in system_prompt.md as the gold standard

---

### File 3: validate_scaffold.sh Updates

**Location**: Modify existing `/Users/velocityworks/IdeaProjects/flaming-horse/incremental_builder/validate_scaffold.sh`  
**Size**: Add ~20 lines  
**Priority**: P1  
**Purpose**: Add checks for QC script and reference docs

**New checks to add**:
```bash
# Check QC script exists and is executable
if [[ ! -x "./qc_final_video.sh" ]]; then
    echo "❌ qc_final_video.sh missing or not executable"
    ALL_GOOD=false
else
    echo "✅ qc_final_video.sh exists and is executable"
fi

# Check reference docs are accessible
echo "Checking reference docs..."
for doc in "${REFERENCE_DOCS[@]}"; do
    if [[ ! -f "$doc" ]]; then
        echo "❌ Missing reference doc: $doc"
        ALL_GOOD=false
    else
        echo "✅ Found: $(basename $doc)"
    fi
done

# Check scene template exists
if [[ ! -f "./scene_template_strict.py" ]]; then
    echo "⚠️  scene_template_strict.py not found (recommended)"
fi
```

---

## Testing Strategy

### Phase 1: Unit Testing (Individual Components)

**Test each updated component in isolation**:

1. **System Prompt**: 
   - Create test project with intentional errors (wrong imports, hardcoded text)
   - Verify agent generates correct code after reading updated prompt
   - Check that examples are clear and unambiguous

2. **Validation Functions**:
   - Create test scenes with known issues:
     - `test_bad_import.py` with `from manimvoiceoverplus import VoiceoverScene`
     - `test_hardcoded.py` with `voiceover(text="hardcoded...")`
     - `test_good.py` with correct patterns
   - Run validation functions, verify correct pass/fail

3. **QC Script**:
   - Create test videos with known issues:
     - Video with no audio track
     - Video with audio < 50% of duration
     - Video with correct audio coverage
   - Run QC script, verify correct detection

### Phase 2: Integration Testing (Full Build)

**Run a complete build with a simple test project**:

```bash
# Create test project
./new_project.sh test_validation ~/test_projects

# Use a VERY simple topic to minimize rendering time
# Topic: "Why is the sky blue?" (30 second video, 2 scenes)

# Run build
./build_video.sh ~/test_projects/test_validation

# Expected outcome:
# - Should complete in < 30 minutes
# - All validation gates should pass
# - QC should pass
# - Video should have continuous audio
```

### Phase 3: Regression Testing (Re-run Coffee Build)

**Verify the updated system can build the coffee video without issues**:

```bash
# Clean slate
rm -rf ~/manim_projects/coffee_mathematics_v2

# Run new_project.sh with same topic
./new_project.sh coffee_mathematics_v2 ~/manim_projects

# Edit topic in state to match original
# Run build
./build_video.sh ~/manim_projects/coffee_mathematics_v2

# Expected outcome:
# - Should complete WITHOUT manual intervention
# - All scenes should pass validation on first try
# - Final QC should pass
# - Video should match quality of manually-fixed original
```

### Success Criteria for Testing

A test PASSES if:
- ✅ Build completes without human intervention
- ✅ All validation gates pass on first attempt
- ✅ QC script gives exit code 0
- ✅ Manual spot-check confirms continuous audio
- ✅ No errors in build.log

A test FAILS if:
- ❌ Requires manual intervention (needs_human_review = True)
- ❌ Validation gates fail repeatedly (>2 retries per scene)
- ❌ QC script gives exit code 1
- ❌ Manual verification finds silent gaps
- ❌ Build log shows repeated errors

---

## Rollout Plan

### Step 1: Implement P0 Changes (30 minutes)

**Order of operations**:

1. Create `qc_final_video.sh` (10 min)
   - Copy from LESSONS_LEARNED.md
   - Make executable
   - Test with existing coffee video

2. Update `system_prompt.md` - Import section (5 min)
   - Add module naming emphasis
   - Copy from this plan

3. Update `system_prompt.md` - Sync section (10 min)
   - Replace existing section
   - Add worked examples
   - Copy from this plan

4. Update `build_video.sh` - Add QC call (5 min)
   - Modify assemble handler
   - Copy from this plan

**Validation**: Run validate_scaffold.sh, should show all files present

---

### Step 2: Implement P1 Changes (45 minutes)

**Order of operations**:

1. Create `scene_template_strict.py` (10 min)
   - Copy from LESSONS_LEARNED.md
   - Verify imports work

2. Update `system_prompt.md` - Anti-patterns (10 min)
   - Add new section
   - Copy from this plan

3. Add validation functions to `build_video.sh` (15 min)
   - Add validate_scene_imports()
   - Add validate_voiceover_sync()
   - Copy from this plan

4. Update build_scenes handler (10 min)
   - Add validation gate calls
   - Copy from this plan

**Validation**: Run unit tests on validation functions

---

### Step 3: Testing (60 minutes)

1. Unit test QC script (10 min)
2. Unit test validation functions (10 min)  
3. Integration test with simple project (30 min)
4. Document results (10 min)

---

### Step 4: P2 Changes (Optional, if time permits)

1. Update `validate_scaffold.sh` (5 min)
2. Update `README.md` with QC section (10 min)

---

## Success Criteria

### For This Update Session

**Minimum viable success** (must achieve):
- ✅ P0 changes implemented (QC script + critical system prompt updates)
- ✅ QC script tested and working on coffee video
- ✅ validate_scaffold.sh passes

**Preferred success** (should achieve):
- ✅ P1 changes implemented (validation functions + template)
- ✅ Unit tests pass for all new components
- ✅ Integration test with simple project succeeds

**Stretch success** (nice to have):
- ✅ P2 changes implemented
- ✅ Regression test (coffee rebuild) succeeds autonomously
- ✅ Documentation fully updated

### For Next Production Build

The **true test** of success is the next production video build:

**Success = Build completes WITHOUT**:
- ❌ Module import errors
- ❌ Voiceover sync issues (silent gaps)
- ❌ Manual intervention for quality fixes
- ❌ False "complete" declarations

**AND with**:
- ✅ All validation gates passing on first attempt
- ✅ QC script returning exit 0
- ✅ Manual verification confirming continuous audio
- ✅ Build log showing clean run

---

## Risk Assessment

### High Risk Items

1. **QC script may have false positives**
   - *Mitigation*: Test on known-good video first
   - *Fallback*: Add `--skip-qc` flag for emergencies

2. **Validation functions may be too strict**
   - *Mitigation*: Start with warnings, not hard failures
   - *Fallback*: Allow override via state flag

3. **Agent may not adapt to new prompt patterns**
   - *Mitigation*: Test with simple project first
   - *Fallback*: Iterate on prompt wording based on results

### Medium Risk Items

1. **Time budget: May not complete P1 in session**
   - *Mitigation*: Prioritize ruthlessly, P0 first
   - *Fallback*: Document what's incomplete for next session

2. **Testing may reveal new issues**
   - *Mitigation*: Budget 60min for testing
   - *Fallback*: Document new issues, don't try to fix in this session

---

## Estimated Time

| Phase | Optimistic | Realistic | Pessimistic |
|-------|-----------|-----------|-------------|
| P0 Implementation | 20 min | 30 min | 45 min |
| P1 Implementation | 30 min | 45 min | 75 min |
| Testing | 30 min | 60 min | 90 min |
| P2 Implementation | 10 min | 15 min | 30 min |
| **Total** | **90 min** | **150 min** | **240 min** |

**Recommended allocation**: 2.5 hours (realistic track)

---

## Rollback Plan

If updates cause issues:

1. **Git is not being used** (per environment context), so manual rollback:
   - Keep backup copies: `system_prompt.md.backup`, `build_video.sh.backup`
   - Document all changes in this plan for easy reversal

2. **Incremental rollback**:
   - If QC script causes issues → disable it in assemble handler
   - If validation too strict → comment out validation gates
   - If prompt changes confuse agent → revert to original wording

3. **Nuclear option**:
   - Restore all `.backup` files
   - Delete new files (qc_final_video.sh, scene_template_strict.py)
   - System returns to pre-update state

---

## Next Steps After Implementation

1. **Run first production build with new system**
   - Choose a simple topic (60-90 second video)
   - Monitor closely for validation effectiveness
   - Document any new issues found

2. **Iterate on system prompt**
   - Based on agent behavior in first build
   - Add more examples if needed
   - Refine anti-patterns section

3. **Enhance QC script**
   - Add more sophisticated checks based on real failures
   - Potentially add visual quality checks (scene transitions, etc.)

4. **Consider additional tooling**:
   - Pre-flight check script (runs before build starts)
   - Post-render preview generator (thumbnails of each scene)
   - Metrics dashboard (track build success rate over time)

---

## Open Questions for Review

1. **QC script strictness**: Should audio coverage threshold be 95% or 90%?
   - Recommendation: Start at 90%, increase if we see issues

2. **Validation retry limit**: How many times should validation auto-retry before needs_human_review?
   - Recommendation: 2 retries per scene (3 attempts total)

3. **Scene template reference**: Should system_prompt.md LINK to template or EMBED it?
   - Recommendation: Embed key sections, link to full file

4. **P2 priority**: Should we do P2 in this session or defer?
   - Recommendation: Do if time permits after P1 + testing

---

## Appendix: Quick Reference

### Files to Modify

1. `system_prompt.md` (~250 lines added)
2. `build_video.sh` (~150 lines added)
3. `README.md` (~40 lines added)
4. `validate_scaffold.sh` (~20 lines added)

### Files to Create

1. `qc_final_video.sh` (~200 lines)
2. `scene_template_strict.py` (~150 lines)

### Total LOC Impact

- **Added**: ~810 lines
- **Modified**: ~50 lines
- **Deleted**: ~15 lines (old prompt sections)
- **Net**: +~845 lines

---

**Status**: Ready for review  
**Next Action**: Await Big D's approval to proceed with implementation  
**Questions**: See "Open Questions for Review" section above
