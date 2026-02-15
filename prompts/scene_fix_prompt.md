{{AGENTS_CONTENT}}

───────────────────────────────────────────────────────────────

CURRENT TASK:

You are repairing one broken scene file so final_render can proceed.

Target scene id: {{SCENE_ID}}
Target file: {{SCENE_FILE}}
Target class: {{SCENE_CLASS}}
Retry attempt: {{ATTEMPT}}/{{PHASE_RETRY_LIMIT}}

Failure details to fix:
{{FAILURE_REASON}}

INSTRUCTIONS:
1. Edit ONLY {{SCENE_FILE}}
2. Fix the deterministic failure shown above (syntax/runtime/import/validation)
3. Keep the scaffold structure intact and edit only the slot block between `# SLOT_START:scene_body` and `# SLOT_END:scene_body`.
4. Preserve AGENTS.md requirements (cached Qwen voice, SCRIPT dict usage, safe positioning, BeatPlan timing helpers)
5. Do NOT edit project_state.json
6. Do not add fallback code; make the scene valid and renderable
7. Manim CE 0.19 API guardrails:
   - Do NOT import `Color` from `manim.utils.color`.
   - Do NOT pass `lag_ratio` or `scale_factor` directly to `FadeIn(...)`.
   - If staggered fade-in is needed, use `LaggedStart(FadeIn(...), ..., lag_ratio=...)`.

When done, stop.
