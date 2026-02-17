# Tests README

## Active Test Suite

This folder currently validates the harness layer (`/harness`) rather than Manim
scene helper functions.

### 1) Mock parser/prompt E2E (no API calls)

```bash
python3 -m pytest -q tests/test_harness_mock_e2e.py
```

Covers:
- Parsing plan/narration/build-scene responses
- Prompt composition for scene-specific narration scoping
- End-to-end artifact writing in a temporary project

### 2) Harness integration smoke checks (no API calls)

```bash
bash tests/test_harness_integration.sh
```

Covers:
- Module imports and required functions
- CLI availability
- Prompt-template presence
- `build_video.sh` harness integration hook
- Core parser helper functions

### 3) Harness dry-run phase coverage (no API calls)

```bash
bash tests/test_harness_dry_run.sh
```

Covers:
- `plan`, `narration`, `build_scenes`, `scene_qc`, `scene_repair` in `--dry-run`
- Uses a self-contained temporary fixture project

### 4) Live API end-to-end

```bash
bash tests/test_harness_e2e.sh
```

Requires:
- `XAI_API_KEY` in environment or `.env`

### 5) CLI help smoke checks

```bash
bash tests/test_cli_help_smoke.sh
```

Covers:
- `scripts/help.sh` output is available
- `create_video.sh --help` points to `scripts/help.sh`
- `build_video.sh --help` points to canonical entrypoint/help
- `new_project.sh --help` points to `scripts/help.sh`
