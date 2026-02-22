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

Scene Descriptions:
- Describe each scene in natural language using Manim CE mobject class names (Text, MathTex, Arrow, NumberLine, BulletedList, etc.)

WRONG:
```
"visual_ideas": [
        "Transition to slightly lighter background",
        "Bullet point 1: 'There is no spoon' - showing a bent spoon image",
        "Bullet point 2: 'I can show you the truth' with opening eye visual",
        "Bullet point 3: 'Free your mind' with brain/circuit imagery",
        "Text highlights each point progressively as narration plays"
      ]
```

RIGHT:
```
{
  "visual_ideas": [
    "Set the Scene background to a slightly lighter shade by placing a FullScreenRectangle mobject with a dark gray fill and no stroke behind all other mobjects.",
    "Create a BulletedList text mobject with the first entry reading 'There is no spoon', and position this BulletedList on the left side of the Frame.",
    "For the first bullet, create a spoon-like shape from Arc and Line mobjects and place it to the RIGHT of the first bullet line so that it visually illustrates the text.",
    "Extend the same BulletedList with a second entry reading 'I can show you the truth', and for this bullet place a door icon built from Rectangle and Line mobjects to the RIGHT of the second bullet line.",
    "Add a third entry to the BulletedList reading 'Free your mind', and for this bullet build a brain-and-circuits motif using Circle and Line mobjects to the RIGHT of the third bullet line.",
    "As narration plays, successively highlight each bullet by drawing a SurroundingRectangle mobject around the active line of the BulletedList, or by reducing the opacity of all non-active Text submobjects so only the current bullet remains fully opaque."
  ]
}

```

Do NOT include "id" or "narration_key" in the scene objects – the harness will assign these automatically.
Do NOT include planning language in the scene content
- WRONG: "Content: Entering the Rabbit Hole"
- RIGHT: "Entering the Rabbit Hole"
Always provide content and visuals, NEVER allow empty scenes.

Planning constraints:
- 12-24 scenes
- 20–45 seconds per scene
- total target duration 480–960 seconds
- no empty fields
- visual ideas must be concrete and topic-specific
- visual ideas must reference Manim CE mobject classes by name; do not assume external image/SVG assets exist
- always include a final recap scene summarizing the video's key points

For non-mathematical topics, default to explainer-slide planning:
- progressive bullet reveals
- evolving right-side visual sequence
- no generic geometric filler unless directly relevant
- visible progression every ~1.5–3 seconds

Output only the JSON object. No Markdown, no code fences, no commentary.
