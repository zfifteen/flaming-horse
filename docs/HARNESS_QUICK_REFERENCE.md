# Harness Quick Reference

## One-Line Commands

```bash
# Canonical user entrypoint (recommended)
./scripts/create_video.sh my_video --topic "My Topic"

# Use orchestrator directly (advanced)
./scripts/build_video.sh projects/my_video

# Test harness dry-run
./tests/test_harness_dry_run.sh

# Direct invocation
python3 -m harness --phase plan --project-dir ./projects/test --topic "Test"
```

## Environment Variables

```bash
# LLM Provider Configuration (provider-agnostic)
# Uncomment ONE provider:
LLM_PROVIDER=XAI
# LLM_PROVIDER=MINIMAX

# Provider-Specific Keys (all defined, one used based on LLM_PROVIDER)
XAI_API_KEY=your_xai_key_here
MINIMAX_API_KEY=your_minimax_key_here

# Provider-Specific Base URLs (defaults provided if omitted)
XAI_BASE_URL=https://api.x.ai/v1
MINIMAX_BASE_URL=https://api.minimax.io/v1

# Provider-Specific Models (optional)
XAI_MODEL=grok-code-fast-1
MINIMAX_MODEL=MiniMax-M2.5
```

## CLI Arguments

```
--phase {plan,narration,build_scenes,scene_qc,scene_repair}
--project-dir PATH           # Required
--topic TEXT                 # Required for plan phase
--retry-context TEXT         # Optional, for retries
--scene-file PATH            # Required for scene_repair
--dry-run                    # Test mode, no API call
```

## Exit Codes

- `0` = Success
- `1` = Model/API failure
- `2` = Parsing failure

## File Structure

```
harness/
├── cli.py              # Main entry point
├── client.py           # Provider-agnostic LLM client
├── prompts.py          # Prompt composer
├── parser.py           # Output parser
└── prompt_templates/   # Phase-specific templates
```

## Token Reduction

- Plan: 58% reduction
- Narration: 56% reduction
- Build scenes: 36% reduction
- Scene QC: 71% reduction
- Scene repair: 84% reduction

## Troubleshooting

| Issue | Solution |
|---|---|
| `No module named harness` | Check PYTHONPATH includes repo root |
| `XAI_API_KEY or MINIMAX_API_KEY not set` | Add to .env file |
| `Unsupported provider` | Set LLM_PROVIDER to XAI or MINIMAX |
| `Parsing failed` | Check logs and retry with corrected context |
| Any other issue | Inspect `build.log` and phase retry context |

## Documentation

- Technical: `harness/README.md`
- Migration: `docs/HARNESS_MIGRATION_GUIDE.md`
- Summary: `docs/HARNESS_IMPLEMENTATION_SUMMARY.md`
