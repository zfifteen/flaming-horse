# Audio Lessons Learned (Manim + ElevenLabs + FFmpeg)

This document captures a real failure mode we hit while generating Manim voiceover videos and assembling them into a single MP4. The symptom looked like a “player bug” (QuickTime going silent mid-video until you seek), but the root cause was in the file: discontinuous audio timestamps.

The intent is to make this repeatable: if you follow the assembly guidance here, you should avoid silent sections, desync, and QuickTime-specific playback failures.

## Executive Summary

- The final assembled MP4 contained **large discontinuities (gaps) in audio timestamps** (AAC packet PTS jumps). That produces “dead air” during normal playback in some players.
- The issue persisted across multiple “re-encode” attempts because the assembly method still preserved/created broken timestamp structure.
- The fix was to **assemble with FFmpeg’s `concat` filter (filtergraph), re-encode**, and **force a continuous audio timeline** using `aresample=async=1:first_pts=0`.

## What We Observed

### User-facing symptom

- Audio cuts out mid-video (especially in QuickTime). It sometimes returns if you seek forward/backward.

### File-level symptom (objective)

- The assembled output had audio packet timestamp jumps. Example gaps (from packet PTS analysis):
  - ~5.648s jump around ~102.6s
  - ~33.563s jump around ~164.0s

When that happens, a player that follows timestamps strictly will render silence until the next audio timestamp.

### Why seeking “fixes” playback

- Seeking causes the player to reinitialize decoding and choose new start points; some players then resume audio even if the overall timeline remains malformed.

## Root Cause

### The critical root cause

The final video’s audio stream had **discontinuous timestamps** (PTS/DTS timeline holes). This is not a subjective compatibility issue; it is a structural issue in the audio stream.

### Why this happened in our pipeline

We were producing multiple scene MP4 files and then assembling them.

The assembly approach that failed was based on FFmpeg’s **concat demuxer** (reading a `scenes.txt` list) and/or approaches that preserved the timestamp issues.

Even when we “re-encoded to H.264/AAC”, the *broken audio timeline* survived because:

- The concat demuxer can preserve/propagate per-file timestamps in ways that result in timeline holes.
- Stream-copy (`-c copy`) is especially risky because it does not rewrite timestamps.
- Re-encode without explicitly fixing audio timing can still yield discontinuities when the input timeline is discontinuous.

### Contributing factor: scenes with audio shorter than video

Some individual scene renders had:

- Video duration > audio duration (the scene ends with silent video / lingering visuals).

This *by itself* is not inherently wrong. It’s common for an animation to show a final beat after narration ends.

However, when stitching multiple MP4s, this can interact with how concatenation is performed.

The safe approach is to use a method that constructs a clean, continuous audio timeline for the final deliverable.

## The Fix (What Worked)

### The key change

We stopped using concat demuxer–based assembly as the primary final step and instead used:

- FFmpeg **concat filter** (`filter_complex`)
- Full re-encode to H.264 + AAC
- Audio timeline normalization: `aresample=async=1:first_pts=0`

This produced a final MP4 with:

- Audio duration ~= video duration
- **No large audio PTS gaps**
- Stable playback in QuickTime

### Working command pattern

Replace the input paths with your scene outputs:

```bash
ffmpeg -y \
  -i scene_01.mp4 \
  -i scene_02.mp4 \
  -i scene_03.mp4 \
  -i scene_04.mp4 \
  -i scene_05.mp4 \
  -filter_complex "\
    [0:v:0][0:a:0]\
    [1:v:0][1:a:0]\
    [2:v:0][2:a:0]\
    [3:v:0][3:a:0]\
    [4:v:0][4:a:0]\
    concat=n=5:v=1:a=1[v][a];\
    [a]aresample=async=1:first_pts=0[aout]" \
  -map "[v]" -map "[aout]" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  final_video.mp4
```

Notes:

- `concat=n=5:v=1:a=1` must match the number of input files.
- `aresample=async=1:first_pts=0` is doing the heavy lifting for “continuous audio timestamps”.
- Re-encoding (`libx264` / `aac`) is intentional; do not stream-copy for the final deliverable.

## Recommended “Correct” Production Workflow

### 1) Render scenes

- Render each scene to an MP4 file (Manim render).
- Ensure each file has an audio stream (AAC) and video stream (H.264).

### 2) Verify each scene output is sane

Per-scene checks (quick):

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,duration -of json scene.mp4
```

What you want:

- Both audio and video streams present.
- Audio duration close to video duration (it can be slightly shorter if you intentionally end on a silent visual beat).

### 3) Assemble with concat filter (NOT concat demuxer)

- Use the `filter_complex` concat approach shown above.
- Always re-encode the final.

### 4) Validate the final output

Basic duration sanity:

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,duration -of json final_video.mp4
```

Audio timestamp continuity check (detect large PTS jumps):

```bash
ffprobe -v error -select_streams a:0 -show_packets -show_entries packet=pts_time -of csv=p=0 final_video.mp4 \
  | python3 - <<'PY'
import sys
pts=[]
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try: pts.append(float(line))
    except: pass
pts.sort()
if len(pts) < 3:
    print('not enough packets')
    raise SystemExit(0)
diffs=[pts[i+1]-pts[i] for i in range(len(pts)-1)]
diffs_pos=sorted(d for d in diffs if d>0)
step=diffs_pos[max(0,int(len(diffs_pos)*0.1))] if diffs_pos else 0.0
gaps=[(pts[i],pts[i+1],d) for i,d in enumerate(diffs) if d>max(0.5, (step*20 if step else 0.5))]
print(f'packets={len(pts)} step~{step:.6f}s gaps={len(gaps)}')
for a,b,d in gaps[:20]:
    print(f'  {a:.3f} -> {b:.3f} gap={d:.3f}s')
PY
```

Goal:

- `gaps=0` (or at least no multi-second jumps).

## What NOT To Do (Pitfalls)

### 1) Avoid `-f concat ... -c copy` for final deliverables

- It’s fast, but it frequently preserves whatever timestamp weirdness exists.
- Even if it “plays in VLC”, QuickTime can fail.

### 2) Avoid assuming “re-encode fixes everything”

- Re-encoding without fixing audio timing may keep discontinuities, depending on how the discontinuity enters the pipeline.
- The `aresample=async=1:first_pts=0` step is the reliable fix when the issue is timestamp continuity.

### 3) Avoid mixing different audio sample rates / layouts across scenes

- Keep scenes consistent: same sample rate (e.g., 48kHz), channels (stereo), codec (AAC).
- Inconsistent audio across inputs increases risk of timestamp and concat quirks.

## Why Concat Filter Works Better

Conceptually:

- **Concat demuxer**: concatenates at the container level; can preserve per-file timing metadata.
- **Concat filter**: concatenates decoded streams in a single filtergraph timeline, then re-encodes. This tends to produce clean, monotonic timestamps.

When paired with `aresample=async=1:first_pts=0`, you get a continuous audio clock.

## Practical Guidance for This Repo

- If you are assembling Manim + ElevenLabs scene renders, default to:
  - concat filter + re-encode
  - `aresample=async=1:first_pts=0`
- If you need a single-file “safe assembler”, consider adding a script that:
  - reads `project_state.json` scene outputs
  - builds the `filter_complex` string
  - runs ffmpeg with the correct flags
  - validates with `ffprobe` and the PTS-gap scan

## Quick Checklist

- Per scene:
  - audio stream exists
  - sample rate consistent (recommend 48000)
- Final assembly:
  - use concat filter (`filter_complex concat`)
  - re-encode video + audio
  - include `aresample=async=1:first_pts=0`
- Post-assembly:
  - `ffprobe` shows audio duration ~= video duration
  - packet PTS scan shows no multi-second gaps

## Appendix: Common Commands

Show streams and durations:

```bash
ffprobe -hide_banner -v error \
  -show_entries format=duration \
  -show_entries stream=index,codec_type,codec_name,sample_rate,channels,start_time,duration \
  -of json file.mp4
```

Extract audio for listening sanity-check:

```bash
ffmpeg -y -i final_video.mp4 -vn -acodec pcm_s16le -ar 48000 -ac 2 final_audio.wav
```
