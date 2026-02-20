# AGENTS.md

Audience: Local coding agents only.

Purpose: This is the operating manual for local coding agents in this repository. It defines system behavior, artifact locations, execution boundaries, and user-preference enforcement.

## 1. Hard Start Rule

Before any code or command work, you MUST read:

1. `docs/policies/USER_PREFERENCES.md`
2. This file

If these sources conflict, STOP and ask.
If current user instructions conflict with stored preferences, STOP and ask.

## 2. Scope and Audience

This file is only for local coding agents in this repository.

NEVER treat this file as backend model prompt content.
NEVER merge backend LLM prompt-policy content into this file.

## 3. Mandatory Pre-Flight Alignment Check

At the start of every task, provide a 3-5 line alignment check before editing code.
This is mandatory.

Required content:

1. Task scope in one sentence.
2. Constraints and preferences that govern execution.
3. Assumptions, if any.
4. Success criteria.

If scope or intent is ambiguous, ask one question and wait.
Do not proceed on assumptions.

Example:

```text
Scope: Update phase transition handling in build orchestration only.
Constraints: Follow USER_PREFERENCES.md, strict scope, no side refactors.
Assumptions: None.
Success criteria: Phase transition bug fixed, existing tests pass, no unrelated file changes.
```

## 4. Instruction Precedence

Use this exact order:

1. `docs/policies/USER_PREFERENCES.md`
2. `AGENTS.md`
3. Code and scripts as source of truth for runtime behavior
4. Other docs

Additional conflict rule:

- If AGENTS guidance appears inconsistent with actual runtime code behavior and it affects execution, stop and ask before proceeding.

## 5. Communication Contract

These are hard rules for agent-user communication in this repo:

1. Be concise and direct. No fluff.
2. Ask before proceeding when intent is ambiguous. No assumptions.
3. Ask one question at a time for clarification.
4. Do not run repeated confirmation loops once approved to proceed.
5. Do not introduce side tasks unless explicitly requested.
6. State constraints and assumptions explicitly in pre-flight checks.

Required example when blocked:

```text
Blocker: Runtime behavior and AGENTS instruction conflict on phase handling.
Question: Should I follow current script behavior or update scripts to match AGENTS?
```

## 6. Project Mission

Flaming Horse is a deterministic, script-orchestrated pipeline that converts a topic into a narrated Manim video.

Canonical user entrypoint:

- `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/create_video.sh`

High-level flow:

1. Create or resume a project
2. Run deterministic phase loop
3. Generate and validate artifacts per phase
4. Render scenes with cached local voice
5. Assemble `final_video.mp4`

## 7. Runtime Architecture

### 7.1 Main components

1. Orchestrator scripts: `/Users/velocityworks/IdeaProjects/flaming-horse/scripts`
2. Harness (LLM calls, prompt composition, parsing): `/Users/velocityworks/IdeaProjects/flaming-horse/harness`
3. Voice services and cached voice integration: `/Users/velocityworks/IdeaProjects/flaming-horse/flaming_horse_voice`
4. Scene helpers: `/Users/velocityworks/IdeaProjects/flaming-horse/flaming_horse/scene_helpers.py`
5. Per-project artifacts: `/Users/velocityworks/IdeaProjects/flaming-horse/projects/<project_name>`

### 7.2 Phase state machine

Canonical phases in code:

- `init -> plan -> review -> narration -> build_scenes -> scene_qc -> precache_voiceovers -> final_render -> assemble -> complete`

Authoritative source:

- `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/update_project_state.py`
- `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/build_video.sh`
- `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/state_schema.json`

Notes:

- `create_video.sh` is the recommended user command.
- `build_video.sh` enforces deterministic phase transitions and retries.
- `update_project_state.py` is the authority for state normalization and phase application.

### 7.3 Deterministic ownership split

Script-owned:

1. State transitions and normalization
2. Scaffolding and structural validation
3. Runtime QC gates and retry loop behavior
4. Render and assembly control

Agent-owned:

1. Requested code changes within scope
2. Creative content generation where explicitly required
3. Root-cause analysis and targeted fixes

## 8. Artifacts and Locations

Per-project structure (typical):

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
  log/
    build.log
    error.log
    conversation.log
```

Voice cache location (default):

- `projects/<project_name>/media/voiceovers/qwen/cache.json`

Reference voice assets (per project):

- `projects/<project_name>/assets/voice_ref/ref.wav`
- `projects/<project_name>/assets/voice_ref/ref.txt`

## 9. Environment Variables and Purpose

Primary variables used by runtime scripts and harness:

1. `LLM_PROVIDER`: selects provider (`XAI` or `MINIMAX`).
2. `XAI_API_KEY`, `MINIMAX_API_KEY`: provider auth.
3. `XAI_BASE_URL`, `MINIMAX_BASE_URL`: optional endpoint overrides.
4. `XAI_MODEL`, `MINIMAX_MODEL`, `AGENT_MODEL`: model selection.
5. `PROJECTS_BASE_DIR`: default base for project directories.
6. `PROJECT_DEFAULT_NAME`: fallback project name for direct build entry.
7. `PHASE_RETRY_LIMIT`: retry budget per retryable phase.
8. `PHASE_RETRY_BACKOFF_SECONDS`: retry wait between attempts.
9. `HF_HUB_OFFLINE`, `TRANSFORMERS_OFFLINE`, `TOKENIZERS_PARALLELISM`: local/offline inference behavior.
10. `FLAMING_HORSE_TTS_BACKEND`: backend route (`qwen` or `mlx` where supported).
11. `FLAMING_HORSE_MLX_PYTHON`, `FLAMING_HORSE_MLX_MODEL_ID`: MLX routing overrides.
12. `FLAMING_HORSE_VOICE_REF_DIR`: optional override for voice reference directory.
13. `PYTHON`, `PYTHON3`: interpreter override (pipeline enforces Python 3.13 in key entry scripts).
14. `AGENT_TEMPERATURE`: harness sampling override.

Authoritative examples:

- `/Users/velocityworks/IdeaProjects/flaming-horse/.env.example`
- `/Users/velocityworks/IdeaProjects/flaming-horse/README.md`

## 10. Repository Map with Edit Policy

Edit policy values:

- `allowed`: normal edits are acceptable.
- `caution`: edit only when task requires; verify side effects.
- `forbidden`: do not edit unless user explicitly requests.

| Path | Purpose | Edit Policy |
| --- | --- | --- |
| `/Users/velocityworks/IdeaProjects/flaming-horse/AGENTS.md` | Local agent operating manual | `allowed` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/docs/policies/USER_PREFERENCES.md` | User-specific hard overrides | `caution` (propose first, edit only after approval) |
| `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/create_video.sh` | Canonical user entrypoint | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/new_project.sh` | Project initialization and bootstrap | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/build_video.sh` | Main deterministic orchestrator | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/update_project_state.py` | State schema normalization and phase application authority | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/state_schema.json` | State schema and phase enum | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/scaffold_scene.py` | Deterministic scene scaffold generation | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/precache_voiceovers_qwen.py` | Voice cache generation step | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/prepare_qwen_voice.py` | Voice backend preparation/warm-up | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/scripts/voice_ref_mediator.py` | Voice reference resolution and validation | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/harness/cli.py` | Harness CLI entry for phase calls | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/harness/client.py` | Provider-agnostic API client | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/harness/prompts.py` | Prompt composition and phase mapping | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/harness/parser.py` | Model output parsing and artifact writing | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/harness/prompts/*` | Prompt assets and phase prompt bodies | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/harness/templates/*` | Reference templates used during prompt composition | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/flaming_horse/scene_helpers.py` | Shared scene layout/animation helpers | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/flaming_horse_voice/*` | Voice service factory and cached service behavior | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/tests/*` | Unit/integration/regression tests | `allowed` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/docs/reference_docs/*` | Reference docs for agent and pipeline | `allowed` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/docs/guides/*` | Setup and operational docs | `allowed` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/projects/<project_name>/*` | Generated project artifacts and logs | `caution` (treat as runtime evidence; avoid ad hoc edits unless user requests) |
| `/Users/velocityworks/IdeaProjects/flaming-horse/.env` | Local secrets and runtime configuration | `forbidden` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/.env.example` | Example env template | `caution` |
| `/Users/velocityworks/IdeaProjects/flaming-horse/.git/*` | VCS internals | `forbidden` |

## 11. Workflow for Local Agents

1. Read `USER_PREFERENCES.md`.
2. Run pre-flight alignment check (3-5 lines).
3. Confirm scope and constraints.
4. Inspect only required files.
5. If ambiguity exists, ask one question and wait.
6. Implement minimal change set.
7. Run targeted verification.
8. Report what changed, why, and residual risk.

## 12. Preference Handling Protocol

When a new preference is discovered:

1. Suggest exact text update for `docs/policies/USER_PREFERENCES.md`.
2. Wait for approval.
3. Edit only after approval.
4. Do not silently persist preferences elsewhere.

## 13. Ambiguity and Contradiction Protocol

Stop and ask when any of the following occurs:

1. Ambiguous user intent with multiple plausible implementations.
2. Conflict between current user instruction and stored preferences.
3. AGENTS guidance appears inconsistent with runtime code behavior and would affect execution.
4. A requested action implies risky/destructive change not explicitly approved.

## 14. Quality and Debugging Standard

Use root-cause-first analysis:

1. Identify first divergence point.
2. Explain causal chain.
3. Propose source-level fix.
4. Use guardrails only as temporary containment when necessary.

When reporting failures, include:

1. Scope (phase/file/scene)
2. Origin
3. Causal chain
4. Primary fix
5. Containment status

## 15. Voice and Rendering Constraints

Hard constraints for local implementation work:

1. Local cached voice flow only for pipeline scenes.
2. Missing cache should fail with actionable error.
3. Scene narration must come from `narration_script.py` via `SCRIPT[...]`.
4. Preserve deterministic orchestrator ownership of state transitions.

## 16. Commands Reference

Canonical:

```bash
./scripts/create_video.sh <project_name> --topic "..."
```

Environment check:

```bash
./scripts/check_dependencies.sh
```

Manual advanced flow:

```bash
./scripts/new_project.sh <project_name> --topic "..."
./scripts/build_video.sh projects/<project_name>
```

Phase reset:

```bash
./scripts/reset_phase.sh projects/<project_name> <phase>
```

## 17. Documentation Hygiene Rule

If you detect drift between docs and runtime behavior:

1. Stop and ask before proceeding if drift affects execution decisions.
2. After alignment, prefer code behavior for implementation decisions.
3. Propose focused doc updates to restore alignment.

## 18. Non-Negotiables

1. Follow `USER_PREFERENCES.md` first.
2. Do not assume intent when unclear.
3. Do not exceed requested scope.
4. Do not silently persist new preferences.
5. Do not proceed through unresolved instruction conflicts.
6. Stop and ask when AGENTS and runtime behavior diverge in execution-relevant ways.
