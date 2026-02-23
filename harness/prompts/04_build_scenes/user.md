Task: Generate exactly ONE scene body for this run.

Scene ID: {{scene_id}}
Scene class: {{scene_class_name}}
Narration key: {{narration_key}}
Title (exact text): {{scene_title}}

File naming/path selection is orchestrator-owned; do not produce or reason about filenames.

Scene details:
{{scene_details}}

Narration text (must be used via SCRIPT key):
SCRIPT["{{narration_key}}"] = {{scene_narration}}
---
## Narration Timing Estimate (Use This To Pace The Scene)

- Narration word count: `{{narration_word_count}}`
- Speech-rate baseline: `{{speech_wpm}} WPM` (normal speech)
- Estimated narration duration: `{{estimated_duration_text}}` (`{{estimated_duration_seconds}}s`)

### Timing Requirements

1. Treat `{{estimated_duration_seconds}}s` as the scene timing budget for narration-synced visuals.
2. **MAX TIMING CONSTRAINT**: Sum of all `run_time=` values must be <= `tracker.duration * 0.85`. Total wait time must be <= `tracker.duration * 0.15`. Total projected time MUST NOT exceed `tracker.duration * 0.95`.
3. Pace animation sequence so visible content remains meaningful from start to end of narration.
4. Do not clear all non-title elements before narration ends.
5. Use transitions (`Transform`, `FadeTransform`, anchored crossfades) instead of full-frame clears.
6. Keep a consistent cadence: introduce or evolve visual state every ~1.5-3 seconds.
7. If the scene overruns the estimate, simplify visuals (fewer elements, shorter transitions) instead of rushing text readability.
8. If the scene underruns the estimate, extend with meaningful visual evolution (diagram progression, highlight passes, or recap callouts), not dead air.
9. Keep text reveal/readability constraints intact.
10. Every scene-body must use `tracker.duration` in timing expressions (`run_time=` and/or `self.wait(...)`) to stay narration-synced.

### Pacing Self-Check Before Output

- [ ] Visual timeline matches `{{estimated_duration_seconds}}s`
- [ ] No black/empty tail while narration is still speaking
- [ ] At least one visual cluster remains visible until narration ends
- [ ] Only valid Manim MObjects API used (see retrieved reference documentation above)

{{reference_section}}
{{retry_section}}

Output format (mandatory):
- Output exactly one JSON object with required field `scene_body`
- The scene_body value is a string containing Python statements separated by \n (backslash-n, NOT double-backslash)
- Example scene_body value: "title = Text(\"Hello\")\ntitle.move_to(UP * 3)"
- No Markdown, no code fences, no XML wrappers.

IMPORTANT: The scene_body string must contain ONLY:
- Variable assignments (e.g., `title = Text(...)`)
- self.play() calls
- self.wait() calls
- Method calls on mobjects

NEVER include in scene_body:
- import statements
- class definitions
- function definitions
- comments (# ...) - THESE BREAK JSON PARSING. DO NOT USE # FOR ANY PURPOSE.
- config assignments
- The scaffold already provides everything else.

Hard requirements:
1. Output must be valid Python and compile as a scene-body block.
2. Use this exact narration key: `SCRIPT["{{narration_key}}"]`.
3. Do NOT add `with self.voiceover(...)` in your output. The scaffold already provides it.
4. Use `self.play(...)` for visual reveals/transitions.
5. Title text must exactly match: `{{scene_title}}`.
6. Keep content specific to this scene only.
7. Return only statements intended to run inside the existing voiceover block.
8. Do not use tabs; use spaces only.
9. Return JSON only, not fenced Python code blocks.
10. This code runs inside `def construct(self):` - only statements valid inside a method (assignments, self.play(), etc.)
11. Do NOT use the `random` module - use deterministic values (e.g., fixed indices or predefined sequences)
12. Include `tracker.duration` in timing math. CRITICAL: Total projected time = sum(all run_time=) + sum(all wait values). This MUST be <= tracker.duration * 0.95. Example: `run_time=min(1.0, tracker.duration * 0.10)` and `self.wait(max(0.2, tracker.duration * 0.03))`.
13. **GEOMETRY RULE (CRITICAL)**: For Polygon, Line, and similar shapes with vertices, you MUST unpack the list or pass individual args. Manim expects: `Polygon(v1, v2, v3)` or `Polygon(*[v1, v2, v3])`. NEVER: `Polygon([v1, v2, v3])`. Use simple shapes like Circle, Rectangle, Square instead of complex Polygon when possible.
14. CAREFULLY consider the placement of text and objects inside the boundaries of the video frame.
15. ENSURE no text or objects are drawn outside the video frame.
16. DO NOT overlap text or objects in the same place, as they will render unreadable.

### Layout and Overlap Examples (MANDATORY — Do Not Repeat These Failures)

Example 1 — Center-stack text collision:
```python
# Wrong: same position
title = Text("Entropy", font_size=48).move_to(UP * 1.0)
subtitle = Text("A measure of disorder", font_size=30).move_to(UP * 1.0)
# Right: stacked with buff, safe_position
title = Text("Entropy", font_size=48).move_to(UP * 2.8)
subtitle = Text("A measure of disorder", font_size=30).next_to(title, DOWN, buff=0.35)
safe_position(subtitle)
```

Example 2 — Label inside diagram (use next_to + safe_position):
```python
# Wrong: label.move_to(box.get_center())
# Right:
label = Text("Low Entropy", font_size=30).next_to(box, UP, buff=0.25)
safe_position(label)
```

Example 3 — Left/right panels intrude center band (push to ±3.8, set_max_width):
```python
# Wrong: font_size=28 at ±2.0
# Right:
left_text = Text("Low Entropy: Ordered", font_size=22).move_to(LEFT * 3.8 + DOWN * 1.5)
right_text = Text("High Entropy: Disordered", font_size=22).move_to(RIGHT * 3.8 + DOWN * 1.5)
center_text = Text("Time flow = entropy increase", font_size=24).move_to(DOWN * 0.2)
left_text.set_max_width(4.2); right_text.set_max_width(4.2); center_text.set_max_width(6.0)
```

Example 4 — Equation collides with right bullets (separate vertical bands):
```python
# Wrong: main_eq at UP*1.5, bullet at RIGHT*3.2+UP*1.0
# Right:
main_eq = MathTex(r"S=\frac{Q}{T}", font_size=64).move_to(UP*1.9)
bullet1 = Text("Entropy increases with heat transfer", font_size=18).set_max_width(4.4)
bullet1.move_to(RIGHT*5.0 + UP*1.1)
safe_position(main_eq); safe_position(bullet1)
```

Example 5 — Text.arrange causes character stacking (use VGroup.arrange):
```python
# Wrong: bullet_tail.arrange(DOWN, aligned_edge=LEFT)  # Text object — stacks chars
# Right:
bullet_a = Text("Irreversible processes are driven by", font_size=20).set_max_width(6.0)
bullet_b = Text("statistical likelihood of higher entropy states", font_size=20).set_max_width(6.0)
bullet_pair = VGroup(bullet_a, bullet_b).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
safe_layout(bullet_pair)
```

Hard rules: `buff >= 0.25` between stacked text; never two text objects at the same coordinates; one focal element in center band at a time.

## Mandatory Readability Self-Check (Return JSON only if all are TRUE)

Before finalizing `scene_body`, verify:

- [ ] Every `.next_to(...)` is immediately followed by `safe_position(...)` on that mobject.
- [ ] Every visible sibling group (2+ elements) is passed through `safe_layout(...)`.
- [ ] Every long `Text(...)` has `.set_max_width(...)` or `clamp_text_width(...)`.
- [ ] No `.arrange(...)` called on `Text` or `MathTex`.
- [ ] No two text blocks share the same center band region.
- [ ] No text/diagram outside the visible frame.
- [ ] Left, center, and right content bands do not overlap.
- [ ] Scene remains readable at normal playback speed.

REJECTION RULE: If any check is false, revise scene_body before outputting JSON.

Required structural pattern:
```python
title = Text("{{scene_title}}", font_size=48, weight=BOLD)
title.move_to(UP * 3.8)
self.play(Write(title))
self.play(...)
self.play(...)
self.wait(...)
```

Allowed API subset:
- `self.play(...)`, `self.wait(...)`
- `Text`, `MathTex`, `Tex`, `VGroup`, standard Manim primitives
- `safe_position`, `safe_layout`, `polished_fade_in`
- `FadeIn`, `FadeOut`, `Create`, `Transform`, `LaggedStart`, `Write`

Geometry construction rule (CRITICAL):
- For Polygon and similar shapes, pass vertices as INDIVIDUAL arguments, NOT as a list:
  - CORRECT: `Polygon(RIGHT * 3 + DOWN, LEFT * 3 + DOWN, UP * 2)`
  - CORRECT: `Polygon(*[RIGHT * 3 + DOWN, LEFT * 3 + DOWN, UP * 2])`
  - WRONG: `Polygon([RIGHT * 3 + DOWN, LEFT * 3 + DOWN, UP * 2])`
- For complex positions, use explicit tuple coordinates: `Polygon((3, -1, 0), (3.8, -1, 0), (3.4, 0.5, 0))`

Forbidden:
- `play_next(...)`, `play_text_next(...)`
- `self.add(...)` for first-time visible content
- `from ... import` or `import ...` statements - do NOT include imports in scene_body
- `random` module usage (`random.choice`, `random.randint`, `random.random`, etc.) - use deterministic values only
- class definitions, config blocks, helper function definitions
- unresolved placeholders like `{{...}}`
- `.to_edge(UP)` for titles/labels
- `self.set_background_color(...)` - DOES NOT EXIST in Manim. Use `config.background_color = BLACK` in a config section instead (NOT in scene_body).
- `self.camera.set_background(...)` - NOT needed, background is handled by config

MathTex rule:
- Use `MathTex(r"... \times ...")` (single backslash command in raw string), not `\\times`.

Final output rule:
- Return only one JSON object containing `scene_body` and no extra text.

⚠️ HARD CONSTRAINT: scene_body must contain ONLY statements valid inside a `construct(self)` method body. NEVER include import statements, class definitions, function definitions (def), or config/scaffold markers. The scaffold already provides these. Violation = instant rejection.
