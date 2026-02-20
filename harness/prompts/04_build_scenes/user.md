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
2. Pace animation sequence so visible content remains meaningful from start to end of narration.
3. Do not clear all non-title elements before narration ends.
4. Use transitions (`Transform`, `FadeTransform`, anchored crossfades) instead of full-frame clears.
5. Keep a consistent cadence: introduce or evolve visual state every ~1.5-3 seconds.
6. If the scene would overrun the estimate, simplify visuals (fewer elements, shorter transitions) instead of rushing text readability.
7. If the scene would underrun the estimate, extend with meaningful visual evolution (diagram progression, highlight passes, or recap callouts), not dead air.
8. Keep text reveal/readability constraints intact.
9. Every scene-body must use `tracker.duration` in timing expressions (`run_time=` and/or `self.wait(...)`) to stay narration-synced.

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
12. Include `tracker.duration` in timing math (for example: `run_time=min(1.2, tracker.duration * 0.15)` and `self.wait(max(0.2, tracker.duration * 0.05))`).

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

Forbidden:
- `play_next(...)`, `play_text_next(...)`
- `self.add(...)` for first-time visible content
- `from ... import` or `import ...` statements - do NOT include imports in scene_body
- `random` module usage (`random.choice`, `random.randint`, `random.random`, etc.) - use deterministic values only
- class definitions, config blocks, helper function definitions
- unresolved placeholders like `{{...}}`
- `.to_edge(UP)` for titles/labels

MathTex rule:
- Use `MathTex(r"... \times ...")` (single backslash command in raw string), not `\\times`.

Final output rule:
- Return only one JSON object containing `scene_body` and no extra text.
