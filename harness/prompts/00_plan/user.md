## Purpose
Create a detailed video plan for the given topic.

## Inputs
- Topic: {{topic}}

## Required Output
Return exactly one JSON object with NO Markdown fences, no commentary:
- `title` (string)
- `description` (string)
- `target_duration_seconds` (integer)
- `scenes` (array)

Each scene must include:
- `title` (string)
- `description` (string)
- `estimated_duration_seconds` (integer)
- `visual_ideas` (array of strings)

**Do NOT include `id` or `narration_key` in scene objects — the harness assigns these automatically.**

## Hard Rules

**Scene count and duration:**
- 12–24 scenes
- 20–45 seconds per scene
- Total target duration: 480–960 seconds
- No empty fields; always include content and visuals

**Visual ideas format** — each entry must be a concrete, actionable Manim CE implementation sentence:
- Reference Manim CE mobject class names by name (Text, MathTex, BulletedList, Arrow, NumberLine, etc.)
- Specify placement and relationship of each element explicitly
- Do NOT use vague descriptions like "show bullet points" or "transition background"
- Do NOT assume external image/SVG assets exist
- Example WRONG: `"Bullet point 1: 'There is no spoon'"`
- Example RIGHT: `"Create a BulletedList mobject with entry 'There is no spoon' positioned LEFT of frame center; place an Arc/Line spoon shape to the RIGHT of the entry."`

**Non-mathematical topics:** default to explainer-slide planning:
- Progressive bullet reveals
- Evolving right-side visual sequence
- No generic geometric filler unless directly relevant
- Visible progression every ~1.5–3 seconds

**Planning language:** never allow empty scenes or generic filler
- WRONG: "Content: Entering the Rabbit Hole"
- RIGHT: "Entering the Rabbit Hole"

## Self-Check Before Responding
- [ ] All scenes have title, description, estimated_duration_seconds, and visual_ideas
- [ ] visual_ideas reference Manim CE mobject class names explicitly
- [ ] Scene count is between 12 and 24
- [ ] Per-scene duration is between 20 and 45 seconds
- [ ] Total duration is between 480 and 960 seconds
- [ ] Final scene is a recap of the video's key points
- [ ] Output is valid JSON only — no Markdown, no code fences, no commentary

## Failure Behavior
If the topic is too narrow for 12 scenes at 20–45s each, create composite scenes that cover related subtopics. Never return fewer than 12 scenes.
