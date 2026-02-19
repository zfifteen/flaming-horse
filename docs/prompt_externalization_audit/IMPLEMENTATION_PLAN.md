# Prompt Externalization Implementation Plan

## Objective
Move all LLM-facing prompt and instruction text out of Python code and into template files under:

`/Users/velocityworks/IdeaProjects/flaming-horse/harness/prompts`

This enables fast prompt iteration without code edits and enforces a single source of truth.
The prompt folder layout must mirror pipeline phase order so users can find prompts by workflow step immediately.

Also keep non-prompt reusable runtime reference content under:

`/Users/velocityworks/IdeaProjects/flaming-horse/harness/templates`

## Inputs Reviewed
- `PROMPT_INFRACTION_REPORT.md`
- `PROMPT_AUDIT_SUMMARY.txt`
- `AUDIT_USAGE_GUIDE.md`
- Current implementation in `harness/prompts.py`
- Current check script: `scripts/check_prompt_compliance.sh`

## Current Gaps
Status baseline (already done):
- `harness/prompt_templates` was renamed to `harness/prompts`.
- Runtime-included reference docs were moved from `docs/reference_docs` into `harness/templates`.

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
5. Runtime prompt includes that are not prompts (long reusable reference blocks) are sourced from `harness/templates`, not `docs/`.
6. Prompt directories are numerically ordered to match the pipeline sequence.
7. Each phase directory exposes task-level prompt files and a phase manifest.

## Desired Prompt Structure (Pipeline-Ordered)
```text
harness/prompts/
  00_plan/
    system.md
    user.md
    manifest.yaml
  01_review/
    system.md
    user.md
    manifest.yaml
  02_narration/
    system.md
    user.md
    manifest.yaml
  03_training/
    system.md
    user.md
    manifest.yaml
  04_build_scenes/
    system.md
    user.md
    task_retry.md
    manifest.yaml
  05_scene_qc/
    system.md
    user.md
    manifest.yaml
  06_scene_repair/
    system.md
    user.md
    task_retry.md
    manifest.yaml
  07_precache_voiceovers/
    README.md
  08_final_render/
    README.md
  09_assemble/
    README.md
  10_complete/
    README.md
  INDEX.md
  README.md
```

Notes:
- For phases not currently LLM-driven, keep `README.md` describing why no prompt files exist yet.
- `manifest.yaml` should define: phase, task list, source files, required placeholders, compose order.

## Implementation Phases

### Phase 1: Add missing user templates
Create pipeline-ordered phase directories and initial task files.
At minimum for active LLM phases:
- `harness/prompts/00_plan/{system.md,user.md,manifest.yaml}`
- `harness/prompts/02_narration/{system.md,user.md,manifest.yaml}`
- `harness/prompts/03_training/{system.md,user.md,manifest.yaml}`
- `harness/prompts/04_build_scenes/{system.md,user.md,task_retry.md,manifest.yaml}`
- `harness/prompts/05_scene_qc/{system.md,user.md,manifest.yaml}`
- `harness/prompts/06_scene_repair/{system.md,user.md,task_retry.md,manifest.yaml}`
- `harness/prompts/01_review/{system.md,user.md,manifest.yaml}` (stub or active per harness support)

Use explicit placeholders (double-curly style), for example:
- `{{topic}}`
- `{{scene_id}}`
- `{{scene_details}}`
- `{{retry_context}}`

### Phase 2: Externalize system wrappers
Move all system wrappers into per-phase `system.md` files.
Move all user prompt bodies into per-phase `user.md` files.
Use task files (for example `task_retry.md`) when a phase has materially different prompts for retry/repair flows.
Retain shared non-prompt includes in `harness/templates`.

### Phase 3: Refactor `harness/prompts.py`
1. Add a deterministic interpolation helper (single-pass, explicit placeholder substitution).
2. Replace embedded f-string prompt bodies with loading from pipeline-ordered directories.
3. Keep phase logic and scene selection logic in code; keep all instructions/content in templates.
4. Ensure empty optional sections (`reference_section`, `retry_section`) are handled cleanly.
5. Add a phase-to-directory mapping table in code (single source), aligned to pipeline order.

### Phase 4: Consolidate docs prompt duplication
For `docs/issues/SCENE_QC_AGENT_PROMPT.md`:
- Convert to a short reference doc that points to canonical template file(s), or
- Remove prompt body and keep only maintenance notes.

### Phase 5: Strengthen compliance checks
Update `scripts/check_prompt_compliance.sh` to verify:
1. No embedded prompt text blocks in `harness/prompts.py`.
2. All expected pipeline-ordered phase directories exist.
3. Required files exist in active LLM phases (`system.md`, `user.md`, `manifest.yaml`).
4. `compose_*_prompt()` loads templates from phase directories (not flat files).
5. `INDEX.md` references each active phase/task file.

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
2. All prompt content used by harness is located in pipeline-ordered phase folders under `harness/prompts`.
3. Compliance checker passes.
4. Dry-run prompt generation passes for all phases.
5. Runtime non-prompt includes are loaded from `harness/templates` (no runtime `docs/` dependency for these blocks).
6. Prompt folder order matches pipeline sequence via numeric prefixes (`00_...` to `10_...`).
7. Each active LLM phase has task-level prompt files and `manifest.yaml`.
8. `harness/prompts/INDEX.md` gives one-click navigation by phase and task.

## Risks and Mitigations
- Risk: Placeholder mismatch causes malformed prompts.
  - Mitigation: add strict missing-placeholder detection during interpolation.

- Risk: Behavior drift from subtle wording differences during extraction.
  - Mitigation: copy existing prompt text verbatim first; optimize wording only in a separate pass.

- Risk: Compliance check false failures.
  - Mitigation: tighten grep patterns to target true prompt blocks only.

## Execution Order
1. Create pipeline-ordered phase directory skeleton + `INDEX.md`
2. Move existing flat prompts into phase directories (no content changes first)
3. Externalize remaining embedded user/system prompt content into phase task files
4. Refactor `harness/prompts.py` loader and mappings
5. Update compliance script for directory/manifest model
6. Consolidate docs duplicate prompt
7. Run verification suite
8. Commit with focused diff
