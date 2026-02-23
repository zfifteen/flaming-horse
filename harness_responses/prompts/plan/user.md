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
- estimated_duration_seconds (positive integer)
- visual_ideas (array of strings, concrete and topic-specific)
- use natural language describing how to render and manipulate Manim objects as per the Manim documentation 

Planning constraints:
- no empty fields
- visual ideas must be concrete and topic-specific

For non-mathematical topics, default to explainer-slide planning:
- progressive bullet reveals
- evolving right-side visual sequence
- no generic geometric filler unless directly relevant
- visible progression every ~1.5-3 seconds
