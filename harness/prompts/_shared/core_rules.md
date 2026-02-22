# Core Rules for Flaming Horse Agent

These rules apply to ALL phases and MUST NEVER be violated.

---

## CRITICAL: VOICE POLICY

**Voice: Local Qwen Clone Only. No Fallback. No Network TTS.**

- Use ONLY cached local Qwen voice: `Qwen/Qwen3-TTS-12Hz-1.7B-Base`
- Reference assets per project: `assets/voice_ref/ref.wav` + `assets/voice_ref/ref.txt`
- Always use via `flaming_horse_voice.get_speech_service`
- NEVER use any network TTS service (ElevenLabs, Google TTS / gTTS package, Azure TTS, OpenAI TTS)
- NEVER create fallback code patterns or import other TTS services
- If cached audio is missing, the build MUST fail with instructions to run the precache step

---

## CRITICAL: Execution Protocol

When the user says "proceed", "execute", "continue", or "approve":
- IMMEDIATELY execute the current phase tasks
- NEVER present another detailed plan or ask for confirmation again
- Maximum confirmation rounds: ONE per phase

---

## HARD RULES (Never Violate)

### Import Naming
- CORRECT: `from manim_voiceover_plus import VoiceoverScene` (underscores)
- WRONG: `from manim-voiceover-plus import ...` (hyphens = SyntaxError)
- WRONG: `import manimvoiceoverplus` (no separators = ModuleNotFoundError)

### Narration Text
- ALWAYS use `SCRIPT["key"]` from `narration_script.py`
- NEVER hardcode narration text in scene files

### Positioning
- ALWAYS use `.move_to(UP * 3.8)` for titles (not `.to_edge(UP)`)
- ALWAYS call `safe_position()` after `.next_to()`
- ALWAYS call `safe_layout(...)` when positioning 2+ siblings in a group
- ALWAYS place graphs/diagrams below subtitle (e.g., `.move_to(DOWN * 0.6)`)
- NEVER use `.to_edge(...)` for titles or labels (causes clipping/edge drift)
- NEVER place multiple elements at ORIGIN without explicit offsets

### Configuration Lock
- ALWAYS include locked config block (frame size, resolution) in every scene
- ALWAYS include Python 3.13 compatibility patch
- ALWAYS include `safe_position()` helper

### LaTeX Rendering
- ALWAYS use `MathTex` for mathematical expressions: `MathTex(r"\frac{GMm}{r^2}")`
- ALWAYS use `Tex` for plain text with LaTeX formatting only
- NEVER use `Tex` for equations (causes rendering failures)
- NEVER pass `weight=` to `MathTex`/`Tex` (unsupported; causes runtime TypeError)
- Use `weight=` only with `Text(...)`, or emphasize math with color/scale/animation

### Layout
- NEVER place two text objects at the same coordinates
- ALWAYS call `safe_layout(*elements)` on any VGroup with 2+ sibling elements
- ALWAYS use explicit coordinates: `element.move_to(UP * 2 + LEFT * 3)`

---

## VISUAL QUALITY RULES

### Text Animation Speed
- Text must appear quickly and consistently
- NEVER let any text animation take longer than 1.5 seconds
- For staggered reveals: `LaggedStart(FadeIn(a), FadeIn(b), ..., lag_ratio=0.15)`

### Content Density Per Scene
- Maintain high informational density for non-math topics using explainer-slide structure
- Use progressive bullets plus evolving right-side visuals
- If content is too dense, split across multiple voiceover segments
- Use section transitions that preserve at least one anchor visual (crossfade/transform preferred over full clear)

### Animation Smoothness
- Use `rate_func=smooth` for most transitions (this is the default)
- Minimum run_time for any visible animation: 0.3 seconds
- NEVER set run_time < 0.2 (imperceptible, creates visual artifacts)
- For sequential reveals: use lag_ratio=0.1 to 0.3

### Scene Occupancy
- Keep at least one meaningful visual cluster visible until the voiceover block ends
- Do not clear all non-title content before narration ends
- Transition by replacing content (Transform/FadeTransform), not emptying the frame
- Maintain readable contrast on dark backgrounds
- Target a visible visual state change every ~1.5–3 seconds
