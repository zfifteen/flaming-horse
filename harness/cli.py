"""
Command-line interface for the Flaming Horse agent harness.
"""

import argparse
import sys
import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from harness.prompts import compose_prompt
from harness.client import call_llm_api
from harness.parser import SchemaValidationError, parse_and_write_artifacts


def load_project_state(project_dir: Path) -> dict:
    """Load project_state.json from the project directory."""
    state_file = project_dir / "project_state.json"
    if not state_file.exists():
        raise FileNotFoundError(f"Project state file not found: {state_file}")

    with open(state_file, "r") as f:
        return json.load(f)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_schema_failure(project_dir: Path, phase: str, error_text: str) -> None:
    """Record schema failure details in project_state.json for orchestrator logs."""
    state_file = project_dir / "project_state.json"
    if not state_file.exists():
        return
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        return

    errors = state.setdefault("errors", [])
    if not isinstance(errors, list):
        errors = []
        state["errors"] = errors
    errors.append(f"Schema validation failed ({phase}): {error_text}")

    history = state.setdefault("history", [])
    if isinstance(history, list):
        history.append(
            {
                "phase": phase,
                "action": "schema_validation_failed",
                "error": error_text,
                "timestamp": utc_timestamp(),
            }
        )

    state["updated_at"] = utc_timestamp()
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def append_conversation_log(
    conversation_log: Path,
    *,
    phase: str,
    system_prompt: str,
    user_prompt: str,
    response_text: Optional[str],
    status: str,
    error_text: Optional[str] = None,
) -> None:
    """Append full prompt/response transcript for a harness call."""
    entry_parts = [
        "============================================================",
        f"timestamp_utc: {utc_timestamp()}",
        f"phase: {phase}",
        f"status: {status}",
    ]
    if error_text:
        entry_parts.append(f"error: {error_text}")
    entry_parts.extend(
        [
            "",
            "----- SYSTEM PROMPT -----",
            system_prompt,
            "",
            "----- USER PROMPT -----",
            user_prompt,
            "",
            "----- ASSISTANT RESPONSE -----",
            response_text if response_text is not None else "<no response>",
            "",
        ]
    )

    with open(conversation_log, "a", encoding="utf-8") as f:
        f.write("\n".join(entry_parts))


def main() -> int:
    """Main entry point for the harness CLI."""
    parser = argparse.ArgumentParser(
        description="Flaming Horse Agent Harness - Provider-agnostic LLM API integration"
    )
    parser.add_argument(
        "--phase",
        required=True,
        choices=[
            "plan",
            "narration",
            "build_scenes",
            "scene_qc",
            "scene_repair",
        ],
        help="Phase to execute",
    )
    parser.add_argument(
        "--project-dir", required=True, type=Path, help="Path to project directory"
    )
    parser.add_argument(
        "--topic", type=str, help="Topic for the video (required for plan phase)"
    )
    parser.add_argument(
        "--retry-context", type=str, help="Error context for retry attempts"
    )
    parser.add_argument(
        "--scene-file", type=Path, help="Scene file path (for scene_repair phase)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Test mode - don't actually call API"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.project_dir.exists():
        print(
            f"❌ Project directory does not exist: {args.project_dir}", file=sys.stderr
        )
        return 1

    if args.phase == "plan" and not args.topic:
        print("❌ --topic is required for plan phase", file=sys.stderr)
        return 1

    if args.phase == "scene_repair" and not args.scene_file:
        print("❌ --scene-file is required for scene_repair phase", file=sys.stderr)
        return 1

    try:
        log_dir = args.project_dir / "log"
        log_dir.mkdir(parents=True, exist_ok=True)
        conversation_log = log_dir / "conversation.log"

        # Load project state
        state = load_project_state(args.project_dir)
        if args.scene_file:
            state["scene_file"] = str(args.scene_file)

        # Compose phase-specific prompt
        system_prompt, user_prompt = compose_prompt(
            phase=args.phase,
            state=state,
            topic=args.topic,
            retry_context=args.retry_context,
            scene_file=args.scene_file,
            project_dir=args.project_dir,
        )

        if args.dry_run:
            print("🔍 DRY RUN MODE")
            print(f"System prompt length: {len(system_prompt)} chars")
            print(f"User prompt length: {len(user_prompt)} chars")
            print("\n=== System Prompt (first 500 chars) ===")
            print(system_prompt[:500])
            print("\n=== User Prompt (first 500 chars) ===")
            print(user_prompt[:500])
            append_conversation_log(
                conversation_log,
                phase=args.phase,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_text=None,
                status="dry_run",
            )
            return 0

        # Optional runtime tuning via environment variables.
        raw_temperature = os.getenv("AGENT_TEMPERATURE", "0.7")
        try:
            temperature = float(raw_temperature)
        except ValueError:
            temperature = 0.7
        temperature = max(0.0, min(2.0, temperature))

        # Call LLM API
        print(f"🤖 Calling LLM API for phase: {args.phase}")
        response_text = call_llm_api(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )
        append_conversation_log(
            conversation_log,
            phase=args.phase,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_text=response_text,
            status="api_success",
        )

        # Parse response and write artifacts
        print(f"📝 Parsing response and writing artifacts...")
        try:
            success = parse_and_write_artifacts(
                phase=args.phase,
                response_text=response_text,
                project_dir=args.project_dir,
                state=state,
            )
        except SchemaValidationError as e:
            debug_file = log_dir / f"debug_response_{args.phase}.txt"
            try:
                debug_file.write_text(response_text)
                print(f"🧾 Wrote debug response: {debug_file}")
            except Exception:
                pass
            record_schema_failure(args.project_dir, args.phase, str(e))
            print(f"❌ Schema validation failed: {e}", file=sys.stderr)
            return 3

        if success:
            print(f"✅ Phase {args.phase} completed successfully")
            return 0
        else:
            debug_file = log_dir / f"debug_response_{args.phase}.txt"
            try:
                debug_file.write_text(response_text)
                print(f"🧾 Wrote debug response: {debug_file}")
            except Exception:
                pass
            print(f"❌ Failed to parse artifacts from response", file=sys.stderr)
            return 2

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        try:
            # Best-effort logging for failures after prompt composition.
            if (
                "conversation_log" in locals()
                and "system_prompt" in locals()
                and "user_prompt" in locals()
            ):
                append_conversation_log(
                    conversation_log,
                    phase=args.phase,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_text=locals().get("response_text"),
                    status="error",
                    error_text=str(e),
                )
        except Exception:
            pass
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
