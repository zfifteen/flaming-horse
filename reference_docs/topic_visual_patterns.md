# Topic Visual Patterns

Use this mapping when converting narration into right-panel visuals for non-math explainer scenes.

## Core Rule

- Extract concrete nouns from narration (objects, systems, devices, timelines).
- Build visuals that directly represent those nouns.
- Avoid generic filler geometry unless it is semantically tied to the topic.

## Pattern Map

### Waves / Music / Acoustics

- Keywords: `string`, `guitar`, `harmonic`, `pipe`, `open pipe`, `closed pipe`, `speaker`, `microphone`
- Visuals:
  - String mode diagram: baseline + nodes (red dots) + antinode markers (green dots) + oscillating curve.
  - Pipe cross-sections: open-open and closed-open rectangles with end-condition labels.
  - Frequency bars: simple bar chart tied to harmonic index.

Suggested sequence:
1. Reveal bullets on left panel.
2. Fade out bullets/subtitle before dense visual block.
3. Introduce string diagram, then transform into pipe diagram.
4. End with callout highlight tied to final narration sentence.

### Physics Mechanisms (Non-equation focus)

- Keywords: `force`, `motion`, `energy transfer`, `reflection`, `collision`
- Visuals:
  - Labeled arrows with moving bodies.
  - Before/after state transitions using `FadeTransform`.
  - Boundary markers for reflection or constraints.

### Process / Workflow / Systems

- Keywords: `pipeline`, `steps`, `flow`, `stages`, `feedback`
- Visuals:
  - Left-to-right stage boxes with connecting arrows.
  - Animated token/cursor moving across stages.
  - Conditional branch highlight for decision points.

### History / Timeline / Sequence

- Keywords: `year`, `era`, `phase`, `milestone`, `evolution`
- Visuals:
  - Horizontal timeline with event markers.
  - Progressive reveal of events with date + label pairs.
  - Period shading to show regime or phase boundaries.

### Biology / Anatomy / Environment

- Keywords: `cell`, `organ`, `ecosystem`, `cycle`, `population`
- Visuals:
  - Simplified labeled diagram (2-4 regions max).
  - Flow arrows for cycle transitions.
  - Comparative side-by-side states when narration contrasts cases.

## Layout and Timing Contract

- Keep title at `UP * 3.8` (or `adaptive_title_position`).
- Subtitle must be `next_to(title, DOWN, buff=0.4)` then `safe_position(subtitle)`.
- Right-panel visuals should sit below subtitle (`DOWN * 0.6` to `DOWN * 1.2`).
- Before dense visual transitions, clear previous text layer (`FadeOut`/`FadeTransform`).
- Target a meaningful visual state change every `~1.5-3s`.

## Anti-Patterns (Reject)

- A single static circle/rectangle unrelated to narration.
- Bullets only for most of the scene with no evolving diagram.
- Adding labels with `.next_to(...)` in a list comprehension without per-label `safe_position(...)`.
- Passing `run_time=` into `play_next(...)` or `play_text_next(...)`.
