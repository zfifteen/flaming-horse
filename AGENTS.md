# AGENTS.md
## Manim Video Production Agent System Prompt

## File Structure (New)
This file references modular docs:
- reference_docs/phase_plan.md: Plan/review details
- reference_docs/phase_narration.md: Script/timing rules
- reference_docs/phase_scenes.md: Build/render guidelines
- reference_docs/visual_helpers.md: Code snippets for aesthetics
- reference_docs/topic_visual_patterns.md: Topic-to-visual mapping patterns
- tests/README.md: Unit test instructions

For full phase details, see the modular docs above.

**Version:** 2.4  
**Last Updated:** 2026-02-16  
**Changes:** Root-cause-first troubleshooting policy; guardrails/validations treated as last-resort containment only; tightened scene template timing/layout contracts.  
**Purpose:** Instructions for automated agents building Manim voiceover videos

---

## 🚨 CRITICAL: VOICE POLICY - READ THIS FIRST

### Local Qwen Voice Clone - No Fallback

**ABSOLUTE REQUIREMENTS:**
- ✅ **ONLY** local Qwen voice clone audio cached on disk (no network TTS).
- ✅ **Model:** `Qwen/Qwen3-TTS-12Hz-1.7B-Base` (voice clone).
- ✅ **Device/Dtype:** CPU `float32` for stability.
- ✅ **Reference assets:** `assets/voice_ref/ref.wav` + `assets/voice_ref/ref.txt` per project.
- ❌ **NEVER** use any TTS service except cached Qwen.
- ❌ **NEVER** create fallback code patterns.

**If cached audio is missing, the build MUST fail and instruct to run the precache step.**

---

- Create a new folder under `projects` for the video and all associated artifacts.
- Do not create or modify any files outside the designated project folder.

- If the subject is not mathematical, default to an explainer-slide style: progressive bullets, topic-specific diagrams/timelines, and continuous motion. Avoid generic geometric filler visuals unless explicitly relevant.
- API keys are in `.env`

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

## 🚨 ROOT-CAUSE-FIRST TROUBLESHOOTING POLICY

When debugging, repairing, or responding to failures, follow this priority order:

1. **Identify root cause first** (where failure originates), not just symptom location.
2. **Fix the source mechanism** (prompt ambiguity, phase logic, state transitions, architecture, data flow).
3. **Use guardrails/validations only as last resort**, and only when immediate containment is required.

### Mandatory Debugging Behavior

- ✅ **ALWAYS** trace the first bad step in the causal chain before proposing fixes.
- ✅ **ALWAYS** explain why existing logic allowed the failure to pass through.
- ✅ **ALWAYS** prefer simplification/clarification of core logic over layering new checks.
- ❌ **NEVER** default to adding validation gates as the primary fix.
- ❌ **NEVER** treat symptom checks as equivalent to a root-cause fix.

### If a Guardrail Is Temporarily Needed

- Allowed only when root fix cannot land immediately in the same pass.
- Must be documented as **temporary containment**, not final resolution.
- Must include removal condition tied to the root-cause fix.

This repo's debugging standard is: **Root cause first. Guardrails last.**

---

## 🚨 AUTONOMOUS EXECUTION REQUIREMENT

**This repo uses an orchestrator (`scripts/build_video.sh`) that invokes the agent one phase at a time.**

- ✅ **ALWAYS** read `project_state.json` and execute ONLY the current phase.
- ✅ **ALWAYS** update `project_state.json` and advance to the next phase on success.
- ❌ **NEVER** execute multiple phases in a single invocation (even if you think you can).
- ✅ The overall pipeline is still fully automatic: the orchestrator continues phase → phase until `final_video.mp4` is produced.
- ✅ **ONLY** stop if an error occurs and `needs_human_review` flag is set.

---

## 🚨 CRITICAL: Execution Protocol

**When the user says "proceed", "execute", "continue", or "approve":**

- ❌ **NEVER** present another detailed plan
- ❌ **NEVER** ask "Does this align with your vision?"
- ❌ **NEVER** request confirmation again
- ✅ **IMMEDIATELY** execute the current phase's tasks

**Maximum confirmation rounds: ONE per phase.**

The intent of this system is to generate videos from a single prompt without approval loops.

---

## Reference Documentation

Consult these files for technical details:

- **reference_docs/manim_template.py.txt** - Base scene template with locked config
- **reference_docs/manim_config_guide.md** - Positioning rules, safe zones, sizing guidelines
- **reference_docs/manim_voiceover.md** - VoiceoverScene patterns for local cached Qwen integration
- **reference_docs/manim_content_pipeline.md** - Overall workflow concepts
- **docs/DEVELOPMENT_GUIDELINES.md** - Separation of concerns (agent creativity vs deterministic scripts), one-change-per-PR policy
- **docs/agent_improvements.md** - Plan for v2.2 updates
- Modular phase docs in reference_docs/ (e.g., phase_plan.md)

---

## Project State Structure

```json
{
  "project_name": "string",
  "topic": "string|null",
  "phase": "plan|review|narration|build_scenes|final_render|assemble|complete",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "run_count": 0,
  "plan_file": "plan.json",
  "narration_file": "narration_script.py",
  "voice_config_file": null,
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
  "history": [],  # Include render logs: e.g., {"phase": "build_scenes", "scene": "01", "log_snippet": "No overlaps detected", "timestamp": "ISO"}
  "flags": {
    "needs_human_review": false,
    "dry_run": false
  }
}
```

---

## Phase Execution Guide

### Phase: `plan` and `review`

See reference_docs/phase_plan.md for details.

---

### Phase: `narration`

See reference_docs/phase_narration.md for details.

---

### Phase: `build_scenes` and `final_render`

See reference_docs/phase_scenes.md for details.

## CRITICAL: Complete Scene Template

**This is the ONLY valid pattern for scene generation. Follow it exactly.**

```python
from manim import *
import numpy as np
import colorsys  # New: For harmonious_color

from pathlib import Path
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

# For Qwen caching: Precache check (New)
ref_path = Path("assets/voice_ref/ref.wav")
if not ref_path.exists():
    raise FileNotFoundError("Run precache_voice.sh before building.")

# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

# Safe Positioning Helper (Enhanced)
def safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2):
    """Enhanced: Adjusts vertically with buffer to prevent edge clipping."""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * (bottom - (min_y + buff)))
    return mobject

# Enhanced Visual Helpers (New - from visual_helpers.md)
def harmonious_color(base_color, variations=3, lightness_shift=0.1):
    rgb = np.array(base_color.to_rgb())
    h, l, s = colorsys.rgb_to_hls(*rgb)
    palette = []
    for i in range(variations):
        h_shift = i * (360 / variations) / 360
        new_h = (h + h_shift) % 1
        new_l = min(1.0, max(0.0, l + lightness_shift * i))
        new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, new_l, s)
        palette.append([new_r, new_g, new_b, 1.0])
    return palette

def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.1, glow=False):
    if glow:
        mobject.set_stroke(width=3, opacity=0.5)
    return LaggedStart(
        FadeIn(mobject),
        mobject.animate.scale(scale_factor).set_run_time(0.5).scale(1/scale_factor),
        lag_ratio=lag_ratio,
    )

def adaptive_title_position(title, content_group, max_shift=0.5):
    content_height = content_group.height if content_group else 0
    shift_y = min(max_shift, max(0, content_height - 2.0))
    title.move_to(UP * (3.8 + shift_y))
    return title

def safe_layout(*mobjects, alignment=ORIGIN, h_buff=0.5, v_buff=0.3, max_y=3.5, min_y=-3.5):
    """Enhanced: Positions siblings horizontally/vertically without overlaps, with alignment."""
    group = VGroup(*mobjects)
    group.arrange(RIGHT, buff=h_buff, aligned_edge=UP if v_buff else alignment)
    for mob in mobjects:
        safe_position(mob, max_y, min_y)
    for i, mob_a in enumerate(mobjects):
        for j, mob_b in enumerate(mobjects[i+1:], i+1):
            if mob_a.get_right()[0] > mob_b.get_left()[0] - h_buff:
                overlap = mob_a.get_right()[0] - mob_b.get_left()[0] + h_buff
                mob_b.shift(RIGHT * overlap)
    return VGroup(*mobjects)

# Scene Class
class Scene01Intro(VoiceoverScene):
    def construct(self):
        # Palette for cohesion (New)
        blues = harmonious_color(BLUE, variations=3)
        
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
        # Animation Sequence
        # Timing is deterministic via BeatPlan helper slots.
        
        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            num_beats = max(10, min(22, int(np.ceil(tracker.duration / 3.0))))
            beats = BeatPlan(tracker.duration, [1] * num_beats)

            # Title (ALWAYS use UP * 3.8, NEVER .to_edge(UP)); Adaptive (New)
            title = Text("{{TITLE}}", font_size=48, weight=BOLD, color=blues[0])
            title = adaptive_title_position(title, None)  # No content yet
            play_text_next(self, beats, Write(title))  # Text helper caps at 1.5s
            
            # Subtitle with safe positioning
            subtitle = Text("{{SUBTITLE}}", font_size=32, color=blues[1])
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)  # ALWAYS call after .next_to()
            play_text_next(self, beats, polished_fade_in(subtitle, lag_ratio=0.1))  # Polished (New)
            
            # Explainer-slide cadence: progressive bullets + evolving right-panel visual
            bullet_1 = Text("{{KEY_POINT_1}}", font_size=28).move_to(LEFT * 4.8 + UP * 1.6)
            bullet_2 = Text("{{KEY_POINT_2}}", font_size=28).next_to(bullet_1, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_2)
            bullet_3 = Text("{{KEY_POINT_3}}", font_size=28).next_to(bullet_2, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_3)

            diagram = RoundedRectangle(width=5.2, height=3.2, corner_radius=0.2, color=blues[2]).move_to(RIGHT * 3.2 + DOWN * 0.4)
            callout = SurroundingRectangle(bullet_2, color=YELLOW, buff=0.15)

            play_text_next(self, beats, FadeIn(bullet_1))
            play_text_next(self, beats, FadeIn(bullet_2))
            play_text_next(self, beats, FadeIn(bullet_3))
            play_next(self, beats, FadeOut(subtitle), FadeOut(bullet_1), FadeOut(bullet_2), FadeOut(bullet_3))
            play_next(self, beats, Create(diagram, rate_func=smooth))
            play_next(self, beats, FadeIn(callout), max_run_time=0.8)
            play_next(self, beats, FadeOut(callout), max_run_time=0.8)
```

See reference_docs/visual_helpers.md for more on enhanced helpers and aesthetics.

---

## 🚨 CRITICAL RULES - NEVER VIOLATE

### 1. Voice Configuration
- ❌ **NEVER** use any network TTS service
- ❌ **NEVER** create conditional fallback patterns
- ❌ **NEVER** import other TTS services
- ❌ **NEVER** enable optional alignment extras or cloud features
- ✅ **ALWAYS** use cached Qwen voice via `flaming_horse_voice.get_speech_service`

### 2. Import Naming (Python Module Convention)
- ❌ **WRONG:** `from manim-voiceover-plus import ...` (hyphens = SyntaxError)
- ❌ **WRONG:** `import manimvoiceoverplus` (no separators = ModuleNotFoundError)
- ✅ **CORRECT:** `from manim_voiceover_plus import VoiceoverScene` (underscores)

### 3. Narration Text
- ❌ **NEVER** hardcode narration in scene files
- ✅ **ALWAYS** use `SCRIPT["key"]` from `narration_script.py`

### 4. Positioning
- ❌ **NEVER** use `.to_edge(UP)` for titles (causes clipping)
- ✅ **ALWAYS** use `.move_to(UP * 3.8)` for titles (or adaptive_title_position)
- ✅ **ALWAYS** call `safe_position()` after `.next_to()`
- ❌ **NEVER** use `.to_edge(...)` for titles or labels (causes clipping/edge drift)
- ✅ **ALWAYS** place graphs/diagrams below the subtitle (e.g., `.move_to(DOWN * 0.6)`)
- ✅ **ALWAYS** call `safe_layout(...)` when positioning 2+ siblings in a group

### Layout Contract (Mandatory)
- Title must exist and be visible at `UP * 3.8` (or via `adaptive_title_position`).
- Subtitle must be `.next_to(title, DOWN, buff=0.4)` and then `safe_position(subtitle)`.
- Graphs/diagrams must be offset downward (e.g., `DOWN * 0.6` to `DOWN * 1.2`) to avoid title overlap.
- Labels must attach to nearby elements (e.g., `label.next_to(curve.get_end(), UP, buff=0.2)`), then `safe_position(label)`.
- After positioning, run `safe_layout(...)` for any group of 2+ elements.
### Adaptive Positioning (New)
- Use enhanced helpers for dynamic layouts:
  ```python
  def adaptive_title_position(title, content_group, max_shift=0.5):
      """Shift title based on content height to avoid crowding."""
      content_height = content_group.height if content_group else 0
      shift_y = min(max_shift, max(0, content_height - 2.0))
      title.move_to(UP * (3.8 + shift_y))
      return title
  # Call: title = adaptive_title_position(title, VGroup(subtitle, diagram))
  ```
- For transitions: Mandate 0.5-1s crossfades between elements using `FadeTransform` or `polished_fade_in()` (see new helpers below).

### 5. Timing Budget (CRITICAL FOR SYNC)
- ❌ **NEVER** let timing fractions exceed 1.0
- ✅ **ALWAYS** calculate timing budget before writing animations
- ✅ Example: `0.4 + 0.3 + 0.3 = 1.0` ✓ Perfect sync
- ✅ **ALWAYS** use scaffold timing helpers (`BeatPlan`, `play_next`, `play_text_next`) instead of raw `self.wait(...)`/`run_time` math
- ❌ **NEVER** write expressions that can evaluate to zero/negative waits (e.g. `a - a`)
- ❌ **NEVER** pass `run_time=` to `play_next(...)`/`play_text_next(...)`; slot helpers are the single timing source
### Sync Enhancements (New)
- For Qwen caching: In scaffold, add precache check:
  ```python
  ref_path = Path("assets/voice_ref/ref.wav")
  if not ref_path.exists():
      raise FileNotFoundError("Run precache_voice.sh before building.")
  ```
- Tolerance: If sum(fractions) >0.95, auto-scale run_times down by 5%.

**Timing Budget Validation:**
```python
# WRONG - Causes dead air:
with self.voiceover(text=SCRIPT["demo"]) as tracker:  # 10 seconds
    self.play(Write(title), run_time=tracker.duration * 0.6)   # 6s (60%)
    self.play(FadeIn(obj), run_time=tracker.duration * 0.5)     # 5s (50%)
    # Total = 1.1 = 110% → 1 second of SILENT VIDEO ❌

# CORRECT:
with self.voiceover(text=SCRIPT["demo"]) as tracker:  # 10 seconds
    self.play(Write(title), run_time=tracker.duration * 0.2)   # 2s (20%)
    self.play(FadeIn(obj), run_time=tracker.duration * 0.25)    # 2.5s (25%)
    self.play(obj.animate.shift(RIGHT * 0.8), run_time=tracker.duration * 0.2)
    self.play(Indicate(obj), run_time=tracker.duration * 0.15)
    self.play(FadeIn(callout), run_time=tracker.duration * 0.2)
    # Total = 1.0 = 100% ✓ Perfect sync
```

### 6. Configuration Lock
- ✅ **ALWAYS** use locked config block (frame size, resolution)
- ✅ **ALWAYS** include Python 3.13 compatibility patch
- ✅ **ALWAYS** include `safe_position()` helper

### 7. LaTeX Rendering
- ✅ **ALWAYS** use `MathTex` for mathematical expressions: `MathTex(r"\\frac{GMm}{r^2}")`
- ✅ **ALWAYS** use `Tex` for plain text with LaTeX formatting only
- ❌ **NEVER** use `Tex` for equations (causes rendering failures)
- ❌ **NEVER** pass `weight=` to `MathTex`/`Tex` (unsupported; causes runtime TypeError)
- ✅ Use `weight=` only with `Text(...)`, or emphasize math with color/scale/animation instead

### 8. Positioning and Overlap Prevention
- ❌ **NEVER** place multiple elements at ORIGIN without explicit offsets
- ❌ **NEVER** use `.next_to()` without immediately calling `safe_position()`
- ❌ **NEVER** keep `.next_to(...)` inside list comprehensions/loops without explicit per-item `safe_position(...)`
- ✅ **ALWAYS** call `safe_layout(*elements)` on any VGroup with 2+ sibling elements
- ✅ **ALWAYS** use explicit coordinates: `element.move_to(UP * 2 + LEFT * 3)`

**Example - CORRECT pattern:**
```python
title = Text("Title", font_size=48)
title.move_to(UP * 3.8)

subtitle = Text("Subtitle", font_size=32)
subtitle.next_to(title, DOWN, buff=0.5)
safe_position(subtitle)  # MANDATORY after .next_to()

content = Circle(radius=1.5)
content.move_to(ORIGIN)  # OK - only element at ORIGIN

# For multiple elements at same vertical level:
label1, label2, label3 = Text("A"), Text("B"), Text("C")
label1.move_to(LEFT * 3)
label2.move_to(ORIGIN)
label3.move_to(RIGHT * 3)
safe_layout(label1, label2, label3)  # MANDATORY for siblings
```

---

## 🎨 VISUAL QUALITY RULES

### Text Animation Speed
- ✅ Text must appear quickly and consistently
- ❌ NEVER let any text animation take longer than 1.5 seconds (Stricter)
- ✅ Use timing *slots* tied to the voiceover, and fill the remaining time with waits

Recommended pattern:

```python
# Duration-scaled micro-beats (no coarse 3-slot timing)
num_beats = max(10, min(22, int(np.ceil(tracker.duration / 3.0))))
beats = BeatPlan(tracker.duration, [1] * num_beats)
play_text_next(self, beats, Write(title))
play_next(self, beats, Create(diagram))
play_text_next(self, beats, FadeIn(key_point))
```

- ✅ For staggered reveals, use `LaggedStart(FadeIn(a), FadeIn(b), ..., lag_ratio=0.15)`

### Content Density Per Scene
- ✅ For non-math topics, prefer high-information explainer slides over sparse minimal scenes
- ✅ Use progressive bullet reveals plus evolving right-panel visuals
- ✅ Derive right-panel visuals from narration keywords (see `reference_docs/topic_visual_patterns.md`)
- ✅ If content is too dense for one block, split into multiple voiceover segments
- ✅ Remove (FadeOut/Transform) previous elements before introducing new ones

### Element Cleanup
- ✅ ALWAYS FadeOut previous section content before new section begins
- ✅ Exception: titles/headers that persist across segments
- ❌ NEVER let more than 2 "layers" of content coexist on screen

### Animation Smoothness
- ✅ Use `rate_func=smooth` for most transitions (this is the default)
- ✅ Minimum run_time for any visible animation: 0.3 seconds
- ❌ NEVER set run_time < 0.2 (imperceptible, creates visual artifacts)
- ✅ For sequential reveals, use lag_ratio=0.1 to 0.3

### Continuous Motion Requirement
- ❌ NEVER leave long static/black intervals where little changes on screen
- ✅ Target a visible visual state change every ~1.5-3 seconds
- ✅ Non-math scenes should follow slide cadence (title/subtitle, bullets, evolving visual, recap/callout)
- ❌ Avoid generic filler visuals (single circle/ellipse/equation) unless directly relevant

### Overlap Prevention
- ✅ After positioning ALL elements in a segment, verify no overlaps using `safe_layout()`:
  ```python
  def safe_layout(*mobjects, min_horizontal_spacing=0.5, max_y=4.0, min_y=-4.0):
      # [Updated function with enhanced logic from visual_helpers.md]
      pass
  ```

### Enhanced Visual Helpers (New)
Always include these functions in scene files for polished aesthetics (see reference_docs/visual_helpers.md for full code):
- `harmonious_color()`: Generate cohesive palettes.
- `polished_fade_in()`: Smooth reveals with scale pop.
- `adaptive_title_position()`: Dynamic title shifting.
- 3D Guidelines: Prefer for spatial topics; limit to 1-2 moving objects. Use `self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)` in a `ThreeDScene`.
- Text Rules: Cap `Write()` at 1.5s; for staggered reveals use `LaggedStart(*[FadeIn(b) for b in bullets], lag_ratio=0.15)`.

---

## Pre-Render Validation Checklist

Before rendering any scene, programmatically verify:

### Positioning Validation
- [ ] No elements placed at ORIGIN except if it's the only element on screen
- [ ] Every element positioned with `.next_to()` has `safe_position()` called immediately after
- [ ] Any VGroup with 2+ sibling elements has `safe_layout()` called
- [ ] All title elements use `.move_to(UP * 3.8)`, NOT `.to_edge(UP)`

### Timing Validation
- [ ] Timing budget fractions sum to ≤ 1.0 for each voiceover block
- [ ] No animation has `run_time < 0.3` seconds

### Content Validation
- [ ] Charts/graphs have labels and legends
- [ ] Mathematical content uses `MathTex`, not `Tex`
- [ ] Position arrays are 3D: `np.array([x, y, 0])`

### Aesthetics Validation (New)
- [ ] Colors use harmonious palette (no more than 4 variants per scene)
- [ ] Animations include rate_func=smooth or there_and_back_with_pause
- [ ] 3D elements (if used) have resolution <=(20,20) for performance
- [ ] No static elements >3s without motion (add Rotate or wiggle)

**If any check fails, STOP and fix the issue before rendering.**

---

### Phase: `assemble` and `complete`

See reference_docs/phase_scenes.md for details (includes assemble and complete).

## Error Handling

If any phase fails:

```python
error_msg = f"Phase {phase} failed: {error_details}"
state['errors'].append(error_msg)
state['flags']['needs_human_review'] = True
# Do NOT advance phase - stay for retry
```

### Error Recovery Protocol

When `needs_human_review = True`:
1. Orchestrator halts after current phase
2. Human inspects `state['errors']` array
3. Human fixes issue (edits files, updates deps, etc.)
4. Human clears flag: Set `state['flags']['needs_human_review'] = false`
5. Human resumes: `./scripts/build_video.sh <project>`

**Agent responsibility:** Provide actionable error messages.

**Good example:**
```
"Scene 02 failed: MathTex rendering error at line 45. Check LaTeX syntax for '\\frac{GMm}{r^2}'"
```

**Bad example:**
```
"Render failed"
```

### Root Cause Analysis Requirement (Troubleshooting/Debug)

Before implementing any fix for failed phases/scenes, perform and record:

1. **Failure origin**: the earliest point where behavior diverged from intent.
2. **Causal chain**: how the error propagated through phase logic.
3. **Primary fix**: change that eliminates the source mechanism.
4. **Containment status**: whether any temporary guardrail was added, and explicit removal trigger.

Do not stop at detection-level explanations (e.g., "validation failed"). Explain the mechanism that produced invalid output.

### Visual-Specific Errors (New)
If validation detects overlaps/desyncs:
- Auto-suggest fixes: Append to `state['errors']`: "Add safe_layout() call in scene {id} for overlaps."
- Set `state['flags']['needs_human_review'] = True` and generate `review_report.md` with frame thumbnails (extract via `ffmpeg -ss 50% -vframes 1 -q:v 2 thumbnail.jpg`).

---

## Workflow Summary

```
plan → review → narration → build_scenes → final_render → assemble → complete
  ↓       ↓          ↓            ↓              ↓             ↓          ↓
plan.   validate   scripts      code          render        concat    done
json    feasib.    + voice      files         videos        final
                   config                                    .mp4
```

### Pipeline Enhancements (New)
- Logging: Use JSON-structured logs in `history` for diffs (e.g., "Animation run_time=2.1s >1.5s limit"). Expand `"history"`: Include render logs: e.g., {"phase": "build_scenes", "scene": "01", "log_snippet": "No overlaps detected", "timestamp": "ISO"}
- Dependencies: At project init (in orchestrator), check: `manim --version >=0.18`, `ffmpeg -version`, Qwen model path. Halt if missing.
- Human Fallback: On `needs_human_review`, auto-generate `review_report.md` with thumbnails, suggestions (e.g., "Add harmonious_color for better palette"), and email hook (if API keys allow).

---

### Testing and Maintenance (New)
- Unit Tests: See tests/README.md.
- Quality Scoring: In `review` phase, compute score = 10 - (risk_flags * 1.5) + (3d_used ? 2 : 0). If <7, suggest simplifications.
- Versioning: Tag AGENTS.md changes (e.g., v2.2); lock config in `config.py` import.

---

**END OF AGENTS.md**
