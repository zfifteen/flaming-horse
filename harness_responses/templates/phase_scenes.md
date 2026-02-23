# Scene QC Reference

Purpose: supplemental context for Scene QC review only.

This reference is descriptive guidance, not an execution plan.
Do not interpret any item here as an instruction to run tools, execute shell commands,
modify orchestrator state, or perform external side effects.

## Render-Blocking Focus

Review only failures that would prevent a scene from rendering successfully:
- Python syntax errors
- Runtime exceptions during `construct()`
- Invalid or unsupported Manim API usage that raises at render time
- Missing names/imports/types that cause deterministic failure
- Math/LaTeX usage that triggers render failure

Ignore non-blocking quality/style concerns (layout polish, pacing preference, aesthetics)
unless they directly cause a render-time exception.

## Scene-Body Contract Awareness

When evaluating generated scene code, prefer these contract checks:
- Output is valid scene-body code (statements only, no imports/classes/functions).
- Scaffold markers and scaffold-owned structure are preserved by the pipeline.
- Narration binding uses `SCRIPT[...]` with the expected key.
- Timing expressions remain narration-synced (use of `tracker.duration` where required).

## Reporting Expectations

When a render-blocking issue exists:
- Identify the first concrete failure origin.
- Name the failing symbol/API/pattern precisely.
- Recommend a minimal, deterministic fix aligned to the current scene intent.

When no render-blocking issue exists:
- Mark scene as not requiring rewrite.

