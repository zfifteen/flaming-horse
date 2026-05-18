# E2E Testing Summary

The active end-to-end path uses the local Grok Build CLI through the canonical
entrypoint:

```bash
./scripts/create_video.sh my_video --topic "My Topic"
```

Required local backend validation:

```bash
grok login
grok models
python3 scripts/test_grok_cli_contract.py
```

Focused regression checks:

```bash
PYTHONPATH=. pytest -q tests/harness_responses
PYTHONPATH=. python3 scripts/test_contracts_vs_runtime.py
bash -n scripts/create_video.sh scripts/new_project.sh scripts/build_video.sh
```

The hosted API-key E2E path is no longer the live harness contract.
