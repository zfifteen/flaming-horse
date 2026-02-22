## Purpose
Generate exactly ONE scene body for the specified scene.

## Inputs
- Scene ID: {{scene_id}}
- Scene class: {{scene_class_name}}
- Narration key: {{narration_key}}
- Title (exact text): {{scene_title}}
- Scene details: {{scene_details}}
- Narration (use via SCRIPT key): `SCRIPT["{{narration_key}}"] = {{scene_narration}}`

File naming/path selection is orchestrator-owned; do not produce or reason about filenames.

## Narration Timing Budget

- Word count: `{{narration_word_count}}`
- Speech rate: `{{speech_wpm}} WPM`
- Estimated duration: `{{estimated_duration_text}}` (`{{estimated_duration_seconds}}s`)

**Timing rules:**
1. Treat `{{estimated_duration_seconds}}s` as the narration timing budget.
2. Total projected time (all run_time + all wait) MUST NOT exceed `tracker.duration * 0.95`.
3. Use `tracker.duration` in ALL timing expressions — example: `run_time=min(1.0, tracker.duration * 0.10)`, `self.wait(max(0.2, tracker.duration * 0.03))`.
4. NEVER use standalone literal timing values unscaled by `tracker.duration` (e.g., `run_time=2` is forbidden; `run_time=min(1.0, tracker.duration * 0.10)` is required).
5. Keep a consistent cadence: introduce or evolve visual state every ~1.5–3 seconds.
6. Do not clear all non-title elements before narration ends.
7. Use transitions (Transform, FadeTransform) instead of full-frame clears.
8. If scene overruns, simplify visuals; if it underruns, extend with visual evolution.

## Required Output Format
- Return exactly one JSON object with required field `scene_body`
- `scene_body` is a string of Python statements separated by `\n`
- Example: `"title = Text(\"Hello\")\ntitle.move_to(UP * 3)"`
- No Markdown, no code fences, no XML wrappers

## What scene_body MUST contain
- Variable assignments
- `self.play(...)` calls
- `self.wait(...)` calls
- Method calls on mobjects

## What scene_body MUST NOT contain
- `import` statements (scaffold provides these)
- `class` or `def` definitions
- `# comments` — THESE BREAK JSON PARSING
- `config` assignments
- `with self.voiceover(...)` — scaffold already owns this wrapper
- `self.add(...)` for first-time visible reveals (use `self.play(...)` instead)
- `.to_edge(UP)` for titles/labels
- `random` module usage — use deterministic hardcoded values only
- `play_next(...)` or `play_text_next(...)`

## Hard Rules

**Voice (CRITICAL):**
- Use ONLY `SCRIPT["{{narration_key}}"]` for narration — DO NOT hardcode narration text
- The scaffold provides `flaming_horse_voice` — do NOT import or configure TTS

**Timing:**
- NEVER use standalone literal timing values unscaled by `tracker.duration` (e.g., `run_time=2` is forbidden)
- Always scale to `tracker.duration`: `run_time=min(1.2, tracker.duration * 0.15)`
- Every scene body MUST reference `tracker.duration` in timing expressions

**Positioning (CRITICAL):**
- Title MUST use: `title = Text("{{scene_title}}", font_size=48, weight=BOLD)` then `.move_to(UP * 3.8)`
- After every `.next_to(...)` call, immediately call `safe_position(...)` on the same mobject
- For every VGroup with 2+ visible siblings, call `safe_layout(...)` on those siblings
- Every long `Text(...)` must use `.set_max_width(...)` or `clamp_text_width(...)`
- NEVER call `.arrange(...)` on `Text` or `MathTex` objects

**Colors:**
- ALWAYS use hex color strings: `color="#0000FF"` not `color=BLUE`
- If Kitchen Sink examples use named colors, this hex rule wins

**Geometry:**
- For Polygon: pass vertices as individual args — `Polygon(v1, v2, v3)` or `Polygon(*verts)`
- NEVER: `Polygon([v1, v2, v3])` (list form causes errors)

**Content:**
- Keep content inside the visible frame boundaries (x: ±7, y: ±4)
- Maintain visible spacing between stacked text (buff >= 0.25 with next_to)
- NEVER overlap text at the same coordinates

**LaTeX:**
- Use `MathTex(r"... \times ...")` (single backslash in raw string)
- Use `MathTex` for equations, `Tex` for formatted text only

**Axis Labels:**
- CORRECT: `x_label = axes.get_x_axis_label("x")` then `.set(font_size=24)`
- WRONG: `axes.get_x_axis_label("x", font_size=24)` — font_size is not a valid parameter

{{reference_section}}
{{retry_section}}

## Self-Check Before Returning JSON

- [ ] All `.next_to(...)` calls immediately followed by `safe_position(...)`
- [ ] All visible sibling groups (2+) passed through `safe_layout(...)`
- [ ] All long `Text(...)` width-bounded with `.set_max_width(...)` or `clamp_text_width(...)`
- [ ] No `.arrange(...)` on `Text` or `MathTex`
- [ ] No two text blocks at the same center coordinates
- [ ] No text or diagram outside visible frame
- [ ] Left, center, and right content bands do not overlap
- [ ] All timing expressions use `tracker.duration` — no literal values
- [ ] No `#` comments in scene_body (they break JSON parsing)
- [ ] Narration accessed via `SCRIPT["{{narration_key}}"]` only
- [ ] Planned visual timeline ~matches `{{estimated_duration_seconds}}s`
- [ ] At least one meaningful visual remains visible until narration ends
- [ ] scene_body is valid Python (no imports, classes, or functions)

**REJECTION RULE:** If any check is false, revise scene_body until all checks pass, then return JSON.

## Failure Behavior
If the scene plan is too complex to satisfy all rules, simplify the visual content (fewer elements, simpler geometry) rather than violating any hard rule. Return working minimal scene body rather than a complex broken one.
