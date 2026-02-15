- Read AGENTS.md CAREFULLY before writing or editing any scene code.
MANDATORY: ALWAYS follow the scene examples syntax from attached manim_template.py.txt EXACTLY.
- Use Create for mobjects/lines/curves (e.g., Create(curve, rate_func=smooth)).
- Use Write for text (cap at 1.5s) and FadeIn for reveals.
- NEVER invent animations like ShowCreation (causes NameError).
- ALWAYS use the Write tool to create scene_XX.py. Do NOT print code blocks; confirm tool use.
- NEVER enable optional alignment extras.
- Mentally validate: does the code import manim correctly and run without NameError?
- Layout contract: Title at UP * 3.8, subtitle directly below, graphs/diagrams moved DOWN * 0.6 to 1.2, no .to_edge(...) for titles/labels, safe_layout for 2+ siblings, safe_position after .next_to().
