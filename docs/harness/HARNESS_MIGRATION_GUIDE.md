# Harness Migration Guide

The live harness backend is the local Grok Build CLI through
`harness_responses/`.

Use this migration shape:

```bash
grok login
grok models
python3 scripts/test_grok_cli_contract.py
```

Remove hosted-provider harness variables from active local configuration:

```bash
LLM_PROVIDER
XAI_API_KEY
XAI_MODEL
MINIMAX_API_KEY
MINIMAX_MODEL
AGENT_MODEL
```

Use the current variables only when overriding defaults:

```bash
GROK_MODEL=grok-build
# GROK_CLI=/absolute/path/to/grok
# GROK_CLI_TIMEOUT_SECONDS=900
```
