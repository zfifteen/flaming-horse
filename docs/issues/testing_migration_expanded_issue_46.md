# Expanded Testing and Migration Plan for Issue #46 Enhancement

## Overview
This document expands on the "Testing and Migration" section from the main implementation plan for issue #46. It provides detailed strategies for validating the update-only scene generation model, including unit and integration testing, dry runs, edge case handling, and regression testing. Migration is explicitly out of scope, as generated projects are disposable development artifacts (see reasoning below).

The goal is to ensure the enhancement reduces first-pass failures, prevents scaffold drift, and maintains pipeline stability without introducing new runtime errors. Testing will focus on the new phases (`scaffold_all`, `validate_specs`, `merge_specs`) and modified `build_scenes` phase.

## Unit Testing
Unit tests will validate individual components in isolation, leveraging pytest (as seen in existing `tests/` directory). Focus on scripts, spec validation, and beat calculations. Existing ad-hoc tests can be reviewed for reuse or replacement.

### Key Test Cases
- **Beat Calculation (Orchestrator)**:
  - Input: Narration text with varying word counts (e.g., 50, 500, 2000 words).
  - Expected: Correct num_beats (`max(5, min(20, int(duration / 10)))`), duration estimate, and beat weights array.
  - Edge: Very short narration (0-10 words) defaults to minimum beats; long narration caps at 20 beats.

- **Spec Validation (`scripts/validate_spec.py`)**:
  - Valid spec: All required fields present, timing_fractions sum ≤1.0, custom_code parses via `ast.parse()`.
  - Invalid spec: Missing `scene_id` → fail; sum(timing_fractions) >1.0 → fail; malformed custom_code (e.g., syntax error) → fail.
  - Forbidden constructs: Detect network calls or unsafe imports in custom_code (e.g., flag `requests.get`).

- **Spec Merging (`scripts/merge_spec.py`)**:
  - Input: Valid spec + scaffold template.
  - Output: Updated .py file with code inserted in SLOT_START/END, using referenced helpers (e.g., `harmonious_color` applied to title).
  - Edge: Custom code snippets inserted verbatim; animation_sequence mapped to `play_text_next`/`play_next` calls.
  - Failure: Invalid spec → script exits with error (no partial writes).

- **Scaffold Generation (Updated `scripts/scaffold_scene.py`)**:
  - Output: Immutable .py with locked config, helpers, class, and empty SLOT_START/END.
  - No example code in slots; ensures immutability (e.g., no agent-editable regions outside slots).

### Implementation Notes
- Use pytest fixtures for mock specs, scaffolds, and narrations.
- Assert no file writes during unit tests (mock file I/O).
- Coverage: Aim for 80%+ on new scripts; test error paths (e.g., FileNotFound for missing scaffold).
- Replace existing ad-hoc tests if they overlap (e.g., merge any useful smoke tests).

## Integration and E2E Testing
Integration tests verify phase interactions; E2E tests simulate full pipeline runs.

### Integration Tests
- **Phase Transitions**: Mock orchestrator advancing from `narration` → `scaffold_all` → `build_scenes` → `validate_specs` → `merge_specs`.
  - Check state updates: `scaffold_created`, `spec_generated`, `validated`, `merged`.
  - Failure in `validate_specs` → `needs_human_review` set, no advance.

- **Spec-to-Scene Pipeline**: Generate spec → validate → merge → dry-run render.
  - Ensure merged .py is syntactically valid and imports correctly.
  - Verify BeatPlan initialization with spec's `beat_weights`.

- **Self-Heal Fallback**: Malformed spec → validate fails → orchestrator queues agent retry with error explanation (e.g., "Custom code syntax error: missing parenthesis").
  - Test retry loop doesn't exceed limits (prevent infinite self-heal).

### E2E Tests
- Update existing `tests/test_harness_e2e.sh` to cover new phases.
- Full run: Create project → narration → scaffold_all → build_scenes (spec output) → validate_specs → merge_specs → final_render (dry-run only).
- Scenarios:
  - Happy path: Valid spec → successful merge → dry-run passes.
  - Failure paths: Invalid spec → validation fails → self-heal triggers → corrected spec succeeds.
  - Edge: Short narration (few beats) → long (many beats); complex visual_pattern with custom_code.

- Dry-Run Integration: After merge, run Manim dry-render (`manim render <scene>.py <class> --dry-run`) to catch runtime errors early (e.g., undefined variables from spec).
  - Fail if dry-run errors (Python syntax, import issues); log to `build.log`.

### Implementation Notes
- Use mock agents for spec generation to control outputs.
- Test in isolated project directories (e.g., under `tests/test_projects/`).
- Performance: Ensure E2E runs <5 minutes; parallelize if needed.
- Edge Cases: Timing fractions sum >1.0 → validation fails; custom_code with forbidden ops (e.g., `os.system`) → flag; very large specs → handle memory gracefully.

## Dry Runs and Simulation
Dry runs use Manim to validate merged scripts for Python runtime errors without full rendering.

### Process
- After `merge_specs`: For each scene, run `manim render <scene_file>.py <SceneClass> --dry-run` (simulate without video output).
- Capture stdout/stderr for errors (e.g., NameError, SyntaxError).
- If errors: Log to state['errors'], set `needs_human_review`, halt pipeline.
- Success: Proceed to `final_render`.

### Benefits
- Catches issues like undefined helpers, invalid Manim calls, or spec-induced bugs early.
- Complements spec validation (static checks) with dynamic interpretation.
- Aligns with existing pipeline: Similar to pre-render validation in current `build_scenes`.

### Edge Handling
- Expect failures: Invalid custom_code often causes dry-run errors; test with known bad specs.
- Logging: Include error snippets in state (e.g., "Dry-run failed: 'harmonious_color' not defined").

## Regression Testing
Ensure changes don't break existing functionality.

### Key Checks
- Existing phases (`plan`, `review`, `narration`, `final_render`, etc.) still work unchanged.
- Scaffold immutability: Confirm agents can't edit locked regions (test via file perms or mocks).
- Voice policy: Specs don't introduce network TTS (validate no forbidden imports).
- Performance: Phase times similar; no new bottlenecks in beat calc or merging.

### Tools
- Run full pipeline on sample projects before/after changes.
- Compare `build.log` outputs for regressions.

## Migration
**Out of Scope**: Generated projects are disposable development artifacts. The `generated/` directory is ignored via `.gitignore`, and projects are for iterating on the generator (often with nonsense topics for troubleshooting). Requirements change rapidly in early beta, so no migration needed—users regenerate as needed.

If scope expands later, potential strategies:
- Tool to extract "effective" specs from existing repaired scenes (reverse-engineer content).
- Re-run pipeline on old projects with new phases.
- But prioritize fresh generation for now.

## CI/CD Integration
**Deferred**: Do not integrate new tests into CI yet (e.g., `.github/workflows/phase-vocabulary.yml`). The codebase is volatile; circle back in a few weeks for stability. Run tests manually or via local scripts for now.

## Conclusion
This expanded plan emphasizes robust testing to handle common failures (e.g., timing errors, invalid code) while keeping migration minimal. Focus on dry runs and E2E to validate the spec-based model reduces self-heal dependence. Implement incrementally: Start with unit tests for new scripts, then integration.

If issues arise, use the auditor skill for root-cause analysis.