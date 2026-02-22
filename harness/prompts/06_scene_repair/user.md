## Purpose
Repair a broken Manim scene that failed to render.

## Inputs
- Scene ID: {{scene_id}}
- Class name: {{scene_class_name}}
- Narration key: {{narration_key}}
- Title (exact match required): {{scene_title}}
- Scene details:
```json
{{scene_details}}
```
- Narration (`SCRIPT["{{narration_key}}"]`):
```text
{{scene_narration}}
```
- Broken file: {{broken_file_name}}
- Current content:
```python
{{broken_file_content}}
```
- Error:
```
{{retry_context}}
```

File naming/path selection is orchestrator-owned; do not produce or reason about filenames.

If this is a retry, build on the previous repair attempt rather than starting from scratch.

## Required Output
Return exactly one JSON object with required field `scene_body`.
- `scene_body`: non-empty string of Python scene-body statements only
- No imports, no class, no config — only statements valid inside `construct(self)`
- No `#` comments — they break JSON parsing
- No markdown, no code fences, no XML
- Do NOT include `with self.voiceover(...)` — scaffold owns that wrapper

## Hard Rules

**Repair scope:**
1. Patch ONLY what is needed to fix the reported failure
2. Preserve this scene's topic and planned meaning
3. Keep title text exactly: `{{scene_title}}`
4. Keep narration key exactly: `SCRIPT["{{narration_key}}"]`
5. Do NOT inject unrelated branding, topics, or project names

**Voice (CRITICAL):**
- Narration MUST use `SCRIPT["{{narration_key}}"]` — no hardcoded text
- NEVER import or configure any TTS service (Qwen TTS is scaffold-owned)

**Timing:**
- Use `tracker.duration` in timing expressions: `run_time=min(1.0, tracker.duration * 0.10)`
- NEVER use standalone literal timing values unscaled by `tracker.duration` (e.g., `run_time=2` is forbidden)

**Positioning:**
- After every `.next_to(...)`: immediately call `safe_position(...)`
- For every 2+ visible sibling group: call `safe_layout(...)`
- Long text: `.set_max_width(...)` or `clamp_text_width(...)`
- NEVER call `.arrange(...)` on `Text` or `MathTex`
- No text-text or text-diagram overlap in same region
- No off-frame content

**No loops in scene body** — write elements explicitly.

## Repair Validation Checklist

- [ ] All `.next_to(...)` usages followed by `safe_position(...)`
- [ ] All 2+ sibling visible groups use `safe_layout(...)`
- [ ] Long text is width-bounded
- [ ] No `.arrange(...)` on `Text` or `MathTex`
- [ ] No text-text or text-diagram overlap
- [ ] No off-frame content
- [ ] Narration accessed via `SCRIPT["{{narration_key}}"]` only
- [ ] All timing uses `tracker.duration` — no literals
- [ ] No `#` comments in scene_body
- [ ] Scene semantically faithful to narration
- [ ] Original error addressed

**REJECTION RULE:** Do not output repaired JSON until every check is true. If conflicts remain, reduce scene complexity and retry.

## Failure Behavior
If the original error cannot be fixed while preserving the scene plan, simplify the visual content to its minimal semantically-faithful form that renders without errors.
