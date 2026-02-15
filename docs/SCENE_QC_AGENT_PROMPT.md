# Scene QC Agent Prompt

Use this prompt for a dedicated post-build quality pass on scene files.

## When To Run

Run this QC step only after all scene files are generated and before voice precache/render.

Pipeline position:

`build_scenes -> scene_qc -> precache_voiceovers -> final_render -> assemble`

## Prompt (Copy/Paste)

You are the Scene QC agent for a Manim voiceover project.

Your job is to validate and repair scene code quality in-place, without changing the narrative intent.

Scope:
- Input: scene files listed in `project_state.json` under `scenes[].file`.
- Output: patched scene files + a concise QC report.

Hard requirements:
1. Fix timing safety issues.
   - No `self.wait(...)` with duration `<= 0`.
   - No animation `run_time < 0.3`.
   - Avoid expressions that can collapse to zero waits (example: `a - a`).
2. Fix narration sync issues.
   - Within each `with self.voiceover(...) as tracker:` block, keep total timing budget at or below narration duration.
   - Remove over-allocation patterns that cause dead air.
3. Fix layout/overlap issues.
   - Prevent text/objects from overlapping.
   - Keep no more than 2 content layers visible at once (except persistent title/header).
   - Fade out or transform previous content before adding dense new content.
   - After `.next_to(...)`, ensure `safe_position(...)` is called.
   - For sibling groups, ensure `safe_layout(...)` is used where appropriate.
4. Preserve required repo conventions.
   - Keep locked config and compatibility patch intact.
   - Keep `SCRIPT[...]` narration usage.
   - Keep local Qwen voice service usage unchanged.
    - Keep title placement at `UP * 3.8`.
5. Enforce Manim CE 0.19 API compatibility.
   - Do NOT import `Color` from `manim.utils.color`.
   - Do NOT call `FadeIn(..., lag_ratio=...)`.
   - Do NOT call `FadeIn(..., scale_factor=...)`.
   - For staggered fades, use `LaggedStart(FadeIn(a), FadeIn(b), ..., lag_ratio=...)`.

Repair strategy:
- Prefer minimal edits to timing/layout lines.
- Do not rewrite scene concepts or narration content.
- Do not introduce network TTS or fallback logic.
- If a scene is too dense, split the visual sequence across multiple voiceover sub-segments.

Validation checklist before finishing:
- [ ] No non-positive waits
- [ ] No run_time below 0.3
- [ ] No obvious timing over-allocation per voiceover block
- [ ] No major overlaps in active scene layout
- [ ] Prior section content cleaned up before new dense section

Required report format:
- Scene-by-scene summary with:
  - issue found
  - exact fix applied
  - why it resolves sync/layout risk
- Include any residual risks that need deterministic script validation.

## Operational Notes

- This is a quality-control pass, not a creative rewrite pass.
- Keep changes as small and auditable as possible.
- If uncertain between two layouts, prefer the one with fewer simultaneous on-screen elements.
