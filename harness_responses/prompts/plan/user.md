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
- 
Natural language scene descriptions:
use natural language to describe each of these Manim objects (Mobject) in scenes, how to render, animate and manipulate Manim objects as per the Manim reference documentation:
- frame
- geometry
- graph
- graphing
- logo
- matrix
- mobject
- svg
- table
- text
- three_d
- types
- utils
- value_tracker
- vector_field

Animations – describe, in natural language, the behavior of objects in scenes using the syntaxt from Manim reference documentation:
- animation
- changing
- composition
- creation
- fading
- growing
- indication
- movement
- numbers
- rotation
- specialized
- speedmodifier
- transform
- transform_matching_parts
- updaters


Planning constraints:
- no empty fields
- visual ideas must be concrete and topic-specific

For non-mathematical topics, default to explainer-slide planning:
- progressive bullet reveals
- evolving right-side visual sequence
- no generic geometric filler unless directly relevant
- visible progression every ~1.5-3 seconds
