{{AGENTS_CONTENT}}

────────────────────────────────────────────────────────────────

CURRENT TASK:

You are executing phase: {{PHASE}}

Working directory: {{PROJECT_DIR}}

Repo root (scripts live here): {{REPO_ROOT_HINT}}
Scene scaffold script (absolute path): {{SCAFFOLD_PATH}}

Files available in this directory:
{{FILES_LIST}}

Video topic (if set): {{TOPIC}}

Reference documentation has been attached to this message:
- manim_content_pipeline.md
- manim_voiceover.md
- manim_template.py.txt
- manim_config_guide.md

The current project_state.json has also been attached.

{{PHASE_INSTRUCTIONS}}

PHASE-SPECIFIC REMINDER:
{{PHASE_SPECIFIC_REMINDER}}

{{RETRY_CONTEXT_NOTICE}}

TOPIC REQUIREMENT:
- For the plan phase, you MUST use the provided video topic (above). If it is empty, fail the phase with an error explaining how to set it.

Begin execution now.
