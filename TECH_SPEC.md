# Flaming Horse — Technical Specification

**Version:** 1.0  
**Date:** 2026-02-23  
**Repository:** `zfifteen/flaming-horse`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Technology Stack](#2-technology-stack)
3. [Directory Structure](#3-directory-structure)
4. [Pipeline State Machine](#4-pipeline-state-machine)
5. [Core Components](#5-core-components)
   - 5.1 [Orchestrator — `scripts/build_video.sh`](#51-orchestrator--scriptsbuild_videosh)
   - 5.2 [Project Initialization — `scripts/new_project.sh` and `scripts/create_video.sh`](#52-project-initialization--scriptsnew_projectsh-and-scriptscreate_videosh)
   - 5.3 [State Authority — `scripts/update_project_state.py`](#53-state-authority--scriptsupdate_project_statepy)
   - 5.4 [Scene Scaffolding — `scripts/scaffold_scene.py`](#54-scene-scaffolding--scriptsscaffold_scenepy)
   - 5.5 [Legacy Harness — `harness/`](#55-legacy-harness--harness)
   - 5.6 [Responses API Harness — `harness_responses/`](#56-responses-api-harness--harness_responses)
   - 5.7 [Scene Helpers — `flaming_horse/scene_helpers.py`](#57-scene-helpers--flaming_horsescene_helperspy)
   - 5.8 [Voice Services — `flaming_horse_voice/`](#58-voice-services--flaming_horse_voice)
6. [Prompt Architecture](#6-prompt-architecture)
7. [Data Contracts](#7-data-contracts)
   - 7.1 [`project_state.json`](#71-project_statejson)
   - 7.2 [`plan.json`](#72-planjson)
   - 7.3 [`narration_script.py`](#73-narration_scriptpy)
   - 7.4 [Scene File Contract](#74-scene-file-contract)
   - 7.5 [Voice Cache Contract — `cache.json`](#75-voice-cache-contract--cachejson)
8. [Validation Gates](#8-validation-gates)
9. [Self-Healing and Retry Logic](#9-self-healing-and-retry-logic)
10. [Configuration and Environment Variables](#10-configuration-and-environment-variables)
11. [Harness Exit Codes](#11-harness-exit-codes)
12. [Logging and Observability](#12-logging-and-observability)
13. [Voice Policy](#13-voice-policy)
14. [Testing](#14-testing)
15. [Render and Assembly](#15-render-and-assembly)
16. [Harness Selection Seam — `FH_HARNESS`](#16-harness-selection-seam--fh_harness)
17. [Known Constraints and Risk Areas](#17-known-constraints-and-risk-areas)

---

## 1. Overview

Flaming Horse is a **deterministic, script-orchestrated pipeline** that converts a topic string into a fully narrated Manim video (`final_video.mp4`) with minimal human intervention.

The pipeline integrates:

- **Bash orchestration** — a phased state machine that drives every stage from project creation through final video assembly.
- **LLM agent harness** — a provider-agnostic harness (`harness/`) that composes phase-specific prompts, calls the LLM API, parses structured outputs, and writes artifacts to disk. A second, isolated harness (`harness_responses/`) is under active development to use the xAI Responses API with schema-constrained structured outputs.
- **Manim CE** — all visual animation is generated as Python scene files and rendered by Manim at 1440p60.
- **Qwen TTS** — a cached local voice clone (Qwen3-TTS-12Hz-1.7B-Base) provides all narration audio. There is no fallback TTS service.
- **FFmpeg** — renders are assembled into a single `final_video.mp4` using a concat filter with audio/video timestamp normalization.

**Canonical user entrypoint:**

```bash
./scripts/create_video.sh <project_name> --topic "Standing waves explained visually"
```

**Output:** `projects/<project_name>/final_video.mp4`

---

## 2. Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Orchestration | Bash (`set -Eeuo pipefail`) | Python 3.13 enforced |
| LLM Integration (legacy) | HTTP to OpenAI-compatible `/chat/completions` | XAI, MiniMax, Ollama |
| LLM Integration (new) | `xai_sdk` via `/v1/responses` | `harness_responses/` only |
| Animation engine | Manim Community Edition | 2560×1440 (16:9), 60fps |
| Voice synthesis | Qwen/Qwen3-TTS-12Hz-1.7B-Base (local) | Cached pre-generation; no runtime TTS calls |
| Video assembly | FFmpeg | concat filter + `aresample=async=1` |
| State management | JSON + Python | `project_state.json`; schema in `state_schema.json` |
| Python version | 3.13 (enforced at build entry) | |
| Testing | pytest + bash smoke tests | No live API calls in standard suite |

---

## 3. Directory Structure

```text
flaming-horse/
├── scripts/                         # Bash/Python orchestration
│   ├── build_video.sh               # Main deterministic orchestrator
│   ├── create_video.sh              # Canonical user entrypoint (create + build)
│   ├── new_project.sh               # Project initialization only
│   ├── reset_phase.sh               # Manual phase reset utility
│   ├── update_project_state.py      # Authoritative state normalization and phase advance
│   ├── scaffold_scene.py            # Scene file template generator
│   ├── scene_validation.sh          # Syntax/import/structure checks
│   ├── validate_scene_timing_budget.py  # Animation timing constraints
│   ├── validate_layout.py           # Mobject overlap detection
│   ├── validate_scene_content.py    # SCRIPT[] reference and content checks
│   ├── precache_voiceovers_qwen.py  # Voice cache generation entry
│   ├── precache_voiceovers_qwen_worker.py  # Per-scene worker
│   ├── prepare_qwen_voice.py        # Voice backend warm-up
│   ├── qwen_tts_mediator.py         # TTS backend routing (qwen/mlx)
│   ├── voice_ref_mediator.py        # Voice reference directory resolution
│   ├── generate_scenes_txt.py       # Generates FFmpeg concat input list
│   ├── qc_final_video.sh            # Post-assembly quality control
│   ├── check_dependencies.sh        # Environment preflight check
│   ├── state_schema.json            # JSON Schema for project_state.json
│   └── ...
│
├── harness/                         # Legacy LLM harness (Chat Completions)
│   ├── cli.py                       # Argparse CLI and main()
│   ├── __main__.py                  # python -m harness entry
│   ├── client.py                    # Provider-agnostic LLM API client
│   ├── prompts.py                   # Phase-specific prompt composer
│   ├── parser.py                    # Response parser and artifact writer
│   ├── prompts/                     # Modular prompt assets (one dir per phase)
│   │   ├── 00_plan/
│   │   ├── 01_review/
│   │   ├── 02_narration/
│   │   ├── 04_build_scenes/
│   │   ├── 05_scene_qc/
│   │   ├── 06_scene_repair/
│   │   └── _shared/
│   ├── templates/                   # Reference templates (kitchen sink, etc.)
│   └── util/
│       └── layout_validator.py
│
├── harness_responses/               # New isolated xAI Responses API harness
│   ├── cli.py
│   ├── client.py                    # Uses xai_sdk chat.parse()
│   ├── parser.py
│   ├── prompts.py
│   ├── schemas/                     # Pydantic models for structured output
│   └── prompts/                     # Phase-specific prompt assets (separate from harness/)
│
├── flaming_horse/
│   └── scene_helpers.py             # Layout, color, animation helpers for scene files
│
├── flaming_horse_voice/             # Voice service implementations
│   ├── service_factory.py           # get_speech_service() entry point
│   ├── qwen_cached.py               # QwenCachedService (strict, no fallback)
│   ├── mlx_cached.py                # MLX TTS cached variant
│   └── mlx_tts_service.py
│
├── tests/                           # Test suite
├── docs/
│   ├── policies/
│   │   ├── USER_PREFERENCES.md
│   │   ├── VOICE_POLICY.md
│   │   └── DEVELOPMENT_GUIDELINES.md
│   ├── reference_docs/              # Phase specifications, visual patterns
│   ├── requirements/                # Feature requirement documents
│   └── guides/                      # Installation and setup guides
│
├── projects/                        # Per-project runtime artifacts (gitignored)
├── examples/                        # Example outputs
├── assets/                          # Shared static assets
├── AGENTS.md                        # Local agent operating manual
├── README.md                        # Quick start and overview
└── .env.example                     # Environment variable template
```

---

## 4. Pipeline State Machine

The pipeline executes phases in strict linear order. `project_state.json` (field: `phase`) is the authoritative current phase.

```
init → plan → review → narration → build_scenes → scene_qc
     → precache_voiceovers → final_render → assemble → complete
```

An additional `error` phase is used as a terminal failure state (distinct from recoverable retries).

### Phase Summary

| Phase | LLM? | Primary Output | Handler |
|---|---|---|---|
| `init` | No | `project_state.json` scaffold | `handle_init` |
| `plan` | Yes | `plan.json` | `handle_plan` |
| `review` | Stub | state advanced | `handle_review` |
| `narration` | Yes | `narration_script.py` | `handle_narration` |
| `build_scenes` | Yes (per scene) | `scene_<N>_<slug>.py` (one per scene) | `handle_build_scenes` |
| `scene_qc` | Yes | `scene_qc_report.md` | `handle_scene_qc` |
| `precache_voiceovers` | No | `media/voiceovers/qwen/cache.json` + `.mp3` files | `handle_precache_voiceovers` |
| `final_render` | No (self-heal may invoke LLM) | Per-scene `.mp4` under `media/videos/` | `handle_final_render` |
| `assemble` | No | `final_video.mp4` | `handle_assemble` |
| `complete` | No | — | `handle_complete` |

### Phase Advancement

Phase advancement is performed exclusively by `scripts/update_project_state.py` and inline Python heredocs inside `build_video.sh`. The LLM agent never writes phase values directly; all agent-produced JSON is parsed, validated, and applied through the state authority scripts.

### Human Review Pause

When `project_state.json.flags.needs_human_review` is `true`, the main loop exits after the current iteration and awaits manual intervention. This flag is set when retry budgets are exhausted or when a validation step produces an unrecoverable failure.

### Backward Compatibility

The legacy phase name `training` is mapped to `build_scenes` during state normalization for projects created before the rename.

---

## 5. Core Components

### 5.1 Orchestrator — `scripts/build_video.sh`

The main orchestrator (`build_video.sh`) is a Bash script implementing the full phase loop. It:

1. **Enforces Python 3.13**: Checks `$PYTHON_BIN` major/minor version and exits 1 if not 3.13.
2. **Loads `.env`**: Sources the `.env` file from repo root if present.
3. **Acquires a lock file**: `$PROJECT_DIR/.build.lock` prevents concurrent builds.
4. **Runs a heartbeat**: A background subshell writes `log/heartbeat.txt` every `$HEARTBEAT_INTERVAL_SECONDS` with current phase, stage, scene, and attempt for crash diagnostics.
5. **Iterates the phase loop**: In each iteration, normalizes state, validates state, backs up state, reads current phase, and dispatches to the appropriate `handle_<phase>` function.
6. **Invokes the harness**: Agent phases call `invoke_agent <phase> <run_count>`, which selects the harness based on `FH_HARNESS` and invokes it as a subprocess, capturing stdout/stderr to `build.log`.
7. **Invokes validation gates**: After each scene build, runs syntax, import, semantic, timing, layout, and runtime checks.
8. **Manages retry budget**: Uses `$PHASE_RETRY_LIMIT` (default: 3) and `$PHASE_RETRY_BACKOFF_SECONDS` (default: 2) for all retryable phases.
9. **Sets `PYTHONPATH`**: Exports `$REPO_ROOT:$SCRIPT_DIR` to ensure all Python invocations find `flaming_horse_voice`, `flaming_horse`, and harness modules.
10. **Plays sound notifications**: `afplay`/`osascript` on macOS for completion and error events (configurable via `PIPELINE_COMPLETION_SOUND`, `PIPELINE_ERROR_SOUND`).

**Key flags and arguments:**

| Flag | Effect |
|---|---|
| `--phase <name>` | Stop after the specified phase completes |
| `--topic "<text>"` | Inject topic override (primarily for plan phase) |
| `--skip-precache` | Skip voice precache step (use existing cache) |
| `--rerender-final` | Reset to `precache_voiceovers` and force fresh voice cache |

### 5.2 Project Initialization — `scripts/new_project.sh` and `scripts/create_video.sh`

- **`new_project.sh`**: Creates `projects/<name>/`, writes an initial `project_state.json` (phase: `plan`), creates `log/`, and optionally creates `voice_clone_config.json`.
- **`create_video.sh`**: Canonical user entrypoint. Calls `new_project.sh` if the project does not exist, then delegates to `build_video.sh`. Accepts the same `--topic`, `--phase` flags.

### 5.3 State Authority — `scripts/update_project_state.py`

`update_project_state.py` is the single source of truth for state manipulation. It:

- **Normalizes** any project state file to match the schema (adds missing keys, repairs invalid types, removes unknown fields).
- **Validates** the state against `state_schema.json` using Python's `jsonschema` library.
- **Advances** the phase based on detected artifacts (e.g., presence of `plan.json` advances `plan → review`).
- **Generates scene IDs deterministically**: Scene `id` and `narration_key` are assigned as `scene_01`, `scene_02`, etc. by array index, ignoring any values the LLM may have produced. This prevents non-deterministic IDs from breaking downstream file naming.
- **Backs up** the state file to `.state_backup.json` before writing changes.

**Phase sequence (from the script):**

```python
PHASE_SEQUENCE = (
    "init", "plan", "review", "narration", "build_scenes",
    "scene_qc", "precache_voiceovers", "final_render", "assemble", "complete", "error"
)
```

### 5.4 Scene Scaffolding — `scripts/scaffold_scene.py`

Generates a deterministic `scene_<N>_<slug>.py` file containing:

- Fixed `from ... import *` block (Manim, numpy, `VoiceoverScene`, `get_speech_service`, all scene helpers, `SCRIPT`).
- Locked render configuration: `frame_height=10`, `frame_width=10*16/9`, `pixel_height=1440`, `pixel_width=2560`.
- A `clamp_text_width()` utility function.
- A `class <ClassName>(VoiceoverScene):` body with `set_speech_service(...)` and a `with self.voiceover(text=SCRIPT["<narration_key>"]) as tracker:` block.
- `# SLOT_START:scene_body` … `# SLOT_END:scene_body` markers delimiting the region the harness will fill.
- Inline `# PROMPT:` comments in the slot region guiding the LLM on output constraints.

The scaffold is the contract between the orchestrator and the LLM: the harness injects only the scene body (pure Python statements, no imports, no class wrapper) into the slot; everything outside the slot is orchestrator-owned and never modified by the agent.

### 5.5 Legacy Harness — `harness/`

**Invoked as:** `python3 -m harness --phase <phase> --project-dir <path> [options]`

**Components:**

| File | Responsibility |
|---|---|
| `cli.py` | Argument parsing, project state loading, prompt composition, LLM call, response parsing, conversation log, exit codes |
| `client.py` | `LLMClient` class — provider-agnostic HTTP client to any OpenAI-compatible `/chat/completions` endpoint |
| `prompts.py` | `compose_prompt(phase, state, ...)` — assembles `(system_prompt, user_prompt)` from modular `system.md`/`user.md` files with `{{placeholder}}` rendering |
| `parser.py` | `parse_and_write_artifacts(phase, response_text, project_dir, state)` — extracts JSON/Python from free-form LLM response, validates, writes to disk |

**Supported phases:** `plan`, `narration`, `build_scenes`, `scene_qc`, `scene_repair`

**Dry-run mode:** `--dry-run` prints prompt sizes and first 500 chars of each prompt without calling the API; writes to `log/conversation.log`.

**Temperature:** Controlled by `AGENT_TEMPERATURE` env var (default: `0.7`; clamped to [0.0, 2.0]).

**LLM Client details (`client.py`):**

- Supported providers: `XAI`, `MINIMAX`, `OLLAMA` (configured via `LLM_PROVIDER`).
- Default models: XAI → `grok-code-fast-1`; MiniMax → `MiniMax-M2.5`; Ollama → `qwen2.5-coder:7b`.
- `max_tokens`: 16,000.
- Request timeout: 300 seconds.
- Retry: 3 attempts with exponential backoff (2s × 2^attempt) on 429, 5xx, and transient connection errors.
- 4xx client errors (except 429) fail immediately.

**Backward-compatible aliases:** `XAIClient = LLMClient`, `call_xai_api = call_llm_api`.

### 5.6 Responses API Harness — `harness_responses/`

A fully isolated second harness that uses the xAI Responses API (`/v1/responses`) via the `xai_sdk` Python package.

**Key architectural differences from legacy harness:**

| Aspect | Legacy `harness/` | `harness_responses/` |
|---|---|---|
| API shape | OpenAI `/chat/completions` | xAI `/v1/responses` |
| Structured output | Free-form parsing in `parser.py` | API-enforced via `chat.parse()` + Pydantic schemas |
| Schema models | None | `harness_responses/schemas/` Pydantic models |
| Isolation | — | Zero imports from `harness/`; enforced by AST-based isolation test |

**Current rollout status:** Phase 1 — `plan` phase wired end-to-end.

**Exit code contract (harness_responses):**
- `0` — success
- `1` — general / recoverable error (retryable)
- `2` — `SemanticValidationError` (business rule violation, retryable)

See [Section 16](#16-harness-selection-seam--fh_harness) for harness selection.

### 5.7 Scene Helpers — `flaming_horse/scene_helpers.py`

Shared Python utilities imported by every generated scene file. All functions are exported via `__all__`.

| Function | Signature | Purpose |
|---|---|---|
| `safe_position` | `(mobject, max_y, min_y, max_x, min_x, buff)` | Clamps mobject inside the frame boundary with a configurable buffer. Adjusts both vertically and horizontally. |
| `harmonious_color` | `(base_color, variations, lightness_shift)` | Generates an HSL-shifted color palette. Accepts Manim color objects or string aliases (`"primary"`, `"secondary"`, `"accent"`, `"neutral"`). Returns a list of `[r, g, b, 1.0]` float lists (ManimColor-compatible). |
| `polished_fade_in` | `(mobject, lag_ratio, scale_factor, glow)` | Returns a `LaggedStart(FadeIn, scale.animate)` animation for a polished entrance. |
| `adaptive_title_position` | `(title, content_group, max_shift)` | Shifts the title upward proportionally to the height of the content group. |
| `safe_layout` | `(*mobjects, alignment, h_buff, v_buff, max_y, min_y, max_x, min_x)` | Arranges mobjects horizontally with `RIGHT` buff, applies `safe_position` to each, then resolves overlaps by shifting rightward. Returns a `VGroup`. |

### 5.8 Voice Services — `flaming_horse_voice/`

**Entry point:** `from flaming_horse_voice import get_speech_service`

```python
def get_speech_service(project_dir) -> QwenCachedService:
    return QwenCachedService.from_project(project_dir)
```

**`QwenCachedService`** (extends `manim_voiceover_plus.services.base.SpeechService`):

- Constructed via `QwenCachedService.from_project(project_dir)`.
- Reads `voice_clone_config.json` to resolve the cache directory (default: `media/voiceovers/qwen/`).
- Reads `cache.json` and builds three lookup indexes:
  - `cache_index`: `narration_key → audio_filename`
  - `text_index`: normalized_text → audio_filename`
  - `duration_index`: `audio_filename → duration_seconds`
- Fallback: if `cache.json` is absent, scans `narration_script.py` for `SCRIPT` keys and checks if matching `.mp3` files exist in the cache directory.
- **Fails hard** (`FileNotFoundError`) if neither index has any entries — no silent fallback.

**`generate_from_text(text, cache_dir, path)`:**

- Resolves audio by `narration_key` (from `Path(path).stem`), then by normalized text match.
- Returns a payload dict with `original_audio`, `final_audio`, `data_hash`, `cached: True`, and optionally `duration`.
- Raises `FileNotFoundError` if the cache file does not exist on disk.

---

## 6. Prompt Architecture

### Directory Layout

```text
harness/prompts/
├── INDEX.md
├── README.md
├── _shared/                         # Shared fragments
├── 00_plan/
│   ├── manifest.yaml                # Phase constraints and output schema
│   ├── system.md                    # System prompt
│   └── user.md                      # User prompt template with {{placeholders}}
├── 01_review/                       # Stub
├── 02_narration/
├── 04_build_scenes/
├── 05_scene_qc/
├── 06_scene_repair/
└── ...
```

### Active Phases

| Phase dir | Status | Output format |
|---|---|---|
| `00_plan` | Active | `json_only` → `plan.json` |
| `01_review` | Stub | state advance only |
| `02_narration` | Active | `narration_script.py` (Python source) |
| `04_build_scenes` | Active | `json_object` with `scene_body` string |
| `05_scene_qc` | Active | `scene_qc_report.md` |
| `06_scene_repair` | Active | `json_object` with `scene_body` string |

### Prompt Template Rendering

`prompts.py` uses `{{placeholder}}` syntax. Double-escaped `{{{{...}}}}` protects literal braces in prompt text. Missing placeholders silently render as empty strings, allowing optional prompt sections.

### Plan Phase Constraints

- Scene count: 12–24
- Scene duration: 20–45 seconds
- Total duration: 480–960 seconds
- Scene `id` and `narration_key` are assigned by the harness after parsing (not by the LLM).

### Build Scenes / Scene Repair Output Contract

Both phases return a `json_object` with a single field `scene_body` containing only the Python statements to inject into the scaffold slot (no imports, no class wrapper, no config assignments). The orchestrator owns the file name and scaffold structure.

### Retry Context

`plan` and `narration` phases accept `--retry-context` to pass failure information back to the LLM as a `RETRY CONTEXT` block in the user prompt.

### Token Reduction (Legacy Harness)

Phase-specific prompt assembly avoids sending irrelevant documentation to the model:

| Phase | Approx. system prompt | vs. all-inclusive baseline (~45K) |
|---|---|---|
| plan | ~19K tokens | −58% |
| narration | ~20K tokens | −56% |
| build_scenes | ~29K tokens | −36% |
| scene_qc | ~24K tokens | −47% |
| scene_repair | ~10K tokens | −78% |

---

## 7. Data Contracts

### 7.1 `project_state.json`

Authoritative schema: `scripts/state_schema.json` (JSON Schema draft/2020-12).

**Required top-level fields:**

| Field | Type | Notes |
|---|---|---|
| `project_name` | string | |
| `topic` | string \| null | Set at project creation |
| `phase` | string (enum) | See phase sequence |
| `created_at` | string (ISO 8601) | |
| `updated_at` | string (ISO 8601) | |
| `run_count` | integer ≥ 0 | Incremented each build loop iteration |
| `plan_file` | string \| null | Relative path to `plan.json` |
| `narration_file` | string \| null | Relative path to `narration_script.py` |
| `voice_config_file` | string \| null | Relative path to `voice_clone_config.json` |
| `scenes` | array of objects | Populated after `plan` phase |
| `current_scene_index` | integer ≥ 0 | Pointer into `scenes[]` during `build_scenes` |
| `errors` | array | Appended on failures; never overwritten |
| `history` | array | Audit trail of phase actions |
| `flags` | object | See below |

**`flags` object:**

| Field | Type | Default | Meaning |
|---|---|---|---|
| `needs_human_review` | boolean | false | Halts the build loop when true |
| `dry_run` | boolean | false | Signals test-only execution |
| `force_replan` | boolean | false | Forces re-execution of plan phase |

**`scenes[]` element fields (after plan):**

| Field | Source | Notes |
|---|---|---|
| `id` | Orchestrator | `scene_01`, `scene_02`, … (deterministic) |
| `narration_key` | Orchestrator | Same value as `id` |
| `title` | LLM (plan) | |
| `description` | LLM (plan) | |
| `estimated_duration_seconds` | LLM (plan) | 20–45s |
| `visual_ideas` | LLM (plan) | Array of strings |
| `file` | Orchestrator | Relative path to scene `.py` file |
| `class_name` | Orchestrator | Python class name derived from scene ID |
| `status` | Orchestrator | `pending`, `built`, `rendered`, `error` |
| `video_file` | Orchestrator | Set after render |
| `verification` | Orchestrator | `{file_size_bytes, duration_seconds, audio_present, verified_at}` |

### 7.2 `plan.json`

Written by the harness after the `plan` phase. Minimum required fields:

```json
{
  "title": "Video Title",
  "description": "Brief description",
  "target_duration_seconds": 600,
  "scenes": [
    {
      "title": "Scene Title",
      "description": "What this scene teaches",
      "estimated_duration_seconds": 30,
      "visual_ideas": ["..."]
    }
  ]
}
```

The harness strips `id` / `narration_key` from LLM output if present, then re-assigns them deterministically by index before writing.

### 7.3 `narration_script.py`

A valid Python module containing a single `SCRIPT` dict assignment:

```python
"""
Narration script for: My Video
"""

SCRIPT = {
    "scene_01": "First narration segment text...",
    "scene_02": "Second narration segment text...",
}
```

- Keys must match the `narration_key` of each scene in `project_state.json`.
- Values must be non-empty, non-placeholder strings (parser rejects punctuation-only values).
- Loaded via `ast.literal_eval` for safety (no `exec` at load time).

**Recovery mechanism:** If the harness writes the `SCRIPT` block to stdout but fails to create the file, `build_video.sh` extracts the `SCRIPT = {...}` block from `build.log`, validates it with `compile()`, and writes it as `narration_script.py`.

### 7.4 Scene File Contract

Each scene file follows this structure (generated by `scaffold_scene.py`):

```python
from pathlib import Path
from manim import *
import numpy as np
from manim_voiceover_plus import VoiceoverScene

from flaming_horse_voice import get_speech_service
from flaming_horse.scene_helpers import (
    safe_position, harmonious_color, polished_fade_in,
    adaptive_title_position, safe_layout,
)
from narration_script import SCRIPT

# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560

def clamp_text_width(text_obj, max_width=6.0): ...

class Scene01Intro(VoiceoverScene):
    def construct(self):
        ref_path = Path("assets/voice_ref/ref.wav")
        if not ref_path.exists():
            raise FileNotFoundError("Run precache_voice.sh before building.")

        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["scene_01"]) as tracker:
            # SLOT_START:scene_body
            <agent-generated body code here>
            # SLOT_END:scene_body
```

**Naming convention:**

- Filename: `scene_<N>_<slug>.py` (e.g., `scene_01_intro.py`, `scene_03_mechanisms.py`)
- Class name: `Scene<N><SlugPascalCase>` (e.g., `Scene01Intro`, `Scene03Mechanisms`)

The parser infers the filename from the class name via `class_name_to_scene_filename()`.

### 7.5 Voice Cache Contract — `cache.json`

Located at `projects/<name>/media/voiceovers/qwen/cache.json` (or as overridden by `voice_clone_config.json`).

Schema: a JSON array of cache entry objects. Each entry must contain at minimum one of:

```json
{
  "narration_key": "scene_01",
  "text": "The spoken narration text...",
  "audio_file": "scene_01.mp3",
  "duration_seconds": 28.4
}
```

Alternative field aliases accepted by `QwenCachedService`:

- Text: `text` → `input_text` → `input_data.text`
- Audio: `audio_file` → `final_audio` → `original_audio`

---

## 8. Validation Gates

Every scene goes through multiple validation layers in sequence during `build_scenes` and `final_render`.

### Layer 1 — Python Syntax (`compile()`)

`scene_python_syntax_ok()` in `build_video.sh` runs `compile(src, filename, "exec")` via an inline Python heredoc. On failure, prints the `SyntaxError` location and message to the log.

### Layer 2 — Import Check

`scene_validation.sh` imports the scene module in an isolated subprocess to verify all imports resolve and no import-time errors occur.

### Layer 3 — Semantic Quality

`validate_scene_semantics()` in `build_video.sh` rejects scenes that:
- Contain unresolved `{{PLACEHOLDER}}` tokens (scaffold not filled).
- Still contain the scaffold demo `Rectangle(width=4, height=2.4)` animation.

### Layer 4 — Timing Budget (`validate_scene_timing_budget.py`)

Verifies that the sum of explicit `run_time` arguments plus narration duration falls within the allowed budget. Fails with exit code 1 if the scene will over- or under-run its estimated duration (default min-ratio: 0.90).

### Layer 5 — Layout Overlap (`validate_layout.py` + `layout_validator.py`)

Static analysis of the scene body to detect mobjects positioned such that their bounding boxes overlap beyond a threshold. Uses the `LayoutValidator` class (`harness/util/layout_validator.py`), which is also integrated into `parser.py` at parse time.

### Layer 6 — SCRIPT Reference (`validate_scene_content.py`)

Checks that:
- Each `SCRIPT[key]` reference corresponds to an existing key in `narration_script.py`.
- No stage-direction text appears in bullet content.
- Text mobjects respect horizontal bounds.
- No excessively long `Wait()` calls (>1.0s).

### Layer 7 — Kitchen Sink Boilerplate Detection (`parser.py`)

`has_kitchen_sink_boilerplate()` rejects responses that include:
- Kitchen Sink example class definitions verbatim.
- `Pattern Family:` docstrings.
- `docs.manim.community` source URLs.

This prevents the model from reproducing reference template content as scene output.

### Layer 8 — Voiceover Sync Check

Before render, verifies that any scene using `VoiceoverScene` also calls `get_speech_service` (mandatory voice policy enforcement at the structural level).

### Layer 9 — Runtime Validation (`manim render --dry_run`)

`validate_scene_runtime()` invokes `manim render <scene_file> <class_name> --dry_run` to perform Manim's own import + construction check without producing video output.

---

## 9. Self-Healing and Retry Logic

### Phase-Level Retry

The main loop in `build_video.sh` retries any phase that returns a non-zero exit code, up to `$PHASE_RETRY_LIMIT` attempts (default: 3). Each retry:
1. Sleeps `$PHASE_RETRY_BACKOFF_SECONDS` (default: 2).
2. Reads the retry context file (`$PROJECT_DIR/.retry_context_<phase>.txt`) if present.
3. Passes `--retry-context` to the harness invocation.

On retry exhaustion, `mark_retry_exhausted()` sets `flags.needs_human_review = true` and halts.

### Scene-Level Self-Heal (`repair_scene_until_valid`)

For scene build failures and pre-render syntax failures, the orchestrator invokes `repair_scene_until_valid(scene_id, scene_file, scene_class, failure_reason)`. This:
1. Extracts the recent error from the log.
2. Invokes `python3 -m harness --phase scene_repair --scene-file <path> --retry-context "<error>"`.
3. After each repair, runs the full validation chain.
4. Repeats up to `$PHASE_RETRY_LIMIT` times.

### Render-Time Self-Heal

If `manim render` fails for a scene during `final_render`, the orchestrator:
1. Captures the failure reason from the render log.
2. Invokes the scene_repair loop.
3. If repair fails after all attempts, reverts `project_state.json` to `phase: build_scenes` and `current_scene_index` pointing at the failed scene, then exits with `needs_human_review = false` to allow automatic re-entry on next run.

### Scaffold Reset

`reset_scene_from_scaffold()` regenerates the scaffold for a scene while **preserving the existing scene body**. It:
1. Backs up the current scene file.
2. Generates a fresh scaffold via `scaffold_scene.py`.
3. Re-injects the old slot content into the new scaffold's slot markers.

This ensures structural repairs (e.g., config drift) do not discard working body code.

### QC-Driven Re-route

After `assemble`, `qc_final_video.sh` checks audio/video duration ratios per scene. If a scene's ratio falls below 0.90, the orchestrator:
1. Identifies the failing scene index.
2. Sets `phase = build_scenes` and `current_scene_index` to that index.
3. Exits the current run cleanly, allowing the pipeline to re-enter and regenerate only the failing scene.

---

## 10. Configuration and Environment Variables

All variables are set in `.env` (sourced by `build_video.sh`) or as shell exports. See `.env.example` for annotated defaults.

### LLM Provider

| Variable | Default | Purpose |
|---|---|---|
| `LLM_PROVIDER` | `XAI` | Active provider: `XAI`, `MINIMAX`, or `OLLAMA` |
| `XAI_API_KEY` | — | xAI API key (required when `LLM_PROVIDER=XAI`) |
| `MINIMAX_API_KEY` | — | MiniMax API key (required when `LLM_PROVIDER=MINIMAX`) |
| `XAI_BASE_URL` | `https://api.x.ai/v1` | xAI endpoint override |
| `MINIMAX_BASE_URL` | `https://api.minimax.io/v1` | MiniMax endpoint override |
| `XAI_MODEL` | `grok-code-fast-1` | xAI model override |
| `MINIMAX_MODEL` | `MiniMax-M2.5` | MiniMax model override |
| `AGENT_MODEL` | `xai/grok-4-1-fast` | Global fallback model (used by `build_video.sh` default) |
| `AGENT_TEMPERATURE` | `0.7` | Sampling temperature; clamped to [0.0, 2.0] |

### Pipeline Behavior

| Variable | Default | Purpose |
|---|---|---|
| `PROJECTS_BASE_DIR` | `projects` | Root directory for project subdirectories |
| `PROJECT_DEFAULT_NAME` | `default_video` | Fallback project name when none specified |
| `PHASE_RETRY_LIMIT` | `3` | Maximum retries per phase or scene |
| `PHASE_RETRY_BACKOFF_SECONDS` | `2` | Sleep between retry attempts |
| `PYTHON` / `PYTHON3` | `python3.13` | Python interpreter override |
| `FH_HARNESS` | `legacy` | Harness selection: `legacy` or `responses` |

### Voice

| Variable | Default | Purpose |
|---|---|---|
| `FLAMING_HORSE_TTS_BACKEND` | `qwen` | TTS backend: `qwen` or `mlx` |
| `FLAMING_HORSE_MLX_PYTHON` | — | Python interpreter for MLX TTS subprocess |
| `FLAMING_HORSE_MLX_MODEL_ID` | — | MLX model identifier override |
| `FLAMING_HORSE_VOICE_REF_DIR` | — | Override voice reference directory (`ref.wav`/`ref.txt`) |

### HuggingFace / Offline Mode

| Variable | Default | Purpose |
|---|---|---|
| `HF_HUB_OFFLINE` | `1` | Force HuggingFace Hub into offline mode |
| `TRANSFORMERS_OFFLINE` | `1` | Force Transformers into offline mode |
| `TOKENIZERS_PARALLELISM` | `false` | Disable tokenizer parallelism |

### Render / Notifications

| Variable | Default | Purpose |
|---|---|---|
| `PARALLEL_RENDERS` | `0` | `0`=auto, `N`=use N jobs, `-1`=disable |
| `PIPELINE_COMPLETION_SOUND` | `1` | Set to `0` to disable completion sound |
| `PIPELINE_ERROR_SOUND` | `1` | Set to `0` to disable error sound |
| `PIPELINE_COMPLETION_SAY` | — | Spoken completion message (macOS `say`) |
| `PIPELINE_ERROR_SAY` | — | Spoken error message (macOS `say`) |
| `HEARTBEAT_INTERVAL_SECONDS` | `5` | Frequency of heartbeat file updates |

---

## 11. Harness Exit Codes

### Legacy Harness (`harness/`)

| Code | Meaning | Orchestrator action |
|---|---|---|
| `0` | Success — artifacts written and validated | Advance phase |
| `1` | General / recoverable error (API error, timeout, missing file) | Retry (up to `PHASE_RETRY_LIMIT`) |
| `2` | Parse failure — could not extract valid artifacts | Retry |
| `3` | Schema validation error — structured output malformed | No retry; writes to `log/debug_response_<phase>.txt`; records to `project_state.json.errors` |

### Responses API Harness (`harness_responses/`)

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | General / recoverable error |
| `2` | `SemanticValidationError` (business rule violation; retryable) |

---

## 12. Logging and Observability

### Log Files (per project)

| File | Content |
|---|---|
| `log/build.log` | Full stdout/stderr from all phases, harness calls, validation steps |
| `log/error.log` | Error events with timestamps and extracted stack traces |
| `log/conversation.log` | Full system prompt + user prompt + assistant response for every harness call |
| `log/heartbeat.txt` | Updated every `HEARTBEAT_INTERVAL_SECONDS` with current phase, stage, scene, attempt, PID |
| `log/crash_diag.log` | Structured diagnostic entries from `diagnostics_log()` — phase, stage, scene, iteration, attempt, error |
| `log/debug_response_<phase>.txt` | Raw model response on parse/schema failures |
| `log/responses_last_response.json` | (`harness_responses/` only) Raw response payload and validation error on failure |

### Conversation Log Format

Each entry in `log/conversation.log`:

```
============================================================
timestamp_utc: <ISO 8601>
phase: <phase>
status: api_success | dry_run | error
[error: <message>]

----- SYSTEM PROMPT -----
<full system prompt>

----- USER PROMPT -----
<full user prompt>

----- ASSISTANT RESPONSE -----
<raw model response>
```

### Crash Diagnostics Format

Each entry in `log/crash_diag.log`:

```
[<timestamp>] level=<INFO|ERROR> pid=<PID> ppid=<PPID> phase=<phase> stage=<stage> scene=<scene_id> iteration=<N> attempt=<N> msg=<message>
```

---

## 13. Voice Policy

**Policy: Cached Qwen voice clone only. No exceptions. No fallback.**

### Mandatory Requirements

- Service: `QwenCachedService` via `flaming_horse_voice.get_speech_service(project_dir)`.
- Model: `Qwen/Qwen3-TTS-12Hz-1.7B-Base` (unless overridden in `voice_clone_config.json`).
- Reference assets: `assets/voice_ref/ref.wav` and `assets/voice_ref/ref.txt` must exist.
- Cache: `media/voiceovers/qwen/cache.json` must be present before `final_render`.

### Prohibited

- `GTTSService` (Google TTS)
- Azure TTS, OpenAI TTS, `pyttsx3`
- Any network TTS service
- Dev-mode fallbacks (`if/else` based on environment)

### Enforcement Mechanisms

1. **Build system**: `validate_scene_semantics()` checks that all `VoiceoverScene` subclasses call `get_speech_service`.
2. **Harness prompt**: `build_scenes` and `scene_repair` system prompts both include the voice policy constraint section.
3. **Runtime**: `QwenCachedService` raises `FileNotFoundError` when cache is missing — no silent fallback.
4. **Parser**: The parser can detect and reject scenes that import prohibited TTS services.

### Cache Pre-generation

The `precache_voiceovers` phase runs `scripts/precache_voiceovers_qwen.py`, which:
1. Reads `narration_script.py` to enumerate all `SCRIPT` keys.
2. Synthesizes audio for each key using the Qwen TTS model.
3. Writes audio files to the cache directory and updates `cache.json`.
4. Implements hash-based change detection: skips re-generation if `narration_script.py` hash matches `.cache_hash`.

---

## 14. Testing

### Test Suite Location

`tests/`

### Test Categories

| Category | Files | Execution | API calls? |
|---|---|---|---|
| Mock parser/prompt E2E | `test_harness_mock_e2e.py` | `pytest -q tests/test_harness_mock_e2e.py` | No |
| Harness integration smoke | `test_harness_integration.sh` | `bash tests/test_harness_integration.sh` | No |
| Harness dry-run coverage | `test_harness_dry_run.sh` | `bash tests/test_harness_dry_run.sh` | No |
| CLI help smoke | `test_cli_help_smoke.sh` | `bash tests/test_cli_help_smoke.sh` | No |
| Scene content regression | `test_scene_content.py` | `pytest tests/test_scene_content.py --project_dir=<path>` | No |
| Harness module coverage | `test_harness_module_coverage.py` | `pytest tests/test_harness_module_coverage.py` | No |
| Scaffold and parser | `test_scaffold_and_parser.py` | `pytest tests/test_scaffold_and_parser.py` | No |
| Scene scaffold contract | `test_scene_scaffold_contract.py` | `pytest tests/test_scene_scaffold_contract.py` | No |
| Layout validation | `test_layout_validation.py` | `pytest tests/test_layout_validation.py` | No |
| Phase vocabulary | `test_phase_vocabulary.py` | `pytest tests/test_phase_vocabulary.py` | No |
| Kitchen sink scenes | `test_kitchen_sink_scenes.py` | `pytest tests/test_kitchen_sink_scenes.py` | No |
| E2E scaffold workflow | `test_e2e_scaffold_workflow.py` | `pytest tests/test_e2e_scaffold_workflow.py` | No |
| Live API E2E | `test_harness_e2e.sh` | `bash tests/test_harness_e2e.sh` | **Yes** (`XAI_API_KEY` required) |
| `harness_responses` isolation | `tests/harness_responses/test_plan_phase.py` | `pytest tests/harness_responses/` | No |

### Key Test Assertions

- **Harness isolation test** (`tests/harness_responses/test_plan_phase.py`): AST-walks all source files in `harness_responses/` to assert zero imports from `harness/`.
- **Kitchen sink boilerplate detection** (`test_scaffold_and_parser.py`): Asserts that responses containing Kitchen Sink example class bodies are rejected.
- **Narration placeholder rejection** (`test_harness_module_coverage.py`): Asserts that punctuation-only narration strings (`"..."`, `"…"`) are rejected as invalid.
- **Scene ID determinism** (`scripts/test_update_project_state.py`): Verifies that `scenes_from_plan()` assigns `scene_01`, `scene_02`, etc. regardless of LLM-provided IDs.

---

## 15. Render and Assembly

### Render Phase (`final_render`)

Manim renders each scene independently:

- Resolution: 1440p (2560×1440), 60fps
- Video path per scene: `media/videos/<scene_id>/1440p60/<ClassName>.mp4`
- Rendered scene validation: `verify_scene_video()` checks file existence, non-zero size, and presence of an audio stream via `ffprobe`.

### Assembly Phase (`assemble`)

After all scenes are rendered:

1. `generate_scenes_txt.py` reads `project_state.json.scenes` and writes `scenes.txt` in FFmpeg concat format.
2. `build_video.sh` verifies all referenced files exist.
3. FFmpeg concat filter assembles the final video:

```
-filter_complex "[0:v:0][0:a:0][1:v:0][1:a:0]...concat=n=<N>:v=1:a=1[v][a];[a]aresample=async=1:first_pts=0[aout]"
-map "[v]" -map "[aout]"
-c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium
-c:a aac -b:a 192k -ar 48000
-movflags +faststart
```

4. Post-assembly QC (`qc_final_video.sh`): compares audio duration to video duration per scene using `ffprobe`. Scenes with `audio_duration / video_duration < 0.90` trigger re-routing to `build_scenes`.

### Render Configuration (locked in scaffold)

```python
config.frame_height = 10
config.frame_width = 10 * 16 / 9    # = 17.778
config.pixel_height = 1440
config.pixel_width = 2560
```

These values are locked in the scaffold and must not be modified by the agent.

---

## 16. Harness Selection Seam — `FH_HARNESS`

`build_video.sh` reads `FH_HARNESS` (default: `legacy`) to select which harness to invoke for agent phases:

| Value | Harness invoked | Entry point |
|---|---|---|
| `legacy` (default) | `harness/` | `python3 -m harness` |
| `responses` | `harness_responses/` | `python3 -m harness_responses` |

When `FH_HARNESS=legacy` (or unset), all existing pipeline behavior is unchanged.

The `harness_responses/` harness is currently implemented for the `plan` phase only (Phase 1 rollout). Phases not yet implemented in `harness_responses/` fall back to the legacy harness or exit with an unsupported-phase error, depending on orchestrator logic.

---

## 17. Known Constraints and Risk Areas

| Area | Description |
|---|---|
| **LLM code generation quality** | The first-order risk during `build_scenes`. The parser, scaffold, and validation gates mitigate but cannot eliminate all model-generated errors. Scene repair loops handle recoverable failures. |
| **Python 3.13 requirement** | All Manim rendering and pipeline scripts require Python 3.13. Using a different interpreter version will cause `build_video.sh` to exit immediately with an actionable message. |
| **Voice cache completeness** | `final_render` will fail if `cache.json` is absent or incomplete. The `precache_voiceovers` phase must run (and succeed) before render. |
| **Single-machine rendering** | Scenes are rendered sequentially on one machine. Parallel rendering is configurable via `PARALLEL_RENDERS` but is experimental. |
| **Manim version pinning** | Manim API surface is large; scene code is generated against Manim CE. Version drift between the model's training data and the installed version may produce `AttributeError`/`ImportError` failures during render. The scene_repair loop addresses these at runtime. |
| **Documentation drift** | Some `harness/README.md` sections describe an older file layout (duplicate `prompt_templates/` listing). The authoritative structure is `harness/prompts/<NN_phase>/`. |
| **`review` phase stub** | The `review` phase is structurally present in the pipeline and state schema but currently performs only deterministic structural checks (plan.json shape validation). No LLM call is made for this phase. |
| **`harness_responses/` partial rollout** | Only `plan` is fully wired in `harness_responses/`. Other phases are not yet implemented. `FH_HARNESS=responses` should only be used when this is understood. |
