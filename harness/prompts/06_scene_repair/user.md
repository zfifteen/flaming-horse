Please repair this scene file that failed to render.

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

**File**: {{broken_file_name}}

**Current Content**:
```python
{{broken_file_content}}
```

**Error**:
```
{{retry_context}}
```

Repair intent is strict:
1. Patch only what is needed to fix the reported failure.
2. Preserve this scene's topic and planned meaning.
3. Keep title text exactly `{{scene_title}}`.
4. Keep SCRIPT key exactly `SCRIPT["{{narration_key}}"]`.
5. Do not inject unrelated branding/topics/project names.

Output ONLY the corrected Python code. No explanations.
