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
    create_video = read_text("scripts/create_video.sh")
    new_project = read_text("scripts/new_project.sh")
    build_video = read_text("scripts/build_video.sh")
    build_phases = shell_array(build_video, "PHASE_SEQUENCE")
    update_phases = list(python_assignment("scripts/update_project_state.py", "PHASE_SEQUENCE"))
    schema_phases = state_schema_phases()

    require(build_phases == BUILD_PHASES, "build_video.sh phase sequence drifted")
    require(update_phases == STATE_PHASES, "update_project_state.py phase sequence drifted")
    require(schema_phases == STATE_PHASES, "state_schema.json phase enum drifted")
    create_video_after_python = create_video.split('PYTHON_BIN="${PYTHON:-python3.13}"', 1)[1]
    require(
        not re.search(r"(?<![\w$])python3(?:\s|$)", create_video_after_python),
        "create_video.sh uses bare python3 after selecting PYTHON_BIN",
    )
    new_project_after_python = new_project.split('PYTHON_BIN="${PYTHON:-python3.13}"', 1)[1]
    require(
        not re.search(r"(?<![\w$])python3(?:\s|$)", new_project_after_python),
        "new_project.sh uses bare python3 after selecting PYTHON_BIN",
    )


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


def check_first_pass_scene_creation_contract() -> None:
    build_video = read_text("scripts/build_video.sh")
    scene_validator = read_text("scripts/scene_validator.py")
    parser = read_text("harness_responses/parser.py")
    build_system = read_text("harness_responses/prompts/build_scenes/system.md")
    build_user = read_text("harness_responses/prompts/build_scenes/user.md")
    prompt_text = f"{build_system}\n{build_user}"

    for required in (
        "first-pass-valid",
        "scaffold structure",
        "Python syntax",
        "import/API validation",
        "voiceover sync",
        "timing budget validation",
        "semantic placeholder checks",
        "manim render --dry_run",
        "ShowCreation",
        "FadeIn(..., lag_ratio=...)",
        "FadeIn(..., scale_factor=...)",
        "set_color(list(...))",
        "set_color(harmonious_color(...))",
    ):
        require(required in prompt_text, f"build_scenes prompt missing {required}")

    for required in (
        "_validate_scene_body_contract",
        "tokenize.COMMENT",
        "attribute_root_name",
        "target_touches_config",
        "is_self_voiceover_call",
        "is_tracker_duration",
        "tracker.duration",
        "ShowCreation",
        '"lag_ratio"',
        '"scale_factor"',
        '"list"',
        '"harmonious_color"',
    ):
        require(required in parser, f"parser missing first-pass scene validation: {required}")

    require(
        "FIRST_PASS_DIAG_FILE=\"${LOG_DIR}/scene_first_pass_diagnostics.jsonl\""
        in build_video,
        "build_video.sh does not define first-pass diagnostics JSONL path",
    )
    require(
        "record_scene_first_pass_diagnostic()" in build_video,
        "build_video.sh does not define first-pass diagnostic writer",
    )
    require(
        "json.dump(event" in build_video and '"attempt_count": attempt_count' in build_video,
        "first-pass diagnostic writer does not emit JSON with attempt_count",
    )
    require(
        "repair_build_scene_first_pass_failure()" in build_video,
        "build_video.sh does not route build_scenes failures through diagnostic wrapper",
    )
    require(
        "invoke_scene_repair_for_gate()" in build_video
        and 'REPAIR_DIAG_FILE="${LOG_DIR}/scene_repair_diagnostics.jsonl"' in build_video
        and '"attempt_count": attempt_count' in build_video,
        "build_video.sh does not centralize scene repair invocation diagnostics",
    )
    require(
        "validate_scene_first_pass_with_owner()" in build_video
        and "scene_validator.py" in build_video
        and "--json" in build_video,
        "build_video.sh does not route build_scenes validation through scene_validator.py",
    )
    require(
        "resolve_scene_metadata.py" in build_video,
        "build_video.sh does not resolve build_scenes metadata through the shared resolver",
    )
    for gate in (
        "template_structure",
        "python_syntax",
        "import_api",
        "voiceover_sync",
        "timing_budget",
        "semantic_quality",
        "runtime_dry_run",
    ):
        require(
            gate in build_video or gate in scene_validator,
            f"build_scenes first-pass gate not classified: {gate}",
        )
    require(
        'repair_scene_until_valid "$scene_id" "$scene_file" "$scene_class" "$reason"'
        in build_video,
        "central repair wrapper no longer invokes repair_scene_until_valid",
    )
    require(
        build_video.count("invoke_scene_repair_for_gate") >= 6,
        "scene repair call sites are not routed through the central wrapper",
    )
    for required in (
        "capture_phase_progress_state()",
        "ensure_phase_made_progress()",
        "mark_phase_no_progress()",
        "--history-action phase_no_progress_detected",
    ):
        require(required in build_video, f"build_video.sh missing no-progress sentinel surface: {required}")
    require(
        '[[ "$phase" == "plan" ]] || return 0' in build_video,
        "no-progress sentinel is not scoped to the plan phase first",
    )
    updater = read_text("scripts/update_project_state.py")
    require(
        '"record-error"' in updater and "def record_error(" in updater,
        "update_project_state.py does not own deterministic record-error mutations",
    )
    require(
        "--mode record-error" in build_video,
        "build_video.sh does not use update_project_state.py for selected record-error mutation",
    )


def check_voice_contract() -> None:
    service_factory = read_text("flaming_horse_voice/service_factory.py")
    build_video = read_text("scripts/build_video.sh")
    ensure_voice_cache = read_text("scripts/ensure_voice_cache.py")
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
    require(
        "def check_voice_cache(" in ensure_voice_cache
        and "selected_output_dir(cfg)" in ensure_voice_cache
        and "cache.json" in ensure_voice_cache,
        "ensure_voice_cache.py does not own voice cache readiness",
    )
    require(
        "ensure_voice_cache.py" in build_video
        and "precache_voiceovers_qwen.py" in build_video
        and "voice_cache_index_path()" not in build_video,
        "build_video.sh does not route voice cache readiness through ensure_voice_cache.py",
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


def check_final_render_contract() -> None:
    build_video = read_text("scripts/build_video.sh")
    verify_scene = read_text("scripts/verify_scene_video.py")
    record_scene = read_text("scripts/record_scene_rendered.py")
    require(
        "verify_scene_video.py" in build_video,
        "build_video.sh does not use verify_scene_video.py for final render verification",
    )
    require(
        "record_scene_rendered.py" in build_video,
        "build_video.sh does not use record_scene_rendered.py for rendered scene state",
    )
    require(
        "def verify_scene_video(" in verify_scene and "-select_streams" in verify_scene,
        "verify_scene_video.py does not own scene video/audio verification",
    )
    require(
        "def record_scene_rendered(" in record_scene
        and 's["status"] = "rendered"' not in build_video
        and 'scene["status"] = "rendered"' not in build_video,
        "record_scene_rendered.py does not own rendered scene state recording",
    )


def check_removed_live_surfaces() -> None:
    removed_service = "MLX" + "CachedService"
    removed_module = "flaming_horse_voice" + ".mlx_cached"
    removed_validation_files = [
        REPO_ROOT / "scripts" / "scene_validation.sh",
        REPO_ROOT / "scripts" / "build_video_validation_integration.patch",
    ]
    for path in removed_validation_files:
        require(not path.exists(), f"dead validation surface still exists: {path.name}")

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
    check_first_pass_scene_creation_contract()
    check_voice_contract()
    check_voice_backend_resolution_contract()
    check_final_render_contract()
    check_removed_live_surfaces()
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
