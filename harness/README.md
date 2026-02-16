# Flaming Horse Agent Harness

A domain-specific agent execution environment that gives the model the ability to write Manim code files while remaining under the orchestrator's deterministic control.

## Overview

The harness provides direct xAI API integration for the Flaming Horse video production pipeline with phase-scoped prompts and deterministic orchestration.

### Key Benefits

1. **Reduced Context Window Waste**: Removes large generic wrapper overhead per invocation
2. **Phase-Specific Prompts**: Only includes documentation relevant to the current phase
3. **Deterministic Control**: Orchestrator remains in bash, harness is just a tool
4. **Direct API Access**: No intermediate layers between our prompts and the model

## Architecture

The harness consists of four core components:

### 1. xAI Client (`client.py`)
- Direct HTTP integration with xAI chat completions API
- Retry logic with exponential backoff
- Token counting utilities
- No framework dependencies

### 2. Prompt Composer (`prompts.py`)
- Assembles phase-specific prompts from modular templates
- Selective document inclusion based on phase needs
- Significant token reduction compared to all-inclusive approach

**Phase-to-document mapping**:
- `plan`: core_rules + plan_system + pipeline overview
- `narration`: core_rules + narration_system + pipeline overview
- `build_scenes`: core_rules + build_scenes_system + template + config + visual helpers
- `scene_qc`: core_rules + qc_system + scenes_doc
- `scene_repair`: core_rules + repair_system + broken file + error

### 3. Output Parser (`parser.py`)
- Extracts JSON, Python code blocks from model responses
- Syntax verification via `compile()` before writing
- Sanitization (removes markdown fences, XML tags)
- Structured output handling

### 4. CLI (`cli.py`, `__main__.py`)
- Command-line interface for bash orchestrator
- Phase-specific argument handling
- Exit codes: 0=success, 1=model failure, 2=parsing failure

## Usage

### From Bash Orchestrator

The harness is invoked directly by `build_video.sh`:

```bash
./scripts/build_video.sh projects/my_video --topic "My Topic"
```

### Direct Invocation

For testing or manual use:

```bash
# Plan phase
python3 -m harness \
  --phase plan \
  --project-dir ./projects/test_video \
  --topic "Types of infinity"

# Narration phase
python3 -m harness \
  --phase narration \
  --project-dir ./projects/test_video

# Build scenes phase
python3 -m harness \
  --phase build_scenes \
  --project-dir ./projects/test_video

# Scene QC phase
python3 -m harness \
  --phase scene_qc \
  --project-dir ./projects/test_video

# Scene repair phase
python3 -m harness \
  --phase scene_repair \
  --project-dir ./projects/test_video \
  --scene-file ./projects/test_video/scene_01.py \
  --retry-context "SyntaxError on line 42"
```

### Dry Run Mode

Test prompt composition without calling the API:

```bash
python3 -m harness \
  --phase plan \
  --project-dir ./projects/test_video \
  --topic "Test" \
  --dry-run
```

## Environment Variables

### Required
- `XAI_API_KEY`: xAI API key for authentication

### Optional
- `AGENT_MODEL`: Model to use (default: `grok-code-fast-1`)

## Exit Codes

- `0`: Success - artifacts written and validated
- `1`: Model invocation failed (API error, timeout, malformed response)
- `2`: Parsing failed (could not extract valid artifacts from response)

## File Structure

```
harness/
├── __init__.py           # Package initialization
├── __main__.py           # CLI entry point
├── cli.py                # Argument parsing and main()
├── client.py             # xAI API client
├── prompts.py            # Phase-specific prompt composer
├── parser.py             # Output extraction and validation
├── README.md             # This file
└── prompt_templates/     # Modular prompt templates
    ├── core_rules.md           # Rules for all phases
    ├── plan_system.md          # Plan phase instructions
    ├── narration_system.md     # Narration phase instructions
    ├── build_scenes_system.md  # Build scenes instructions
    ├── scene_qc_system.md      # QC phase instructions
    └── repair_system.md        # Repair phase instructions
```

## Integration with Bash Orchestrator

The harness is a **tool being orchestrated**, not the orchestrator itself. The bash pipeline (`build_video.sh`) remains responsible for:

- Phase progression and state transitions
- Validation gates (syntax, imports, timing, layout)
- Retry and self-heal logic
- External tool invocation (manim, ffmpeg, TTS)

The harness only:
1. Receives phase + context from orchestrator
2. Composes optimized prompt
3. Calls xAI API
4. Parses response
5. Writes artifacts to disk
6. Exits with status code

## Adoption Status

The harness is the single supported runner for phase execution.

## Token Reduction Examples

Measured savings per phase (approximate):

| Phase | Prior Baseline | Harness System Prompt | Reduction |
|---|---|---|---|
| plan | ~45K tokens | ~19K tokens | **~58%** |
| narration | ~45K tokens | ~20K tokens | **~56%** |
| build_scenes | ~45K tokens | ~29K tokens | **~36%** |
| scene_qc | ~45K tokens | ~24K tokens | **~47%** |
| scene_repair | ~45K tokens | ~10K tokens | **~78%** |

These savings compound across:
- Multiple retries (3-5 per phase common)
- Multiple scenes (6-8 per video)
- Self-heal loops (3 attempts per failure)

## Development

### Adding a New Phase

1. Create prompt template in `prompt_templates/<phase>_system.md`
2. Add phase logic to `prompts.py` (e.g., `compose_<phase>_prompt()`)
3. Add parsing logic to `parser.py` (e.g., `parse_<phase>_response()`)
4. Update CLI choices in `cli.py`
5. Test with `--dry-run` mode first

### Testing

```bash
# Test CLI help
python3 -m harness --help

# Test dry-run for all phases
python3 -m harness --phase plan --project-dir projects/matrix-multiplication --topic "Test" --dry-run
python3 -m harness --phase narration --project-dir projects/matrix-multiplication --dry-run
python3 -m harness --phase build_scenes --project-dir projects/matrix-multiplication --dry-run
```

## Troubleshooting

### API Key Not Found
```
ValueError: XAI_API_KEY environment variable not set
```
**Solution**: Set `XAI_API_KEY` in `.env` file

### Parsing Failed
```
❌ Failed to parse artifacts from response
```
**Solution**: Check logs for model response format. May need to adjust extraction patterns in `parser.py`

### Timeout Errors
```
requests.exceptions.Timeout
```
**Solution**: Increase timeout in `client.py` or check network connectivity

## Future Enhancements

- [ ] Support for multiple providers (Anthropic, OpenAI, etc.)
- [ ] Streaming output for real-time progress
- [ ] Better error recovery with partial results
- [ ] Prompt caching for faster retries
- [ ] Token usage tracking and reporting
- [ ] Web UI for monitoring builds
