# Validation Improvements - Post simple_math Test

## Background

The `simple_math` test revealed 3 critical bugs that passed validation:

1. **Empty ElevenLabs path** - `pass` statement instead of service initialization
2. **Timing budget overflow** - Animation fractions summed to >100%
3. **No production render requirement** - Never tested ElevenLabs in production

All 3 bugs were syntactically valid but semantically wrong.

## Proposed Additions to validate_voiceover_sync()

### Check 1: ElevenLabs Path Completeness

**Problem:** Scene had this code:
```python
if os.getenv("MANIM_VOICE_PROD"):
    pass  # BUG: empty path!
```

This is valid Python but means production renders silently fall back to gTTS.

**Solution:** Add to `validate_voiceover_sync()` in `build_video.sh`:

```bash
# Check: ElevenLabs production path is not empty
echo "  - Checking ElevenLabs production path..." | tee -a "$LOG_FILE"
if grep -q "if os.getenv.*MANIM_VOICE_PROD" "$scene_file"; then
    # Look for 'pass' statement in the production block
    if grep -A 3 "if os.getenv.*MANIM_VOICE_PROD" "$scene_file" | grep -q "^\s*pass\s*$"; then
        echo "    ✗ ERROR: ElevenLabs production path is empty (just 'pass')" | tee -a "$LOG_FILE"
        echo "    This will cause production renders to fall back to gTTS!" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # Verify ElevenLabsService is actually initialized
    if ! grep -A 5 "if os.getenv.*MANIM_VOICE_PROD" "$scene_file" | grep -q "ElevenLabsService"; then
        echo "    ✗ ERROR: ElevenLabs production path missing service initialization" | tee -a "$LOG_FILE"
        return 1
    fi
    
    echo "    ✓ ElevenLabs production path implemented" | tee -a "$LOG_FILE"
fi
```

### Check 2: Timing Budget Validation

**Problem:** Scene had this code:
```python
with self.voiceover(text=SCRIPT["welcome"]) as tracker:
    self.play(Write(title), run_time=tracker.duration * 0.7)      # 70%
    self.play(FadeIn(subtitle), run_time=tracker.duration * 0.4)  # 40%
    self.wait(tracker.duration * 0.2)                              # 20%
    # Total = 130% - animations run LONGER than audio!
```

**Solution:** Add timing budget warning to system prompt (not scriptable validation):

```markdown
## CRITICAL: Animation Timing Budget

When using `tracker.duration` for animation timing, ALL `run_time` fractions must sum to ≤ 1.0:

**WRONG - Timing Overrun:**
```python
with self.voiceover(text=SCRIPT["demo"]) as tracker:  # e.g., 10 seconds
    self.play(Write(title), run_time=tracker.duration * 0.6)   # 6s
    self.play(FadeIn(obj), run_time=tracker.duration * 0.5)     # 5s
    # Total = 1.1 = 110% → Animations run 1s LONGER than audio → DESYNC
```

**CORRECT - Timing Budget:**
```python
with self.voiceover(text=SCRIPT["demo"]) as tracker:  # e.g., 10 seconds
    self.play(Write(title), run_time=tracker.duration * 0.5)   # 5s
    self.play(FadeIn(obj), run_time=tracker.duration * 0.4)     # 4s
    self.wait(tracker.duration * 0.1)                           # 1s buffer
    # Total = 1.0 = 100% → Perfect sync
```

**Rule:** Before generating a scene, calculate the sum of all fractions. It MUST be ≤ 1.0.

**Why:** If fractions exceed 1.0, animations will run longer than audio, creating dead air at the end.
```

### Check 3: Production Render Requirement

**Problem:** We declared success after gTTS renders, never tested ElevenLabs.

**Solution:** Add to Phase 3 instructions in `system_prompt.md`:

```markdown
### Phase 3 Exit Criteria (UPDATED)

Before declaring Phase 3 complete, you MUST:

1. Run `build_video.sh` with `MANIM_VOICE_PROD=1` (ElevenLabs)
2. Verify final video uses ElevenLabs voice (not gTTS)
3. Run `qc_final_video.sh` and confirm PASSED
4. Check audio coverage is ≥95%

**NOT acceptable:**
- ❌ Only testing with gTTS (default/dev mode)
- ❌ Assuming ElevenLabs works without testing
- ❌ QC passing but never hearing the actual voice

**Verification command:**
```bash
MANIM_VOICE_PROD=1 ./build_video.sh ~/manim_projects/your_project
./qc_final_video.sh ~/manim_projects/your_project/final_video_elevenlabs.mp4
# Then: WATCH the video and confirm voice sounds correct
```
```

## Implementation Priority

**P0 (Add now):**
1. ElevenLabs path validation (scriptable check)
2. Production render requirement (Phase 3 exit criteria)

**P1 (Add to docs):**
3. Timing budget warning (system prompt education)

**P2 (Future enhancement):**
4. Automated timing budget validation (parse Python and sum fractions)

## Expected Impact

With these changes:
- **Bug #1** would be caught: "ERROR: ElevenLabs production path is empty"
- **Bug #2** would be prevented: Timing budget warning in prompt
- **Bug #3** would be caught: Phase 3 wouldn't pass without ElevenLabs test

## Testing the Improvements

Create a new test project with intentional bugs:
1. Leave ElevenLabs path as `pass`
2. Make timing fractions sum to 1.2
3. Try to complete Phase 3 without production render

Validation should catch all 3 issues.
