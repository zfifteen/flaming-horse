Write the full narration for this video.

Title: {{title}}

Plan JSON:
```json
{{plan_json}}
```

Task requirements:
- Return one narration entry per scene using each scene's `narration_key` as the key.
- Cover the scene's planned teaching goal and visual intent without repeating identical phrasing across scenes.
- Keep pacing natural for voiceover (~150-180 words per minute).
- Target each scene duration within about plus/minus 5 seconds.
- Keep wording simple, direct, and beginner-friendly unless the topic requires technical terms.
- Make transitions between scenes feel continuous at the full-video level.

Critical output constraints:
- Output exactly one JSON object with this shape:
  `{"script": {"<narration_key>": "<narration text>", ...}}`
- Include all scene keys from the plan inside `script` and no extra keys outside `script`.
- Use valid JSON with double-quoted keys and strings.
- Output only the JSON object. No markdown, no code fences, no commentary.

### Self-Check Before Output

- [ ] Every scene's `narration_key` from the plan is present as a key inside `script`.
- [ ] No extra keys exist outside the `script` object.
- [ ] All narration values are non-empty strings (no placeholders like "..." or "TBD").
- [ ] Output is a single JSON object `{"script": {...}}` with no markdown or code fences.
