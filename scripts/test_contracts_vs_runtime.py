#!/usr/bin/env python3
"""Sentinel checks for high-impact contract/runtime drift.

This intentionally checks only the active contract surfaces that steer local
agents. It is not a documentation linter.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

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


def check_harness_contract() -> None:
    agents = read_text("AGENTS.md")
    harness_contract = read_text("docs/architecture/HARNESS_CONTRACT.md")
    build_video = read_text("scripts/build_video.sh")
    cli_phases = list(python_assignment("harness_responses/cli.py", "_IMPLEMENTED_PHASES"))

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
        "-m harness " not in build_video and "-m harness\n" not in build_video,
        "build_video.sh still invokes legacy harness",
    )
    require(cli_phases == HARNESS_PHASES, "harness_responses CLI phase list drifted")


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
    check_phase_contract()
    check_scaffold_contract()
    check_voice_contract()
    check_removed_live_surfaces()
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
