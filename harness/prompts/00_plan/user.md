Create a video plan for this topic:
{{topic}}

Return one JSON object with:
- title (string)
- description (string)
- target_duration_seconds (integer)
- scenes (array)

Each scene must include:
- title (string)
- description (string)
- estimated_duration_seconds (integer)
- visual_ideas (array of strings)

Do NOT include "id" or "narration_key" in the scene objects - the harness will assign these automatically.

Planning constraints:
- 8-12 scenes
- 20-45 seconds per scene
- total target duration 240-480 seconds
- no empty fields
- visual ideas must be concrete and topic-specific

For non-mathematical topics, default to explainer-slide planning:
- progressive bullet reveals
- evolving right-side visual sequence
- no generic geometric filler unless directly relevant
- visible progression every ~1.5-3 seconds

Output only the JSON object. No markdown, no code fences, no commentary.
