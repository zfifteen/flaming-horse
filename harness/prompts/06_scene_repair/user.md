Please repair this scene file that failed to render.

**Current Scene ID**: {{scene_id}}
**Expected Class Name**: {{scene_class_name}}
**Expected Narration Key**: {{narration_key}}
**Expected Title (Exact Match Required)**: {{scene_title}}

File naming/path selection is orchestrator-owned; do not produce or reason about filenames.

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

If this is a retry, the current content above reflects the previous repair attempt.
Build on what was previously tried rather than starting from scratch.

Repair intent is strict:
1. Patch only what is needed to fix the reported failure.
2. Preserve this scene's topic and planned meaning.
3. Keep title text exactly `{{scene_title}}`.
4. Keep SCRIPT key exactly `SCRIPT["{{narration_key}}"]`.
5. Do not inject unrelated branding/topics/project names.
6. Do NOT include `with self.voiceover(...)` in repaired body output. The scaffold already owns that wrapper.
7. Use `tracker.duration` in timing expressions (`run_time=` and/or `self.wait(...)`) so animation timing stays synced with narration.

## Mandatory Repair Validation Checklist

Your repaired `scene_body` must satisfy ALL:

- [ ] All `.next_to(...)` usages are followed by `safe_position(...)`.
- [ ] All 2+ sibling visible groups use `safe_layout(...)`.
- [ ] Long text is width-bounded (`.set_max_width(...)` or `clamp_text_width(...)`).
- [ ] No `.arrange(...)` called on `Text` or `MathTex`.
- [ ] No text-text or text-diagram overlap in the same region.
- [ ] No off-frame content.
- [ ] Scene remains semantically faithful to narration.

REJECTION RULE:
- Do not output repaired JSON until every check is true.
- If conflicts remain, reduce scene complexity and retry.

Output exactly one JSON object with required field `scene_body`.
No explanations, no markdown/code fences, no XML.

🚫 CRITICAL: Never use `#` comments in scene_body - they break JSON parsing.
