# Phase Scenes Build and Render Details

## Phase: `build_scenes`

**Goal:** Generate Manim scene files one at a time

**Process:**
1. Get current scene: `scene = state['scenes'][state['current_scene_index']]`
2. Scaffold the scene file first using (run from repo root, or use an absolute path):
   ```bash
   python3 scripts/scaffold_scene.py \
       --project <project_dir> \
       --scene-id <scene_file_without_py> \
       --class-name <SceneClassName> \
       --narration-key <script_key>
   ```
3. Fill in animations inside the scaffolded `# TODO: Add animations here` block
   - Parse narration beats: Use `BeatPlan(tracker.duration, [beat_durations])` where durations = tracker.duration * (words_per_beat / total_words).
   - Use the full narration duration with staged visual beats; avoid long tail idle waits.
   - Prefer duration-scaled micro-beats per scene: `num_beats = max(10, min(22, int(np.ceil(tracker.duration / 3.0))))`.
   - Fixed 8-12 beats is only acceptable for short scenes; longer narration must use proportionally more beats.
   - Beat slot count must be sufficient for animation call count; if slots are exhausted, increase beat count or split into multiple voiceover blocks.
   - Never pass `run_time=` into `play_next(...)` or `play_text_next(...)`; slot helpers are the timing source.
   - If deviation >10% in dry-run, rebalance beat slots and flag in state.
4. Keep the generated boilerplate structure unchanged unless absolutely necessary
5. Update scene status to `'built'` AND persist required render metadata into state:
   - `scene['file'] = '<scene_id>.py'`
   - `scene['class_name'] = '<SceneClassName>'`

### Pre-Render Validation (New)
After filling animations, perform a dry-run simulation:
1. Run `manim -s <scene_file> <SceneClass>` (still render) to generate a frame.
2. Parse the Manim log for warnings (e.g., grep for "LaTeX" or "collision"). If warnings >0, add to `scene['pre_render_warnings'] = [...]` and flag `needs_human_review`.
3. For visual overlap check: Use a helper script (e.g., `scripts/validate_layout.py`) to load the scene, position mobjects, and assert no bounding box intersections (e.g., via `mobject.get_bounding_box()` comparisons).
Update state: `scene['validation_passed'] = True` only if all checks pass.

6. Increment `current_scene_index`
7. If all scenes built: advance to `final_render`

### Layout Checklist (Mandatory)
- Title must exist and be visible at `UP * 3.8` (or via `adaptive_title_position`).
- Subtitle must be `.next_to(title, DOWN, buff=0.4)` and then `safe_position(subtitle)`.
- Graphs/diagrams must be offset downward (e.g., `DOWN * 0.6` to `DOWN * 1.2`) to avoid title overlap.
- Labels must attach to nearby elements (e.g., `label.next_to(curve.get_end(), UP, buff=0.2)`), then `safe_position(label)`.
- Do not use `.next_to(...)` inside list comprehensions unless each element is subsequently passed through `safe_position(...)` explicitly.
- After positioning, run `safe_layout(...)` for free-positioned sibling clusters; for strict `.next_to(...)` chains, call `safe_position(...)` per element.
- ❌ NEVER use `.to_edge(...)` for titles or labels (causes clipping/edge drift).
- For non-math topics, default to explainer-slide layout: left-panel progressive bullets + right-panel evolving topic visual.
- Derive right-panel visuals from narration keywords; use `reference_docs/topic_visual_patterns.md` patterns.
- Ensure a visible transition every ~1.5-3 seconds; avoid static black intervals.

---

## Phase: `final_render`

**Goal:** Render all scenes with cached Qwen voice (production quality) and verify output

**Actions:**
1. For each scene in `state['scenes']`:
   ```bash
   manim render <scene_file> <SceneClass> -qh
   ```
   - Performance: Default to `-pql` for validation, then `-qh` if passes. Add `-o {scene_id}_preview.mp4`.

2. **MANDATORY VERIFICATION** after each render:
   ```python
   import os
   from moviepy.editor import VideoFileClip
   
   video_path = f"media/videos/{scene['id']}/1440p60/{scene['class_name']}.mp4"
   
   # Check 1: File exists
   if not os.path.exists(video_path):
       raise FileNotFoundError(f"Scene {scene['id']} failed to render")
   
   # Check 2: File size > 0
   file_size = os.path.getsize(video_path)
   if file_size == 0:
       raise ValueError(f"Scene {scene['id']} rendered as 0 bytes")
   
   # Check 3: Video duration matches estimate ±5%
   clip = VideoFileClip(video_path)
   expected_duration = float(scene['estimated_duration'].rstrip('s'))
   actual_duration = clip.duration
   
   if not (expected_duration * 0.95 <= actual_duration <= expected_duration * 1.05):
       print(f"WARNING: Scene {scene['id']} duration mismatch - "
             f"expected {expected_duration}s, got {actual_duration}s")
   
   # Check 4: Audio track present
   if clip.audio is None:
       raise ValueError(f"Scene {scene['id']} has no audio track")
   
   # Add after existing checks:
   # Check 5: Visual Quality (New)
   # Extract a mid-frame and check for black/empty frames using FFprobe
   import subprocess
   subprocess.run([
       "ffprobe", "-v", "error", "-select_streams", "v:0",
       "-show_frames", "-show_entries", "frame=pict_type,pixdiffs",
       "-of", "csv=p=0", video_path
   ], capture_output=True, check=True)
   # Flag if >10% frames are black (pict_type=B with high pixdiffs variance)
   # If fails, raise ValueError("Visual artifacts detected in {scene['id']}")
   
   # Check 6: Audio-Visual Sync (New)
   # Use FFprobe to check A/V timestamp delta <0.1s
   # Command: ffprobe -show_entries stream=avg_frame_rate,start_pts -select_streams v:0,a:0
   # If delta >0.1s, re-encode with `self.wait(0.1)` buffer in scene code.
   
   clip.close()
   
   # Log verification to state
   scene['verification'] = {
       'file_size_bytes': file_size,
       'duration_seconds': actual_duration,
       'audio_present': True,
       'verified_at': datetime.now().isoformat()
   }
   ```

3. Update scene metadata with output video path
4. Mark scenes as `"rendered"`

**Critical:** Must actually execute render commands AND verify output. Do not skip or simulate.

**State Update:**
```python
for scene in state['scenes']:
    scene['status'] = 'rendered'
    scene['video_file'] = f"media/videos/{scene['id']}/1440p60/{scene['class_name']}.mp4"

state['phase'] = 'assemble'
```

## Parallel Rendering (Automatic)

The orchestrator automatically renders scenes in parallel when:
- `PARALLEL_RENDERS` env var set (0=auto, N=use N jobs, -1=disable)
- GNU parallel installed
- All scenes pass pre-render validation

**Agent action:** None required. Orchestrator handles parallelization.

Required env vars (set by orchestrator):
- `MANIM_VOICE_PROD=1`
- `PYTHONPATH=<repo_root>`
- `FLAMING_HORSE_TTS_BACKEND=qwen`
- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`
- `TOKENIZERS_PARALLELISM=false`
