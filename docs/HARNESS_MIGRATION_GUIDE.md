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

- Required: `XAI_API_KEY`
- Optional: `AGENT_MODEL`

Example `.env` values:

```dotenv
XAI_API_KEY=your_key_here
AGENT_MODEL=xai/grok-4-1-fast
```

## Validation and Recovery

- Syntax, import, semantic, and runtime checks stay in `scripts/build_video.sh`.
- Failed scene builds are repaired through `scene_repair` with retry context.
- `project_state.json` updates remain deterministic via `scripts/update_project_state.py`.

## Troubleshooting

- If harness fails to parse model output, inspect `build.log` and retry context files.
- If API calls fail, verify `XAI_API_KEY`, model name, and network access.
- If scene runtime validation fails, use scaffold reset + scene repair loop output for root-cause fixes.
