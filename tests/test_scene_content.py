import pytest
import re
import json
from pathlib import Path

# Test functions for scene content validation


def test_no_planning_text_in_scenes(project_dir):
    """Fail if scene files contain text derived from plan.json narrative_beats instead of narration_script.py"""
    project_path = Path(project_dir)
    state_file = project_path / "project_state.json"
    with open(state_file) as f:
        state = json.load(f)

    for scene in state["scenes"]:
        scene_file = project_path / scene["file"]
        with open(scene_file) as f:
            content = f.read()
        # Check for hardcoded text that might be from plan.json (simple heuristic: long strings not SCRIPT)
        # This is a basic check; in practice, scenes should use SCRIPT["key"]
        matches = re.findall(r'Text\("([^"]{20,})"', content)  # Long hardcoded strings
        for match in matches:
            if re.search(r"\b(explain|describe|show|pause|deliver)\b", match, re.I):
                pytest.fail(f"Planning text detected in {scene_file}: '{match}'")


def test_horizontal_bounds(project_dir):
    """Fail if elements positioned outside LEFT * 3.5 to RIGHT * 3.5"""
    project_path = Path(project_dir)
    state_file = project_path / "project_state.json"
    with open(state_file) as f:
        state = json.load(f)

    for scene in state["scenes"]:
        scene_file = project_path / scene["file"]
        with open(scene_file) as f:
            content = f.read()
        # Check for positions like LEFT * 4.8 or RIGHT * 4.0
        if re.search(r"LEFT \* [4-9]\.[0-9]+|RIGHT \* [4-9]\.[0-9]+", content):
            pytest.fail(f"Horizontal bound violation in {scene_file}")
        # Ensure set_max_width(6.0) is used for Text elements
        text_lines = [
            line
            for line in content.split("\n")
            if "Text(" in line and ".set_max_width" not in line
        ]
        if text_lines:
            pytest.fail(f"Text elements without set_max_width in {scene_file}")


def test_stage_direction_blacklist(project_dir):
    """Fail if bullet text contains stage directions like 'Deliver', 'Pause for', 'Transition to'"""
    project_path = Path(project_dir)
    state_file = project_path / "project_state.json"
    with open(state_file) as f:
        state = json.load(f)

    patterns = [r"^Deliver\b", r"^Pause for\b", r"^Transition to\b"]
    for scene in state["scenes"]:
        scene_file = project_path / scene["file"]
        with open(scene_file) as f:
            content = f.read()
        # Extract bullet text (heuristic: Text("{{{KEY_POINT_")
        bullets = re.findall(r'Text\("{{{{KEY_POINT_[0-9]+}}}}"', content)
        for bullet in bullets:
            for pattern in patterns:
                if re.search(pattern, bullet, re.I):
                    pytest.fail(
                        f"Stage direction in bullet: '{bullet}' in {scene_file}"
                    )


def test_no_runtime_passed_to_play_next(project_dir):
    """Fail if run_time= is passed to play_next or play_text_next"""
    project_path = Path(project_dir)
    state_file = project_path / "project_state.json"
    with open(state_file) as f:
        state = json.load(f)

    for scene in state["scenes"]:
        scene_file = project_path / scene["file"]
        with open(scene_file) as f:
            content = f.read()
        if re.search(r"play_next\([^)]*run_time\s*=", content) or re.search(
            r"play_text_next\([^)]*run_time\s*=", content
        ):
            pytest.fail(f"run_time passed to slot helper in {scene_file}")


def test_no_long_waits(project_dir):
    """Fail if self.wait(x) with x > 1.0"""
    project_path = Path(project_dir)
    state_file = project_path / "project_state.json"
    with open(state_file) as f:
        state = json.load(f)

    for scene in state["scenes"]:
        scene_file = project_path / scene["file"]
        with open(scene_file) as f:
            content = f.read()
        waits = re.findall(r"self\.wait\(([0-9.]+)\)", content)
        for wait in waits:
            if float(wait) > 1.0:
                pytest.fail(f"Long wait {wait}s in {scene_file}")
