# Core Rules for Flaming Horse Agent

**These rules apply to ALL phases and MUST NEVER be violated.**

---

## 🚨 CRITICAL: VOICE POLICY - READ THIS FIRST

### Local Qwen Voice Clone - No Fallback

**ABSOLUTE REQUIREMENTS:**
- ✅ **ONLY** local Qwen voice clone audio cached on disk (no network TTS).
- ✅ **Model:** `Qwen/Qwen3-TTS-12Hz-1.7B-Base` (voice clone).
- ✅ **Device/Dtype:** CPU `float32` for stability.
- ✅ **Reference assets:** `assets/voice_ref/ref.wav` + `assets/voice_ref/ref.txt` per project.
- ❌ **NEVER** use any network TTS service (e.g., ElevenLabs, Google TTS, Azure TTS).
- ❌ **NEVER** create fallback code patterns.

**If cached audio is missing, the build MUST fail and instruct to run the precache step.**

---

## 🚨 CRITICAL: Execution Protocol

**When the user says "proceed", "execute", "continue", or "approve":**

- ❌ **NEVER** present another detailed plan
- ❌ **NEVER** ask "Does this align with your vision?"
- ❌ **NEVER** request confirmation again
- ✅ **IMMEDIATELY** execute the current phase's tasks

**Maximum confirmation rounds: ONE per phase.**

The intent of this system is to generate videos from a single prompt without approval loops.

---

## 🚨 CRITICAL RULES - NEVER VIOLATE

### 1. Voice Configuration
- ❌ **NEVER** use any network TTS service
- ❌ **NEVER** create conditional fallback patterns
- ❌ **NEVER** import other TTS services
- ❌ **NEVER** enable optional alignment extras or cloud features
- ✅ **ALWAYS** use cached Qwen voice via `flaming_horse_voice.get_speech_service`

### 2. Import Naming (Python Module Convention)
- ❌ **WRONG:** `from manim-voiceover-plus import ...` (hyphens = SyntaxError)
- ❌ **WRONG:** `import manimvoiceoverplus` (no separators = ModuleNotFoundError)
- ✅ **CORRECT:** `from manim_voiceover_plus import VoiceoverScene` (underscores)

### 3. Narration Text
- ❌ **NEVER** hardcode narration in scene files
- ✅ **ALWAYS** use `SCRIPT["key"]` from `narration_script.py`

### 4. Positioning
- ❌ **NEVER** use `.to_edge(UP)` for titles (causes clipping)
- ✅ **ALWAYS** use `.move_to(UP * 3.8)` for titles (or adaptive_title_position)
- ✅ **ALWAYS** call `safe_position()` after `.next_to()`
- ❌ **NEVER** use `.to_edge(...)` for titles or labels (causes clipping/edge drift)
- ✅ **ALWAYS** place graphs/diagrams below the subtitle (e.g., `.move_to(DOWN * 0.6)`)
- ✅ **ALWAYS** call `safe_layout(...)` when positioning 2+ siblings in a group

### 5. Configuration Lock
- ✅ **ALWAYS** use locked config block (frame size, resolution)
- ✅ **ALWAYS** include Python 3.13 compatibility patch
- ✅ **ALWAYS** include `safe_position()` helper

### 6. LaTeX Rendering
- ✅ **ALWAYS** use `MathTex` for mathematical expressions: `MathTex(r"\\frac{GMm}{r^2}")`
- ✅ **ALWAYS** use `Tex` for plain text with LaTeX formatting only
- ❌ **NEVER** use `Tex` for equations (causes rendering failures)
- ❌ **NEVER** pass `weight=` to `MathTex`/`Tex` (unsupported; causes runtime TypeError)
- ✅ Use `weight=` only with `Text(...)`, or emphasize math with color/scale/animation instead

### 7. Positioning and Overlap Prevention
- ❌ **NEVER** place multiple elements at ORIGIN without explicit offsets
- ❌ **NEVER** use `.next_to()` without immediately calling `safe_position()`
- ✅ **ALWAYS** call `safe_layout(*elements)` on any VGroup with 2+ sibling elements
- ✅ **ALWAYS** use explicit coordinates: `element.move_to(UP * 2 + LEFT * 3)`

---

## 🎨 VISUAL QUALITY RULES

### Text Animation Speed
- ✅ Text must appear quickly and consistently
- ❌ NEVER let any text animation take longer than 1.5 seconds
- ✅ For staggered reveals, use `LaggedStart(FadeIn(a), FadeIn(b), ..., lag_ratio=0.15)`

### Content Density Per Scene
- ✅ Maintain high informational density for non-math topics using explainer-slide structure
- ✅ Use progressive bullets plus evolving right-side visuals instead of sparse placeholder scenes
- ✅ If content is too dense for one block, split across multiple voiceover segments
- ✅ Remove (FadeOut/Transform) previous elements before introducing new ones

### Element Cleanup
- ✅ ALWAYS FadeOut previous section content before new section begins
- ✅ Exception: titles/headers that persist across segments
- ❌ NEVER let more than 2 "layers" of content coexist on screen

### Animation Smoothness
- ✅ Use `rate_func=smooth` for most transitions (this is the default)
- ✅ Minimum run_time for any visible animation: 0.3 seconds
- ❌ NEVER set run_time < 0.2 (imperceptible, creates visual artifacts)
- ✅ For sequential reveals, use lag_ratio=0.1 to 0.3

### Continuous Motion Standard
- ❌ NEVER leave long static/black intervals where little changes on screen
- ✅ Target a visible visual state change every ~1.5-3 seconds
- ✅ For non-math topics, default to explainer-slide cadence: title/subtitle, progressive bullets, evolving diagram, recap/callout
- ❌ Avoid generic filler visuals (single circle/ellipse/equation) unless explicitly topic-relevant
