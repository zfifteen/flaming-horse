#!/usr/bin/env python3
"""Live contract check for the Flaming Horse Grok CLI backend."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MINIMUM_VERSION = (0, 1, 212)
DEFAULT_MODEL = "grok-build"
REQUIRED_FLAGS = [
    "--cwd",
    "--sandbox",
    "--prompt-file",
    "--output-format",
    "--no-subagents",
    "--disable-web-search",
    "--max-turns",
    "--permission-mode",
    "--always-approve",
    "--no-memory",
    "--model",
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def resolve_grok() -> str:
    configured = os.getenv("GROK_CLI", "").strip()
    if configured:
        path = Path(os.path.expanduser(configured))
        if not path.exists():
            fail(f"GROK_CLI path does not exist: {configured}")
        if not path.is_file():
            fail(f"GROK_CLI is not a file: {configured}")
        if not os.access(path, os.X_OK):
            fail(f"GROK_CLI is not executable: {configured}")
        return str(path)
    discovered = shutil.which("grok")
    if not discovered:
        fail("grok CLI not found")
    return discovered


def run_command(cmd: list[str], *, cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def parse_version(text: str) -> tuple[int, int, int]:
    match = re.search(r"\bgrok\s+(\d+)\.(\d+)\.(\d+)\b", text)
    if not match:
        fail(f"Could not parse grok version from: {text.strip()}")
    return tuple(int(part) for part in match.groups())


def check_help(grok: str) -> str:
    result = run_command([grok, "--help"], cwd=REPO_ROOT)
    if result.returncode != 0:
        fail(f"grok --help failed:\n{result.stderr or result.stdout}")
    help_text = result.stdout + result.stderr
    for flag in REQUIRED_FLAGS:
        if flag not in help_text:
            fail(f"required Grok CLI flag missing from --help: {flag}")
    for value in ("json", "bypassPermissions"):
        if value not in help_text:
            fail(f"required Grok CLI option value missing from --help: {value}")
    return help_text


def check_version(grok: str) -> str:
    result = run_command([grok, "--version"], cwd=REPO_ROOT)
    if result.returncode != 0:
        fail(f"grok --version failed:\n{result.stderr or result.stdout}")
    version_text = result.stdout + result.stderr
    parsed = parse_version(version_text)
    if parsed < MINIMUM_VERSION:
        fail(
            "grok version is older than the Flaming Horse contract: "
            f"{parsed} < {MINIMUM_VERSION}"
        )
    return version_text.strip()


def check_models(grok: str) -> None:
    result = run_command([grok, "models"], cwd=REPO_ROOT)
    output = result.stdout + result.stderr
    if result.returncode != 0:
        fail(f"grok models failed. Run `grok login`.\n{output}")
    if DEFAULT_MODEL not in output:
        fail(f"grok models did not list required model {DEFAULT_MODEL!r}.\n{output}")


def check_staged_json_write(grok: str) -> None:
    with tempfile.TemporaryDirectory(prefix=".grok_contract_", dir=REPO_ROOT) as tmp:
        root = Path(tmp)
        project_dir = root / "project"
        log_dir = root / "log"
        project_dir.mkdir()
        log_dir.mkdir()
        marker_path = project_dir / "read_marker.txt"
        marker_text = "flaming-horse-grok-read-contract"
        marker_path.write_text(marker_text, encoding="utf-8")
        prompt_path = log_dir / "prompt.md"
        staged_path = log_dir / "staged.json"
        prompt_path.write_text(
            "\n".join(
                [
                    "Write exactly one JSON object to this staged response file:",
                    str(staged_path),
                    "Before writing, read this project file:",
                    str(marker_path),
                    'The JSON object must be {"ok": true, "marker": "<file contents>"} where marker is the exact project-file content.',
                    "Do not write markdown, code fences, or prose to the file.",
                    "Do not create or edit any other files.",
                    "When finished, print only the staged response file path.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        cmd = [
            grok,
            "--cwd",
            str(log_dir),
            "--sandbox",
            "workspace",
            "--prompt-file",
            str(prompt_path),
            "--output-format",
            "json",
            "--no-subagents",
            "--disable-web-search",
            "--max-turns",
            "1",
            "--permission-mode",
            "bypassPermissions",
            "--always-approve",
            "--no-memory",
            "--model",
            DEFAULT_MODEL,
        ]
        result = run_command(cmd, cwd=log_dir)
        if result.returncode != 0:
            fail(f"staged JSON smoke failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        if not staged_path.exists():
            fail("Grok CLI exited successfully but did not write staged JSON")
        payload = json.loads(staged_path.read_text(encoding="utf-8"))
        if payload != {"ok": True, "marker": marker_text}:
            fail(f"unexpected staged JSON payload: {payload!r}")


def main() -> int:
    grok = resolve_grok()
    check_help(grok)
    version_text = check_version(grok)
    check_models(grok)
    check_staged_json_write(grok)
    print(f"OK: Grok CLI contract verified ({version_text}, model {DEFAULT_MODEL})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
