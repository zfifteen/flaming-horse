#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_TOOL = REPO_ROOT / "scripts" / "update_project_state.py"
STATE_SCHEMA = REPO_ROOT / "scripts" / "state_schema.json"


def _canonical_phases() -> list[str]:
    out = subprocess.check_output(
        ["python3", str(STATE_TOOL), "--print-phases"],
        cwd=REPO_ROOT,
        text=True,
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def test_state_schema_phase_enum_matches_canonical_source() -> None:
    expected = _canonical_phases()
    schema = json.loads(STATE_SCHEMA.read_text(encoding="utf-8"))
    actual = schema["properties"]["phase"]["enum"]
    assert actual == expected
