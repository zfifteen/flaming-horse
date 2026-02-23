"""
Command-line interface for harness_responses.

Supports phases implemented in this harness:
- plan
- narration
- build_scenes
- scene_qc
- scene_repair
Exit codes match legacy harness contract: 0=success, 1=recoverable/phase failure, 2=config error.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from harness_responses.parser import SemanticValidationError, write_phase_artifacts
from harness_responses.prompts import compose_prompt, consume_last_retrieval_info

# Phases implemented in Phase 1
_IMPLEMENTED_PHASES = ["plan", "narration", "build_scenes", "scene_qc", "scene_repair"]


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_project_state(project_dir: Path) -> dict:
    state_file = project_dir / "project_state.json"
    if not state_file.exists():
        raise FileNotFoundError(f"Project state file not found: {state_file}")
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def _append_conversation_log(
    log_path: Path,
    *,
    phase: str,
    system_prompt: str,
    user_prompt: str,
    response_id: Optional[str],
    status: str,
    api_mode: str,
    tools_enabled: bool,
    store: bool,
    retrieval_info: Optional[Dict[str, Any]] = None,
    assistant_response_content: Optional[str] = None,
    error_text: Optional[str] = None,
) -> None:
    parts = [
        "============================================================",
        f"timestamp_utc: {_utc_timestamp()}",
        f"phase: {phase}",
        f"status: {status}",
        f"api_mode: {api_mode}",
        f"tools_enabled: {tools_enabled}",
        f"store: {store}",
    ]
    if response_id:
        parts.append(f"response_id: {response_id}")
    if error_text:
        parts.append(f"error: {error_text}")
    parts.extend(
        [
            "",
            "----- SYSTEM PROMPT -----",
            system_prompt,
            "",
            "----- USER PROMPT -----",
            user_prompt,
            "",
        ]
    )
    if retrieval_info:
        parts.extend(
            [
                "----- COLLECTIONS RETRIEVAL -----",
                json.dumps(retrieval_info, indent=2, default=str),
                "",
            ]
        )
    if assistant_response_content is not None:
        parts.extend(
            [
                "----- ASSISTANT RESPONSE (RAW CONTENT) -----",
                assistant_response_content,
                "",
            ]
        )
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")


def _stringify_response_content(raw_response: Any) -> str:
    content = getattr(raw_response, "content", None)
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    chunks.append(text)
                    continue
                body = item.get("content")
                if isinstance(body, str):
                    chunks.append(body)
                    continue
                chunks.append(json.dumps(item, default=str))
                continue
            chunks.append(str(item))
        return "".join(chunks)
    try:
        return json.dumps(content, default=str)
    except Exception:
        return str(content)


def _get_schema_for_phase(phase: str):
    """Return the Pydantic schema class for the given phase."""
    if phase == "plan":
        from harness_responses.schemas.plan import PlanResponse
        return PlanResponse
    if phase == "narration":
        from harness_responses.schemas.narration import NarrationResponse
        return NarrationResponse
    if phase == "build_scenes":
        from harness_responses.schemas.build_scenes import BuildScenesResponse
        return BuildScenesResponse
    if phase == "scene_qc":
        from harness_responses.schemas.scene_qc import SceneQcResponse
        return SceneQcResponse
    if phase == "scene_repair":
        from harness_responses.schemas.scene_repair import SceneRepairResponse
        return SceneRepairResponse
    raise NotImplementedError(f"No schema for phase: {phase}")


def main() -> int:
    """Main entry point for harness_responses CLI."""
    parser = argparse.ArgumentParser(
        description="Flaming Horse harness_responses — xAI Responses API harness"
    )
    parser.add_argument(
        "--phase",
        required=True,
        choices=_IMPLEMENTED_PHASES,
        help="Phase to execute",
    )
    parser.add_argument(
        "--project-dir",
        required=True,
        type=Path,
        help="Path to project directory",
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="Topic for the video (required for plan phase)",
    )
    parser.add_argument(
        "--retry-context",
        type=str,
        default="",
        help="Error context for retry attempts",
    )
    parser.add_argument(
        "--scene-file",
        type=Path,
        help="Scene file path (required for scene_repair phase)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build and validate prompt/request payload without making API calls",
    )

    args = parser.parse_args()

    # Validate project directory
    if not args.project_dir.exists():
        print(
            f"❌ Project directory does not exist: {args.project_dir}",
            file=sys.stderr,
        )
        return 1

    # Phase-specific input validation
    if args.phase == "plan" and not args.topic:
        print("❌ --topic is required for plan phase", file=sys.stderr)
        return 1
    if args.phase == "scene_repair" and not args.scene_file:
        print("❌ --scene-file is required for scene_repair phase", file=sys.stderr)
        return 1

    # Runtime config
    raw_temperature = os.getenv("AGENT_TEMPERATURE", "0.7")
    try:
        temperature = float(raw_temperature)
    except ValueError:
        temperature = 0.7
    temperature = max(0.0, min(2.0, temperature))

    store = False  # stateful mode is opt-in; default stateless
    enable_web_search = False  # tools off by default

    log_dir = args.project_dir / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    conversation_log = log_dir / "conversation.log"

    system_prompt = ""
    user_prompt = ""
    retrieval_info: Dict[str, Any] = {}

    try:
        system_prompt, user_prompt = compose_prompt(
            phase=args.phase,
            project_dir=args.project_dir,
            topic=args.topic or "",
            retry_context=args.retry_context or "",
            scene_file=args.scene_file,
        )
        retrieval_info = consume_last_retrieval_info()

        if args.dry_run:
            print("🔍 DRY RUN MODE — harness_responses")
            print(f"   Phase:          {args.phase}")
            print(f"   System prompt:  {len(system_prompt)} chars")
            print(f"   User prompt:    {len(user_prompt)} chars")
            print(f"   Temperature:    {temperature}")
            print(f"   Store:          {store}")
            print(f"   Web search:     {enable_web_search}")
            schema_cls = _get_schema_for_phase(args.phase)
            print(f"   Schema:         {schema_cls.__name__}")
            print("\n=== System Prompt (first 500 chars) ===")
            print(system_prompt[:500])
            print("\n=== User Prompt (first 500 chars) ===")
            print(user_prompt[:500])
            _append_conversation_log(
                conversation_log,
                phase=args.phase,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_id=None,
                status="dry_run",
                api_mode="responses",
                tools_enabled=enable_web_search,
                store=store,
                retrieval_info=retrieval_info or None,
            )
            return 0

        # Import client only when not in dry-run to avoid requiring XAI_API_KEY
        from harness_responses.client import call_responses_api

        schema_cls = _get_schema_for_phase(args.phase)

        print(f"🤖 harness_responses calling Responses API for phase: {args.phase}")
        raw_response, parsed = call_responses_api(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=schema_cls,
            temperature=temperature,
            store=store,
            enable_web_search=enable_web_search,
        )

        response_id: Optional[str] = getattr(raw_response, "id", None)
        if response_id:
            print(f"   Response ID: {response_id}")

        assistant_response_content = _stringify_response_content(raw_response)
        _append_conversation_log(
            conversation_log,
            phase=args.phase,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_id=response_id,
            status="api_success",
            api_mode="responses",
            tools_enabled=enable_web_search,
            store=store,
            retrieval_info=retrieval_info or None,
            assistant_response_content=assistant_response_content,
        )

        print(f"📝 Validating and writing artifacts for phase: {args.phase}")
        try:
            write_phase_artifacts(
                phase=args.phase,
                parsed=parsed,
                project_dir=args.project_dir,
                raw_response=raw_response,
            )
        except SemanticValidationError as exc:
            print(f"❌ Semantic validation failed: {exc}", file=sys.stderr)
            return 2

        print(f"✅ Phase {args.phase} completed successfully")
        return 0

    except FileNotFoundError as exc:
        print(f"❌ File not found: {exc}", file=sys.stderr)
        return 1
    except NotImplementedError as exc:
        print(f"❌ Not implemented: {exc}", file=sys.stderr)
        return 2
    except EnvironmentError as exc:
        # Missing API key or other config errors
        print(f"❌ Configuration error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        try:
            if system_prompt:
                _append_conversation_log(
                    conversation_log,
                    phase=args.phase,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_id=None,
                    status="error",
                    api_mode="responses",
                    tools_enabled=enable_web_search,
                    store=store,
                    retrieval_info=retrieval_info or None,
                    error_text=str(exc),
                )
        except Exception:
            pass
        print(f"❌ Error: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
