# Manim Content Pipeline
_Reference for pipeline agents_

This document describes the Manim Content Pipeline's coding and integration patterns. The orchestrator (`build_video.sh`) owns phase progression, rendering, and assembly. Agents own creative content only.

---

## 1. Locked Configuration (Do Not Modify)

```python
config.frame_height = 10
config.frame_width = 10 * 16/9   # 17.78
config.pixel_height = 1440
config.pixel_width = 2560
```

Safe coordinate zones: horizontal ±7, vertical ±4.

---

## 2. VoiceoverScene and Cached Qwen (Non-Negotiable)

Scene classes inherit from `VoiceoverScene`. Voice service is cached Qwen — no network TTS, no fallback.

```python
from pathlib import Path
from flaming_horse_voice import get_speech_service

self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
```

**If cached audio is missing, the build MUST fail.** Run the precache step.

---

## 3. Narration Script Pattern

Narration text lives in `narration_script.py` as a central `SCRIPT` dict:

```python
SCRIPT = {
    "intro": "Welcome to ...",
    "setup": "To understand this ...",
    "demo": "Now watch as ...",
}
```

Scenes reference it via `SCRIPT["key"]`. Never hardcode narration inline in scene files.

---

## 4. Syncing Visuals to Audio

Use `tracker.duration` for narration-synced timing:

```python
with self.voiceover(text=SCRIPT["intro"]) as tracker:
    self.play(Write(title), run_time=tracker.duration * 0.8)
    self.wait(tracker.duration * 0.2)
```

Sum of all `run_time=` values must be ≤ `tracker.duration * 0.85`. Total projected time must not exceed `tracker.duration * 0.95`.

For bookmark-synced animations:

```python
with self.voiceover(
    text="The <bookmark mark='SHOW_FORMULA'/>formula is shown here."
) as tracker:
    self.wait_until_bookmark("SHOW_FORMULA")
    self.play(Write(formula))
```

---

## 5. Layout Checklist (Mandatory)

- Title at `UP * 3.8` (or `adaptive_title_position`). Never `.to_edge(UP)`.
- Subtitle `.next_to(title, DOWN, buff=0.4)` then `safe_position(subtitle)`.
- Graphs/diagrams offset downward (`DOWN * 0.6` to `DOWN * 1.2`) to avoid title overlap.
- Labels: `.next_to(element, direction, buff=0.2)` then `safe_position(label)`.
- `safe_layout(...)` for free-positioned sibling clusters (2+ elements).
- `safe_position(...)` per element after `.next_to(...)` chains.
