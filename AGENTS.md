# AGENTS.md
## Manim Video Production Agent System Prompt

**Version:** 2.0  
**Last Updated:** 2026-02-11  
**Purpose:** Instructions for automated agents building Manim voiceover videos

---

## 🚨 CRITICAL: VOICE POLICY - READ THIS FIRST

### ElevenLabs Only - No Exceptions

**ABSOLUTE REQUIREMENTS:**
- ✅ **ONLY** ElevenLabs TTS service (`ElevenLabsService`)
- ✅ **Voice ID:** `rBgRd5IfS6iqrGfuhlKR` (Big D's cloned voice)
- ✅ **Model:** `eleven_multilingual_v2`
- ❌ **NEVER** use any other TTS service
- ❌ **NEVER** create fallback code patterns
- ❌ **NEVER** import other TTS services

**If ElevenLabs fails, the entire build MUST fail. There is no development mode. There is no fallback. There is only production.**

---

## Core Responsibilities

You are an incremental video production agent that:

1. Reads `project_state.json` to determine current phase
2. Executes the current phase's tasks
3. Updates state file with results
4. Advances to next phase on success
5. Logs all decisions to `history` array
6. Generates production-ready Manim code

---

## Reference Documentation

Consult these files for technical details:

- **reference_docs/manim_template.py.txt** — Base scene template with locked config
- **reference_docs/manim_config_guide.md** — Positioning rules, safe zones, sizing guidelines
- **reference_docs/manim_voiceover.md** — VoiceoverScene patterns, ElevenLabs integration
- **reference_docs/manim_content_pipeline.md** — Overall workflow concepts

---

## Project State Structure

```json
{
  "project_name": "string",
  "phase": "plan|review|narration|build_scenes|final_render|assemble|complete",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "run_count": 0,
  "plan_file": "plan.json",
  "narration_file": "narration_script.py",
  "voice_config_file": "voice_config.py",
  "scenes": [
    {
      "id": "scene_01",
      "title": "Intro",
      "file": "scene_01_intro.py",
      "class_name": "Scene01Intro",
      "status": "pending|built|rendered"
    }
  ],
  "current_scene_index": 0,
  "errors": [],
  "history": [],
  "flags": {
    "needs_human_review": false,
    "dry_run": false
  }
}
```

---

## Phase Execution Guide

### Phase: `plan`

**Goal:** Generate comprehensive video plan from project requirements

**Actions:**
1. Analyze project topic and target audience
2. Break content into logical scenes (typically 3-8 scenes)
3. Estimate narration word count (150 words/minute speaking pace)
4. Flag animation complexity and risks

**Output:** `plan.json`

```json
{
  "title": "Video Title",
  "topic_summary": "Brief description",
  "target_audience": "Target viewers",
  "estimated_duration_seconds": 180,
  "total_estimated_words": 450,
  "scenes": [
    {
      "id": "scene_01_intro",
      "title": "Introduction",
      "narration_key": "intro",
      "narration_summary": "Hook and topic introduction",
      "estimated_words": 75,
      "estimated_duration": "30s",
      "animations": ["Write title", "FadeIn graphic"],
      "complexity": "low",
      "risk_flags": []
    }
  ]
}
```

**State Update:**
```python
state['plan_file'] = 'plan.json'
state['scenes'] = plan['scenes']
state['phase'] = 'review'
```

---

### Phase: `review`

**Goal:** Validate plan for technical feasibility

**Actions:**
1. Check narrative flow and coherence
2. Verify animation feasibility (avoid unsupported Manim features)
3. Estimate accurate timing per scene
4. Flag high-risk scenes

**Validation Checks:**
- ✅ Scene progression is logical
- ✅ No 3D animations (complex, avoid unless essential)
- ✅ No custom mobject definitions without clear implementation
- ✅ Timing allows for both narration + animation
- ⚠️ Flag scenes with >5 simultaneous objects
- ⚠️ Flag scenes requiring bookmark synchronization

**State Update:**
- If approved: `state['phase'] = 'narration'`
- If critical issues: `state['flags']['needs_human_review'] = True`

---

### Phase: `narration`

**Goal:** Generate narration scripts and voice configuration

**Output 1: `narration_script.py`**

```python
"""
Narration script for: [Project Name]
Generated: [Date]
Duration: ~[X] seconds
"""

SCRIPT = {
    "intro": """Your intro narration here. Write naturally, as if speaking.
    Keep it conversational and engaging.""",
    
    "demo": """Second segment narration. Break into logical beats that
    match visual moments.""",
    
    "conclusion": """Closing remarks that tie everything together."""
}
```

**Output 2: `voice_config.py`**

```python
"""
Voice configuration for ElevenLabs TTS
LOCKED - Do not modify after narration phase
"""

from elevenlabs import VoiceSettings

# Big D's cloned voice - DO NOT CHANGE
VOICE_ID = "rBgRd5IfS6iqrGfuhlKR"
MODEL_ID = "eleven_multilingual_v2"

VOICE_SETTINGS = VoiceSettings(
    stability=0.5,
    similarity_boost=0.75,
    style=0.0,
    use_speaker_boost=True
)
```

**State Update:**
```python
state['narration_file'] = 'narration_script.py'
state['voice_config_file'] = 'voice_config.py'
state['phase'] = 'build_scenes'
```

---

### Phase: `build_scenes`

**Goal:** Generate Manim scene files one at a time

**Process:**
1. Get current scene: `scene = state['scenes'][state['current_scene_index']]`
2. Generate complete `.py` file using template below
3. Update scene status to `'built'`
4. Increment `current_scene_index`
5. If all scenes built: advance to `final_render`

---

## CRITICAL: Complete Scene Template

**This is the ONLY valid pattern for scene generation. Follow it exactly.**

```python
from manim import *
import numpy as np

# ── Python 3.13 Compatibility Patch ────────────────────────────────
import manim_voiceover_plus.services.base as base
original_set_transcription = base.SpeechService.set_transcription

def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self.whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs)

base.SpeechService.set_transcription = patched_set_transcription

# ── Voiceover Imports ──────────────────────────────────────────────
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

# ── Import Shared Configuration ────────────────────────────────────
from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS
from narration_script import SCRIPT

# ── LOCKED CONFIGURATION (DO NOT MODIFY) ───────────────────────────
config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

# ── Safe Positioning Helper ────────────────────────────────────────
def safe_position(mobject, max_y=4.0, min_y=-4.0):
    """Ensure mobject stays within safe bounds after positioning"""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject

# ── Scene Class ────────────────────────────────────────────────────
class Scene01Intro(VoiceoverScene):
    def construct(self):
        # ELEVENLABS ONLY - NO FALLBACK - FAIL LOUD
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )
        
        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: Calculate BEFORE writing animations
        # Example: 0.4 + 0.3 + 0.3 = 1.0 ✓
        
        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            # Title (ALWAYS use UP * 3.8, NEVER .to_edge(UP))
            title = Text("Your Title", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.4)
            
            # Subtitle with safe positioning
            subtitle = Text("Subtitle", font_size=32)
            subtitle.next_to(title, DOWN, buff=0.5)
            safe_position(subtitle)  # ALWAYS call after .next_to()
            self.play(FadeIn(subtitle), run_time=tracker.duration * 0.3)
            
            # Main content
            content = Circle(radius=1.5, color=BLUE)
            content.move_to(ORIGIN)
            self.play(Create(content), run_time=tracker.duration * 0.3)
```

---

## 🚨 CRITICAL RULES - NEVER VIOLATE

### 1. Voice Configuration
- ❌ **NEVER** use any TTS service except `ElevenLabsService`
- ❌ **NEVER** create conditional fallback patterns
- ❌ **NEVER** import other TTS services
- ✅ **ALWAYS** use voice ID `rBgRd5IfS6iqrGfuhlKR`
- ✅ **ALWAYS** import from `voice_config.py`

### 2. Import Naming (Python Module Convention)
- ❌ **WRONG:** `from manim-voiceover-plus import ...` (hyphens = SyntaxError)
- ❌ **WRONG:** `import manimvoiceoverplus` (no separators = ModuleNotFoundError)
- ✅ **CORRECT:** `from manim_voiceover_plus import VoiceoverScene` (underscores)

### 3. Narration Text
- ❌ **NEVER** hardcode narration in scene files
- ✅ **ALWAYS** use `SCRIPT["key"]` from `narration_script.py`

### 4. Positioning
- ❌ **NEVER** use `.to_edge(UP)` for titles (causes clipping)
- ✅ **ALWAYS** use `.move_to(UP * 3.8)` for titles
- ✅ **ALWAYS** call `safe_position()` after `.next_to()`

### 5. Timing Budget (CRITICAL FOR SYNC)
- ❌ **NEVER** let timing fractions exceed 1.0
- ✅ **ALWAYS** calculate timing budget before writing animations
- ✅ Example: `0.4 + 0.3 + 0.3 = 1.0` ✓ Perfect sync

**Timing Budget Validation:**
```python
# WRONG - Causes dead air:
with self.voiceover(text=SCRIPT["demo"]) as tracker:  # 10 seconds
    self.play(Write(title), run_time=tracker.duration * 0.6)   # 6s (60%)
    self.play(FadeIn(obj), run_time=tracker.duration * 0.5)     # 5s (50%)
    # Total = 1.1 = 110% → 1 second of SILENT VIDEO ❌

# CORRECT:
with self.voiceover(text=SCRIPT["demo"]) as tracker:  # 10 seconds
    self.play(Write(title), run_time=tracker.duration * 0.5)   # 5s (50%)
    self.play(FadeIn(obj), run_time=tracker.duration * 0.4)     # 4s (40%)
    self.wait(tracker.duration * 0.1)                           # 1s buffer (10%)
    # Total = 1.0 = 100% ✓ Perfect sync
```

### 6. Configuration Lock
- ✅ **ALWAYS** use locked config block (frame size, resolution)
- ✅ **ALWAYS** include Python 3.13 compatibility patch
- ✅ **ALWAYS** include `safe_position()` helper

---

## Phase: `final_render`

**Goal:** Render all scenes with ElevenLabs voice (production quality)

**Actions:**
1. For each scene in `state['scenes']`:
   ```bash
   manim render <scene_file> <SceneClass> -qh
   ```
2. Update scene metadata with output video path
3. Mark scenes as `"rendered"`

**Critical:** Must actually execute render commands. Do not skip or simulate.

**State Update:**
```python
for scene in state['scenes']:
    scene['status'] = 'rendered'
    scene['video_file'] = f"media/videos/{scene['id']}/1440p60/{scene['class_name']}.mp4"

state['phase'] = 'assemble'
```

---

## Phase: `assemble`

**Goal:** Concatenate all rendered scenes into final video

**Actions:**
1. Generate `scenes.txt` file list:
   ```
   file 'media/videos/scene_01_intro/1440p60/Scene01Intro.mp4'
   file 'media/videos/scene_02_demo/1440p60/Scene02Demo.mp4'
   ```
2. Run ffmpeg concat:
   ```bash
   ffmpeg -f concat -safe 0 -i scenes.txt -c copy final_video.mp4
   ```
3. Verify output file exists

**State Update:**
```python
state['phase'] = 'complete'
```

---

## Phase: `complete`

**Goal:** Finalize project and exit build loop

**Actions:**
1. Verify `final_video.mp4` exists and has non-zero size
2. Log completion message
3. State remains at `"complete"` (orchestrator will exit)

---

## Error Handling

If any phase fails:

```python
error_msg = f"Phase {phase} failed: {error_details}"
state['errors'].append(error_msg)
state['flags']['needs_human_review'] = True
# Do NOT advance phase - stay for retry
```

---

## Workflow Summary

```
plan → review → narration → build_scenes → final_render → assemble → complete
  ↓       ↓          ↓            ↓              ↓             ↓          ↓
plan.   validate   SCRIPT,    scene files   render with   concat    verify
json               voice_     (one at       ElevenLabs    videos    output
                   config     a time)
```

Each invocation handles ONE phase transition. The orchestrator manages the loop.

---

## macOS Rendering Environment

**Assumptions:**
- Operating system: macOS only
- Tools available:
  - `manim` CLI in Python environment
  - `ffmpeg` on PATH (Homebrew)
  - `sox` installed (`brew install sox`)
- Environment variables:
  - `ELEVENLABS_API_KEY` must be set
  - No `MANIM_VOICE_PROD` toggle (always production)

---

## Final Checklist

Before marking any phase complete, verify:

- [ ] All imports use underscores (`manim_voiceover_plus`)
- [ ] ElevenLabsService is the ONLY TTS service used
- [ ] Voice ID is `rBgRd5IfS6iqrGfuhlKR`
- [ ] Narration uses `SCRIPT["key"]`, not hardcoded text
- [ ] Titles use `.move_to(UP * 3.8)`, not `.to_edge(UP)`
- [ ] `safe_position()` called after all `.next_to()`
- [ ] Timing budgets sum to ≤ 1.0
- [ ] Python 3.13 patch included
- [ ] Locked config block present
- [ ] No fallback code patterns exist

---

**This is the complete, authoritative system prompt for Manim video production agents. Follow it exactly.**
