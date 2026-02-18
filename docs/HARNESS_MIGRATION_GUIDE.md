# Harness Runtime Guide

This repository now uses the Python harness as the only supported runner for generative phases.

## Current State

- `scripts/build_video.sh` invokes `python3 -m harness` for agent-driven phases.
- State transitions, retries, and validation gates remain in the orchestrator.
- Prompt composition is phase-scoped in `harness/prompts.py`.

## How to Run

```bash
./scripts/build_video.sh projects/my_video --topic "My Topic"
```

Direct harness invocation (for debugging):

```bash
python3 -m harness --phase plan --project-dir ./projects/my_video --topic "My Topic"
python3 -m harness --phase narration --project-dir ./projects/my_video
python3 -m harness --phase build_scenes --project-dir ./projects/my_video
python3 -m harness --phase scene_qc --project-dir ./projects/my_video
python3 -m harness --phase scene_repair --project-dir ./projects/my_video --scene-file ./projects/my_video/scene_01.py --retry-context "SyntaxError"
```

## Environment

The harness is provider-agnostic. Configure via environment variables:

### Required
- `LLM_PROVIDER` - Provider name (XAI or MINIMAX)
- `{PROVIDER}_API_KEY` - Provider-specific API key

### Optional
- `{PROVIDER}_BASE_URL` - Provider endpoint (defaults provided)
- `{PROVIDER}_MODEL` - Provider model (defaults provided)
- `AGENT_MODEL` - Global fallback model

Example `.env` values:

```dotenv
# LLM Provider Configuration
LLM_PROVIDER=XAI

# Provider-Specific Keys
XAI_API_KEY=your_xai_key_here
MINIMAX_API_KEY=your_minimax_key_here

# Provider-Specific (optional)
XAI_BASE_URL=https://api.x.ai/v1
MINIMAX_BASE_URL=https://api.minimax.io/v1
XAI_MODEL=grok-code-fast-1
MINIMAX_MODEL=MiniMax-M2.5
```

## Validation and Recovery

- Syntax, import, semantic, and runtime checks stay in `scripts/build_video.sh`.
- Failed scene builds are repaired through `scene_repair` with retry context.
- `project_state.json` updates remain deterministic via `scripts/update_project_state.py`.

## Troubleshooting

- If harness fails to parse model output, inspect `build.log` and retry context files.
- If API calls fail, verify `{PROVIDER}_API_KEY`, model name, and network access.
- To switch providers, change `LLM_PROVIDER` in `.env` (XAI or MINIMAX).
- If scene runtime validation fails, use scaffold reset + scene repair loop output for root-cause fixes.
