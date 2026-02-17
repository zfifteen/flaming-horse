Highest leverage finding: several Space reference docs conflict with each other on filenames, Manim CLI flags, “dev mode” environment variables, and text animation timing rules. Those inconsistencies can directly produce the exact failures in `pain_points.md`, especially “final video does not exist”, partial renders being reported as complete, audio desync from extra waits, and chronic overlaps from a too-weak positioning helper.

Below are the Space-file issues most likely contributing to each pain point, plus concrete revisions to fix them.

## 1) False completion claims and “final_video.mp4 does not exist”
### Likely contributing issues in Space docs
1) **Inconsistent final output filename**
- `README.md` and `AGENTS.md` describe `finalvideo.mp4` (no underscore).  
- The pain points mention the agent claiming `final_video.mp4` which then “does not exist”.
- This mismatch invites hallucinated paths and “it exists” disputes.

2) **Render command and output-path assumptions are internally inconsistent**
- `AGENTS.md` instructs rendering with `manim render ... -qh` and then records paths as `.../1440p60...mp4`.
- `manim_config_guide.md` says “Render normally manim file.py SceneName no flags needed”.
- Using `-qh` can override resolution settings and change output folder naming (commonly 1080p), which makes the later `1440p60` hardcoded path wrong and can cascade into “file missing”.

3) **`manim_content_pipeline.md` shows a “MANIMVOICEPROD toggle” pattern**
- That reintroduces “dev mode” concepts despite the “ElevenLabs only, no fallback” rules elsewhere.
- It increases the chance the agent uses the wrong code path or reports success without the production artifacts.

### Recommended revisions
**Edit all docs to a single canonical output filename.**
- Pick one: `final_video.mp4` (more readable) or `finalvideo.mp4` (current).  
- Then update everywhere: `README.md`, `AGENTS.md`, `manim_content_pipeline.md`, and any template snippets.

**Fix `AGENTS.md` finalrender phase to remove `manim render` and `-qh`, and remove hardcoded `1440p60` path assumptions.**
- Replace with:
  - Render command: `manim scene_XX.py SceneXX` (no quality flags) to respect the locked config.
  - After each render, locate output by searching the `media/videos` tree for the newest mp4 for that scene class (or parse Manim output), then write that exact path into state.
- Add a hard gate:
  - “Do not advance to assemble unless every scene in state has status `rendered` AND the referenced mp4 file exists and has non-zero size.”

**Remove or explicitly forbid MANIMVOICEPROD in `manim_content_pipeline.md`.**
- If you want to keep it as historical context, label it “DEPRECATED / PROHIBITED IN THIS SPACE”.

## 2) Persistent element overlap and clipping
### Likely contributing issues in Space docs
1) **The positioning helper only clamps vertical bounds**
- `safeposition(...)` in template and config guide clamps top and bottom only, not left and right.
- Pain points include overlaps, not just clipping. Clamping does not solve overlap, and it does not protect horizontal collisions.

2) **No enforced overlap detection step**
- `AGENTS.md` includes a `check_overlap` snippet, but it is not integrated into a required workflow (“must run on all text blocks”, “must fail build if overlaps found”, etc.).

3) **Naming mismatch and weak affordances**
- Pain points refer to `safe_position()`. The docs define `safeposition(...)`.
- Even if the agent “tries to comply”, inconsistent naming increases missed calls and inconsistent mental models.

4) **Conflicting layout guidance across docs**
- `manim_config_guide.md` strongly discourages `.to_edge(UP)` for titles, but `HOW_TO_ANIMATE.md` examples include `.toedgeUP` style positioning.
- Agents can import tactics from `HOW_TO_ANIMATE.md` without realizing the Space safe-zone policy differs.

### Recommended revisions
**Upgrade `safeposition` into a real “safe layout” utility and standardize its name.**
- Rename everywhere to `safe_position(mobject, ...)` for consistency with the pain points and typical naming.
- Extend it to clamp both axes:
  - Clamp X within `[-7, 7]` (or a configurable margin).
  - Clamp Y within `[-4, 4]`.
- Add `safe_group(VGroup)` guidance: clamp after arranging.

**Add a mandatory “layout validation” step in `AGENTS.md` per voiceover block.**
- After creating and positioning all mobjects for a segment:
  - Run a lightweight overlap check on “primary text” objects.
  - If overlap detected, automatically reflow:
    - Reduce scale slightly, increase vertical spacing, or split into multiple voiceover blocks.
- Make this a “fail the phase” condition, not a suggestion.

**Add explicit z-order rules**
- Add to `AGENTS.md` and `manim_config_guide.md`:
  - “Text should always be in front of shapes.”
  - Use `set_z_index` (or `bring_to_front`) on titles, subtitles, labels.
  - Provide one canonical pattern.

**Patch `HOW_TO_ANIMATE.md` with a prominent warning banner**
- “This guide contains legacy examples that may violate Space safe-zone rules. Treat it as animation-technique reference, not layout policy.”
- Add a small section showing how to translate its techniques into Space-safe positioning.

## 3) Audio and voiceover integration failures (cut-outs, clipping, sync drift)
### Likely contributing issues in Space docs
1) **Docs encourage manual timing budgets plus explicit waits**
- `AGENTS.md` shows using `tracker.duration * fractions` and sometimes `self.wait(tracker.duration * 0.1)` as buffer.
- `manim_voiceover.md` emphasizes the context manager already waits for audio completion, and explicit waits are often unnecessary.
- This mismatch invites over-waiting, under-consuming tracker duration, and inconsistent total video lengths across segments, which can lead to perceived “gaps” or misalignment.

2) **No required preflight for ElevenLabs env var**
- `README.md` and `AGENTS.md` mention `ELEVENLABSAPIKEY`, but there is no hard “preflight check” section that fails early with a clear error if missing.
- Pain point shows the system silently proceeding with “no errors” despite missing key.

### Recommended revisions
**Declare one canonical sync strategy**
Add a “Sync Canon” section (in `AGENTS.md` and `manim_voiceover.md`):
- Default: within each `with self.voiceover(...) as tracker:` block, make the primary animation consume `tracker.duration` (or consume most of it) and avoid explicit waits unless `tracker.get_remaining()` is used.
- If splitting into multiple animations:
  - Provide a helper like `split_duration(tracker.duration, weights)` that asserts sum(weights) == 1.0 (within epsilon).
- Add a hard rule:
  - “Never add `self.wait()` outside a voiceover block to ‘pad’ narration. Use tracker-based remaining-time handling.”

**Add an ElevenLabs preflight checklist**
In `AGENTS.md` (and optionally `README.md`):
- Before any render phase, verify:
  - `ELEVENLABSAPIKEY` exists in environment (and optionally `.env`).
  - A minimal “one-line TTS call” smoke test can run.
- If missing, append to `state.errors`, set `needs_human_review`, and do not advance phase.

## 4) Timing budget errors (fractions exceed 1.0, missing budgets)
### Likely contributing issues in Space docs
- `AGENTS.md` requires fractions sum to ≤ 1.0, but there is no standard helper and no “preferred simplest pattern”. This encourages ad hoc math and omissions.
- The time-budget requirement conflicts conceptually with the voiceover context manager auto-wait behavior, so agents may treat the budgeting as “documentation theater” and skip it.

### Recommended revisions
**Reduce degrees of freedom**
In `AGENTS.md`, redefine “timing budget compliance” as one of:
- Pattern A (recommended): one main animation uses `runtime=tracker.duration` and avoid fractional budgets entirely.
- Pattern B: fractional budgets only when you need multiple distinct beats, and you must use a provided helper plus an assertion.

Add a short code snippet to the template that agents can copy verbatim:
- `def allocate(tracker, weights): ... assert abs(sum(weights) - 1.0) < 1e-6 ... return [tracker.duration*w for w in weights]`

## 5) Under-implemented animations versus plan.json
### Likely contributing issues in Space docs
1) **Planning and implementation are not mechanically linked**
- `AGENTS.md` tells the agent to produce plans, but it does not require traceability between “planned animation bullets” and “implemented code”.
- Nothing forces “if plan says particle system, implement it or downgrade plan explicitly.”

2) **Mixed incentives**
- `AGENTS.md` review phase emphasizes feasibility and avoiding high-risk features.
- `HOW_TO_ANIMATE.md` is rich but oriented around other scene classes and older patterns, so the agent may retreat to basic shapes instead of adapting advanced techniques into VoiceoverScene form.

3) **Over-restrictive rule for non-math topics**
- `AGENTS.md` says “If the subject is not mathematical… do not draw geometric or mathematical objects.”
- This can accidentally ban useful visual metaphors (boxes, arrows, flows, simple geometry) and lead to sparse scenes.

### Recommended revisions
**Add a “Plan to Code Traceability Contract” in `AGENTS.md`**
For each scene file, require:
- A header comment listing each planned animation bullet.
- A checkbox status:
  - Implemented
  - Implemented with downgrade (and why)
  - Deferred (must update plan.json and state)

**Define a minimum visual richness baseline**
In `AGENTS.md` “visual quality rules”, add something like:
- “Each scene must contain at least:
  - 1 title or persistent header,
  - 2 labeled visual elements (diagram, chart, annotated graphic),
  - 1 transformation (not only fades).”

**Relax and rewrite the “non-math” rule**
Replace with:
- “Prefer infographics (text, tables, charts, diagrams). Avoid gratuitous pure-geometry proofs. Simple geometric primitives are allowed as visual metaphors when labeled.”

## 6) Files created in wrong locations and placeholder-literal mistakes
### Likely contributing issues in Space docs
- Docs tell the agent to “create a new folder under projects”, but do not provide a naming convention, and many examples use placeholders like `myvideo`.
- Agents sometimes copy placeholders literally.

### Recommended revisions
Add a “Project folder naming” section (in `README.md` and `AGENTS.md`):
- Rule: never use placeholder strings like `myvideo`, `new-video-folder` in final filesystem writes.
- Provide a deterministic naming convention:
  - `projects/<kebab-topic>-<YYYYMMDD-HHMM>` or `projects/<kebab-topic>-v1`
- Add a “where artifacts must go” list:
  - Only inside that project folder, no exceptions.

## 7) Tex vs MathTex, and NumPy 2D vs 3D coordinate bugs
### Likely contributing issues in Space docs
- `manim_template.py.txt` shows `MathTex` in an example, but there is no explicit rule in `AGENTS.md`.
- There is no explicit coordinate-shape rule: Manim positions are 3D vectors (x, y, z), and many agent-generated bugs come from using 2D arrays.

### Recommended revisions
Add two short “never again” rules to `AGENTS.md`:
- **LaTeX rule**: “Use `MathTex` for equations and anything involving math mode. Use `Tex` only for pure text LaTeX.”
- **Vector rule**: “All points are 3D: `np.array([x, y, 0.0])`.”
  - Provide helper `P(x, y, z=0.0)` in the template.

## 8) Missing labels, legends, annotations
### Likely contributing issues in Space docs
- The docs say “use charts and graphs” but do not require axis labels, units, legends, or callouts.
- The animation guides are technique-focused, not information-design focused.

### Recommended revisions
Add an “Information Design Checklist” (best placed in `AGENTS.md` and optionally `manim_config_guide.md`):
- Every chart must include:
  - axis labels, units, and at least 2 ticks,
  - legend if multiple series,
  - a highlighted takeaway annotation (arrow + label),
  - consistent color mapping.

---

### Consolidation recommendation (prevents future drift)
Create one short “Single Source of Truth” doc (or a top section in `AGENTS.md`) that defines the invariants, then reference it from every other doc:
- Output filename (one string)
- Render command (one canonical form)
- Forbidden flags (`-ql`, `-qh`, etc) if you want config to win
- Env var name `ELEVENLABSAPIKEY`
- Helper names: `safe_position`, `P(x,y,z)`
- No dev mode / no fallback

This directly attacks the inconsistency-driven failures that show up repeatedly in `pain_points.md`.

If you want, the next step can be a concrete patch list per file (exact lines to remove/replace) based on your preferred canonical choices for: final output filename and render command.