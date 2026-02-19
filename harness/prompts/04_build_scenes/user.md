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

{{reference_section}}
{{retry_section}}

Output format (mandatory):
```python
# python scene body only
```

Hard requirements:
1. Output must be valid Python and compile as a scene-body block.
2. Use this exact narration key: `SCRIPT["{{narration_key}}"]`.
3. Use voice sync pattern: `with self.voiceover(text=SCRIPT["{{narration_key}}"]) as tracker:`
4. Use `self.play(...)` for visual reveals/transitions.
5. Title text must exactly match: `{{scene_title}}`.
6. Keep content specific to this scene only.
7. Indentation is mandatory: every executable line inside `with self.voiceover(...):` must be indented exactly one block (4 spaces) deeper than the `with` line.
8. Do not use tabs; use spaces only.
9. Return exactly one fenced Python code block (start with ```python and end with ```).

Required structural pattern (must compile exactly as Python block structure):
```python
title = Text("{{scene_title}}", font_size=48, weight=BOLD)
title.move_to(UP * 3.8)
self.play(Write(title))

with self.voiceover(text=SCRIPT["{{narration_key}}"]) as tracker:
    # all narration-synced actions must be indented in this block
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
- imports, class definitions, config blocks, helper function definitions
- unresolved placeholders like `{{...}}`
- `.to_edge(UP)` for titles/labels

MathTex rule:
- Use `MathTex(r"... \times ...")` (single backslash command in raw string), not `\\times`.

Final output rule:
- Return only one fenced Python block containing scene body code and no extra text.
- BAD wrapper example (forbidden):
```text
Any plain text outside fences.
```
- GOOD wrapper example (required):
```text
```python
# code...
```
```
