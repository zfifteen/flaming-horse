#!/usr/bin/env python3
"""Deterministic scene validation surface for scaffolded Flaming Horse scenes."""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import subprocess
import sys
import textwrap
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SLOT_START = "# SLOT_START:scene_body"
SLOT_END = "# SLOT_END:scene_body"

REQUIRED_SCAFFOLD_SIGNATURES = [
    "from narration_script import SCRIPT",
    "# LOCKED CONFIGURATION (DO NOT MODIFY)",
    "config.frame_height = 10",
    "config.frame_width = 10 * 16 / 9",
    "config.pixel_height = 1440",
    "config.pixel_width = 2560",
    "self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))",
    SLOT_START,
    SLOT_END,
]

VOICEOVER_SCRIPT_RE = re.compile(
    r"with\s+self\.voiceover\(\s*text\s*=\s*SCRIPT\[[^\]]+\]\s*\)\s+as\s+tracker:"
)


@dataclass
class GateResult:
    gate: str
    ok: bool
    message: str
    details: list[str] | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "gate": self.gate,
            "ok": self.ok,
            "message": self.message,
        }
        if self.details:
            payload["details"] = self.details
        return payload


def _pass(gate: str, message: str, details: list[str] | None = None) -> GateResult:
    return GateResult(gate=gate, ok=True, message=message, details=details)


def _fail(gate: str, message: str, details: list[str] | None = None) -> GateResult:
    return GateResult(gate=gate, ok=False, message=message, details=details)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _extract_scene_body(scene_text: str) -> tuple[str | None, str | None]:
    start_idx = scene_text.find(SLOT_START)
    if start_idx < 0:
        return None, "SLOT_START marker not found"
    end_idx = scene_text.find(SLOT_END, start_idx)
    if end_idx < 0:
        return None, "SLOT_END marker not found"
    if end_idx < start_idx:
        return None, "slot markers are out of order"
    body_start = start_idx + len(SLOT_START)
    return scene_text[body_start:end_idx], None


def validate_template_structure(scene_text: str) -> GateResult:
    missing = [sig for sig in REQUIRED_SCAFFOLD_SIGNATURES if sig not in scene_text]
    if missing:
        return _fail(
            "template_structure",
            f"Scene is missing required scaffold signature: {missing[0]}",
            missing,
        )

    voiceover_count = len(VOICEOVER_SCRIPT_RE.findall(scene_text))
    if voiceover_count < 1:
        return _fail(
            "template_structure",
            "Scene missing required voiceover wrapper using SCRIPT key",
        )
    if voiceover_count > 1:
        return _fail(
            "template_structure",
            f"Scene has nested/duplicate voiceover wrappers ({voiceover_count} found)",
        )

    body, error = _extract_scene_body(scene_text)
    if error:
        return _fail("template_structure", f"Scene has invalid slot marker structure: {error}")
    if body is None:
        return _fail("template_structure", "Scene has invalid slot marker structure")

    return _pass("template_structure", "Template structure checks passed")


def validate_python_syntax(scene_text: str, scene_file: Path) -> GateResult:
    try:
        compile(scene_text, str(scene_file), "exec")
    except SyntaxError as exc:
        return _fail("python_syntax", f"Scene has syntax errors: {exc}")
    return _pass("python_syntax", "Python syntax valid")


def validate_import_api(scene_text: str) -> GateResult:
    if "from manimvoiceoverplus import" in scene_text or "import manimvoiceoverplus" in scene_text:
        return _fail(
            "import_api",
            "Scene uses 'manimvoiceoverplus'; use 'manim_voiceover_plus'",
        )
    if "from manim-voiceover-plus import" in scene_text or "import manim-voiceover-plus" in scene_text:
        return _fail(
            "import_api",
            "Scene uses 'manim-voiceover-plus'; use 'manim_voiceover_plus'",
        )
    if re.search(r"from\s+manim\.utils\.color\s+import\s+Color", scene_text):
        return _fail(
            "import_api",
            "Invalid import 'from manim.utils.color import Color'",
        )
    if re.search(r"FadeIn\([^\n)]*lag_ratio\s*=", scene_text):
        return _fail(
            "import_api",
            "FadeIn(..., lag_ratio=...) is unsupported in this Manim version",
        )
    if re.search(r"FadeIn\([^\n)]*scale_factor\s*=", scene_text):
        return _fail(
            "import_api",
            "FadeIn(..., scale_factor=...) is unsupported in this Manim version",
        )
    if re.search(r"&lt;|&gt;", scene_text):
        return _fail(
            "import_api",
            "Scene contains escaped HTML operators (&lt;/&gt;)",
        )
    if re.search(r"set_color\(\s*list\(", scene_text):
        return _fail(
            "import_api",
            "set_color(list(...)) is invalid for Manim color parsing",
        )
    if re.search(r"set_color\(\s*harmonious_color\(", scene_text):
        return _fail(
            "import_api",
            "set_color(harmonious_color(...)) is invalid without selecting a concrete safe color",
        )
    return _pass("import_api", "Import/API checks passed")


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _attribute_root_name(node: ast.AST) -> str:
    current = node
    while isinstance(current, ast.Attribute):
        current = current.value
    if isinstance(current, ast.Name):
        return current.id
    return ""


def _target_touches_config(target: ast.AST) -> bool:
    return (
        isinstance(target, ast.Name)
        and target.id == "config"
    ) or (
        isinstance(target, ast.Attribute)
        and _attribute_root_name(target) == "config"
    )


def _is_self_voiceover_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "voiceover"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "self"
    )


def _is_tracker_duration(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "duration"
        and isinstance(node.value, ast.Name)
        and node.value.id == "tracker"
    )


def _is_script_subscript(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id == "SCRIPT"
    )


def validate_scene_body_contract(scene_body: str) -> GateResult:
    candidate = textwrap.dedent(scene_body).strip()
    if not candidate:
        return _fail("scene_body_contract", "scene_body cannot be empty")

    body_lines = [
        line.strip()
        for line in candidate.split("\n")
        if line.strip() and not line.strip().startswith("#")
    ]
    if not body_lines:
        return _fail("scene_body_contract", "scene_body must contain a non-comment statement")

    try:
        for token in tokenize.generate_tokens(io.StringIO(candidate).readline):
            if token.type == tokenize.COMMENT:
                return _fail(
                    "scene_body_contract",
                    f"scene_body line {token.start[0]} must not contain comments",
                )
    except tokenize.TokenError as exc:
        return _fail("scene_body_contract", f"scene_body must be valid Python statements: {exc}")

    try:
        tree = ast.parse(candidate)
    except SyntaxError as exc:
        return _fail("scene_body_contract", f"scene_body must be valid Python statements: {exc}")

    forbidden_nodes = (
        ast.Import,
        ast.ImportFrom,
        ast.ClassDef,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
    )
    uses_tracker_duration = False
    for node in ast.walk(tree):
        if isinstance(node, forbidden_nodes):
            return _fail(
                "scene_body_contract",
                "scene_body must not include imports, class definitions, or function definitions",
            )
        if _is_tracker_duration(node):
            uses_tracker_duration = True
        if isinstance(node, ast.Assign) and any(_target_touches_config(t) for t in node.targets):
            return _fail("scene_body_contract", "scene_body must not modify Manim config")
        if isinstance(node, ast.AnnAssign) and _target_touches_config(node.target):
            return _fail("scene_body_contract", "scene_body must not modify Manim config")
        if isinstance(node, ast.AugAssign) and _target_touches_config(node.target):
            return _fail("scene_body_contract", "scene_body must not modify Manim config")
        if isinstance(node, ast.With):
            for item in node.items:
                if _is_self_voiceover_call(item.context_expr):
                    return _fail("scene_body_contract", "scaffold owns the voiceover wrapper")
        if isinstance(node, ast.Name) and node.id == "random":
            return _fail("scene_body_contract", "scene_body must be deterministic and not use random")
        if isinstance(node, ast.Attribute) and (
            node.attr == "random" or _attribute_root_name(node) == "random"
        ):
            return _fail("scene_body_contract", "scene_body must be deterministic and not use random")
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name == "ShowCreation":
            return _fail("scene_body_contract", "Use Create(...) instead of ShowCreation(...)")
        if name == "FadeIn":
            kw_names = {kw.arg for kw in node.keywords if kw.arg}
            if "lag_ratio" in kw_names:
                return _fail(
                    "scene_body_contract",
                    "Use LaggedStart(..., lag_ratio=...) instead of FadeIn(..., lag_ratio=...)",
                )
            if "scale_factor" in kw_names:
                return _fail("scene_body_contract", "FadeIn(..., scale_factor=...) is unsupported")
        if name == "set_color" and node.args:
            first_arg = node.args[0]
            if isinstance(first_arg, ast.Call):
                first_name = _call_name(first_arg.func)
                if first_name == "list":
                    return _fail("scene_body_contract", "set_color(list(...)) is not Manim-compatible")
                if first_name == "harmonious_color":
                    return _fail(
                        "scene_body_contract",
                        "select a concrete Manim-compatible color before set_color(...)",
                    )

    if not uses_tracker_duration:
        return _fail(
            "scene_body_contract",
            "scene_body must use tracker.duration for narration-synced timing",
        )
    return _pass("scene_body_contract", "Scene body contract checks passed")


def validate_voiceover_sync(scene_text: str) -> GateResult:
    try:
        tree = ast.parse(scene_text)
    except SyntaxError as exc:
        return _fail("voiceover_sync", f"Scene has syntax errors: {exc}")

    for node in ast.walk(tree):
        if not _is_self_voiceover_call(node):
            continue
        text_arg = next((kw.value for kw in node.keywords if kw.arg == "text"), None)
        if text_arg is None:
            return _fail("voiceover_sync", "Scene voiceover call must use SCRIPT dictionary text")
        if not _is_script_subscript(text_arg):
            return _fail(
                "voiceover_sync",
                "Scene uses hardcoded narration text instead of SCRIPT dictionary",
            )
    if "tracker.duration" not in scene_text:
        return _fail(
            "voiceover_sync",
            "Scene must use tracker.duration for synchronization",
        )
    if "VoiceoverScene" in scene_text and "get_speech_service" not in scene_text:
        return _fail("voiceover_sync", "Scene missing cached voice service")
    return _pass("voiceover_sync", "Voiceover sync checks passed")


def validate_semantic_quality(scene_text: str) -> GateResult:
    if re.search(r"\{\{[^}]+\}\}", scene_text):
        return _fail(
            "semantic_quality",
            "Scene contains unresolved placeholder tokens",
        )
    if re.search(
        r"box\s*=\s*Rectangle\(\s*width\s*=\s*4(\.0)?,\s*height\s*=\s*2\.4",
        scene_text,
    ):
        return _fail(
            "semantic_quality",
            "Scene contains scaffold demo rectangle animation",
        )
    return _pass("semantic_quality", "Semantic quality validation passed")


def validate_timing_budget(
    scene_file: Path,
    project_dir: Path | None,
    min_ratio: str,
    auto_adjust: bool,
) -> GateResult:
    if project_dir is None:
        return _pass("timing_budget", "Timing budget skipped: project_dir not provided")

    script_path = Path(__file__).resolve().parent / "validate_scene_timing_budget.py"
    cmd = [
        sys.executable,
        str(script_path),
        "--scene-file",
        str(scene_file),
        "--project-dir",
        str(project_dir),
        "--min-ratio",
        min_ratio,
    ]
    if auto_adjust:
        cmd.append("--auto-adjust")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    details = [line for line in (result.stdout + result.stderr).splitlines() if line.strip()]
    if result.returncode == 0:
        return _pass("timing_budget", "Timing budget validation passed", details)
    if result.returncode == 2:
        return _pass("timing_budget", "Timing budget validation indeterminate", details)
    return _fail("timing_budget", "Scene failed deterministic timing budget validation", details)


def validate_scene_file(
    scene_file: Path,
    project_dir: Path | None = None,
    min_timing_ratio: str = "0.90",
    auto_adjust_timing: bool = False,
) -> dict[str, Any]:
    checks: list[GateResult] = []
    try:
        scene_text = _read_text(scene_file)
    except OSError as exc:
        checks.append(_fail("scene_file", f"Scene file could not be read: {exc}"))
        return _result(scene_file, checks)

    for check in (
        validate_template_structure(scene_text),
        validate_python_syntax(scene_text, scene_file),
        validate_import_api(scene_text),
    ):
        checks.append(check)
        if not check.ok:
            return _result(scene_file, checks)

    body, error = _extract_scene_body(scene_text)
    if error or body is None:
        checks.append(_fail("scene_body_contract", error or "Scene body could not be extracted"))
        return _result(scene_file, checks)

    for check in (
        validate_scene_body_contract(body),
        validate_voiceover_sync(scene_text),
        validate_timing_budget(scene_file, project_dir, min_timing_ratio, auto_adjust_timing),
        validate_semantic_quality(scene_text),
    ):
        checks.append(check)
        if not check.ok:
            return _result(scene_file, checks)

    return _result(scene_file, checks)


def _result(scene_file: Path, checks: list[GateResult]) -> dict[str, Any]:
    failed = next((check for check in checks if not check.ok), None)
    return {
        "ok": failed is None,
        "scene_file": str(scene_file),
        "first_failed_gate": failed.gate if failed else None,
        "failure_summary": failed.message if failed else None,
        "checks": [check.as_dict() for check in checks],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a scaffolded Flaming Horse scene.")
    parser.add_argument("--scene-file", required=True, type=Path)
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--min-timing-ratio", default="0.90")
    parser.add_argument("--auto-adjust-timing", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit stable JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    result = validate_scene_file(
        scene_file=args.scene_file,
        project_dir=args.project_dir,
        min_timing_ratio=args.min_timing_ratio,
        auto_adjust_timing=args.auto_adjust_timing,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["ok"] else "FAIL"
        print(f"{status}: {args.scene_file}")
        for check in result["checks"]:
            prefix = "✓" if check["ok"] else "✗"
            print(f"{prefix} {check['gate']}: {check['message']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
