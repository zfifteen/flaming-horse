# Harness Responses

The live `harness_responses/` backend invokes the local Grok Build CLI.

It does not use hosted API keys, xAI Collections, web search, or API
conversation continuation. It writes a prompt file and requires Grok to write
one staged JSON response file in the project log directory.

Validate the live CLI contract with:

```bash
python3 scripts/test_grok_cli_contract.py
```
