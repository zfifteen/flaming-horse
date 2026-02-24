Generate the scene body for this run.

Scene ID: {{scene_id}}
Scene file: {{scene_file_name}}
Scene class: {{scene_class_name}}
Narration key: {{narration_key}}
Title (exact text): {{scene_title}}

Uploaded template file reference:
{{template_file_reference}}

Scene details:
{{scene_details}}

Narration text (must be used via SCRIPT key):
SCRIPT["{{narration_key}}"] = {{scene_narration}}

Timing guidance:
- Estimated narration duration: `{{estimated_duration_text}}` (`{{estimated_duration_seconds}}s`)
- Use `tracker.duration` in timing math (`run_time=` and/or `self.wait(...)`).
- Keep total projected time <= `tracker.duration * 0.95`.

{{reference_section}}
{{retry_section}}

Output requirements:
1. Return exactly one JSON object with required field `scene_body`.
2. `scene_body` must contain only statements valid inside `construct(self)`:
- assignments
- `self.play(...)`
- `self.wait(...)`
- method calls on mobjects
3. Do not include imports, class/function definitions, comments, or scaffold markers.
4. Do not include `with self.voiceover(...)`; scaffold already provides it.
5. Keep title text exactly `{{scene_title}}`.
6. Keep SCRIPT key exactly `SCRIPT["{{narration_key}}"]`.
7. Use deterministic code; do not use `random`.
8. Return JSON only (no markdown/code fences/XML/explanations).

Example JSON shape:
{"scene_body": "title = Text(\"{{scene_title}}\")\\nself.play(Write(title), run_time=min(1.0, tracker.duration * 0.10))"}
