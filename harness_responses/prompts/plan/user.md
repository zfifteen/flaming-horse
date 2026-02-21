Create a video plan for this topic:
{{topic}}

Return a structured JSON object with:
- title (string)
- description (string)
- target_duration_seconds (integer)
- scenes (array)

Each scene must include:
- title (string)
- description (string)
- estimated_duration_seconds (integer, 20-45)
- visual_ideas (array of strings, concrete and topic-specific)

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
