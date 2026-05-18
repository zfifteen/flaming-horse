#!/usr/bin/env python3
"""Sentinel checks for high-impact contract/runtime drift.

This intentionally checks only the active contract surfaces that steer local
agents. It is not a documentation linter.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

BUILD_PHASES = [
    "init",
    "plan",
    "review",
    "narration",
    "build_scenes",
    "scene_qc",
    "precache_voiceovers",
    "final_render",
    "assemble",
    "complete",
]
STATE_PHASES = [*BUILD_PHASES, "error"]
HARNESS_PHASES = ["plan", "narration", "build_scenes", "scene_qc", "scene_repair"]
SLOT_START = "# SLOT_START:scene_body"
SLOT_END = "# SLOT_END:scene_body"


def read_text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def shell_array(script_text: str, name: str) -> list[str]:
    match = re.search(rf"^{name}=\(\n(?P<body>.*?)^\)", script_text, re.M | re.S)
    if not match:
        fail(f"{name} shell array not found")
    return re.findall(r'"([^"]+)"', match.group("body"))


def python_assignment(path: str, name: str) -> Any:
    tree = ast.parse(read_text(path), filename=path)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name:
                return ast.literal_eval(node.value)
    fail(f"{name} assignment not found in {path}")


def state_schema_phases() -> list[str]:
    schema = json.loads(read_text("scripts/state_schema.json"))
    return schema["properties"]["phase"]["enum"]


def invokes_legacy_harness(script_text: str) -> bool:
    return (
        re.search(r"(?<![\w-])-m\s+['\"]?harness(?:\s|$|['\"])", script_text)
        is not None
    )


def check_harness_contract() -> None:
    agents = read_text("AGENTS.md")
    harness_contract = read_text("docs/architecture/HARNESS_CONTRACT.md")
    build_video = read_text("scripts/build_video.sh")
    client = read_text("harness_responses/client.py")
    cli_phases = list(python_assignment("harness_responses/cli.py", "_IMPLEMENTED_PHASES"))

    require(
        invokes_legacy_harness("python3  -m harness'"),
        "legacy harness detector missed quoted invocation",
    )
    require(
        not invokes_legacy_harness("python3 -m harness_responses"),
        "legacy harness detector matched harness_responses",
    )

    require("harness_responses/" in agents, "AGENTS.md does not name harness_responses/")
    require(
        "harness_responses/" in harness_contract,
        "HARNESS_CONTRACT.md does not name harness_responses/",
    )
    require(
        "-m harness_responses" in build_video,
        "build_video.sh does not invoke harness_responses",
    )
    require(
        not invokes_legacy_harness(build_video),
        "build_video.sh still invokes legacy harness",
    )
    require(cli_phases == HARNESS_PHASES, "harness_responses CLI phase list drifted")
    require(
        "--permission-mode" in client and "bypassPermissions" in client,
        "Grok CLI permission-mode contract drifted",
    )
    require("--always-approve" in client, "Grok CLI approval contract drifted")
    require("--sandbox" in client and "workspace" in client, "Grok sandbox contract drifted")
    require(
        "scripts/test_grok_cli_contract.py" in harness_contract,
        "HARNESS_CONTRACT.md does not point to the live Grok CLI contract check",
    )
    for env_name in ("GROK_CLI", "GROK_MODEL", "GROK_CLI_TIMEOUT_SECONDS"):
        require(
            f"export {env_name}" in build_video,
            f"build_video.sh does not export {env_name} for harness subprocesses",
        )


def check_harness_docs_contract() -> None:
    active_docs = [
        "README.md",
        "TECH_SPEC.md",
        "CURRENT_STATE.md",
        ".env.example",
        "docs/architecture/HARNESS_CONTRACT.md",
        "docs/guides/HOW_TO_ADD_API_KEY.md",
        "docs/guides/WHERE_TO_ADD_API_KEY.md",
        "docs/harness/HARNESS_QUICK_REFERENCE.md",
        "docs/harness/HARNESS_MIGRATION_GUIDE.md",
        "docs/engineering/IMPLEMENTATION_COMPLETE.md",
        "docs/testing/E2E_TESTING_SUMMARY.md",
    ]
    stale_runtime_vars = [
        "LLM_PROVIDER=",
        "XAI_API_KEY=",
        "XAI_MODEL=",
        "AGENT_MODEL=",
        "MINIMAX_API_KEY=",
        "MINIMAX_MODEL=",
    ]
    for path in active_docs:
        text = read_text(path)
        for stale in stale_runtime_vars:
            require(stale not in text, f"{path} still documents stale runtime variable {stale}")
    cli = read_text("harness_responses/cli.py")
    client = read_text("harness_responses/client.py")
    prompts = read_text("harness_responses/prompts.py")
    require("AGENT_TEMPERATURE" not in cli, "CLI still parses inert AGENT_TEMPERATURE")
    require("store: True" not in cli, "CLI still logs inert store=True")
    require(
        "consume_last_retrieval_info" not in cli,
        "dead retrieval-info shim still exists in harness_responses/cli.py",
    )
    require(
        "consume_last_retrieval_info" not in prompts,
        "dead retrieval-info shim still exists in harness_responses/prompts.py",
    )
    require("tools_enabled" not in cli, "CLI still logs inert tools_enabled field")
    require(
        "temperature:" not in client and "max_tokens:" not in client,
        "client still exposes inert generation knobs",
    )


def check_phase_contract() -> None:
    build_video = read_text("scripts/build_video.sh")
    build_phases = shell_array(build_video, "PHASE_SEQUENCE")
    update_phases = list(python_assignment("scripts/update_project_state.py", "PHASE_SEQUENCE"))
    schema_phases = state_schema_phases()

    require(build_phases == BUILD_PHASES, "build_video.sh phase sequence drifted")
    require(update_phases == STATE_PHASES, "update_project_state.py phase sequence drifted")
    require(schema_phases == STATE_PHASES, "state_schema.json phase enum drifted")


def check_scaffold_contract() -> None:
    scaffold = read_text("scripts/scaffold_scene.py")
    parser = read_text("harness_responses/parser.py")
    for marker in (SLOT_START, SLOT_END):
        require(marker in scaffold, f"{marker} missing from scaffold_scene.py")
        require(marker in parser, f"{marker} missing from harness_responses/parser.py")
    require(
        "get_speech_service(Path(__file__).resolve().parent)" in scaffold,
        "scaffold does not use project-local cached speech service",
    )


def check_voice_contract() -> None:
    service_factory = read_text("flaming_horse_voice/service_factory.py")
    require(
        "voice_clone_config.json" in service_factory,
        "service_factory does not load voice_clone_config.json",
    )
    require(
        "selected_tts_backend(cfg)" in service_factory,
        "service_factory does not validate selected backend from project config",
    )
    require(
        "from flaming_horse_voice.qwen_cached import QwenCachedService" in service_factory,
        "service_factory does not use QwenCachedService as cache reader",
    )
    require(
        "return QwenCachedService.from_project(project_dir)" in service_factory,
        "service_factory return path no longer uses QwenCachedService.from_project",
    )


def check_voice_backend_resolution_contract() -> None:
    from tts_backend_config import build_voice_clone_config

    saved_env = os.environ.copy()
    try:
        for key in list(os.environ):
            if key.startswith("FLAMING_HORSE_"):
                os.environ.pop(key)
        os.environ["FLAMING_HORSE_TTS_BACKEND"] = "mlx"
        os.environ["FLAMING_HORSE_MLX_PYTHON"] = "/env/mlx/python"
        cfg = build_voice_clone_config({})
    finally:
        os.environ.clear()
        os.environ.update(saved_env)

    require(
        "qwen_python" not in cfg,
        "new MLX voice configs must not synthesize qwen_python",
    )

    prepare_voice = read_text("scripts/prepare_qwen_voice.py")
    require(
        "selected_output_dir(cfg)" in prepare_voice,
        "prepare_qwen_voice.py does not use shared selected_output_dir",
    )
    require(
        "compute_fingerprint(" in prepare_voice
        and "backend," in prepare_voice
        and "str(model_id)," in prepare_voice
        and "str(python_path)," in prepare_voice,
        "prepare_qwen_voice.py fingerprint does not use resolved model/backend/worker",
    )
    require(
        '"backend": backend' in prepare_voice
        and '"worker_python": worker_python' in prepare_voice,
        "prepare_qwen_voice.py fingerprint does not include backend and worker python",
    )

    mlx_service = read_text("flaming_horse_voice/mlx_tts_service.py")
    require(
        "def resolve_ref_audio(" in mlx_service,
        "mlx_tts_service.py does not validate MLX reference audio explicitly",
    )
    require(
        "Path(REF_AUDIO).read_bytes()" not in mlx_service,
        "mlx_tts_service.py still reads global REF_AUDIO directly for cache key",
    )
    require(
        not re.search(r"^model\s*=\s*load_model\(", mlx_service, re.M),
        "mlx_tts_service.py loads model at import time",
    )


def check_removed_live_surfaces() -> None:
    removed_service = "MLX" + "CachedService"
    removed_module = "flaming_horse_voice" + ".mlx_cached"
    live_files = [
        *Path(REPO_ROOT / "flaming_horse_voice").glob("*.py"),
        *Path(REPO_ROOT / "scripts").glob("*.py"),
        *Path(REPO_ROOT / "harness_responses").rglob("*.py"),
    ]
    for path in live_files:
        if path == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(REPO_ROOT)
        require(removed_service not in text, f"dead MLX cached service reference in {rel}")
        require(
            removed_module not in text,
            f"dead mlx_cached import reference in {rel}",
        )


def main() -> int:
    check_harness_contract()
    check_harness_docs_contract()
    check_phase_contract()
    check_scaffold_contract()
    check_voice_contract()
    check_voice_backend_resolution_contract()
    check_removed_live_surfaces()
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
