- Read AGENTS.md CAREFULLY before writing or editing any scene code.
MANDATORY: ALWAYS follow the scene examples syntax from `reference_docs/manim_template.py.txt` EXACTLY.
- Infrastructure tasks are owned by the orchestrator. Do NOT run scaffold scripts, shell setup commands, or state-management commands.
- Target scene for this run:
  - id: `{{TARGET_SCENE_ID}}`
  - file: `{{TARGET_SCENE_FILE}}`
  - class: `{{TARGET_SCENE_CLASS}}`
  - narration key: `{{TARGET_NARRATION_KEY}}`
- Edit ONLY the target scene file above.
- Never write scene files from scratch. Update only the editable slot block between:
  - `# SLOT_START:scene_body`
  - `# SLOT_END:scene_body`
- Keep protected scaffold structure unchanged (imports, config, helpers, speech service setup, voiceover wrapper).
- Use Create for mobjects/lines/curves (e.g., Create(curve, rate_func=smooth)).
- Use Write for text (cap at 1.5s) and FadeIn for reveals.
- NEVER invent animations like ShowCreation (causes NameError).
- Manim CE 0.19 compatibility rules:
  - NEVER use `from manim.utils.color import Color`.
- NEVER pass `lag_ratio` or `scale_factor` directly to `FadeIn(...)`.
- For staggered reveals, use `LaggedStart(FadeIn(a), FadeIn(b), ..., lag_ratio=...)`.
- Use built-in color constants (`BLUE`, `YELLOW`, etc.) or `.set_color(...)`.
- NEVER enable optional alignment extras.
- Mentally validate: does the code import manim correctly and run without NameError?
- Layout contract: Title at UP * 3.8, subtitle directly below, graphs/diagrams moved DOWN * 0.6 to 1.2, no .to_edge(...) for titles/labels, safe_layout for 2+ siblings, safe_position after .next_to().

SEMANTIC VALIDATION REQUIREMENTS:

Your scene MUST pass these validation checks:

1. **Non-empty construct() body**: The construct() method must contain substantive animation logic, not just `pass` or empty body. Include actual self.play(), self.wait(), and mobject creation.

2. **Valid narration wiring**: Use `with self.voiceover(text=SCRIPT["{{TARGET_NARRATION_KEY}}"]) as tracker:` and keep `SCRIPT` imported from `narration_script.py`.

3. **Proper timing flow**: Include self.wait() calls between animation sequences for pacing. Don't chain self.play() calls without timing.

4. **No placeholder code**: Remove all TODO/FIXME comments from construct() body. Implement actual animations.

5. **Valid animations**: Ensure all self.play() calls have valid animation arguments. No empty self.play().

6. **Syntax correctness**: Code must parse without SyntaxError. Test mentally before finalizing.

Common validation failures to avoid:
- Empty construct() or only `pass`
- Missing `SCRIPT` import
- Voiceover not using `SCRIPT[...]` narration key
- No self.wait() calls (animations need timing)
- self.play() with no arguments
- TODO/FIXME placeholders in construct()
- Syntax errors from incomplete edits

Validation runs automatically after build. Fix issues proactively to avoid self-heal loop.
