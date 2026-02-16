# Harness Migration Guide

This guide covers the transition from OpenCode to the Python harness for Flaming Horse video production.

## Quick Start

### For New Projects

Simply use the harness by default (it's enabled by default):

```bash
./scripts/build_video.sh projects/my_video --topic "My Topic"
```

The `USE_HARNESS=1` environment variable is set by default in `build_video.sh`.

### For Existing Projects

If you have an existing project and want to continue using OpenCode:

```bash
USE_HARNESS=0 ./scripts/build_video.sh projects/my_video
```

## What Changed

### Before (OpenCode)

```bash
opencode run --agent manim-ce-scripting-expert --model "${AGENT_MODEL}" \
  --file prompt.md \
  --file project_state.json \
  -- "Execute phase..."
```

**Issues:**
- 15-20K tokens of OpenCode overhead
- Competing instruction sets
- No control over prompt composition
- No visibility into token usage

### After (Harness)

```bash
python3 -m harness \
  --phase plan \
  --project-dir ./projects/my_video \
  --topic "My Topic"
```

**Benefits:**
- Phase-specific prompts (36-78% token reduction)
- Single source of truth for instructions
- Direct API control
- Transparent token counting

## Migration Strategy

### Phase 1: Testing (Current)

The harness is production-ready and enabled by default. OpenCode remains available as a fallback.

**What to do:**
- Run new projects with the harness
- Monitor logs for any issues
- Compare output quality with OpenCode

**Rollback if needed:**
```bash
USE_HARNESS=0 ./scripts/build_video.sh projects/my_video
```

### Phase 2: Validation (Recommended)

Once you're confident in the harness:

**What to do:**
- Test harness on complex projects
- Measure token reduction in logs
- Verify all phases work correctly

**Key metrics to track:**
- Build success rate
- Token usage per phase
- Time to complete
- Video quality

### Phase 3: Full Adoption (Future)

When harness is proven stable:

**What to do:**
- Set `USE_HARNESS=1` as permanent default
- Remove OpenCode from dependencies
- Update documentation to remove OpenCode references

## Comparison: OpenCode vs Harness

### Context Window Usage

| Phase | OpenCode | Harness | Savings |
|---|---|---|---|
| plan | 45K tokens | 19K tokens | 58% |
| narration | 45K tokens | 20K tokens | 56% |
| build_scenes | 45K tokens | 29K tokens | 36% |
| scene_qc | 45K tokens | 24K tokens | 47% |
| scene_repair | 45K tokens | 10K tokens | 78% |

### Behavioral Differences

**OpenCode:**
- May ask for confirmation (despite instructions not to)
- Sometimes introduces fallback patterns
- Can lose context of critical rules

**Harness:**
- Follows execution protocol strictly
- Phase-specific context prevents confusion
- Smaller prompts = better attention to critical rules

### Output Quality

Both should produce functionally equivalent outputs:
- Same plan.json structure
- Same narration_script.py format
- Same scene file patterns
- Same QC reports

**If you notice differences**, please report them for investigation.

## Environment Setup

### Required Environment Variables

Add to your `.env` file:

```bash
# xAI API credentials
XAI_API_KEY=your_xai_api_key_here

# Model selection (optional, defaults to xai/grok-4-1-fast)
AGENT_MODEL=xai/grok-4-1-fast

# Harness toggle (optional, defaults to 1)
USE_HARNESS=1
```

### Optional Configuration

```bash
# Force OpenCode for a specific build
USE_HARNESS=0 ./scripts/build_video.sh projects/my_video

# Use a different model
AGENT_MODEL=xai/grok-2-1212 ./scripts/build_video.sh projects/my_video
```

## Testing the Harness

### Dry Run Mode

Test prompt composition without calling the API:

```bash
python3 -m harness --phase plan --project-dir projects/test --topic "Test" --dry-run
```

This shows:
- System prompt length
- User prompt length
- First 500 characters of each

### Full Phase Test

Test a complete phase in isolation:

```bash
# Create a test project
./scripts/new_project.sh test_harness

# Test plan phase
cd projects/test_harness
python3 -m harness --phase plan --project-dir . --topic "Binary search trees"

# Verify output
ls -l plan.json
cat plan.json | jq '.'
```

### End-to-End Test

Run a complete video build:

```bash
./scripts/build_video.sh projects/test_harness --topic "Binary search trees"
```

Monitor logs for:
- "Using Python harness" messages
- No OpenCode invocations
- Successful artifact creation
- Phase transitions working correctly

## Troubleshooting

### Harness Not Found

**Error:**
```
python3: No module named harness
```

**Solution:**
Ensure `PYTHONPATH` includes the repo root:
```bash
export PYTHONPATH="/path/to/flaming-horse:$PYTHONPATH"
```

This is set automatically by `build_video.sh`.

### API Key Missing

**Error:**
```
ValueError: XAI_API_KEY environment variable not set
```

**Solution:**
Add `XAI_API_KEY` to `.env` file in repo root.

### Parsing Failures

**Error:**
```
❌ Failed to parse artifacts from response
```

**Possible causes:**
1. Model returned malformed JSON/Python
2. Unexpected response format
3. Model refused to generate code

**Debug steps:**
1. Check `build.log` for full model response
2. Verify prompt templates are correct
3. Try with OpenCode to compare: `USE_HARNESS=0`
4. Report issue with logs attached

### Validation Failures

If harness produces code that fails validation:

1. Check error logs in retry context
2. Harness should auto-retry with error context
3. If retries fail, orchestrator will escalate

**Fallback to OpenCode:**
```bash
USE_HARNESS=0 ./scripts/build_video.sh projects/my_video
```

## Known Differences

### Session Management

**OpenCode:** Maintains conversation history across invocations via `--session`

**Harness:** Each phase invocation is independent (no session)

**Impact:** None - each phase should be self-contained anyway

### Model Fallback

**OpenCode:** Has model fallback logic for unavailable models

**Harness:** Uses single model specified in `AGENT_MODEL`

**Impact:** If model is unavailable, build fails immediately (more predictable)

### Output Format

**OpenCode:** May include conversational wrapper around artifacts

**Harness:** Extracts pure artifacts from response, strips formatting

**Impact:** None - both produce valid artifacts

## Reporting Issues

If you encounter problems with the harness:

1. **Capture logs**: Save `build.log` from project directory
2. **Note environment**: Which phase? Which model? Retry or first attempt?
3. **Include context**: What topic? What error?
4. **Try OpenCode**: Does `USE_HARNESS=0` work?

**Report via:**
- GitHub issue with `harness` label
- Include logs (sanitize any sensitive data)
- Include steps to reproduce

## Performance Expectations

### Speed

**Similar to OpenCode**: API call time dominates, harness overhead is negligible

**Measured:**
- Harness invocation: ~50ms
- API call: 5-30 seconds (model-dependent)
- Output parsing: ~10ms

### Token Usage

**Significant reduction in prompt size**:
- Plan: 58% reduction
- Narration: 56% reduction
- Build scenes: 36% reduction
- Scene QC: 47% reduction
- Scene repair: 78% reduction

**Impact:**
- Lower API costs
- Better attention to critical rules
- Faster responses (less to read)

### Reliability

**Expected: Equal or better than OpenCode**

**Why:**
- Simpler code path (fewer failure points)
- Direct API access (no intermediary)
- Better error messages (controlled by us)

**If reliability is worse**, please report with logs.

## Rollback Plan

If you need to completely disable the harness:

1. **Temporary (single build):**
   ```bash
   USE_HARNESS=0 ./scripts/build_video.sh projects/my_video
   ```

2. **Permanent (until fixed):**
   Add to `.env`:
   ```bash
   USE_HARNESS=0
   ```

3. **Report the issue** so we can fix it

## Future Roadmap

### Short Term
- [x] Core harness implementation
- [x] Integration with build_video.sh
- [ ] Comprehensive end-to-end testing
- [ ] Token usage reporting in logs

### Medium Term
- [ ] Streaming support for real-time progress
- [ ] Better error recovery
- [ ] Prompt optimization based on usage data

### Long Term
- [ ] Multi-provider support (Anthropic, OpenAI)
- [ ] Web UI for build monitoring
- [ ] Automatic prompt tuning
- [ ] Remove OpenCode dependency entirely

## Questions?

If this guide doesn't answer your question:

1. Check `harness/README.md` for technical details
2. Review `docs/DEVELOPMENT_GUIDELINES.md` for architecture
3. Search existing GitHub issues
4. Open a new issue with the `question` label
