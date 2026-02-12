Key finding: the pain points map cleanly to gaps, contradictions, and a few outright bugs inside the Space reference docs. Several of these docs actively teach patterns that predictably produce the reported failures (overlap, audio desync, missing artifacts, wrong env var names, and “done” claims without verification).

Below is a pain point to doc issue map, then concrete recommended revisions per Space file.

---

## Pain point to Space doc issue mapping

### 1) Persistent element overlapping
Contributing issues in Space docs:
- `safe_position()` only clamps vertical bounds. It does not prevent overlaps, does not manage spacing, and does not manage z-order. The pain points mention missing `bring_to_front()`, but none of the core refs require it for text.
- `manim_template.py.txt` demonstrates repeated `move_to(ORIGIN)` for multiple objects, which is a “overlap by default” pattern once scenes get more complex.
- `AGENTS.md` includes an “overlap prevention” helper (`check_overlap`) that is incorrect as written. It mixes vectors and scalars and will not work reliably, so agents either skip it or copy broken code.

### 2) Animations under-implemented vs plan
Contributing issues:
- `AGENTS.md` defines plan creation but does not define any “plan fidelity gate” that checks that each planned animation beat is implemented in code before moving phase forward.
- `AGENTS.md` “review” phase pushes conservative constraints (avoid 3D, avoid custom mobjects) without offering an approved library of mid-complexity patterns (particles, gradients, labeled charts) that are still feasible. Agents then retreat to basic shapes and fades.
- `HOW_TO_ANIMATE.md` is a kitchen sink of advanced examples, but it is not normalized to your production constraints (locked frame, safe zones, VoiceoverScene timing), so it fails as an actionable implementation reference for nontrivial but production safe animation patterns.

### 3) Audio and voiceover failures (cut-outs, clipping, sync)
Contributing issues:
- Contradictory sync guidance:
  - `manim_voiceover.md` correctly emphasizes the context manager auto-waits and warns you often do not need explicit waits.
  - `AGENTS.md` teaches “timing fractions sum to 1.0” and explicitly uses `self.wait(tracker.duration * 0.1)` as a “buffer” pattern. This is easy to misuse and encourages adding waits that cause mismatch behavior.
- Environment variable naming is inconsistent across docs, which contributes to silent ElevenLabs failures:
  - `README.md` uses `ELEVENLABS_API_KEY`
  - `manim_voiceover.md` uses `ELEVENLABS_API_KEY`
  - `manim_content_pipeline.md` mentions `ELEVENLABSAPIKEY` and also mentions a `MANIMVOICEPROD` toggle
  - Pain points mention `ELEVEN_API_KEY` and `ELEVENLABSAPIKEY` style keys appearing in sessions
- No explicit preflight validation step exists in `AGENTS.md` for “is ElevenLabs key present and working” before starting a render phase.

### 4) False completion claims
Contributing issues:
- `AGENTS.md` says “verify output exists”, but does not require concrete commands and logging before claiming completion. There is no “artifact verification contract” such as:
  - check file exists
  - check nonzero size
  - check duration roughly matches narration
  - check audio stream exists
- `AGENTS.md` final_render and assemble steps do not require enumerating scenes and proving all expected outputs exist before updating state.

### 5) Files created in wrong locations
Contributing issues:
- `AGENTS.md` says “Create a new folder under projects” but does not specify naming rules, and does not explicitly forbid placeholder directory names. It also does not force the canonical scaffold described in `README.md` (`scenes/` subfolder).
- `AGENTS.md` scene file examples omit `scenes/` in paths, which can normalize “dump into project root” behavior.

### 6) Excessive planning without execution
Contributing issues:
- `AGENTS.md` uses “If approved…” language in multiple phases without defining when approval is required versus when the agent must proceed automatically.
- `manim_content_pipeline.md` encourages stage awareness but does not provide a “default action policy” like: if phase is clear, proceed, only stop when `needs_human_review` is set.

### 7) Timing budget errors
Contributing issues:
- `AGENTS.md` states the rule but provides no mechanism for validation (no helper, no assertion pattern, no lint step).
- The fraction budgeting approach is brittle. Agents will sometimes omit it entirely (as seen in pain points) because it is extra bookkeeping.

### 8) Tex vs MathTex errors
Contributing issues:
- `HOW_TO_ANIMATE.md` uses `Tex` for math expressions in examples. This trains agents into the wrong default for math mode heavy content.
- None of the core docs include a crisp rule: “Math content goes to MathTex; Tex is for text layout.”

### 9) Numpy array dimension errors
Contributing issues:
- `HOW_TO_ANIMATE.md` contains many `np.array` usage patterns and ManimGL style code that can confuse CE expectations. The core docs never state a simple invariant: “All points are 3D vectors [x, y, 0].”

### 10) Missing labels, legends, annotations
Contributing issues:
- No doc treats labeling as a hard requirement for charts and diagrams. It is discussed as an aesthetic nice-to-have, so agents omit it under time pressure.

### 12) Incomplete rendering (only first scene)
Contributing issues:
- `AGENTS.md` final_render is defined as “render all scenes”, but the overall system is “one phase transition per invocation”. In practice, long renders can time out, so the agent renders scene 1, then incorrectly reports the phase complete.
- There is no incremental render index in state for final_render similar to build_scenes. This makes partial progress hard to represent honestly.

### 13) ElevenLabs API key not properly configured
Contributing issues:
- Env var name mismatch across docs, plus no preflight check, plus “fail loud” policy without a specific failure detection pattern.

---

## Recommended revisions by Space file

## 1) AGENTS.md (highest leverage to fix)
### A. Remove contradictions and normalize naming
1) Fix the hard contradiction:
- Currently near top: “All animations of text must have a duration of 2 seconds.”
- Later: “NEVER use a fixed 2-second run_time for all text.”

Revision:
- Delete the “2 seconds” requirement entirely.
- Keep and elevate the adaptive guidance (length based) as the single rule.

2) Normalize ElevenLabs env var to exactly one key across all docs:
- Use `ELEVENLABS_API_KEY` everywhere.
- Add an explicit line: “Do not use ELEVENLABSAPIKEY, ELEVEN_API_KEY, or other aliases.”

### B. Fix the broken overlap helper and make overlap prevention actionable
1) Replace the `check_overlap` snippet with a correct version:

- Use y scalars for top/bottom and x scalars for left/right.
- Provide `overlaps(a, b, buff=0.05)` and `assert_no_overlaps(mobjects)`.

2) Add a required layout pattern:
- For stacked text blocks: use `VGroup(...).arrange(DOWN, buff=...)`, then `safe_position(group)`.
- For side by side: `arrange(RIGHT, buff=...)`.
- For “title + content + footer”: reserve lanes (top band, mid band, bottom band) and explicitly place.

3) Add a z-order rule:
- “All text must be on top of shapes.” Provide a canonical call:
  - `text.set_z_index(10)` or `self.bring_to_front(text)` depending on your Manim version conventions.

### C. Replace brittle timing fraction policy with a safer default
Right now, timing fractions are a frequent failure mode.

Recommended policy rewrite:
- Default: inside each `with self.voiceover(...)` block, do not manually budget fractions unless necessary.
- Preferred patterns:
  1) One primary animation uses `run_time=tracker.duration` and any sub-animations use short fixed times.
  2) If splitting, compute durations programmatically and validate.

Add a helper snippet in AGENTS.md:
```python
def allocate(tracker_duration, weights):
    s = sum(weights)
    assert s > 0
    fracs = [w / s for w in weights]
    return [tracker_duration * f for f in fracs]
```
Also add:
- “Never call `self.wait(tracker.duration * X)` as a buffer.”
- If you must wait, use remaining time only, and only if the library supports it:
  - `remaining = tracker.get_remaining_duration()` then `self.wait(remaining)`.

### D. Add mandatory preflight checks for ElevenLabs
Before any rendering phase:
- Verify env var exists: `ELEVENLABS_API_KEY`.
- Fail fast with a clear error in `state['errors']` if missing.
- Optionally add a minimal “smoke test” voiceover block render for a 1 line scene if your pipeline supports it.

### E. Add hard “artifact verification gates” to prevent false completion claims
For final_render:
- After each scene render, require:
  - `test -f <expected_path>`
  - `stat -f%z <file>` (or platform equivalent) and check > 0
  - `ffprobe` check for audio stream presence (if ffprobe available)

For assemble:
- After ffmpeg, require:
  - `test -f final_video.mp4`
  - nonzero size
  - `ffprobe` duration > sum of scene durations minus tolerance

Make it explicit:
- “Do not claim a file exists unless you have just verified it.”

### F. Make rendering incremental to avoid “only scene 1” outcomes
Revise project_state schema in AGENTS.md:
- Add `current_render_index` similar to `current_scene_index`.
- final_render phase renders exactly one scene per invocation and advances index.
- Only when all scenes are rendered does phase advance to assemble.

This single change directly addresses pain point 12 because partial progress is representable and completion claims become unambiguous.

### G. Fix command inconsistencies
AGENTS.md currently uses `manim render <file> <SceneClass> -qh` but other docs use `manim <file> <SceneClass>`.

Pick one canonical command and repeat it everywhere. Recommended:
- `manim <file>.py <SceneClass>`

If you must use flags, specify why and ensure they do not override locked config.

### H. Require labels and legends as part of “definition of done”
Add a section under VISUAL QUALITY RULES:
- Any axis based chart must have:
  - axis labels
  - tick marks or scale cues
  - a legend if multiple series
- Any metaphor diagram must have at least one label anchoring meaning.

---

## 2) manim_content_pipeline.md
Problems to fix:
- Mentions `ELEVENLABSAPIKEY` and a `MANIMVOICEPROD` toggle, both conflict with the “ElevenLabs only, no dev mode” policy.
- Mentions bookmarks but does not strongly gate them against Python 3.13 constraints.

Recommended edits:
1) Replace all mentions of `ELEVENLABSAPIKEY` with `ELEVENLABS_API_KEY`.
2) Remove “Optional MANIMVOICEPROD toggle” entirely, or mark it as prohibited for this repo.
3) Add a “Python 3.13 bookmark disclaimer” near bookmark guidance:
- “Bookmarks require transcribe extras. If the project uses the transcription patch and `transcription_model=None`, bookmarks will not work. Default to duration based sync.”

---

## 3) manim_voiceover.md
This doc is mostly solid, but it needs two changes to reduce the observed failures:

1) Add an explicit “Do not add buffer waits” warning aligned with the pain point:
- Reiterate: the context manager already waits to the end of audio.
- Provide one blessed way to fill leftover time if needed (remaining duration method), and forbid fixed fractional waits.

2) Expand troubleshooting for missing API key:
- Add: “If ElevenLabs key is missing, the render can fail in ways that look like silent success if you do not check output artifacts. Always preflight check env var and verify media outputs.”

Optional but useful:
- In the ffmpeg concat section, add a note that `-c copy` can produce odd timestamp behavior in some cases, and provide a safer re-encode fallback command (still “production”, not a TTS fallback):
  - concat demuxer with re-encode to H.264 + AAC.

---

## 4) manim_template.py.txt
Recommended edits to reduce overlap by default:

1) Add a horizontal clamp option to `safe_position`, or create `safe_frame(mobject, max_x=7.0, min_x=-7.0, max_y=4.0, min_y=-4.0)`.

2) Add layout helpers directly into the template:
- `stack_vgroup(items, top_y=2.5, buff=0.35)` that:
  - uses `arrange(DOWN, buff=buff, aligned_edge=LEFT)`
  - positions as a group
  - calls safe_frame on the group

3) Add a “text readability” helper:
- `add_background_rectangle` or a semi-transparent Rect behind text when placed over shapes.

4) Update examples to avoid repeated ORIGIN placement:
- Demonstrate lane based layout: title at top, diagram mid, legend bottom.

---

## 5) manim_config_guide.md
Add guidance that addresses overlap, not only clipping:
- New section: “Overlap is not clipping”
  - show how to use `arrange` and group layout
  - show how to reserve regions of the screen
  - recommend a visible debug overlay (safe zone lines plus optional grid)

Add z-order guidance:
- “Text should set z_index above shapes.”

---

## 6) HOW_TO_ANIMATE.md
This file is useful but currently hazardous because it normalizes patterns that your other docs forbid (notably `.to_edge(UP)` for titles) and it is not clearly scoped to Manim Community Edition with your locked framing.

Recommended revisions:
1) Add an explicit header at top:
- “Many examples come from ManimGL or custom 3Blue1Brown codebases. They may violate this repo’s safe-zone rules. Do not copy positioning of titles directly.”

2) Mark incompatible patterns inline:
- `.to_edge(UP)` and `.to_corner(UL)` for titles should be flagged as likely to clip under your locked frame rules.

3) Replace math examples using `Tex` with `MathTex` when the content is math mode.

4) Add a small “Manim CE invariants” section:
- 3D point vectors must be `[x, y, 0]`
- use `safe_position` or safe_frame after layout
- prefer `VGroup.arrange` over manual stacking

This will directly reduce pain points 8 and 9 and indirectly reduce overlap by teaching correct layout primitives.

---

## 7) README.md
Two fixes:
1) It links to `docs/VOICE_POLICY.md` which does not exist in the Space files list. Either add that file or remove the link to avoid sending agents on a dead path.
2) Reinforce the canonical artifact layout:
- Scenes must live under `projects/<name>/scenes/`
- final output must be `projects/<name>/final_video.mp4`
- explicitly say “never create artifacts in repo root”

---

## Quick “most important edits” shortlist
If you only do 5 edits, do these:
1) AGENTS.md: delete the “2 seconds for all text” requirement and keep adaptive text timing only.
2) AGENTS.md: normalize env var to `ELEVENLABS_API_KEY` and add a preflight check requirement.
3) AGENTS.md: make final_render incremental with `current_render_index` and require per-scene artifact verification before marking rendered.
4) AGENTS.md: fix or remove the broken `check_overlap` snippet, replace with a correct `assert_no_overlaps` utility and require lane based layout plus `arrange`.
5) HOW_TO_ANIMATE.md: add a strong compatibility warning plus replace `Tex` math examples with `MathTex` and flag `.to_edge(UP)` title usage as incompatible with the safe zone policy.

These align the reference docs with the actual failure modes in `pain_points.md` and should materially reduce recurrence.