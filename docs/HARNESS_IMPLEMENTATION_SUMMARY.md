# Harness Implementation Summary

This document summarizes the Python harness architecture used by the Flaming Horse pipeline.

## Delivered Components

- `harness/client.py`: direct xAI chat completions client with retry behavior.
- `harness/prompts.py`: phase-specific prompt composer.
- `harness/parser.py`: structured extraction and syntax validation for artifacts.
- `harness/cli.py` + `harness/__main__.py`: command entry points for orchestrator integration.

## Orchestrator Integration

- `scripts/build_video.sh` calls `python3 -m harness` for:
  - `plan`
  - `narration`
  - `build_scenes`
  - `scene_qc`
  - `scene_repair`
- Orchestrator remains responsible for deterministic state transitions and validation gates.

## Prompt Strategy

- Use phase-scoped references to reduce prompt bloat.
- Keep reusable constraints in prompt templates under `harness/prompt_templates/`.
- Inject current-scene details and narration text only for targeted scene generation.

## Quality Controls

- Parser-level extraction and sanitization.
- Python compile checks before writing artifacts.
- Build-time validation and retry loops in shell orchestrator.

## Operational Notes

- Required environment variable: `XAI_API_KEY`.
- Recommended model default: `xai/grok-4-1-fast`.
- Use dry-run mode for prompt verification without API calls.

## Status

Harness integration is active and production-ready within the current pipeline design.
