# Harness Responses Operations Guide

This guide describes how to run and operate the `harness_responses` path in Flaming Horse.

## Purpose

`harness_responses` is the xAI Responses API harness selected via `FH_HARNESS=responses`.
It coexists with legacy `harness` and is selected at runtime.

## Runtime Selection

Default behavior (legacy harness):

```bash
./scripts/build_video.sh projects/<project_name>
```

Enable Responses harness:

```bash
FH_HARNESS=responses ./scripts/build_video.sh projects/<project_name>
```

The orchestrator keeps deterministic phase control in both modes.

## Current Phase Coverage

| Phase | Legacy `harness` | `harness_responses` |
| --- | --- | --- |
| `plan` | yes | yes |
| `build_scenes` | yes | yes |
| `scene_repair` | yes | yes |
| `review` | yes | no |
| `narration` | yes | no |
| `scene_qc` | yes | no |

Notes:
- For phases not implemented in `harness_responses`, use legacy harness.
- `build_video.sh` routes phase calls according to `FH_HARNESS`.

## Behavior Differences

1. API path:
- Legacy: HTTP chat completions client in `harness/client.py`.
- Responses: `xai_sdk` structured parsing in `harness_responses/client.py`.

2. Output contract:
- Legacy: free-form text parsed by regex/JSON extraction.
- Responses: schema-first parsing with Pydantic model validation.

3. Failure diagnostics:
- Responses writes `log/responses_last_response.json` on semantic-validation failures.

4. Optional web search flag:
- Responses supports `enable_web_search` wiring in client call setup.

## Recommended Operation Mode

1. Use legacy harness for full end-to-end pipeline coverage.
2. Use `FH_HARNESS=responses` when validating structured-output behavior for implemented phases.

## Rollback Procedure

If a run fails under Responses harness and you need immediate fallback:

1. Switch back to legacy harness:

```bash
unset FH_HARNESS
```

2. Reset to the phase you want to retry:

```bash
./scripts/reset_phase.sh projects/<project_name> <phase>
```

3. Re-run:

```bash
./scripts/build_video.sh projects/<project_name>
```

## Direct Smoke Commands

Run harness directly for targeted validation:

```bash
python3 -m harness_responses --phase plan --project-dir /tmp/my_project --topic "..."
python3 -m harness_responses --phase build_scenes --project-dir /tmp/my_project
python3 -m harness_responses --phase scene_repair --project-dir /tmp/my_project --scene-file /tmp/my_project/scene_01.py --retry-context "..."
```
