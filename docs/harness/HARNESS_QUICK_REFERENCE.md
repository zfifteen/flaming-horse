# Harness Quick Reference

## Commands

```bash
./scripts/create_video.sh my_video --topic "My Topic"
./scripts/build_video.sh projects/my_video
python3 -m harness_responses --phase plan --project-dir ./projects/test --topic "Test"
```

## Local Grok CLI

```bash
grok login
grok models
python3 scripts/test_grok_cli_contract.py
```

Optional `.env` values:

```bash
GROK_MODEL=grok-build
# GROK_CLI=/absolute/path/to/grok
# GROK_CLI_TIMEOUT_SECONDS=900
```

## Phases

```text
plan
narration
build_scenes
scene_qc
scene_repair
```

## Exit Codes

- `0`: success
- `1`: recoverable phase failure
- `2`: configuration, implementation, or semantic validation failure
