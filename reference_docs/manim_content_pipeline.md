# Manim Content Pipeline
_A high-level reference for assistants_

This document describes the **Manim Content Pipeline**, a reusable pattern for going from raw subject matter to a narrated Manim video with cached Qwen audio and a macOS-based render script.

The goal is not to enforce a strict sequence but to give assistants a **shared mental model** of the whole pipeline so they can enter at any stage and still act coherently.

---

## 1. Overview

The pipeline transforms input material into a final video in up to five conceptual stages:

1. Subject material understanding
2. Z-mapping insight analysis
3. Narration script generation
4. Manim scene generation with cached Qwen integration
5. Bash-based rendering on macOS

These stages are **logically ordered** but **operationally flexible**:

- The user will often follow them in order.
- The user may also jump in at any stage (for example, starting from an existing script, or asking only for Manim code).

Assistants should treat this document as the **big-picture blueprint** for how to collaborate with the user on content creation.

---

## 2. Subject Material Understanding

**Purpose:** Build a correct and rich understanding of the topic that the video will explain.

### Inputs

- Raw text (notes, essays, research papers, blog posts)
- Code (for algorithm or dataflow explanations)
- URLs to online resources
- High-level descriptions of ideas

### Assistant Responsibilities

- Parse and internalize the material.
- Use external references and tools to clarify unclear parts when needed.
- Identify:
  - Key concepts
  - Important relationships
  - Potential "aha moments"
  - Likely target audience and difficulty level (if not given, ask)

### Outputs

- An internal conceptual model of the topic.
- Optional: a brief, structured summary that the assistant can refer back to during later stages.

Assistants should treat this stage as **optional but recommended**. If the user clearly indicates that the topic is already understood by both sides, they can skip directly to later stages.

---

## 3. Z-Mapping Insight Analysis

**Purpose:** Translate the topic into a structured insight map that can drive a narrative and visuals.

The user provides **ad hoc instructions** for Z-mapping each time. Assistants **must not assume a fixed formalism** for the Z-mapping framework. The only guarantees are:

- There is a **Z-mapping** framework the user cares about.
- It organizes content into multiple layers of depth or perspective.
- The user will specify the mapping strategy, layer definitions, and scope when they invoke it.

### Assistant Responsibilities

- When asked for a Z-mapping analysis:
  - Follow the user's specific instructions for how to map the content.
  - Organize the topic into clear layers or slices as instructed.
  - Explicitly highlight:
    - What is foundational
    - What is structural
    - Where the main insights live
    - Where open questions or frontiers appear (if requested)

### Outputs

- A **structured Z-mapping document** that:
  - Lists the layers or categories specified by the user.
  - Assigns key facts, relationships, and insights to each.
  - Suggests which parts are most visually expressive and which are best handled in narration.

Assistants should think of this as the **bridge between "understanding" and "storytelling"**.

---

## 4. Narration Script Generation

**Purpose:** Turn the Z-mapping (or any conceptual plan) into a spoken narration script that can be fed into Manim's voiceover workflow.

Scripts are meant to be **spoken**, not read. They should be:

- Clear, concise, and conversational.
- Divided into segments that can map naturally to scenes or major beats.

### Inputs

- The Z-mapping analysis (preferred).
- Or: any other structured outline, or even free-form user notes.

### Assistant Responsibilities

1. **Segment the script**

   - Break the content into named sections that map to logical phases of the video, for example:
     - `intro`, `setup`, `core_demo`, `insight`, `conclusion`
   - Each segment should be roughly 15 to 45 seconds of speech (about 40 to 120 words), unless the user specifies otherwise.

2. **Write narration text**

   - Use natural spoken language.
   - Maintain consistent tone and difficulty level.
   - Ensure smooth transitions between segments.

3. **Optionally add stage directions**

   - Include non-spoken comments or markers that describe what should be on screen.
   - Make it easy to copy these into Manim code or a SCRIPT dictionary.

4. **Bookmarks (optional)**

   - If the user wants precise sync (e.g., an element appears at a specific word), the assistant can insert bookmark tags like:
     - `<bookmark mark="SHOW_FORMULA"/>`
   - The Manim code can later use `self.wait_until_bookmark("SHOW_FORMULA")` to sync animations.

### Outputs

- A **segment-indexed script**, suitable for dropping into a Python dictionary, for example:

  ```python
  SCRIPT = {
      "intro": "Narration text here...",
      "setup": "Next segment text...",
      "insight": "Deeper insight text...",
      "conclusion": "Closing remarks...",
  }
  ```

- Or, the same content in a format that can be easily converted into such a dictionary.

Assistants should be prepared to **revise and iterate** on the script based on user feedback before proceeding to code.

---

## 5. Manim Scene Generation with Cached Qwen Integration

**Purpose:** Convert the narration script and conceptual plan into a Manim Python file that:

- Uses the Space's **locked configuration**.
- Integrates **manim-voiceover** with cached **Qwen** audio.
- Synchronizes animation timing with generated audio.

### 5.1. Template and Configuration

Assistants must treat the Space's template as authoritative:

- Base imports and config:
    - Manim CE (`from manim import *`)
    - `numpy` if needed (`import numpy as np`)
    - `VoiceoverScene` and cached Qwen service from this repo (`flaming_horse_voice`)
    - Locked config values:
        - `config.frame_height = 10`
        - `config.frame_width = 10 * 16/9`
        - `config.pixel_height = 1440`
        - `config.pixel_width = 2560`
        - (do not change these)
- Safe positioning:
    - Use explicit coordinates like `UP * 3.8` for titles.
    - Avoid top-edge clipping.
    - Keep important content within +/-7 horizontally and +/-4 vertically.
    - Use the `safe_position()` helper after `.next_to()` chains.

#### Layout Checklist (Mandatory)

- Title must exist and be visible at `UP * 3.8` (or via `adaptive_title_position`).
- Subtitle must be `.next_to(title, DOWN, buff=0.4)` and then `safe_position(subtitle)`.
- Graphs/diagrams must be offset downward (e.g., `DOWN * 0.6` to `DOWN * 1.2`) to avoid title overlap.
- Labels must attach to nearby elements (e.g., `label.next_to(curve.get_end(), UP, buff=0.2)`), then `safe_position(label)`.
- After positioning, run `safe_layout(...)` for free-positioned sibling clusters; for strict `.next_to(...)` chains, call `safe_position(...)` per element.
- ❌ NEVER use `.to_edge(...)` for titles or labels (causes clipping/edge drift).

### 5.2. VoiceoverScene and Cached Qwen

The generated scene class should:

- Inherit from `VoiceoverScene`.
- Configure the cached Qwen service at the start of `construct()` or in a helper.
- Use the project directory to resolve cached audio:

```python
from pathlib import Path
from flaming_horse_voice import get_speech_service

self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
```

### 5.3. Using the Narration Script in Code

There are two common patterns:

1. **Central SCRIPT dictionary**

   ```python
   SCRIPT = {
       "intro": "Welcome to ...",
       "setup": "To understand this ...",
       "demo": "Now watch as ...",
   }

   class TopicExplainer(VoiceoverScene):
       def construct(self):
           self.set_speech_service(...)
           with self.voiceover(text=SCRIPT["intro"]) as tracker:
               # Intro animations
               ...
   ```

2. **Inline text inside `with` blocks**

   ```python
   with self.voiceover(text="Welcome to ...") as tracker:
       ...
   ```

Assistants should favor the **central SCRIPT dictionary** when the goal is reusability or multi-scene projects, since it keeps narration text in one place.

### 5.4. Syncing Visuals to Audio

Inside each `with self.voiceover(...) as tracker:` block:

- Use `tracker.duration` to set `run_time` for primary animations:

  ```python
  with self.voiceover(text=SCRIPT["intro"]) as tracker:
      self.play(Write(title), run_time=tracker.duration)
  ```

- Use `tracker.get_remaining()` to fill unused audio time with waits:

  ```python
  with self.voiceover(text=SCRIPT["setup"]) as tracker:
      self.play(Create(diagram), run_time=2)
      remaining = tracker.get_remaining()
      if remaining > 0:
          self.wait(remaining)
  ```

- If bookmark tags are present in the script:

  ```python
  with self.voiceover(
      text="The <bookmark mark='SHOW_FORMULA'/>formula is shown here."
  ) as tracker:
      self.wait_until_bookmark("SHOW_FORMULA")
      self.play(Write(formula))
  ```

Assistants should design animations to **match the rhythm of the voiceover**, not the other way around.

### 5.5. Multi-Scene Projects

For longer videos:

- Use a shared config file only for narration text; cached Qwen audio is configured
  via `voice_clone_config.json` at the project root.
- Create multiple scene files that import the shared config and define different `VoiceoverScene` subclasses.
- The bash render stage can then render each scene and optionally concatenate the outputs.

---

## 6. Bash Rendering on macOS

**Purpose:** Automate the full render of the Manim project on the user's MacBook, including cached Qwen voiceover.

### 6.1. Assumptions

- Operating system: **macOS only**.
- Tools available:
    - `manim` CLI in the user's Python environment.
    - `ffmpeg` installed via Homebrew and on PATH (if concatenation is needed).
    - `sox` installed via Homebrew (`brew install sox`).
- Environment has:
    - Local Qwen venv configured via `voice_clone_config.json`

### 6.2. Single-Scene Case

For a single Manim file and scene (for example, `topic_explainer.py` and `TopicExplainer`):

- Bash script responsibilities:
    - Set environment variables if desired.
    - Call `manim` with the correct file and scene.
    - Optionally echo the output path.

Example pattern:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Render
manim topic_explainer.py TopicExplainer

echo "Render complete. Check the media/videos directory."
```

Manim (with manim-voiceover) generates the video file with audio already synchronized.

### 6.3. Multi-Scene Concatenation

If multiple scenes are rendered separately:

1. Render each scene via `manim`, producing multiple `.mp4` files.
2. Create a `scenes.txt` listing them:

   ```text
   file 'scene_intro.mp4'
   file 'scene_body.mp4'
   file 'scene_outro.mp4'
   ```

3. Use `ffmpeg` concat:

   ```bash
   ffmpeg -f concat -safe 0 -i scenes.txt -c copy final_video.mp4
   ```

The bash script can automate all of these steps.

Assistants should generate scripts that:

- Assume macOS paths and tools.
- Have minimal, robust defaults.
- Can be edited by the user to change paths or scene names.

---

## 7. How Assistants Should Use This Pipeline

When the user asks for help related to Manim video creation, assistants should:

1. **Identify the current stage(s)**
    - Is the user providing raw subject matter?
    - Asking for a Z-mapping analysis?
    - Asking for a narration script?
    - Asking directly for Manim code?
    - Asking for a bash script?

2. **Respond with stage-aware outputs**
    - If the user is early in the process, suggest or perform earlier stages as needed.
    - If the user jumps in mid-pipeline, respect that and work from there, but keep the rest of the pipeline in mind.

3. **Maintain compatibility**
    - Generated Manim code must align with:
        - The Space's template configuration (`manim_template.py.txt`).
    - The `VoiceoverScene` and cached Qwen integration patterns (`manim_voiceover.md`).
        - The sizing and positioning rules (`manim_config_guide.md`).
    - Bash scripts must assume a **macOS environment**.
    - The cached Qwen model is `Qwen/Qwen3-TTS-12Hz-1.7B-Base` unless the user overrides it in `voice_clone_config.json`.

4. **Be explicit and modular**
    - Clearly separate:
        - Conceptual analysis
        - Script generation
        - Manim code
        - Bash scripts
    - This allows the user to swap or update one part without breaking others.

This document is intended as a **long-lived reference**. Assistants should interpret it as the default blueprint for "Manim Content Pipeline" work unless the user explicitly overrides some part of it in a given conversation.
