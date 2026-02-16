# Harness Quick Reference

## One-Line Commands

```bash
# Use harness (default)
./scripts/build_video.sh projects/my_video --topic "My Topic"

# Use OpenCode (fallback)
USE_HARNESS=0 ./scripts/build_video.sh projects/my_video

# Test harness dry-run
./tests/test_harness_dry_run.sh

# Direct invocation
python3 -m harness --phase plan --project-dir ./projects/test --topic "Test"
```

## Environment Variables

```bash
# Required for harness
XAI_API_KEY=your_xai_api_key_here

# Optional
AGENT_MODEL=xai/grok-4-1-fast  # Model selection
USE_HARNESS=1                   # 1=harness, 0=OpenCode
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
├── client.py           # xAI API client
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
| `XAI_API_KEY not set` | Add to .env file |
| `Parsing failed` | Check logs, try USE_HARNESS=0 |
| Any other issue | Set USE_HARNESS=0 as fallback |

## Documentation

- Technical: `harness/README.md`
- Migration: `docs/HARNESS_MIGRATION_GUIDE.md`
- Summary: `docs/HARNESS_IMPLEMENTATION_SUMMARY.md`
