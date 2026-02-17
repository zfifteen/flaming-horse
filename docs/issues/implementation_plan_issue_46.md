# Implementation Plan: Make Scene Generation Update-Only via Structured Spec + Immutable Scaffold

## Overview
This plan implements the enhancement from GitHub issue #46 to shift Flaming Horse's scene generation from full-file authoring (prone to drift on scaffold signatures/placeholders) to an update-only model. The agent will output a structured scene content spec (JSON), and a deterministic merge script will inject it into pre-created immutable scaffolds. This separates creative decisions (agent) from syntax/API-safe code emission (scripts), aiming to reduce first-pass failures, self-heal loops, and runtime validation churn.

Key goals:
- Agent never edits or creates scene files directly.
- Scaffolds are immutable (imports, config, helpers, class structure) and pre-created early.
- Spec includes content, helpers references, visual patterns, and custom code snippets.
- Orchestrator handles beat calculation based on narration word count.
- New validation phase ensures spec integrity before merging.
- Self-heal as fallback: If spec malformed, return to agent with explanation for correction.

## Spec Format Definition
The scene content spec is a JSON object output by the agent during `build_scenes`. It defines the creative content and animation sequence without generating code.

```json
{
  "scene_id": "scene_01_intro",
  "narration_key": "intro",
  "title": "Introduction to Topic",
  "subtitle": "Key Concepts Overview",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "visual_pattern": "explainer_slide_left_bullets_right_diagram",
  "visual_elements": [
    {
      "type": "diagram",
      "description": "Rounded rectangle with evolving content",
      "position": "RIGHT * 3.2 + DOWN * 0.6",
      "helpers": ["harmonious_color", "polished_fade_in"]
    }
  ],
  "animation_sequence": [
    {
      "step": 1,
      "description": "Write title with adaptive positioning",
      "animation": "Write(title)",
      "helpers": ["adaptive_title_position"],
      "timing_fraction": 0.1
    },
    {
      "step": 2,
      "description": "Fade in subtitle",
      "animation": "FadeIn(subtitle)",
      "helpers": ["polished_fade_in"],
      "timing_fraction": 0.1
    },
    {
      "step": 3,
      "description": "Progressive bullet reveals",
      "animation": "LaggedStart(*[FadeIn(bullet) for bullet in bullets], lag_ratio=0.15)",
      "timing_fraction": 0.2
    },
    {
      "step": 4,
      "description": "Create diagram and fade out bullets",
      "animation": "Create(diagram), FadeOut(subtitle), FadeOut(*bullets)",
      "timing_fraction": 0.3
    },
    {
      "step": 5,
      "description": "Custom code snippet for dynamic elements",
      "custom_code": "node_left = Dot(LEFT * 1.0 + DOWN * 1.8, color=RED)\nnode_right = Dot(RIGHT * 1.0 + DOWN * 1.8, color=RED)\nplay_next(self, beats, FadeIn(node_left), FadeIn(node_right))",
      "timing_fraction": 0.3
    }
  ],
  "beat_weights": [1, 1, 1, 1, 1],  // Optional: Agent can override default weights
  "metadata": {
    "estimated_duration": 15.0,  // In seconds, for validation
    "custom_imports": []  // If needed, but keep minimal
  }
}
```

- **Fields**:
  - `scene_id`, `narration_key`: From state, for context.
  - `title`, `subtitle`, `key_points`: Content strings/arrays.
  - `visual_pattern`: Key from `docs/reference_docs/topic_visual_patterns.md` (e.g., "explainer_slide").
  - `visual_elements`: Array of objects describing diagrams/labels, with type, description, position (Manim coords), and helper references.
  - `animation_sequence`: Ordered list of steps. Each has description, animation (code string), helpers array, timing_fraction (sums to ≤1.0), and optional custom_code (full Python snippet).
  - `beat_weights`: Array of numbers (e.g., [1]*n) for BeatPlan; agent can specify, but orchestrator provides default.
  - `metadata`: Estimated duration, custom imports (discouraged).
- **Validation Rules**: Required fields: scene_id, narration_key, title, animation_sequence. Timing fractions sum to ≤1.0. Custom code must be syntactically valid Python (checked via AST parse).

## Changes to Phases
### New Phase: `scaffold_all` (After `narration`, Before `build_scenes`)
- **Goal**: Pre-create immutable scaffold files for all scenes.
- **Actions**:
  1. For each scene in `state['scenes']`, run `scripts/scaffold_scene.py` with --project, --scene-id, --class-name, --narration-key.
  2. Scaffold includes: Locked imports/config, helpers (safe_position, harmonious_color, etc.), class definition, construct method with voiceover setup and empty SLOT_START/END markers.
  3. Update state: `scene['scaffold_created'] = true`.
- **Orchestrator**: Advance to `scaffold_all` after `narration` completes.

### New Phase: `validate_specs` (After `build_scenes` Generates Specs, Before Merging)
- **Goal**: Validate agent-generated specs before merging.
- **Actions**:
  1. For each scene spec:
     - Check required fields present.
     - Sum timing_fractions ≤1.0.
     - Simulate code generation: Parse custom_code with `ast.parse()`; ensure no forbidden constructs (e.g., no network calls).
     - Estimate total duration from beat weights and narration duration.
  2. If fails: Set `needs_human_review = true`, add errors to state['errors'], stay in phase.
- **Orchestrator**: If all pass, advance to `merge_specs` (new phase); else, halt.

### Modified Phase: `build_scenes`
- **Goal**: Agent generates spec (JSON), not scene code.
- **Actions**:
  1. Read current scene from state.
  2. Orchestrator provides: Narration text, word count, recommended num_beats (calculated as below).
  3. Agent outputs spec JSON to `projects/<project>/specs/<scene_id>.json`.
  4. Update state: `scene['spec_generated'] = true`, `scene['spec_file'] = 'specs/<scene_id>.json'`.
- **No file editing**: Agent never touches .py files.

### New Phase: `merge_specs` (After `validate_specs`, Before `final_render`)
- **Goal**: Deterministically merge validated specs into scaffolds.
- **Actions**:
  1. For each scene: Run new `scripts/merge_spec.py --project <proj> --scene-id <id> --spec-file <file>`.
     - Script: Read scaffold, replace SLOT_START/END with generated code from spec.
     - Generate code: Map spec to Manim calls (e.g., title = Text(spec['title'], ...); play_text_next(...)).
     - Use helpers as referenced; insert custom_code directly.
     - Ensure BeatPlan uses spec's beat_weights or default.
  2. Update state: `scene['merged'] = true`.
- **Deterministic**: No agent involvement; pure code emission.

### Existing Phases: `final_render`, `assemble`, `complete`
- No changes; they operate on merged .py files as before.

## Orchestrator Changes
- **Beat Calculation**: In `build_scenes`, before invoking agent:
  - Read narration text for scene from `narration_script.py`.
  - Count words: `len(text.split())`.
  - Assume speaking rate: 150 wpm (words per minute).
  - Duration estimate: `words / (150 / 60)` seconds.
  - Num beats: `max(5, min(20, int(duration / 10)))` (one beat every ~10 seconds, adjusted for short/long scenes).
  - Provide to agent: recommended_num_beats, estimated_duration.
- **State Updates**: Add fields like `scaffold_created`, `spec_generated`, `validated`, `merged`.
- **Self-Heal Integration**: If spec malformed in `validate_specs`, set `needs_human_review`, but also queue for agent retry with error explanation (e.g., "Timing fractions sum to 1.2 >1.0; adjust step 5").

## Agent Prompt Changes
- **System Prompt (harness/prompt_templates/build_scenes_system.md)**: Update to instruct outputting JSON spec, not Python code. Provide spec schema. Reference helpers/visual patterns. Include recommended_num_beats and estimated_duration.
- **Example Output**: Show sample JSON spec in prompt.
- **Restrictions**: No file I/O; no creating/editing .py files.

## New Scripts/Tools
1. **`scripts/merge_spec.py`**: 
   - Inputs: --project, --scene-id, --spec-file.
   - Reads scaffold .py, spec JSON.
   - Generates code inside SLOT_START/END: Define variables (title, bullets), apply helpers, build animation sequence with play_text_next/play_next.
   - Handles custom_code: Insert as-is.
   - Writes updated .py.

2. **`scripts/validate_spec.py`** (for `validate_specs` phase):
   - Inputs: spec JSON.
   - Checks: Required fields, sum(timing_fractions) <=1.0, ast.parse(custom_code).
   - Outputs: Pass/fail with details.

3. **Updated `scripts/scaffold_scene.py`**: Modify template to have empty SLOT_START/END (no default example code). Ensure immutability.

## Testing and Migration
- **Unit Tests**: Add tests in `tests/` for spec validation, merge output, beat calculation.
- **E2E Tests**: Update `tests/test_harness_e2e.sh` to cover new phases.
- **Existing Projects**: Out of scope; assume fresh projects only.
- **Dry Runs**: Add --dry-run to simulate spec generation without writing files.

## Acceptance Criteria Mapping
- **Agent cannot create scene files**: Enforced by scaffold pre-creation and no edit perms in build_scenes.
- **First-pass edits only slot regions**: Merge script only touches SLOT_START/END.
- **Reduce failures**: Validation catches issues early; deterministic merge prevents drift.
- **Existing repaired projects render**: N/A (out of scope).
- **Self-heal fallback**: Triggered on malformed spec, with explanation to agent.