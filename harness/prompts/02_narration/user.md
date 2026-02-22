## Purpose
Write full narration for each scene in the video plan.

## Inputs
- Title: {{title}}
- Plan JSON:
```json
{{plan_json}}
```

## Required Output
Return exactly one JSON object:
`{"script": {"<narration_key>": "<narration text>", ...}}`

- One entry per scene using each scene's `narration_key` as the key
- Include ALL scene keys from the plan inside `script`
- No extra keys outside `script`
- Valid JSON with double-quoted keys and strings
- Output ONLY the JSON object — no markdown, no code fences, no commentary

## Hard Rules
- Cover each scene's planned teaching goal and visual intent
- Do not repeat identical phrasing across scenes
- Pacing: ~150–180 words per minute (natural voiceover speed)
- Target each scene duration within ±5 seconds of its estimated_duration_seconds
- Keep wording simple, direct, beginner-friendly (unless topic requires technical terms)
- Make transitions between scenes feel continuous at the full-video level

## Soft Guidelines
- Prefer concrete phrasing over abstract filler
- Avoid stage directions or production notes in narration text
- Maintain continuity so the script feels like one coherent lesson

## Self-Check Before Responding
- [ ] Every scene's narration_key is present in the output
- [ ] No scene narration is empty or placeholder-only text
- [ ] Pacing is approximately 150-180 WPM per scene
- [ ] Output is valid JSON only

## Failure Behavior
If a scene description is ambiguous, write narration that best matches the scene title and surrounding context. Never omit a scene key.
