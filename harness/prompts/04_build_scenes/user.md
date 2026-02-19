You are generating exactly ONE scene file for this run.

Current Scene ID: {{scene_id}}
Expected File Name: {{scene_file_name}}
Expected Class Name: {{scene_class_name}}
Expected Narration Key: {{narration_key}}
Expected Title (exact match required): {{scene_title}}

Scene details from plan:
{{scene_details}}

Current scene narration from SCRIPT["{{narration_key}}"]:
{{scene_narration}}

{{reference_section}}

{{retry_section}}

Available in scaffold:
- Text(), MathTex(), Circle(), Rectangle(), Line(), Arrow(), VGroup()
- harmonious_color(), safe_position(), polished_fade_in(), safe_layout()
- UP * 3.8, LEFT * 3.5, RIGHT * 3.5, DOWN * 0.4
- self.play() for animations
- Built-in colors like GREEN or hex strings

Canonical execution contract for this run:
This is the run-scoped source of truth for output and syntax constraints.

Output format:
<scene_body>
scene body code only
</scene_body>

Hard output mechanics:
1. START with <scene_body>; nothing before it.
2. END with </scene_body>; nothing after it.
3. NO imports - scaffold already has them.
4. NO class definition - scaffold already has it.
5. NO config block - scaffold already has it.
6. NO helper function definitions - scaffold already has them.
7. NO loops - write each element explicitly.
8. NO random functions - deterministic output only.
9. 4 spaces indentation to match scaffold expectations.

Generate ONLY the scene body code for `{{scene_id}}`.

Hard requirements:
1. Use the exact SCRIPT key: `SCRIPT["{{narration_key}}"]`.
2. The title text in code must exactly match: `{{scene_title}}` (no paraphrase).
3. Use subtitle and bullets grounded in this scene's plan details; do not use placeholders.
4. Keep semantics strictly scene-specific: use only this scene's plan details + narration text.
5. Do not introduce unrelated branding/topics/project names unless they appear in this scene's provided inputs.
6. Use class name `{{scene_class_name}}` and output code for file `{{scene_file_name}}` only.
7. Follow positioning rules (title at `UP * 3.8`, `safe_position` after `.next_to`, etc.).
8. Use standard `self.play()` for animations.
9. Forbidden placeholder strings/tokens: `{{{{TITLE}}}}`, `{{{{SUBTITLE}}}}`, `{{{{KEY_POINT_1}}}}`, `{{{{KEY_POINT_2}}}}`, `{{{{KEY_POINT_3}}}}` (and any `{{{{...}}}}` left in scaffold strings).
10. Do not reuse scaffold demo animations (default box/shape demo) unless explicitly required by this scene's plan.

Output only scene body code wrapped in <scene_body> tags. Do not include imports, config, class definition, or helper functions.
