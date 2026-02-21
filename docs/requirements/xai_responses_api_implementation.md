# xAI Responses API Implementation Requirements (v1)

## 1. Purpose

Define requirements for implementing a new, fully isolated Responses-API harness for Flaming Horse.

This document captures the first draft based on current repository behavior and decisions from this session, and is intended for iterative refinement.

## 2. Problem Statement

Flaming Horse currently uses Chat Completions shape (`/chat/completions`) in `harness/client.py`.

The project wants to adopt xAI Responses API capabilities, primarily:

1. Schema-constrained structured outputs.
2. Native tool support (notably web search for Manim CE documentation).
3. Better reasoning support path.
4. Stateful-capable workflows for future training/error-learning behavior.

The chosen architecture is to build a separate harness, not a dual backend path inside the existing harness.

## 3. Scope

In scope:

1. Create a new harness implementation under `harness_responses/`.
2. Use xAI Responses API as the only API contract in the new harness.
3. Keep prompts/templates/parser contracts separate from legacy harness.
4. Add one orchestrator seam in `scripts/build_video.sh` for harness selection.
5. Roll out phases incrementally with explicit gates.

Out of scope:

1. Refactoring legacy harness internals to support both APIs.
2. Changing default runtime behavior before acceptance criteria are met.
3. Merging prompts/templates between harnesses.

## 4. Architecture Decision

### 4.1 Isolation requirement

`harness_responses` must have zero code dependencies on `harness/`.

Required isolation:

1. No imports from legacy harness modules.
2. Separate prompt assets and templates.
3. Separate parser and response-shape assumptions.
4. Separate tests for new harness.

### 4.2 Orchestrator seam

Add exactly one top-level runtime selection seam using `FH_HARNESS` to choose harness implementation.

`FH_HARNESS` contract:

1. `legacy` (default): existing harness path.
2. `responses`: `harness_responses` path.

When not explicitly enabled, existing harness behavior must remain unchanged.

### 4.3 Client implementation choice

`harness_responses/client.py` must use the `xai_sdk` Python package (not raw HTTP) for structured generation calls.

Structured validation layers:

1. Layer 1 (API-enforced): `chat.parse()` with schema models to constrain structural output.
2. Layer 2 (client semantic): phase-specific semantic checks before artifact write.

`parser.py` in `harness_responses` must focus on semantic validation and artifact conversion, not free-form structural parsing.

## 5. Functional Requirements

### 5.1 API contract

1. Use `POST /v1/responses` for xAI calls.
2. Parse Responses-native output format only.
3. No assumptions about Chat Completions fields such as `choices[0].message.content`.

### 5.2 Structured outputs

1. Implement schema-constrained output for `plan` and `review` phases first.
2. Validate schema before artifact write.
3. Fail with actionable errors on schema mismatch.

### 5.3 Tooling capabilities

1. Support optional native tools in Responses.
2. `web_search` must be disabled by default.
3. Per-phase tool allow-list must be configurable.
4. For tool-enabled runs, log source/citation metadata for tool-derived claims.
5. v1 policy: only `scene_repair` may enable `web_search`; all other phases must keep it disabled.

### 5.4 Stateful behavior

1. Stateful mode must be explicit and opt-in.
2. `store=false` is the default for all phases.
3. State/storage settings must be logged per run for auditability.

### 5.5 Determinism guardrails

1. `build_scenes` starts with tools off by default.
2. Render-critical behavior must prioritize reproducibility and debuggability.
3. Non-deterministic features (tools/stateful context) must be bounded by config and phase.

### 5.6 Dry-run support

`harness_responses` must support `--dry-run` with parity to legacy harness intent:

1. Build and log final prompt/request payload shape.
2. Perform schema/model wiring checks that do not require network I/O.
3. Skip outbound API calls and artifact writes.
4. Exit with success only when dry-run validation passes.

## 6. Non-Functional Requirements

1. Reliability: retry behavior must be at least parity with current harness expectations.
2. Observability: include response IDs, validation outcomes, API mode, tools enabled, and state/store flags in logs.
3. Backward compatibility: legacy harness path remains unchanged.
4. Maintainability: clear boundaries between harnesses to avoid cross-coupled changes.
5. Exit code parity: preserve legacy contract (`0` success, `1` recoverable/phase failure, `2` usage/configuration error).
6. Failure diagnostics: on structured-output or semantic-validation failure, write `projects/<project_name>/log/responses_last_response.json` containing raw response payload, extracted content, and validation error context.

## 7. Proposed File/Directory Contract

Required new paths:

1. `harness_responses/__init__.py`
2. `harness_responses/__main__.py`
3. `harness_responses/cli.py`
4. `harness_responses/client.py`
5. `harness_responses/parser.py`
6. `harness_responses/prompts.py`
7. `harness_responses/schemas/*` (Pydantic models and/or JSON Schema assets)
8. `harness_responses/prompts/<phase>/system.md`
9. `harness_responses/prompts/<phase>/user.md`
10. `harness_responses/templates/*`
11. `tests/harness_responses/*`

## 8. Rollout Plan (Requirements-Level)

Phase 1:

1. Wire `plan` phase end-to-end in `harness_responses`.
2. Enforce schema-constrained output for `plan`.
3. Add unit + integration tests for `plan`.

Phase 2:

1. Add `review`.
2. Add `narration`.
3. Keep tooling disabled by default unless explicitly enabled per phase.

Phase 3:

1. Add `build_scenes`.
2. Start with tool-off default and deterministic guardrails.
3. Evaluate optional tool-on mode after baseline stability.

Phase 4:

1. Add `scene_qc`.
2. Add `scene_repair`.
3. Keep `web_search` policy restricted to `scene_repair` only (opt-in, phase-gated).

## 9. Testing Requirements

Minimum required tests:

1. Unit tests: request construction and Responses output parsing.
2. Unit tests: schema validation pass/fail behavior.
3. Integration tests: `plan` phase produces valid `plan.json`.
4. Regression checks: legacy harness tests remain unaffected.

## 10. Acceptance Criteria

The migration milestone is accepted when:

1. `harness_responses` runs `plan` end-to-end using xAI Responses API.
2. Output is schema-validated before write.
3. Failures include actionable diagnostics (including response identifier and validation error details).
4. Legacy harness behavior remains unchanged unless runtime selection explicitly chooses `harness_responses`.
5. `python3 -m harness_responses` is invocable and phase dispatch works for implemented phases.
6. Exit code behavior matches legacy contract (`0/1/2`).

## 11. Risks and Mitigations

1. Risk: Increased maintenance overhead from parallel harnesses.
   Mitigation: strict isolation and explicit ownership boundaries.
2. Risk: Non-determinism from tool usage.
   Mitigation: default tool-off for render-critical phases; phase-bound allow-list.
3. Risk: State/storage behavior introduces unexpected context coupling.
   Mitigation: opt-in stateful mode with explicit logging and defaults favoring stateless execution.
4. Risk: Prompt/template drift between `harness/` and `harness_responses/` creates behavior divergence during rollout.
   Mitigation: define a prompt parity review checklist per phase and a documented legacy deprecation window before default cutover.

## 12. Open Questions for Next Iteration

1. What exact schema definitions should be used for `plan` and `review` artifacts inside `harness_responses/schemas/`?
2. What metrics define go/no-go for enabling `harness_responses` as default?

Initial go/no-go recommendation for default switch:

1. 100% pass rate for Phase 1 required tests.
2. <5% token usage increase versus legacy baseline for matched inputs.
3. Zero determinism failures across 10 repeated runs on a fixed validation topic set.
