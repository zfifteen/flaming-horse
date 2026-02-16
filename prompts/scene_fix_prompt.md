───────────────────────────────────────────────────────────────

CURRENT TASK:

You are repairing one broken scene file so final_render can proceed.

Target scene id: {{SCENE_ID}}
Target file: {{SCENE_FILE}}
Target class: {{SCENE_CLASS}}
Retry attempt: {{ATTEMPT}}/{{PHASE_RETRY_LIMIT}}

Failure details to fix:
{{FAILURE_REASON}}

VALIDATION REQUIREMENTS:

The scene must pass semantic validation checks:
1. Valid Python syntax (no SyntaxError)
2. Non-empty narration_text assignment with actual content
3. construct() method exists with non-trivial body (not just `pass`)
4. No TODO/FIXME placeholders in construct() body
5. Proper Manim imports present
6. Valid Scene class definition inheriting from Scene
7. No empty self.play() calls
8. Appropriate timing with self.wait() calls after animations

Common validation failures to avoid:
- Empty construct() body or only containing `pass`
- Missing or empty narration_text = ""
- Broken self.play() calls with invalid arguments
- Missing self.wait() timing between animation sequences
- Syntax errors from incomplete refactoring
- Missing imports for Manim objects used in scene

INSTRUCTIONS:
1. Edit ONLY {{SCENE_FILE}}
2. Fix the deterministic failure shown above (syntax/runtime/import/validation)
3. Keep the scaffold structure intact and edit only the slot block between `# SLOT_START:scene_body` and `# SLOT_END:scene_body`.
4. Preserve repository AGENTS.md requirements (cached Qwen voice, SCRIPT dict usage, safe positioning, BeatPlan timing helpers)
5. Do NOT edit project_state.json
6. Do not add fallback code; make the scene valid and renderable
7. Manim CE 0.19 API guardrails:
   - Do NOT import `Color` from `manim.utils.color`.
   - Do NOT pass `lag_ratio` or `scale_factor` directly to `FadeIn(...)`.
   - If staggered fade-in is needed, use `LaggedStart(FadeIn(...), ..., lag_ratio=...)`.
8. Ensure construct() has substantive animation logic (not empty/placeholder)
9. Verify narration_text contains the actual narration content for this scene
10. Add appropriate self.wait() calls for timing between animation sequences

SELF-HEAL OPTIMIZATION:
This is attempt {{ATTEMPT}} of {{PHASE_RETRY_LIMIT}}. The self-heal loop will:
- Terminate early if no changes detected between attempts
- Apply exponential backoff between retries
- Track scene file hash to detect convergence

Make substantive fixes that address the root cause. Superficial changes will be detected.

When done, stop.
