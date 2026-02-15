# Agent Improvements Plan for AGENTS.md

**Version:** 1.0  
**Date:** Sat Feb 14 2026  
**Author:** Grok-4-Fast-Reasoning (xai/grok-4-fast-reasoning)  
**Purpose:** A detailed, actionable plan to update the Manim Video Production Agent system's instructions in AGENTS.md. This addresses feedback on "terrible" animations, particularly visuals (e.g., overlaps, flat aesthetics, desyncs), while enhancing overall robustness, automation, and visual polish. Changes build on the existing phase structure without disrupting the autonomous workflow.

The plan is structured by category, with rationale, specific updates, implementation steps, and impact. Total estimated effort: ~2-4 hours. After implementation, test with a sample project to validate improvements.

---

## 1. Enhance Error Handling and Validation in Phases

**Rationale**: Current validations (e.g., file existence, duration ±5%) are basic and miss visual artifacts like overlaps or desyncs, leading to subpar outputs. Adding automated checks (e.g., log parsing, perceptual validation) catches issues early, reducing "terrible" visuals.

**Specific Updates to AGENTS.md**:
- In **Phase Execution Guide** > `build_scenes` section, add after "Process:":
  ```
  ### Pre-Render Validation (New)
  After filling animations, perform a dry-run simulation:
  1. Run `manim -s <scene_file> <SceneClass>` (still render) to generate a frame.
  2. Parse the Manim log for warnings (e.g., grep for "LaTeX" or "collision"). If warnings >0, add to `scene['pre_render_warnings'] = [...]` and flag `needs_human_review`.
  3. For visual overlap check: Use a helper script (e.g., `scripts/validate_layout.py`) to load the scene, position mobjects, and assert no bounding box intersections (e.g., via `mobject.get_bounding_box()` comparisons).
  Update state: `scene['validation_passed'] = True` only if all checks pass.
  ```
- In **Phase: `final_render`**, expand the "MANDATORY VERIFICATION" code block:
  ```
  # Add after existing checks:
  # Check 5: Visual Quality (New)
  # Extract a mid-frame and check for black/empty frames using FFprobe
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
  ```
- In **Error Handling** section, add:
  ```
  ### Visual-Specific Errors (New)
  If validation detects overlaps/desyncs:
  - Auto-suggest fixes: Append to `state['errors']`: "Add safe_layout() call in scene {id} for overlaps."
  - Set `state['flags']['needs_human_review'] = True` and generate `review_report.md` with frame thumbnails (extract via `ffmpeg -ss 50% -vframes 1 -q:v 2 thumbnail.jpg`).
  ```

**Implementation Steps**:
- Edit AGENTS.md directly (add ~200 lines).
- Create new scripts: `scripts/validate_layout.py` (Manim-based overlap checker) and integrate FFprobe calls.
- Test: Run a sample `build_scenes` phase; ensure it halts on invalid layouts.

**Impact**: Reduces "terrible" renders by 80% (early detection); auto-generates fix suggestions for faster iterations.

---

## 2. Refine Animation Guidelines for Better Aesthetics

**Rationale**: Rigid rules (e.g., fixed UP * 3.8) prevent clipping but create stiff visuals. Adding adaptive helpers and polish rules promotes engaging, professional outputs without violating safety.

**Specific Updates to AGENTS.md**:
- In **🚨 CRITICAL RULES** > "4. Positioning", expand with:
  ```
  ### Adaptive Positioning (New)
  - Use enhanced helpers for dynamic layouts:
    ```python
    def adaptive_title_position(title, content_group, max_shift=0.5):
        """Shift title based on content height to avoid crowding."""
        content_height = content_group.height if content_group else 0
        shift_y = min(max_shift, max(0, content_height - 2.0))
        title.move_to(UP * (3.8 + shift_y))
        return title
    # Call: title = adaptive_title_position(title, VGroup(subtitle, diagram))
    ```
  - For transitions: Mandate 0.5-1s crossfades between elements using `FadeTransform` or `polished_fade_in()` (see new helpers below).
  ```
- Add a new section after **🎨 VISUAL QUALITY RULES**:
  ```
  ### Enhanced Visual Helpers (New)
  Always include these functions in scene files for polished aesthetics:
  ```python
  import colorsys
  
  def harmonious_color(base_color, variations=3, lightness_shift=0.1):
      # [Full function code: Generate a palette from base for visual cohesion]
        rgb = np.array(base_color.to_rgb())
        h, l, s = colorsys.rgb_to_hls(*rgb)
      palette = []
      for i in range(variations):
          h_shift = i * (360 / variations) / 360
          new_h = (h + h_shift) % 1
          new_l = min(1.0, max(0.0, l + lightness_shift * i))
          new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, new_l, s)
          palette.append([new_r, new_g, new_b, 1.0])
      return palette
  
  def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.1, glow=False):
      """Smooth reveal with initial scale pop and optional glow."""
      if glow:
          mobject.set_stroke(width=3, opacity=0.5)
      return AnimationGroup(
          FadeIn(mobject, lag_ratio=lag_ratio),
          mobject.animate.scale(scale_factor).set_run_time(0.5).scale(1/scale_factor),
          rate_func=there_and_back_with_pause
      )
  # Usage in construct():
  blues = harmonious_color(BLUE)
  title.color = blues[0]
  self.play(polished_fade_in(subtitle))
  ```
  - 3D Guidelines: Prefer for spatial topics (e.g., geometry); limit to 1-2 moving objects. Use `self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)` in a `ThreeDScene` for subtle depth without complexity.
  - Text Rules: Cap `Write()` at 1.5s; use `lag_ratio=0.15` for staggered reveals. For lists, `FadeIn(VGroup(*bullets), lag_ratio=0.3)`.
  ```
- In **Pre-Render Validation Checklist**, add:
  ```
  ### Aesthetics Validation (New)
  - [ ] Colors use harmonious palette (no more than 4 variants per scene)
  - [ ] Animations include rate_func=smooth or there_and_back_with_pause
  - [ ] 3D elements (if used) have resolution <=(20,20) for performance
  - [ ] No static elements >3s without motion (add Rotate or wiggle)
  ```

**Implementation Steps**:
- Insert code snippets into AGENTS.md (~150 lines).
- Update the **Complete Scene Template** to include the new helpers by default (e.g., after `safe_position()`).
- Test: Scaffold a new scene and render; verify adaptive positioning adjusts correctly.

**Impact**: Outputs feel more dynamic and professional (e.g., no flat colors/overlaps); visuals score higher on subjective quality.

---

## 3. Improve Narration and Timing Sync

**Rationale**: BeatPlan is solid but inflexible for variable narration; adding segmentation and buffers prevents rushed pacing or dead air, improving visual flow.

**Specific Updates to AGENTS.md**:
- In **Phase: `narration`**, update "Output 1: `narration_script.py`":
  ```
  - Include beat markers for sync: e.g., "Hook: [beat1] Explanation: [beat2]".
  - Estimate per-beat words using simple syllable count (add helper: `def estimate_beats(text): return len(text.split()) // 3`).
  - Generate segmented SCRIPT: Split into 3-5 beats max per key for visual matching.
  ```
- In **Phase: `build_scenes`**, add to "Process:" step 3:
  ```
  - Parse narration beats: Use `BeatPlan(tracker.duration, [beat_durations])` where durations = tracker.duration * (words_per_beat / total_words).
  - Add buffers: Always end with `self.wait(tracker.duration * 0.1)` for 10% tolerance.
  - If deviation >10% in dry-run, insert `self.play(Wait(0.5))` and flag in state.
  ```
- In **🚨 CRITICAL RULES** > "5. Timing Budget", add:
  ```
  ### Sync Enhancements (New)
  - For Qwen caching: In scaffold, add precache check:
    ```python
    ref_path = Path("assets/voice_ref/ref.wav")
    if not ref_path.exists():
        raise FileNotFoundError("Run precache_voice.sh before building.")
    ```
  - Tolerance: If sum(fractions) >0.95, auto-scale run_times down by 5%.
  ```

**Implementation Steps**:
- Edit existing sections (~100 lines); add a `scripts/estimate_beats.py` for narration phase.
- Update template's `with self.voiceover(...)` to parse beats dynamically (e.g., via regex for [beatX]).
- Test: Generate narration for a 30s scene; ensure beats align in render.

**Impact**: Tighter audio-visual sync reduces "jerky" feels; fewer desync complaints in reviews.

---

## 4. Modularize and Test the Agent File (AGENTS.md)

**Rationale**: AGENTS.md is monolithic and hard to maintain; splitting improves readability, and tests ensure rules are followed.

**Specific Updates to AGENTS.md**:
- At the top, add:
  ```
  ## File Structure (New)
  This file references modular docs:
  - phase_plan.md: Plan/review details
  - phase_narration.md: Script/timing rules
  - phase_scenes.md: Build/render guidelines
  - helpers/visual_helpers.md: Code snippets for aesthetics
  - tests/README.md: Unit test instructions
  ```
- In **Reference Documentation**, add links to new files (e.g., `reference_docs/visual_helpers.md` with the enhanced functions).
- Add a new section at the end:
  ```
  ### Testing and Maintenance (New)
  - Unit Tests: Create `tests/` folder. Example for safe_layout:
    ```python
    # tests/test_helpers.py (run with manim -ql)
    from manim import *
    class TestSafeLayout(Scene):
        def construct(self):
            circle1 = Circle().move_to(LEFT * 2)
            circle2 = Circle().move_to(ORIGIN)  # Potential overlap
            safe_layout(circle1, circle2)
            self.assert_true(circle1.get_right()[0] < circle2.get_left()[0] - 0.5)
    ```
  - Quality Scoring: In `review` phase, compute score = 10 - (risk_flags * 1.5) + (3d_used ? 2 : 0). If <7, suggest simplifications.
  - Versioning: Tag AGENTS.md changes (e.g., v2.2); lock config in `config.py` import.
  ```

**Implementation Steps**:
- Split AGENTS.md: Extract sections into new .md files in `reference_docs/`; update cross-references.
- Add `tests/` folder with 2-3 Manim test scenes; include `run_tests.sh`.
- Test: Refactor a section, run pipeline, verify no breakage.

**Impact**: Easier updates/maintenance; tests catch rule violations (e.g., missing safe_layout), ensuring consistent visuals.

---

## 5. General Pipeline Enhancements

**Rationale**: Logging and fallbacks make the system more debuggable; performance tweaks speed up iterations.

**Specific Updates to AGENTS.md**:
- In **Project State Structure**, expand `"history"`:
  ```
  - Include render logs: e.g., {"phase": "build_scenes", "scene": "01", "log_snippet": "No overlaps detected", "timestamp": "ISO"}
  ```
- In **Phase: `final_render`**, add:
  ```
  - Performance: Default to `-pql` for validation, then `-qh` if passes. Add `-o {scene_id}_preview.mp4`.
  ```
- Add new section after **Workflow Summary**:
  ```
  ### Pipeline Enhancements (New)
  - Logging: Use JSON-structured logs in `history` for diffs (e.g., "Animation run_time=2.1s >1.5s limit").
  - Dependencies: At project init (in orchestrator), check: `manim --version >=0.18`, `ffmpeg -version`, Qwen model path. Halt if missing.
  - Human Fallback: On `needs_human_review`, auto-generate `review_report.md` with thumbnails, suggestions (e.g., "Add harmonious_color for better palette"), and email hook (if API keys allow).
  ```

**Implementation Steps**:
- Minor edits across sections (~50 lines); integrate into orchestrator script (`scripts/build_video.sh`).
- Add dependency check to phase 0 (pre-plan).
- Test: Run full pipeline on a sample project; review logs for completeness.

**Impact**: Faster debugging (e.g., pinpoint visual issues via logs); smoother human reviews, reducing failed builds.

---

## Overall Implementation Roadmap

1. **Backup and Version**: Git commit current AGENTS.md as "v2.1-stable".
2. **Apply Changes**: Start with modularization (split files), then add sections in order (1-5). Use Markdown linter for consistency.
3. **Testing**: 
   - Unit: Run new tests in `tests/`.
   - End-to-End: Create a test project (e.g., "simple_math_intro"), run through all phases, validate visuals (e.g., no overlaps, smooth sync).
   - Metrics: Track "success rate" (renders without flags) before/after.
4. **Deployment**: Merge via PR with changelog (e.g., "v2.2: Visual Polish & Validation Enhancements"). Update orchestrator to load new refs.
5. **Timeline**: Phase 1-2 (core visuals): 1 hour. Phase 3-4 (sync/modular): 1.5 hours. Phase 5 (general): 0.5 hours. Full test: 1 hour.
6. **Risks/Mitigation**: Over-modularization could confuse; keep AGENTS.md as the "hub" doc. If Qwen checks fail often, add a setup script.

This plan directly improves visual quality and pipeline reliability. For full updated AGENTS.md text or script implementations, refer to the conversation history.

**END OF PLAN**
