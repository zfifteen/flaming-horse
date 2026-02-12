# manim-voiceover Integration Guide

## 🚨 CRITICAL: VOICE SERVICE CONFIGURATION

**FOR THIS PROJECT: ELEVENLABS ONLY - NO OTHER TTS SERVICES ALLOWED**

- ✅ **Voice Service:** ElevenLabs ONLY
- ✅ **Voice ID:** `rBgRd5IfS6iqrGfuhlKR` (Big D's cloned voice)
- ✅ **Model:** `eleven_multilingual_v2`
- ❌ **DO NOT use:** gTTS, Azure, OpenAI, pyttsx3, or any other TTS backend
- ❌ **DO NOT create fallback code** - ElevenLabs or FAIL

**This document describes various TTS options for reference, but YOU MUST ONLY USE ELEVENLABS.**

---

## Overview

`manim-voiceover` is the official Manim Community plugin for adding voiceover narration
to Manim animations directly in Python. It eliminates the need for manual audio/video
synchronization via external editors or ffmpeg stitching.

**Key capabilities:**

- Define voiceover text inline with animation code using `with self.voiceover(...)` blocks
- Automatic audio generation via pluggable TTS backends (**WE USE ELEVENLABS ONLY**)
- Automatic duration-based sync: animations stretch or Manim waits to match audio length
- Per-word animation triggers via XML bookmark tags and OpenAI Whisper transcription
- Microphone recording mode for manual voiceover capture during render
- Built-in translation support via DeepL for multilingual output

**Repository:** https://github.com/ManimCommunity/manim-voiceover
**PyPI:** https://pypi.org/project/manim-voiceover/

---

## Installation

This project uses `manim-voiceover-plus` exclusively:

```bash
pip install --upgrade "manim-voiceover-plus[elevenlabs]"
```

**Do NOT install the `[transcribe]` extra unless you need bookmark-driven per-word sync.**
The `[transcribe]` extra pulls in `openai-whisper` and `stable-ts`, which fail to build
on Python 3.13 due to removed `pkg_resources`. If you only need duration-based sync
(which covers the vast majority of use cases), `[elevenlabs]` alone is sufficient.

```bash
# ONLY if you need per-word bookmark timing (and are NOT on Python 3.13):
pip install "manim-voiceover-plus[elevenlabs,transcribe]"

# For translation via DeepL
pip install "manim-voiceover-plus[elevenlabs,translate]"

# For microphone recording
pip install "manim-voiceover-plus[elevenlabs,recorder]"
```

### System Dependency: SoX

manim-voiceover requires SoX (Sound eXchange) for audio processing:

```bash
# macOS
brew install sox
```

### Environment Variable

Set your ElevenLabs API key as an environment variable:

```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

Or in a `.env` file (manim-voiceover reads from `python-dotenv`):

```
ELEVENLABS_API_KEY=your_api_key_here
```

---

## Critical: Python 3.13 Transcription Bug Workaround

### The Problem

`manim-voiceover-plus` v0.6.9 has a regression in `SpeechService.__init__` (the base
class for all TTS backends including ElevenLabs). During initialization, it
**unconditionally** calls `self.set_transcription()`, which tries to import `whisper`
and `stable_whisper` **before** checking whether `transcription_model` is `None`.

This means even if you pass `transcription_model=None`, the import check fires first,
fails (because you correctly did not install whisper), prompts interactively, and raises
`ImportError` if you decline.

The call chain from the traceback:

```
ElevenLabsService.__init__()
  -> SpeechService.__init__()        # base.py:82
    -> self.set_transcription()      # base.py:82
      -> import whisper              # base.py:~140 (BEFORE None check)
      -> ImportError raised          # base.py:149
```

### The Fix

Add this patch **before** importing from `manim_voiceover_plus`. It intercepts
`set_transcription()` and short-circuits it when `model=None`, before the broken
import check ever runs.

```python
import manim_voiceover_plus.services.base as _base
_original_set_transcription = _base.SpeechService.set_transcription

def _patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self._whisper_model = None
        return
    _original_set_transcription(self, model=model, kwargs=kwargs)

_base.SpeechService.set_transcription = _patched_set_transcription
```

**Place this block at the top of your scene file, after `from manim import *` but
before importing `VoiceoverScene` or `ElevenLabsService`.**

Then pass `transcription_model=None` when constructing `ElevenLabsService`:

```python
self.set_speech_service(
    ElevenLabsService(
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        voice_settings=VOICE_SETTINGS,
        transcription_model=None,
    )
)
```

### When You Do NOT Need This Patch

- If you are using gTTS, pyttsx3, or another backend that does not trigger the
  transcription init path
- If you have whisper and stable-ts installed (e.g., on Python 3.12 or earlier)
- If a future version of `manim-voiceover-plus` fixes the bug upstream

### When You DO Need This Patch

- You are on Python 3.13
- You are using `manim-voiceover-plus[elevenlabs]` without the `[transcribe]` extra
- You do not need bookmark-driven per-word sync (you use `tracker.duration` instead)

---

## Core Concepts

### VoiceoverScene

Instead of inheriting from `Scene`, your class inherits from `VoiceoverScene`.
This adds the `self.voiceover()` and `self.set_speech_service()` methods.

```python
from manim_voiceover_plus import VoiceoverScene

class MyScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(...)  # configure TTS backend
        ...
```

**Import paths (ONLY valid pattern):**

```python
# ONLY VALID IMPORT PATTERN
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings
```

### The `with self.voiceover(...)` Block

This is the central mechanism. Wrap animations in a `with` block:

```python
with self.voiceover(text="This circle is drawn as I speak.") as tracker:
    self.play(Create(circle), run_time=tracker.duration)
```

**Behavior:**
- The TTS backend generates audio for the given text
- `tracker.duration` returns the total audio duration in seconds
- If animations finish before the voiceover, Manim waits automatically for the
  audio to complete when the `with` block exits
- If no `run_time` is set, the animation plays at its default speed and Manim waits
  for the audio to finish

### The Tracker Object

The `tracker` provides timing information for precise sync:

```python
with self.voiceover(text="First we draw, then we transform.") as tracker:
    self.play(Create(circle), run_time=tracker.duration / 2)
    self.play(Transform(circle, square), run_time=tracker.duration / 2)
```

Or let the context manager handle the remaining wait automatically:

```python
with self.voiceover(text="Draw and then wait for me to finish.") as tracker:
    self.play(Create(circle), run_time=2)
    # No explicit wait needed; context manager waits for audio to end
```

### Bookmarks (Per-Word Animation Triggers)

Bookmarks let you trigger animations at specific words in the narration:

```python
with self.voiceover(
    text='You simply add an <bookmark mark="A"/>XML tag to trigger animations.'
) as tracker:
    self.wait_until_bookmark("A")
    self.play(Write(sentence))
```

**How it works:**
- Insert `<bookmark mark="NAME"/>` in the voiceover text at the trigger point
- Call `self.wait_until_bookmark("NAME")` to pause until that word is spoken
- Whisper transcription determines the exact timing of each word
- This requires the `transcribe` extra: `pip install "manim-voiceover-plus[transcribe]"`

**IMPORTANT:** Bookmarks require whisper and the `[transcribe]` extra. If you are
using `transcription_model=None` (which you should be on Python 3.13 without the
transcribe extra), bookmarks will NOT work. Use `tracker.duration` based sync instead.

---

## ElevenLabs Configuration

### Basic Setup

```python
from manim import *

# Apply transcription patch (see "Critical" section above)
import manim_voiceover_plus.services.base as _base
_original_set_transcription = _base.SpeechService.set_transcription
def _patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self._whisper_model = None
        return
    _original_set_transcription(self, model=model, kwargs=kwargs)
_base.SpeechService.set_transcription = _patched_set_transcription

from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

class MyScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id="YOUR_VOICE_CLONE_ID",
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                ),
                transcription_model=None,
            )
        )
        # ... animations with self.voiceover() blocks
```

### ElevenLabsService Parameters

| Parameter | Type | Description |
|---|---|---|
| `voice_id` | str | The voice ID from your ElevenLabs account (clone or preset) |
| `voice_name` | str | Alternative to voice_id; looks up by name |
| `model_id` | str | TTS model: `eleven_multilingual_v2`, `eleven_turbo_v2_5`, `eleven_v3`, etc. |
| `voice_settings` | `VoiceSettings` | **Must be an `elevenlabs.VoiceSettings` Pydantic object, not a plain dict.** The plus fork calls `.model_dump()` on this value internally. |
| `output_format` | str | Audio format: `mp3_44100_128` (default), `pcm_44100`, etc. |
| `transcription_model` | str/None | Whisper model for bookmarks. **Always set to `None` unless you have the `[transcribe]` extra installed and need bookmark sync.** |

### Voice Settings

`voice_settings` **must** be an `elevenlabs.VoiceSettings` Pydantic object.
`manim-voiceover-plus` v0.6.9 calls `.model_dump()` on this value, which will crash
with `AttributeError` if you pass a plain dict.

```python
from elevenlabs import VoiceSettings

# Correct:
voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)

# WRONG (will crash with AttributeError: 'dict' object has no attribute 'model_dump'):
# voice_settings={"stability": 0.5, "similarity_boost": 0.75}
```

**VoiceSettings fields:**

- **stability** (0.0 to 1.0): Higher = more consistent, lower = more expressive/variable
- **similarity_boost** (0.0 to 1.0): Higher = closer match to original voice, lower = more natural variation
- **style** (0.0 to 1.0): Higher = more expressive delivery (only supported by some models)
- **use_speaker_boost** (bool): Enhances speaker similarity at cost of some generality

**Recommended starting point for voice clones:**

```python
from elevenlabs import VoiceSettings

VOICE_SETTINGS = VoiceSettings(
    stability=0.5,
    similarity_boost=0.75,
    style=0.0,
    use_speaker_boost=True,
)
```

### Using eleven_v3 Model

For using the `eleven_v3` model:

```python
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

class MyScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_name="Liam",
                model_id="eleven_v3",
                voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75),
                transcription_model=None,
            )
        )
```

### Known Issue: Transcription Model Bug

When using newer ElevenLabs models, the Whisper transcription step can fail.
Workaround: set `transcription_model=None` to disable per-word timing.
This disables bookmark functionality but allows basic duration-based sync to work.

**On Python 3.13 with manim-voiceover-plus v0.6.9:** `transcription_model=None` alone
is NOT sufficient due to a regression where the import check fires before the None
check. You MUST also apply the monkey-patch described in the "Critical" section above.

---

## Integration with Our Manim Template

### Combining VoiceoverScene with Custom Config

The standard template uses `Scene` as the base class. When adding voiceover,
change the inheritance to `VoiceoverScene`. All other config remains identical.

```python
from manim import *
import numpy as np

# ---------------------------------------------------------------------------
# Patch: bypass v0.6.9 transcription import regression
# ---------------------------------------------------------------------------
import manim_voiceover_plus.services.base as _base
_original_set_transcription = _base.SpeechService.set_transcription
def _patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self._whisper_model = None
        return
    _original_set_transcription(self, model=model, kwargs=kwargs)
_base.SpeechService.set_transcription = _patched_set_transcription
# ---------------------------------------------------------------------------

from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

# ============================================================================
# OPTIMIZED CONFIGURATION - DO NOT MODIFY THESE VALUES
# ============================================================================
config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560
# ============================================================================


def safe_position(mobject, max_y=4.0, min_y=-4.0):
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject


# ---------------------------------------------------------------------------
# Voice configuration (edit these per project)
# ---------------------------------------------------------------------------
VOICE_ID = "YOUR_CLONE_ID"
MODEL_ID = "eleven_multilingual_v2"
VOICE_SETTINGS = VoiceSettings(
    stability=0.5,
    similarity_boost=0.75,
)


class NarratedScene(VoiceoverScene):
    """Base class for all narrated scenes in this project."""

    def setup_voice(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )

    def construct(self):
        self.setup_voice()
        # Override in subclass
```

### Full Example: Narrated Research Scene

```python
class GravityAnomalyExplainer(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )

        title = Text("Gravity Anomalies", font_size=48, weight=BOLD)
        subtitle = Text("Bouguer Correction", font_size=32, color=BLUE)
        subtitle.next_to(title, DOWN, buff=0.3)
        title_group = VGroup(title, subtitle).move_to(ORIGIN)

        with self.voiceover(
            text="Today we explore gravity anomalies and the Bouguer correction."
        ) as tracker:
            self.play(Write(title_group), run_time=tracker.duration)

        title_group.generate_target()
        title_group.target.scale(0.6).move_to(UP * 3.8)

        with self.voiceover(
            text="The Bouguer correction accounts for the gravitational effect "
                 "of terrain between the observation point and sea level."
        ) as tracker:
            self.play(MoveToTarget(title_group), run_time=2)

            formula = MathTex(
                r"\Delta g_B = 2 \pi G \rho h",
                font_size=48, color=GOLD
            )
            formula.move_to(ORIGIN)
            self.play(Write(formula), run_time=tracker.duration - 2.5)

        self.wait(1)
```

---

## Workflow Patterns

### ⚠️ DEPRECATED PATTERN - DO NOT USE

~~Pattern 1: Develop Fast, Render Final~~ **PROHIBITED FOR THIS PROJECT**

**The following pattern is shown for reference only. DO NOT implement it:**

```python
# ❌ WRONG - DO NOT USE THIS PATTERN
import os
from manim_voiceover_plus.services.gtts import GTTSService  # ❌ PROHIBITED

class MyScene(VoiceoverScene):
    def construct(self):
        if os.getenv("MANIM_VOICE_PROD"):
            self.set_speech_service(ElevenLabsService(...))
        else:
            self.set_speech_service(GTTSService(...))  # ❌ NEVER DO THIS
```

**✅ CORRECT PATTERN - ELEVENLABS ONLY:**

```python
# ✅ CORRECT - ELEVENLABS ONLY, NO FALLBACK
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS

class MyScene(VoiceoverScene):
    def construct(self):
        # ELEVENLABS ONLY - NO DEV MODE, NO FALLBACK
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,              # rBgRd5IfS6iqrGfuhlKR
                model_id=MODEL_ID,               # eleven_multilingual_v2
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )
```

### Pattern: Script-First Workflow

Write all narration text first as a standalone script, then build animations around it.
This mirrors a traditional video production workflow:

```python
SCRIPT = {
    "intro": "Welcome to this exploration of DNA breathing dynamics.",
    "setup": "DNA is not a rigid molecule. It undergoes thermal fluctuations called breathing.",
    "demo": "Watch as the base pairs open and close in response to temperature changes.",
    "conclusion": "These breathing dynamics have implications for gene regulation and drug binding.",
}

class DNABreathing(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )

        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            # title animation
            ...

        with self.voiceover(text=SCRIPT["setup"]) as tracker:
            # DNA structure animation
            ...
```

### Pattern 3: Multi-Scene Video with Consistent Voice

For videos with multiple scenes rendered separately and combined later:

```python
# voice_config.py (shared across scenes)
from elevenlabs import VoiceSettings

VOICE_ID = "YOUR_CLONE_ID"
MODEL_ID = "eleven_multilingual_v2"
VOICE_SETTINGS = VoiceSettings(stability=0.5, similarity_boost=0.75)
```

```python
# scene_01_intro.py
from voice_config import *

class Intro(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )
        ...
```

Render each scene separately and concatenate with ffmpeg:

```bash
manim scene_01_intro.py Intro
manim scene_02_analysis.py Analysis
ffmpeg -f concat -i scenes.txt -c copy final_video.mp4
```

### Pattern 4: Bookmark-Driven Precision Sync

**Requires the `[transcribe]` extra. Does NOT work on Python 3.13.**
**Do NOT apply the transcription patch if using bookmarks.**

For educational content where specific visuals must appear at exact words:

```python
with self.voiceover(
    text='The <bookmark mark="formula"/>formula for gravitational potential is '
         '<bookmark mark="show_eq"/>shown here, where G is the '
         '<bookmark mark="highlight_G"/>gravitational constant.'
) as tracker:
    self.wait_until_bookmark("formula")
    self.play(Write(Text("Formula:", font_size=32).move_to(UP * 2)))

    self.wait_until_bookmark("show_eq")
    eq = MathTex(r"U = -\frac{GMm}{r}", font_size=48)
    self.play(Write(eq))

    self.wait_until_bookmark("highlight_G")
    self.play(eq[0][4].animate.set_color(YELLOW))
```

---

## Audio Caching

manim-voiceover caches generated audio files locally. This means:

- Re-rendering a scene does NOT re-generate audio if the text has not changed
- Audio files are stored in `media/voiceovers/` by default
- To force regeneration, delete the cache directory or change the text

This is especially important for ElevenLabs where each generation consumes credits.
Unchanged voiceover blocks are free on re-render.

---

## Translation Support

manim-voiceover integrates with DeepL for automatic translation:

```python
from manim_voiceover_plus.translate import get_gettext
from elevenlabs import VoiceSettings

_ = get_gettext()

class TranslatedScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75),
                transcription_model=None,
            )
        )

        with self.voiceover(text=_("This circle is drawn as I speak.")) as tracker:
            self.play(Create(circle), run_time=tracker.duration)
```

Requires `DEEPL_API_KEY` environment variable and the `translate` extra.

---

## Troubleshooting

### Common Issues

| Issue | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: elevenlabs` | Wrong extras installed | `pip install "manim-voiceover-plus[elevenlabs]"` |
| `ElevenLabs API version mismatch` | Upstream package pins old SDK | Switch to `manim-voiceover-plus` |
| `SoX not found` | Missing system dependency | `brew install sox` (macOS) |
| Bookmark timing is wrong | Whisper transcription inaccurate | Try `transcription_model="base"` or `"small"` |
| `transcription_model` error | Incompatible with newer EL models | Set `transcription_model=None` |
| `ImportError: transcribe extras` even with `transcription_model=None` | v0.6.9 regression: import check fires before None check | Apply the monkey-patch from the "Critical" section. Do NOT install whisper as a workaround. |
| `AttributeError: 'dict' object has no attribute 'model_dump'` | `voice_settings` passed as plain dict | Use `elevenlabs.VoiceSettings(...)` Pydantic object instead of a dict |
| Audio overlaps between scenes | Tracker duration not consumed | Ensure `run_time=tracker.duration` or let context manager auto-wait |
| Python 3.13 compatibility | Upstream not updated | Use `manim-voiceover-plus` |
| `pkg_resources` deprecation warning | `manim-voiceover-plus` imports it at top level | Cosmetic only; install `setuptools>=69` to silence, or ignore |

### Debugging Audio Sync

If audio and visuals are misaligned:

1. Check that `run_time=tracker.duration` is set on the primary animation
2. The `with self.voiceover(...)` context manager automatically waits for the audio
   to finish when the block exits. You do not need explicit wait calls for basic sync.
3. If you need to split `tracker.duration` across multiple animations, use arithmetic:
   ```python
   with self.voiceover(text="Long narration here.") as tracker:
       self.play(Create(obj), run_time=tracker.duration * 0.4)
       self.play(Transform(obj, obj2), run_time=tracker.duration * 0.6)
   ```
4. Inspect generated audio files in `media/voiceovers/` for unexpected duration

### Render Command

No special flags needed. The template config handles quality:

```bash
# Standard render (quality baked into config)
manim my_scene.py MyScene

# With caching disabled (forces audio regeneration)
manim my_scene.py MyScene --disable_caching
```

---

## Supported TTS Backends

| Backend | Quality | Cost | Latency | Offline | Install Extra |
|---|---|---|---|---|---|
| ElevenLabs | Excellent | Paid (per char) | Medium | No | `elevenlabs` |
| Azure TTS | Very Good | Paid (per char) | Low | No | `azure` |
| OpenAI TTS | Very Good | Paid (per char) | Medium | No | `openai` |
| gTTS | Decent | Free | Low | No | `gtts` |
| Coqui TTS | Good | Free | High | Yes | `coqui` |
| pyttsx3 | Basic | Free | Instant | Yes | `pyttsx3` |
| Recorder | Your voice | Free | N/A | Yes | `recorder` |

---

## Quick Reference

### Minimal ElevenLabs Scene (Python 3.13 Safe)

```python
from manim import *

# Patch v0.6.9 transcription regression
import manim_voiceover_plus.services.base as _base
_orig_st = _base.SpeechService.set_transcription
def _patched_st(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self._whisper_model = None
        return
    _orig_st(self, model=model, kwargs=kwargs)
_base.SpeechService.set_transcription = _patched_st

from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

class QuickDemo(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id="YOUR_ID",
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75),
                transcription_model=None,
            )
        )
        circle = Circle(color=BLUE)
        with self.voiceover(text="A circle appears.") as tracker:
            self.play(Create(circle), run_time=tracker.duration)
        self.wait(1)
```

### Import Paths (ONLY valid pattern)

```python
# ONLY VALID IMPORT PATTERN
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings
```
