"""
Command-line interface for the Flaming Horse agent harness.
"""

import argparse
import sys
import json
import os
from pathlib import Path
from typing import Optional

from harness.prompts import compose_prompt
from harness.client import call_xai_api
from harness.parser import parse_and_write_artifacts


def load_project_state(project_dir: Path) -> dict:
    """Load project_state.json from the project directory."""
    state_file = project_dir / "project_state.json"
    if not state_file.exists():
        raise FileNotFoundError(f"Project state file not found: {state_file}")

    with open(state_file, "r") as f:
        return json.load(f)


def main() -> int:
    """Main entry point for the harness CLI."""
    parser = argparse.ArgumentParser(
        description="Flaming Horse Agent Harness - Direct xAI API integration"
    )
    parser.add_argument(
        "--phase",
        required=True,
        choices=["plan", "narration", "build_scenes", "scene_qc", "scene_repair"],
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
        # Load project state
        state = load_project_state(args.project_dir)

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
            return 0

        # Optional runtime tuning via environment variables.
        raw_temperature = os.getenv("AGENT_TEMPERATURE", "0.7")
        try:
            temperature = float(raw_temperature)
        except ValueError:
            temperature = 0.7
        temperature = max(0.0, min(2.0, temperature))

        # Call xAI API
        print(f"🤖 Calling xAI API for phase: {args.phase}")
        response_text = call_xai_api(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )

        # Parse response and write artifacts
        print(f"📝 Parsing response and writing artifacts...")
        success = parse_and_write_artifacts(
            phase=args.phase,
            response_text=response_text,
            project_dir=args.project_dir,
            state=state,
        )

        if success:
            print(f"✅ Phase {args.phase} completed successfully")
            return 0
        else:
            debug_file = args.project_dir / f"debug_response_{args.phase}.txt"
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
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
