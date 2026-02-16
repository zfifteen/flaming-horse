# Prompt Registry

This directory is the single source of truth for orchestrator prompt text/snippets.

## Rules
- Keep policy/contract rules in `AGENTS.md`.
- Keep runtime prompt wording/snippets in this directory.
- `scripts/build_video.sh` should assemble prompts from these templates instead of embedding long inline prompt blocks.
- Use `{{TOKEN}}` placeholders for dynamic values rendered by the orchestrator.

## Templates
- `phase_prompt.md`: Main per-phase prompt template assembled by orchestrator.
- `phase_prompt_instructions.md`: Shared per-phase instructions appended to phase prompts.
- `phase_build_scenes.md`: Build-scenes phase-specific reminder snippet.
- `scene_fix_prompt.md`: Targeted scene-repair prompt.
