# Prompt Externalization Implementation Plan

## Objective
Move all LLM-facing prompt and instruction text out of Python code and into template files under:

`/Users/velocityworks/IdeaProjects/flaming-horse/harness/prompts`

This enables fast prompt iteration without code edits and enforces a single source of truth.

## Inputs Reviewed
- `PROMPT_INFRACTION_REPORT.md`
- `PROMPT_AUDIT_SUMMARY.txt`
- `AUDIT_USAGE_GUIDE.md`
- Current implementation in `harness/prompts.py`
- Current check script: `scripts/check_prompt_compliance.sh`

## Current Gaps
1. User prompts are embedded in `harness/prompts.py` for:
- plan
- narration
- build_scenes
- scene_qc
- scene_repair
- training

2. System wrappers/headers are embedded in `harness/prompts.py` for all phases.

3. `docs/issues/SCENE_QC_AGENT_PROMPT.md` duplicates prompt content outside `harness/prompts`.

## Target End State
1. Every LLM prompt string sent through `harness/cli.py -> harness/prompts.py` is sourced from files in `harness/prompts`.
2. `harness/prompts.py` only performs:
- template loading
- variable interpolation
- prompt composition orchestration

3. Compliance check passes with no false positives.
4. Prompt edits require no Python code changes in normal iteration.

## Implementation Phases

### Phase 1: Add missing user templates
Create:
- `harness/prompts/plan_user.md`
- `harness/prompts/narration_user.md`
- `harness/prompts/build_scenes_user.md`
- `harness/prompts/scene_qc_user.md`
- `harness/prompts/scene_repair_user.md`
- `harness/prompts/training_user.md`

Use explicit placeholders (double-curly style), for example:
- `{{topic}}`
- `{{scene_id}}`
- `{{scene_details}}`
- `{{retry_context}}`

### Phase 2: Externalize system wrappers
Create per-phase system wrapper templates that include headings/separators and references to existing content templates, or fully inline complete system prompts in phase-specific template files. Preferred approach:
- `plan_system_full.md`
- `narration_system_full.md`
- `build_scenes_system_full.md`
- `scene_qc_system_full.md`
- `scene_repair_system_full.md`
- `training_system_full.md`

Then retain `core_rules.md` and reference docs as reusable content blocks where useful.

### Phase 3: Refactor `harness/prompts.py`
1. Add a deterministic interpolation helper (single-pass, explicit placeholder substitution).
2. Replace embedded f-string prompt bodies with template loading + interpolation maps.
3. Keep phase logic and scene selection logic in code; keep instructions/content in templates.
4. Ensure empty optional sections (`reference_section`, `retry_section`) are handled cleanly.

### Phase 4: Consolidate docs prompt duplication
For `docs/issues/SCENE_QC_AGENT_PROMPT.md`:
- Convert to a short reference doc that points to canonical template file(s), or
- Remove prompt body and keep only maintenance notes.

### Phase 5: Strengthen compliance checks
Update `scripts/check_prompt_compliance.sh` to verify:
1. No embedded prompt text blocks in `harness/prompts.py`.
2. All expected template files exist.
3. `compose_*_prompt()` loads templates for both system and user prompts.

## Verification
Run:

```bash
./scripts/check_prompt_compliance.sh
python3 -m harness --phase plan --project-dir <tmp_project> --topic "test" --dry-run
python3 -m harness --phase narration --project-dir <tmp_project> --dry-run
python3 -m harness --phase build_scenes --project-dir <tmp_project> --dry-run
python3 -m harness --phase scene_qc --project-dir <tmp_project> --dry-run
python3 -m harness --phase scene_repair --project-dir <tmp_project> --scene-file <scene.py> --dry-run
python3 -m harness --phase training --project-dir <tmp_project> --dry-run
```

Optional regression checks:

```bash
bash tests/test_harness_dry_run.sh
bash tests/test_harness_integration.sh
```

## Acceptance Criteria
1. Zero LLM-instruction strings remain embedded in `harness/prompts.py`.
2. All prompt content used by harness is located in `harness/prompts`.
3. Compliance checker passes.
4. Dry-run prompt generation passes for all phases.
5. Documentation points to canonical template paths.

## Risks and Mitigations
- Risk: Placeholder mismatch causes malformed prompts.
  - Mitigation: add strict missing-placeholder detection during interpolation.

- Risk: Behavior drift from subtle wording differences during extraction.
  - Mitigation: copy existing prompt text verbatim first; optimize wording only in a separate pass.

- Risk: Compliance check false failures.
  - Mitigation: tighten grep patterns to target true prompt blocks only.

## Execution Order
1. Add templates
2. Refactor `harness/prompts.py`
3. Update compliance script
4. Consolidate docs duplicate prompt
5. Run verification suite
6. Commit with focused diff
