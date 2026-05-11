# AGENTS.md

Audience: Local coding agents only.

Purpose: This file is the repository instruction router. It defines mandatory read order, execution boundaries, and the contract documents that describe the current Flaming Horse runtime.

## 1. Hard Start Rule

Before any code or command work, read:

1. `docs/policies/USER_PREFERENCES.md`
2. This file
3. The focused contract document that matches the task:
   - `docs/architecture/PIPELINE_CONTRACT.md` for entrypoints, state, phases, and artifacts.
   - `docs/architecture/HARNESS_CONTRACT.md` for LLM calls, prompt composition, schemas, and artifact writing.
   - `docs/architecture/SCENE_GENERATION_CONTRACT.md` for scaffold, scene-body, Manim validation, and repair behavior.
   - `docs/architecture/VOICE_CONTRACT.md` for local cached voice generation and render-time audio lookup.

If `USER_PREFERENCES.md` and this file conflict, stop and ask.
If current user instructions conflict with stored preferences, stop and ask.
If a contract document conflicts with runtime code and the mismatch affects execution, stop and ask before proceeding.

## 2. Scope And Audience

This file is only for local coding agents in this repository.

Never treat this file as backend model prompt content.
Never merge backend LLM prompt-policy content into this file.
Never copy generated scene instructions into this file.

## 3. Instruction Precedence

Use this repository-local order for stored repository guidance:

1. `docs/policies/USER_PREFERENCES.md`
2. `AGENTS.md`
3. Current runtime code and scripts
4. Focused contract documents in `docs/architecture/`
5. Other docs

Runtime code is the source of truth for what actually executes. Contract docs are the source of truth for intended local agent understanding. When they diverge in a way that changes execution, stop and ask.

## 4. Mandatory Pre-Flight Alignment Check

At the start of every task, provide a 3-5 line alignment check before editing code or documentation.

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

## 5. Communication Contract

1. Be concise and direct.
2. Ask before proceeding when intent is ambiguous.
3. Ask one question at a time for clarification.
4. Do not run repeated confirmation loops once approved to proceed.
5. Do not introduce side tasks unless explicitly requested.
6. State constraints and assumptions explicitly in pre-flight checks.

Required example when blocked:

```text
Blocker: Runtime behavior and instruction contract conflict on phase handling.
Question: Should I follow current script behavior or update scripts to match the contract?
```

## 6. Project Mission

Flaming Horse is a deterministic, script-orchestrated pipeline that converts a topic into a narrated Manim video.

Canonical user entrypoint:

```bash
./scripts/create_video.sh <project_name> --topic "..."
```

Primary user outcome:

```text
projects/<project_name>/final_video.mp4
```

## 7. Runtime Sources Of Truth

Core runtime files:

1. `scripts/create_video.sh`
2. `scripts/new_project.sh`
3. `scripts/build_video.sh`
4. `scripts/update_project_state.py`
5. `scripts/state_schema.json`
6. `harness_responses/cli.py`
7. `harness_responses/prompts.py`
8. `harness_responses/client.py`
9. `harness_responses/parser.py`
10. `scripts/scaffold_scene.py`
11. `flaming_horse_voice/service_factory.py`

The live harness path is `harness_responses/`.
Do not use stale `harness/` paths unless the user explicitly asks to inspect old documentation.

## 8. Generated Artifact Boundary

Generated project artifacts are evidence by default, not fix targets.

Default remediation targets:

1. Orchestrator scripts.
2. Harness schemas, prompts, parser, and client.
3. Scene scaffold/template code.
4. Deterministic validators.
5. Voice cache/service integration.

Do not patch `projects/<project_name>/scene_*.py`, `plan.json`, `narration_script.py`, or other generated artifacts unless the user explicitly requests a project-level containment patch.

## 9. Non-Negotiables

1. Follow `docs/policies/USER_PREFERENCES.md` first.
2. Do not assume intent when unclear.
3. Do not exceed requested scope.
4. Do not silently persist new preferences.
5. Preserve deterministic orchestrator ownership of `project_state.json`.
6. Preserve local cached voice policy for pipeline scenes.
7. Prefer source-level fixes over repair-loop guardrails.
8. Keep research and generation code deterministic when deterministic construction is possible.
