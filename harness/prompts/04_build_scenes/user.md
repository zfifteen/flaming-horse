Generate exactly ONE scene body for this run.

Scene ID: {{scene_id}}
Scene file: {{scene_file_name}}
Scene class: {{scene_class_name}}
Narration key: {{narration_key}}
Title (exact text): {{scene_title}}

Scene details:
{{scene_details}}

Narration text (must be used via SCRIPT key):
SCRIPT["{{narration_key}}"] = {{scene_narration}}

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
7. If the scene would overrun the estimate, simplify visuals (fewer elements, shorter transitions) instead of rushing text readability.
8. If the scene would underrun the estimate, extend with meaningful visual evolution (diagram progression, highlight passes, or recap callouts), not dead air.
9. Keep text reveal/readability constraints intact.
10. Every scene-body must use `tracker.duration` in timing expressions (`run_time=` and/or `self.wait(...)`) to stay narration-synced.

### Self-Check Before Output

- [ ] Planned visual timeline approximately matches `{{estimated_duration_seconds}}s`
- [ ] No long black/near-empty tail while narration is still speaking
- [ ] At least one meaningful visual cluster remains visible until narration end

{{reference_section}}
{{retry_section}}

Output format (mandatory):
- Output exactly one JSON object.
- Required field: `scene_body` (non-empty string containing valid Python scene-body code).
- No markdown, no code fences, no XML wrappers.

JSON OUTPUT EXAMPLE (copy this format exactly):
```json
{"scene_body": "title = Text(\"The Title\", font_size=48)\\ntitle.move_to(UP * 3.8)\\nself.play(Write(title), run_time=min(1.0, tracker.duration * 0.10))"}
```

Note: Use \\n for newlines inside the JSON string value. Escape quotes with \\".

IMPORTANT: The scene_body string must contain ONLY:
- Variable assignments (e.g., `title = Text(...)`)
- self.play() calls
- self.wait() calls
- Method calls on mobjects

NEVER include in scene_body:
- import statements
- class definitions
- function definitions
- comments (# ...)
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

Required structural pattern (must compile exactly as Python block structure):
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
- `safe_position`, `safe_layout`, `polished_fade_in`, `harmonious_color`
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
- `self.set_background_color(...)` - DOES NOT EXIST in Manim. Use `config.background_color = BLACK` in config section instead (NOT in scene_body).
- `self.camera.set_background(...)` - NOT needed, background is handled by config

MathTex rule:
- Use `MathTex(r"... \times ...")` (single backslash command in raw string), not `\\times`.

Final output rule:
- Return only one JSON object containing `scene_body` and no extra text.

+ HARD CONSTRAINT: scene_body must contain ONLY statements valid inside
+ a `construct(self)` method body. NEVER include: import statements,
+ class definitions, function definitions (def), or config/scaffold
+ markers. The scaffold already provides these. Violation = instant rejection.

