You are generating exactly ONE scene file for this run.

**Current Scene ID**: {{scene_id}}
**Expected File Name**: {{scene_file_name}}
**Expected Class Name**: {{scene_class_name}}
**Expected Narration Key**: {{narration_key}}
**Expected Title (Exact Match Required)**: {{scene_title}}

**Scene Details from Plan**:
```json
{{scene_details}}
```

**Current Scene Narration** (`SCRIPT["{{narration_key}}"]`):
```text
{{scene_narration}}
```

{{reference_section}}

{{retry_section}}

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

Output ONLY the scene body code wrapped in <scene_body> XML tags as shown in your system instructions. Do NOT include imports, config, class definition, or helper functions - those are already in the scaffold.
