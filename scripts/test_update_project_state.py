#!/usr/bin/env python3
"""Basic correctness tests for scripts/update_project_state.py.

Run:
  python3 scripts/test_update_project_state.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
UPDATER = REPO_ROOT / "scripts" / "update_project_state.py"


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(UPDATER), *args],
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=True,
    )


def read_state(project_dir: Path) -> dict:
    return json.loads((project_dir / "project_state.json").read_text(encoding="utf-8"))


def write_state_raw(project_dir: Path, text: str) -> None:
    (project_dir / "project_state.json").write_text(text, encoding="utf-8")


def require(condition: bool, msg: str) -> None:
    if not condition:
        raise AssertionError(msg)


def make_project_dir(tmp: Path) -> Path:
    project_dir = tmp / "proj"
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def test_normalize_repairs_trailing_garbage() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        project_dir = make_project_dir(tmp)
        write_state_raw(
            project_dir,
            '{"project_name":"x","phase":"plan","created_at":"t","updated_at":"t","run_count":0,"scenes":[],"current_scene_index":0,"errors":[],"history":[],"flags":{"needs_human_review":false,"dry_run":false,"force_replan":false}}\nGARBAGE\n',
        )
        cp = run("--project-dir", str(project_dir), "--mode", "normalize")
        require(cp.returncode == 0, f"normalize failed: {cp.stderr}")
        state = read_state(project_dir)
        require(isinstance(state, dict), "state must be dict")
        require("flags" in state and isinstance(state["flags"], dict), "flags missing")
        require(state["phase"] == "plan", "phase changed unexpectedly")


def test_normalize_restores_missing_flags() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        project_dir = make_project_dir(tmp)
        write_state_raw(
            project_dir,
            '{"project_name":"x","phase":"plan","created_at":"t","updated_at":"t","run_count":0,"scenes":[],"current_scene_index":0,"errors":[],"history":[]}',
        )
        cp = run("--project-dir", str(project_dir), "--mode", "normalize")
        require(cp.returncode == 0, f"normalize failed: {cp.stderr}")
        state = read_state(project_dir)
        require(state["flags"]["needs_human_review"] is False, "default flags missing")


def test_apply_plan_reads_plan_json() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        project_dir = make_project_dir(tmp)
        # Minimal state
        write_state_raw(
            project_dir,
            json.dumps(
                {
                    "project_name": "x",
                    "topic": "t",
                    "phase": "plan",
                    "created_at": "t",
                    "updated_at": "t",
                    "run_count": 0,
                    "plan_file": None,
                    "narration_file": None,
                    "voice_config_file": None,
                    "scenes": [],
                    "current_scene_index": 0,
                    "errors": [],
                    "history": [],
                    "flags": {
                        "needs_human_review": False,
                        "dry_run": False,
                        "force_replan": False,
                    },
                },
                indent=2,
            ),
        )
        (project_dir / "plan.json").write_text(
            json.dumps(
                {
                    "title": "Vid",
                    "topic_summary": "s",
                    "target_audience": "a",
                    "estimated_duration_seconds": 10,
                    "total_estimated_words": 20,
                    "scenes": [
                        {
                            "id": "scene_01_intro",
                            "title": "Intro",
                            "narration_key": "intro",
                            "narration_summary": "x",
                            "estimated_words": 10,
                            "estimated_duration": "4s",
                            "animations": [],
                            "complexity": "low",
                            "risk_flags": [],
                        }
                    ],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        cp = run(
            "--project-dir",
            str(project_dir),
            "--mode",
            "apply",
            "--phase",
            "plan",
        )
        require(cp.returncode == 0, f"apply plan failed: {cp.stderr}")
        state = read_state(project_dir)
        require(state["phase"] == "review", "plan should advance to review")
        require(len(state["scenes"]) == 1, "scenes not populated")
        require(
            state["scenes"][0]["id"] == "scene_01",
            "scene id should be script-generated, not LLM-provided",
        )
        require(
            state["scenes"][0]["narration_key"] == "scene_01",
            "narration key should be script-generated, not LLM-provided",
        )
        require(
            state["scenes"][0]["status"] == "pending", "scene status should be pending"
        )


def test_apply_build_scenes_marks_built() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        project_dir = make_project_dir(tmp)

        # State with one pending scene
        write_state_raw(
            project_dir,
            json.dumps(
                {
                    "project_name": "x",
                    "topic": "t",
                    "phase": "build_scenes",
                    "created_at": "t",
                    "updated_at": "t",
                    "run_count": 0,
                    "plan_file": "plan.json",
                    "narration_file": "narration_script.py",
                    "voice_config_file": None,
                    "scenes": [
                        {
                            "id": "scene_01_intro",
                            "title": "Intro",
                            "narration_key": "intro",
                            "narration_summary": "",
                            "estimated_words": 0,
                            "estimated_duration": "1s",
                            "animations": [],
                            "complexity": "low",
                            "risk_flags": [],
                            "status": "pending",
                        }
                    ],
                    "current_scene_index": 0,
                    "errors": [
                        "build_scenes incomplete: expected scene_01_intro.py not found",
                    ],
                    "history": [],
                    "flags": {
                        "needs_human_review": False,
                        "dry_run": False,
                        "force_replan": False,
                    },
                },
                indent=2,
            ),
        )

        # Minimal scene file with VoiceoverScene class
        (project_dir / "scene_01_intro.py").write_text(
            "from manim_voiceover_plus import VoiceoverScene\n\nclass Scene01Intro(VoiceoverScene):\n    def construct(self):\n        pass\n",
            encoding="utf-8",
        )

        cp = run(
            "--project-dir",
            str(project_dir),
            "--mode",
            "apply",
            "--phase",
            "build_scenes",
        )
        require(cp.returncode == 0, f"apply build_scenes failed: {cp.stderr}")
        state = read_state(project_dir)
        require(state["scenes"][0]["status"] == "built", "scene not marked built")
        require(
            state["scenes"][0]["class_name"] == "Scene01Intro",
            "class_name not inferred",
        )
        require(
            state["phase"] == "scene_qc",
            "single scene should advance to scene_qc",
        )
        require(
            "build_scenes incomplete: expected scene_01_intro.py not found"
            not in state["errors"],
            "stale build_scenes incomplete error not cleared",
        )


def test_apply_narration_stays_when_script_missing_scene_keys() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        project_dir = make_project_dir(tmp)

        write_state_raw(
            project_dir,
            json.dumps(
                {
                    "project_name": "x",
                    "topic": "t",
                    "phase": "narration",
                    "created_at": "t",
                    "updated_at": "t",
                    "run_count": 0,
                    "plan_file": "plan.json",
                    "narration_file": None,
                    "voice_config_file": None,
                    "scenes": [
                        {"id": "scene_01", "title": "One", "narration_key": "scene_01"},
                        {"id": "scene_02", "title": "Two", "narration_key": "scene_02"},
                    ],
                    "current_scene_index": 0,
                    "errors": [],
                    "history": [],
                    "flags": {
                        "needs_human_review": False,
                        "dry_run": False,
                        "force_replan": False,
                    },
                },
                indent=2,
            ),
        )
        (project_dir / "narration_script.py").write_text(
            'SCRIPT = {"scene_01": "hello"}\n', encoding="utf-8"
        )

        cp = run(
            "--project-dir",
            str(project_dir),
            "--mode",
            "apply",
            "--phase",
            "narration",
        )
        require(cp.returncode == 0, f"apply narration failed: {cp.stderr}")
        state = read_state(project_dir)
        require(state["phase"] == "narration", "phase should remain narration")
        require(
            state["flags"]["needs_human_review"] is False,
            "missing narration keys should be retryable",
        )
        require(
            any(
                isinstance(err, str)
                and err.startswith("narration failed: missing SCRIPT entries")
                for err in state["errors"]
            ),
            "missing key error should be recorded",
        )


def test_apply_narration_advances_when_script_has_all_scene_keys() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        project_dir = make_project_dir(tmp)

        write_state_raw(
            project_dir,
            json.dumps(
                {
                    "project_name": "x",
                    "topic": "t",
                    "phase": "narration",
                    "created_at": "t",
                    "updated_at": "t",
                    "run_count": 0,
                    "plan_file": "plan.json",
                    "narration_file": None,
                    "voice_config_file": None,
                    "scenes": [
                        {"id": "scene_01", "title": "One", "narration_key": "scene_01"},
                        {"id": "scene_02", "title": "Two", "narration_key": "scene_02"},
                    ],
                    "current_scene_index": 0,
                    "errors": ["narration failed: missing SCRIPT entries for keys: scene_02"],
                    "history": [],
                    "flags": {
                        "needs_human_review": True,
                        "dry_run": False,
                        "force_replan": False,
                    },
                },
                indent=2,
            ),
        )
        (project_dir / "narration_script.py").write_text(
            'SCRIPT = {"scene_01": "hello", "scene_02": "world"}\n', encoding="utf-8"
        )

        cp = run(
            "--project-dir",
            str(project_dir),
            "--mode",
            "apply",
            "--phase",
            "narration",
        )
        require(cp.returncode == 0, f"apply narration failed: {cp.stderr}")
        state = read_state(project_dir)
        require(state["phase"] == "build_scenes", "narration should advance to build_scenes")
        require(
            state["narration_file"] == "narration_script.py",
            "narration_file should be set",
        )
        require(
            state["flags"]["needs_human_review"] is False,
            "successful narration should clear human review flag",
        )
        require(
            not any(
                isinstance(err, str) and err.startswith("narration failed:")
                for err in state["errors"]
            ),
            "narration failure errors should be cleared after success",
        )


def main() -> int:
    require(UPDATER.exists(), f"missing: {UPDATER}")

    tests = [
        test_normalize_repairs_trailing_garbage,
        test_normalize_restores_missing_flags,
        test_apply_plan_reads_plan_json,
        test_apply_build_scenes_marks_built,
        test_apply_narration_stays_when_script_missing_scene_keys,
        test_apply_narration_advances_when_script_has_all_scene_keys,
    ]

    for t in tests:
        t()

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
