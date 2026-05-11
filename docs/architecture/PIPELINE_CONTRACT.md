# Pipeline Contract

Audience: Local coding agents working on Flaming Horse.

Purpose: Define the current shell-script pipeline from a topic argument to `final_video.mp4`.

## Primary Use Case

The primary user workflow is:

```bash
./scripts/create_video.sh my_video --topic "Standing waves explained visually"
```

Expected output:

```text
projects/my_video/final_video.mp4
```

The secondary workflow is assistant-mediated operation of the same framework. Assistants should improve the framework, inspect runs, and operate scripts. They should not replace the pipeline by hand-authoring final generated scenes.

## Entrypoint Flow

The canonical path is:

1. `scripts/create_video.sh`
   - Sources `.env` when present.
   - Enforces Python 3.13 through `${PYTHON:-python3.13}`.
   - Parses `<project_name>`, `--topic`, `--phase`, `--projects-dir`, `--build-args`, and `--skip-precache`.
   - Resolves the project directory.
   - Resumes if `project_state.json` exists.
   - Calls `scripts/new_project.sh` for a new project.
   - Calls `scripts/prepare_voice_service.py`.
   - `exec`s `scripts/build_video.sh`.

2. `scripts/new_project.sh`
   - Creates `projects/<project_name>/`.
   - Writes `voice_clone_config.json`.
   - Seeds `assets/voice_ref/ref.wav` and `assets/voice_ref/ref.txt`.
   - Writes `project_state.json` with `phase: "plan"`.

3. `scripts/build_video.sh`
   - Acquires `.build.lock`.
   - Starts heartbeat diagnostics.
   - Normalizes and validates `project_state.json`.
   - Runs the current phase.
   - Applies deterministic state transitions through `scripts/update_project_state.py`.
   - Repeats until `complete`, failure, or human-review pause.

## Phase Sequence

Current canonical phase sequence:

```text
init -> plan -> review -> narration -> build_scenes -> scene_qc -> precache_voiceovers -> final_render -> assemble -> complete
```

`training` is not a current canonical phase. `scripts/update_project_state.py` maps legacy `training` state to `build_scenes`.

## State Ownership

`project_state.json` is script-owned.

Agents and harness phases may create or update phase artifacts such as:

1. `plan.json`
2. `narration_script.py`
3. `scene_*.py` scene-body content through scaffold injection
4. `scene_qc_report.md`

State normalization and phase advancement are owned by:

1. `scripts/update_project_state.py`
2. `scripts/build_video.sh`
3. `scripts/state_schema.json`

The harness must not be trusted as the authority for phase transitions.

## Artifact Layout

Typical generated project layout:

```text
projects/<project_name>/
  project_state.json
  plan.json
  narration_script.py
  scene_*.py
  voice_clone_config.json
  scene_qc_report.md
  scenes.txt
  final_video.mp4
  assets/
    voice_ref/
      ref.wav
      ref.txt
  media/
    voiceovers/
    videos/
  log/
    build.log
    error.log
    conversation.log
```

Generated artifacts are runtime evidence by default. Fix generator, orchestrator, prompt, parser, scaffold, validator, or voice integration code before patching a one-off project artifact.

## Loop And Retry Behavior

`build_video.sh` treats these phases as retryable:

```text
init, plan, narration, build_scenes, scene_qc, final_render, assemble
```

Retry context is written to:

```text
projects/<project_name>/.agent_retry_<phase>.md
```

Current behavior includes repair and recovery branches around model output. This is part of the current runtime, not a guarantee that first-pass generation is valid.

## Human Review Boundary

The loop pauses when:

```json
{"flags": {"needs_human_review": true}}
```

When reporting a pause or failure, include:

1. Phase.
2. Origin.
3. Causal chain.
4. Primary source-level fix.
5. Whether any containment was used.

## Execution-Relevant Drift

If this document diverges from `scripts/create_video.sh`, `scripts/build_video.sh`, `scripts/update_project_state.py`, or `scripts/state_schema.json`, runtime code wins for current behavior. Stop and ask before changing execution based on the document.
