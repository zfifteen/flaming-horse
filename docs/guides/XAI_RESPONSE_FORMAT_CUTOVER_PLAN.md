# xAI `response_format` Cutover Plan (Harness Responses)

Status key:
- `[ ]` pending
- `[-]` in progress
- `[x]` completed

## Goal
Move all xAI interaction phases in `harness_responses` to schema-enforced JSON via `response_format`, with no text/fallback parsing path.

## Scope
- In scope: `plan`, `narration`, `build_scenes`, `scene_qc`, `scene_repair` in `harness_responses`.
- Out of scope: full pipeline run, legacy harness behavior changes.

## Checklist
- [x] Refactor API call path to use `response_format` JSON mode in `/Users/velocityworks/IdeaProjects/flaming-horse/harness_responses/client.py`.
- [x] Parse response payload into phase Pydantic models with strict validation (single path, no fallback parsing).
- [x] Remove unsupported schema constraints for xAI structured outputs in `/Users/velocityworks/IdeaProjects/flaming-horse/harness_responses/schemas/*.py`:
  - string `min_length`/`max_length`
  - array `min_items`/`max_items` equivalents
- [x] Keep semantic constraints in `/Users/velocityworks/IdeaProjects/flaming-horse/harness_responses/parser.py` (non-empty content, scene counts, duration bounds, etc.).
- [x] Update unit tests in `/Users/velocityworks/IdeaProjects/flaming-horse/tests/harness_responses/test_plan_phase.py` for `response_format` behavior.
- [x] Add/adjust negative tests for:
  - malformed/non-JSON response content
  - schema-invalid JSON payload
- [x] Run targeted test suite:
  - `PYTHONPATH=. pytest tests/harness_responses/test_plan_phase.py -q`
  - `PYTHONPATH=. pytest tests/test_collections_rag.py -q`
- [x] Run targeted phase API checks (no full pipeline):
  - `plan`
  - `build_scenes`
  - `scene_repair`
  - `narration`
  - `scene_qc`
- [x] Verify artifacts and logs are correct for each phase:
  - `plan.json`
  - `scene_*.py`
  - `narration_script.py`
  - `scene_qc_report.md`
  - `log/conversation.log`
  - `log/responses_last_response.json` (on validation failure; covered via test path)
- [x] Summarize residual risks and any remaining blockers.

## Done Criteria
- All in-scope phases use schema-enforced JSON through `response_format`.
- No fallback/text parsing path exists in `harness_responses`.
- Tests and targeted phase checks pass.
- Plan checklist reflects final status for every item.
