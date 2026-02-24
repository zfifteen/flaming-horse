# Collections Integration Plan (Responses Harness)

Status key:
- `[ ]` pending
- `[-]` in progress
- `[x]` completed

## Goal
Restore and improve Collections-backed retrieval in `harness_responses` so active build/repair phases are grounded on Manim/API references, with full response and retrieval logging.

## Checklist
- [x] Audit legacy Collections behavior in:
  - `/Users/velocityworks/IdeaProjects/flaming-horse/harness/collections.py`
  - `/Users/velocityworks/IdeaProjects/flaming-horse/harness/prompts.py`
- [x] Add `/Users/velocityworks/IdeaProjects/flaming-horse/harness_responses/collections.py` using xAI SDK `client.collections.search(...)` semantics from docs.
- [x] Preserve env/config parity:
  - `XAI_API_KEY`
  - `XAI_COLLECTION_ID` / `FLAMING_HORSE_COLLECTION_ID`
  - default collection fallback
  - retry/backoff + fail-soft behavior
- [x] Add error-aware query builder for build/repair retrieval (scene details + retry/error context, symbol-aware extraction).
- [x] Wire retrieval into `/Users/velocityworks/IdeaProjects/flaming-horse/harness_responses/prompts.py`:
  - `build_scenes` uses retrieval result for `reference_section`
  - `scene_repair` uses retrieval result for `reference_section`
  - static docs fallback when retrieval yields no chunks
- [x] Extend `/Users/velocityworks/IdeaProjects/flaming-horse/harness_responses/cli.py` logging to include:
  - full assistant/model response content (untruncated)
  - parsed structured payload
  - retrieval metadata (query, hit count, collection id, formatted chunks)
- [x] Update/add tests for retrieval module and prompt injection.
- [x] Run targeted tests for harness_responses + collections:
  - `PYTHONPATH=. pytest tests/harness_responses/test_plan_phase.py -q`
  - `PYTHONPATH=. pytest tests/test_collections_rag.py -q`
- [x] Report residual risks and follow-up hardening options.
