# Harness Contract

Audience: Local coding agents working on Flaming Horse harness behavior.

Purpose: Define the live LLM harness path, prompt composition, schema validation, and artifact writing contracts.

## Live Harness

The live harness path is:

```text
harness_responses/
```

The orchestrator invokes it with:

```bash
python -m harness_responses --phase <phase> --project-dir <project_dir>
```

There is no live `harness/` directory on the current mainline. Treat references to `harness/` as stale unless the task is explicitly about old docs.

## Implemented Phases

`harness_responses` implements:

1. `plan`
2. `narration`
3. `build_scenes`
4. `scene_qc`
5. `scene_repair`

Phase dispatch starts in:

```text
harness_responses/cli.py
```

## Runtime Flow

For each harness phase:

1. `harness_responses/cli.py` parses CLI arguments and phase.
2. `harness_responses/prompts.py` composes system and user prompts from `harness_responses/prompts/<phase>/`.
3. `harness_responses/client.py` writes a phase prompt file and invokes the local Grok Build CLI from the project log directory with Grok's `workspace` sandbox.
4. Grok may read the repository and project filesystem, but sandboxed writes are limited to the log directory and the required staged JSON response file.
5. The staged JSON is parsed into the phase Pydantic schema.
6. `harness_responses/parser.py` performs semantic validation and writes artifacts.

Backend session metadata is stored in:

```text
projects/<project_name>/log/responses_session.json
```

The Grok CLI backend is stateless per phase. The session file is retained as a
compatibility metadata record, not as a conversation-continuation contract.

Per-call prompt and staged response files are written as:

```text
projects/<project_name>/log/grok_prompt_<phase>_<timestamp>.md
projects/<project_name>/log/grok_response_<phase>_<timestamp>.json
```

These files are retained as execution evidence. A project with many retries
will accumulate one prompt file and one staged-response file per Grok call.
The current contract favors auditability over log rotation.
If a failure occurs after prompt writing and before staged response writing,
the prompt-only record is also retained as evidence of the attempted call.

Prompt and response records are appended to:

```text
projects/<project_name>/log/conversation.log
```

Semantic-validation diagnostics are written to:

```text
projects/<project_name>/log/responses_last_response.json
```

## Schemas

Schema files:

```text
harness_responses/schemas/plan.py
harness_responses/schemas/narration.py
harness_responses/schemas/build_scenes.py
harness_responses/schemas/scene_qc.py
harness_responses/schemas/scene_repair.py
```

Current schema surface:

1. `plan`: title, description, target duration, scene list.
2. `narration`: `script` mapping from narration key to narration text.
3. `build_scenes`: `scene_body` string.
4. `scene_qc`: `report_markdown` string.
5. `scene_repair`: `scene_body` string.

Schemas validate output shape. They do not by themselves prove Manim correctness.

## Artifact Writers

`harness_responses/parser.py` owns artifact conversion:

1. `plan` writes `plan.json`.
2. `narration` writes `narration_script.py`.
3. `build_scenes` injects `scene_body` into the current scaffold.
4. `scene_qc` writes `scene_qc_report.md`.
5. `scene_repair` injects repaired `scene_body` into the current scaffold.

The parser must not own phase transitions. `scripts/update_project_state.py` owns state application after artifacts exist.

## Prompt Files

Prompt assets live under:

```text
harness_responses/prompts/
```

Template/reference assets live under:

```text
harness_responses/templates/
```

Prompt instructions must not contradict parser or scaffold contracts. If one prompt asks for comments and another forbids comments, fix the prompt source instead of relying on scene repair.

## Tooling And Retrieval

Current `harness_responses/client.py` supports:

1. Local Grok Build CLI invocation.
2. Prompt-file execution from the project log directory.
3. Required staged JSON file output.
4. Pydantic validation before parser promotion.
5. No web search, xAI collections, xAI file upload, or API conversation continuation.

The minimum verified Grok CLI version for this backend is:

```text
grok 0.1.212
```

The backend requires the local CLI to support these flags:

```text
--cwd
--sandbox workspace
--prompt-file
--output-format json
--no-subagents
--disable-web-search
--max-turns 1
--permission-mode bypassPermissions
--always-approve
--no-memory
--model grok-build
```

`scripts/test_grok_cli_contract.py` is the live contract check for this flag
surface. It verifies the installed binary, required model, and staged JSON write
using the same headless invocation shape as the harness.

The `bypassPermissions` plus `always-approve` pair is intentionally narrow to
the staged JSON writer contract. Less-permissive headless modes did not write
the staged file reliably in local testing. The security invariant is therefore:

```text
Grok runs from projects/<project_name>/log, uses workspace sandboxing, has no
web search, has no subagents, and is instructed to write only the staged JSON
file. Parser-owned artifact promotion remains deterministic.
```

Do not present filesystem read access as artifact ownership. Grok may inspect
files, but only the harness parser promotes validated artifacts into canonical
project files.

## Exit Codes

The CLI contract is:

1. `0`: success.
2. `1`: recoverable phase failure.
3. `2`: configuration, implementation, or semantic validation failure.

Grok CLI timeout is a configuration failure. Raise
`GROK_CLI_TIMEOUT_SECONDS` if a phase is expected to run longer.

`build_video.sh` uses these return codes to decide retry, pause, or failure behavior.

## Execution-Relevant Drift

If this document diverges from `harness_responses/*.py` or `scripts/build_video.sh`, runtime code wins for current behavior. Stop and ask before changing execution based on the document.
