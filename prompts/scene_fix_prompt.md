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
3. Preserve AGENTS.md requirements (cached Qwen voice, SCRIPT dict usage, safe positioning, BeatPlan timing helpers)
4. Do NOT edit project_state.json
5. Do not add fallback code; make the scene valid and renderable

When done, stop.
