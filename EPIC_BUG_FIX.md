# EPIC BUG FIX: Qwen Precache "Hang" + flash-attn Warning Loop

Date: 2026-02-13

## What Was Happening

Builds for `projects/123-square-roots` repeatedly appeared to hang at:

- `Warning: flash-attn is not installed...`
- `Setting pad_token_id to eos_token_id...`

Then the pipeline restarted `precache_voiceovers`, causing long rework and making progress hard to see.

## Root Cause

This was not a real `flash-attn` install failure. It was a compound reliability issue:

1. **Misleading warning:** `qwen_tts` emits a `flash-attn` warning on CPU builds. It is non-fatal in this repo's CPU/float32 mode.
2. **Long silent generation:** after `pad_token_id` log, CPU generation can run for minutes with little/no progress output.
3. **Poor resume behavior:** if `.mp3` files existed but `cache.json` was missing, precache regenerated everything instead of reusing existing audio.
4. **Stream handling risk:** synchronous stdout/stderr reads in precache orchestration could make output appear stalled and were less robust under long-running worker output.

## Fixes Applied

### 1) Suppress only the known non-fatal flash-attn warning

Updated:

- `scripts/prepare_qwen_voice.py`
- `scripts/precache_voiceovers_qwen.py`

Added:

- `SUPPRESSED_STDERR_SUBSTRINGS`
- `should_forward_worker_stderr(line)`

Behavior:

- Filters only these lines:
  - `Warning: flash-attn is not installed.`
  - `Will only run the manual PyTorch version.`
  - `Please install flash-attn for faster inference.`
- Also filters the surrounding `********` wrapper lines emitted by the dependency.
- Keeps all other warnings/errors visible.

### 2) Make worker stream handling robust

Updated:

- `scripts/precache_voiceovers_qwen.py`

Added:

- `_stream_lines(...)` helper
- Concurrent reader threads for worker `stdout` and `stderr`

Why:

- Avoids fragile alternating `readline()` loop behavior.
- Keeps logs flowing and reduces apparent stalls.

### 3) Add resume from existing audio artifacts

Updated:

- `scripts/precache_voiceovers_qwen.py`

Added:

- `bootstrap_existing_entries_from_media(...)`

Behavior:

- If `cache.json` is missing but `<narration_key>.mp3` files already exist, the script synthesizes cache entries and treats them as cache hits.
- This prevents re-generating already completed narration keys after interruption/restart.

## Validation Performed

1. Syntax checks passed:

- `python3 -m py_compile scripts/prepare_qwen_voice.py scripts/precache_voiceovers_qwen.py`

2. Restarted build and observed live:

- `./scripts/build_video.sh ./projects/123-square-roots`

3. Confirmed resume behavior in `build.log`:

- `Recovered 4 existing audio files...`
- `Cache hit: intro`
- `Cache hit: definition`
- `Cache hit: visualization`
- `Cache hit: calculation`
- Generated only missing keys (`applications`, `recap`).

4. Confirmed full pipeline completion:

- All scenes rendered
- FFmpeg assembly succeeded
- QC passed
- Final artifact produced

Final output:

- `projects/123-square-roots/final_video.mp4`

## What This Fix Changes Going Forward

- The non-fatal `flash-attn` warning no longer pollutes logs.
- Interrupted precache runs resume from existing `.mp3` outputs.
- Precache subprocess streaming is more reliable.
- Build retries should be dramatically faster when partial cache exists.

## Notes

- CPU/float32 local Qwen voice clone remains the enforced repo policy.
- No network TTS fallback was introduced.
- No changes were made to voice model selection or offline behavior.
