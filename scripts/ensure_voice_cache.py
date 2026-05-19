#!/usr/bin/env python3
"""Check Flaming Horse cached voice readiness."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

from tts_backend_config import selected_output_dir


def _result(
    *,
    ok: bool,
    project_dir: Path,
    cache_dir: Path | None = None,
    cache_index: Path | None = None,
    reason: str = "",
) -> dict[str, Any]:
    return {
        "ok": ok,
        "project_dir": str(project_dir),
        "cache_dir": str(cache_dir) if cache_dir is not None else "",
        "cache_index": str(cache_index) if cache_index is not None else "",
        "reason": reason,
    }


def load_voice_config(project_dir: Path) -> dict[str, Any]:
    config_path = project_dir / "voice_clone_config.json"
    if not config_path.exists():
        return {}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"voice_clone_config.json is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("voice_clone_config.json root must be an object")
    return data


def resolve_cache_dir(project_dir: Path, cfg: dict[str, Any]) -> Path:
    output_dir = Path(selected_output_dir(cfg)).expanduser()
    if not output_dir.is_absolute():
        output_dir = project_dir / output_dir
    return output_dir.resolve()


def _cache_text(entry: dict[str, Any]) -> str:
    text = entry.get("text")
    if isinstance(text, str) and text.strip():
        return text.strip()

    input_text = entry.get("input_text")
    if isinstance(input_text, str) and input_text.strip():
        return input_text.strip()

    input_data = entry.get("input_data")
    if isinstance(input_data, dict):
        nested_text = input_data.get("text")
        if isinstance(nested_text, str) and nested_text.strip():
            return nested_text.strip()
    return ""


def _cache_audio_file(entry: dict[str, Any]) -> str:
    for key in ("audio_file", "final_audio", "original_audio"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _load_script(script_path: Path) -> dict[str, str]:
    if not script_path.exists():
        raise ValueError(f"narration_script.py missing: {script_path}")
    try:
        tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=str(script_path))
    except (OSError, SyntaxError, ValueError) as exc:
        raise ValueError(f"narration_script.py could not be parsed: {exc}") from exc

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "SCRIPT":
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, TypeError) as exc:
                    raise ValueError("narration_script.py SCRIPT must be a literal dict") from exc
                if not isinstance(value, dict):
                    raise ValueError("narration_script.py SCRIPT must be a dict")
                result: dict[str, str] = {}
                for key, text in value.items():
                    if isinstance(key, str) and isinstance(text, str) and key.strip():
                        result[key] = text
                if not result:
                    raise ValueError("narration_script.py SCRIPT has no usable entries")
                return result
    raise ValueError("narration_script.py does not define SCRIPT")


def _normalize_text(text: str) -> str:
    return " ".join(str(text).split())


def _validate_cache_entries(
    cache_dir: Path,
    cache_data: list[Any],
    required_script: dict[str, str],
) -> str:
    if not cache_data:
        return "cache index contains no entries"

    key_index: dict[str, str] = {}
    text_index: dict[str, str] = {}
    for index, entry in enumerate(cache_data):
        if not isinstance(entry, dict):
            return f"cache entry {index} must be an object"

        narration_key = entry.get("narration_key")
        has_narration_key = isinstance(narration_key, str) and bool(narration_key.strip())
        has_text = bool(_cache_text(entry))
        audio_file = _cache_audio_file(entry)

        if not audio_file:
            return f"cache entry {index} has no audio file"
        if not has_narration_key and not has_text:
            return f"cache entry {index} has neither narration_key nor text"
        if not (cache_dir / audio_file).exists():
            return f"cache entry {index} audio file missing: {audio_file}"

        if has_narration_key:
            key_index[str(narration_key).strip()] = audio_file
        text = _cache_text(entry)
        if text:
            text_index[_normalize_text(text)] = audio_file

    if not key_index and not text_index:
        return "cache index contains no usable entries"

    missing = []
    for key, text in required_script.items():
        if key in key_index:
            continue
        if _normalize_text(text) in text_index:
            continue
        missing.append(key)
    if missing:
        return "cache missing required narration key: " + missing[0]
    return ""


def check_voice_cache(project_dir: Path) -> dict[str, Any]:
    project_dir = project_dir.resolve()
    try:
        cfg = load_voice_config(project_dir)
        cache_dir = resolve_cache_dir(project_dir, cfg)
    except ValueError as exc:
        return _result(ok=False, project_dir=project_dir, reason=str(exc))

    cache_index = cache_dir / "cache.json"
    if not cache_index.exists():
        return _result(
            ok=False,
            project_dir=project_dir,
            cache_dir=cache_dir,
            cache_index=cache_index,
            reason="cache index missing",
        )

    try:
        cache_data = json.loads(cache_index.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return _result(
            ok=False,
            project_dir=project_dir,
            cache_dir=cache_dir,
            cache_index=cache_index,
            reason=f"cache index is not valid JSON: {exc}",
        )
    if not isinstance(cache_data, list):
        return _result(
            ok=False,
            project_dir=project_dir,
            cache_dir=cache_dir,
            cache_index=cache_index,
            reason="cache index root must be a list",
        )
    try:
        required_script = _load_script(project_dir / "narration_script.py")
    except ValueError as exc:
        return _result(
            ok=False,
            project_dir=project_dir,
            cache_dir=cache_dir,
            cache_index=cache_index,
            reason=str(exc),
        )

    entry_error = _validate_cache_entries(cache_dir, cache_data, required_script)
    if entry_error:
        return _result(
            ok=False,
            project_dir=project_dir,
            cache_dir=cache_dir,
            cache_index=cache_index,
            reason=entry_error,
        )

    return _result(
        ok=True,
        project_dir=project_dir,
        cache_dir=cache_dir,
        cache_index=cache_index,
        reason="voice cache ready",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="check cache readiness")
    parser.add_argument("--json", action="store_true", help="emit JSON result")
    args = parser.parse_args()

    if not args.check:
        parser.error("--check is required")

    result = check_voice_cache(args.project_dir)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["ok"]:
        print(f"Voice cache ready: {result['cache_index']}")
    else:
        print(f"Voice cache not ready: {result['reason']}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
