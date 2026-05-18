# Local Grok CLI Authentication

The live Flaming Horse harness no longer uses hosted LLM API keys.

Authenticate the local Grok Build CLI instead:

```bash
grok login
grok models
```

The required model is:

```text
grok-build
```

Optional `.env` settings:

```bash
GROK_MODEL=grok-build
# GROK_CLI=/absolute/path/to/grok
# GROK_CLI_TIMEOUT_SECONDS=900
```

Validate the local backend contract with:

```bash
python3 scripts/test_grok_cli_contract.py
```
