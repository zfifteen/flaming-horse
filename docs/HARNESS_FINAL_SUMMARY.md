# Harness Final Summary

The Flaming Horse pipeline now uses the Python harness as the single execution path for agent phases.

## Final Architecture

- `scripts/build_video.sh` orchestrates phases, retries, and validations.
- `python3 -m harness` handles model calls and artifact generation.
- `scripts/update_project_state.py` applies deterministic state changes.

## Outcomes

- Phase-scoped prompts reduce unnecessary token usage.
- Agent outputs are parsed and validated before downstream steps.
- Failure handling remains deterministic via retry context + repair phases.

## What to Monitor

- API reliability and retry frequency
- Parse failure frequency per phase
- Scene repair loop frequency and root-cause categories

## Recommended Follow-ups

1. Add per-phase telemetry for token and latency trends.
2. Add regression tests for prompt composition edge cases.
3. Keep documentation aligned with orchestrator behavior and supported phases.
