#!/usr/bin/env python3
"""Validate projected scene timing against narration duration budget.

This script performs a deterministic static analysis over scene code:
- sums explicit `self.play(..., run_time=...)` terms
- sums explicit `self.wait(...)` terms (`self.wait()` defaults to 1.0s)
- compares projected scene duration against cached narration duration

Exit codes:
- 0: pass (projected ratio >= threshold)
- 1: fail (definitive projected ratio below threshold)
- 2: indeterminate (insufficient data to make a definitive decision)
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional


@dataclass
class TimingTerm:
    kind: str
    lineno: int
    expr_text: str
    value: Optional[float]
    multiplier: int = 1


def _read_cache_entries(cache_data: Any) -> Iterable[dict[str, Any]]:
    if isinstance(cache_data, list):
        for item in cache_data:
            if isinstance(item, dict):
                yield item
        return

    if isinstance(cache_data, dict):
        candidates = ("entries", "items", "cache", "voiceovers", "data")
        for key in candidates:
            value = cache_data.get(key)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        yield item


def _duration_from_cache(project_dir: Path, scene_id: str) -> Optional[float]:
    cache_path = project_dir / "media" / "voiceovers" / "qwen" / "cache.json"
    if not cache_path.exists():
        print(f"[timing-budget] WARN: cache index missing: {cache_path}")
        return None

    try:
        raw = json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[timing-budget] WARN: failed to parse cache index: {exc}")
        return None

    for entry in _read_cache_entries(raw):
        key = entry.get("narration_key") or entry.get("key") or entry.get("scene_id")
        if str(key) != scene_id:
            continue
        duration = entry.get("duration_seconds") or entry.get("duration")
        if isinstance(duration, (int, float)) and duration > 0:
            return float(duration)
        try:
            maybe = float(duration)
            if maybe > 0:
                return maybe
        except Exception:
            pass
    return None


def _expr_text(source: str, node: ast.AST) -> str:
    seg = ast.get_source_segment(source, node)
    return (seg or "<expr>").strip()


def _safe_eval(node: ast.AST, tracker_duration: float) -> Optional[float]:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.Name):
        if node.id == "tracker_duration":
            return tracker_duration
        return None

    if isinstance(node, ast.Attribute):
        if isinstance(node.value, ast.Name) and node.value.id == "tracker" and node.attr == "duration":
            return tracker_duration
        return None

    if isinstance(node, ast.UnaryOp):
        val = _safe_eval(node.operand, tracker_duration)
        if val is None:
            return None
        if isinstance(node.op, ast.UAdd):
            return +val
        if isinstance(node.op, ast.USub):
            return -val
        return None

    if isinstance(node, ast.BinOp):
        left = _safe_eval(node.left, tracker_duration)
        right = _safe_eval(node.right, tracker_duration)
        if left is None or right is None:
            return None
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                return None
            return left / right
        if isinstance(node.op, ast.Pow):
            return left**right
        return None

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            return None
        if node.func.id == "min":
            values = [_safe_eval(arg, tracker_duration) for arg in node.args]
            if not values or any(v is None for v in values):
                return None
            return min(values)
        if node.func.id == "max":
            values = [_safe_eval(arg, tracker_duration) for arg in node.args]
            if not values or any(v is None for v in values):
                return None
            return max(values)
        return None

    return None


def _collect_timing_terms(scene_source: str, tracker_duration: float) -> list[TimingTerm]:
    tree = ast.parse(scene_source)
    terms: list[TimingTerm] = []
    default_play_seconds = 1.0

    def _range_iteration_count(iter_node: ast.AST) -> Optional[int]:
        if not isinstance(iter_node, ast.Call):
            return None
        if not isinstance(iter_node.func, ast.Name) or iter_node.func.id != "range":
            return None

        values: list[int] = []
        for arg in iter_node.args:
            val = _safe_eval(arg, tracker_duration)
            if val is None:
                return None
            as_int = int(val)
            if float(as_int) != float(val):
                return None
            values.append(as_int)

        if len(values) == 1:
            start, stop, step = 0, values[0], 1
        elif len(values) == 2:
            start, stop, step = values[0], values[1], 1
        elif len(values) == 3:
            start, stop, step = values[0], values[1], values[2]
        else:
            return None

        if step == 0:
            return None
        return len(range(start, stop, step))

    def _visit(node: ast.AST, multiplier: int = 1) -> None:
        if isinstance(node, ast.For):
            loop_count = _range_iteration_count(node.iter)
            loop_multiplier = multiplier * loop_count if loop_count is not None else multiplier
            for child in node.body:
                _visit(child, loop_multiplier)
            for child in node.orelse:
                _visit(child, multiplier)
            return

        if isinstance(node, ast.Call):
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "self"
            ):
                if node.func.attr == "play":
                    has_run_time = False
                    for kw in node.keywords:
                        if kw.arg != "run_time":
                            continue
                        has_run_time = True
                        value = _safe_eval(kw.value, tracker_duration)
                        terms.append(
                            TimingTerm(
                                kind="run_time",
                                lineno=getattr(kw.value, "lineno", getattr(node, "lineno", 0)),
                                expr_text=_expr_text(scene_source, kw.value),
                                value=value * multiplier if value is not None else None,
                                multiplier=multiplier,
                            )
                        )
                    if not has_run_time:
                        terms.append(
                            TimingTerm(
                                kind="play_default",
                                lineno=getattr(node, "lineno", 0),
                                expr_text="(default play run_time)",
                                value=default_play_seconds * multiplier,
                                multiplier=multiplier,
                            )
                        )

                if node.func.attr == "wait":
                    if node.args:
                        expr_node = node.args[0]
                        value = _safe_eval(expr_node, tracker_duration)
                        terms.append(
                            TimingTerm(
                                kind="wait",
                                lineno=getattr(expr_node, "lineno", getattr(node, "lineno", 0)),
                                expr_text=_expr_text(scene_source, expr_node),
                                value=value * multiplier if value is not None else None,
                                multiplier=multiplier,
                            )
                        )
                    else:
                        terms.append(
                            TimingTerm(
                                kind="wait",
                                lineno=getattr(node, "lineno", 0),
                                expr_text="(default wait)",
                                value=1.0 * multiplier,
                                multiplier=multiplier,
                            )
                        )

        for child in ast.iter_child_nodes(node):
            _visit(child, multiplier)

    _visit(tree, 1)
    return sorted(terms, key=lambda t: t.lineno)


def _scene_id_from_path(scene_path: Path) -> str:
    scene_id = scene_path.stem
    scene_id = re.sub(r"[^a-zA-Z0-9_]+", "", scene_id)
    return scene_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene-file", required=True)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--min-ratio", type=float, default=0.90)
    args = parser.parse_args()

    scene_file = Path(args.scene_file).resolve()
    project_dir = Path(args.project_dir).resolve()
    scene_id = _scene_id_from_path(scene_file)

    if not scene_file.exists():
        print(f"[timing-budget] WARN: scene file missing: {scene_file}")
        return 2

    narration_duration = _duration_from_cache(project_dir, scene_id)
    if narration_duration is None:
        print(f"[timing-budget] WARN: no narration duration found for {scene_id}")
        return 2

    source = scene_file.read_text(encoding="utf-8")
    terms = _collect_timing_terms(source, narration_duration)

    known_terms = [term for term in terms if term.value is not None]
    unknown_terms = [term for term in terms if term.value is None]
    projected = sum(term.value for term in known_terms if term.value is not None)

    if projected <= 0:
        print(f"[timing-budget] WARN: no explicit timing terms found in {scene_file.name}")
        return 2

    ratio = narration_duration / projected if projected > 0 else 0.0
    print(
        f"[timing-budget] scene={scene_id} narration={narration_duration:.2f}s "
        f"projected={projected:.2f}s ratio={ratio:.3f} threshold={args.min_ratio:.2f}"
    )

    if unknown_terms:
        print("[timing-budget] WARN: unparsed timing expressions:")
        for term in unknown_terms:
            print(f"  - line {term.lineno}: {term.kind}={term.expr_text}")

    if ratio < args.min_ratio:
        print("[timing-budget] FAIL: projected timing exceeds narration budget")
        print("[timing-budget] Offending terms:")
        for term in known_terms:
            if term.value is None:
                continue
            mult = f" ({term.multiplier}x)" if term.multiplier > 1 else ""
            print(f"  - line {term.lineno}: {term.kind}={term.expr_text}{mult} -> {term.value:.2f}s")
        return 1

    if unknown_terms:
        print("[timing-budget] WARN: budget may be incomplete due to unparsed terms")
        return 2

    print("[timing-budget] PASS: projected timing budget is compliant")
    return 0


if __name__ == "__main__":
    sys.exit(main())
