# Implementation Status

The active harness path is `harness_responses/`.

The active backend is the local Grok Build CLI. Validate it with:

```bash
python3 scripts/test_grok_cli_contract.py
```

The canonical user entrypoint remains:

```bash
./scripts/create_video.sh my_video --topic "My Topic"
```
