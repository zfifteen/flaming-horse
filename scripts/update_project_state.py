#!/usr/bin/env python3
"""Deterministic project_state.json management.

This script is the single authority for reading, repairing, normalizing, and
advancing a project's state. It exists because the LLM agent occasionally
produces malformed JSON edits.

Design goals:
- Always produce valid JSON.
- Always include required top-level fields (including `flags`).
- Never rely on an agent to edit project_state.json correctly.
- Advance phases deterministically based on generated artifacts.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


VALID_PHASES = {
    "init",
    "plan",
    "review",
    "training",
    "narration",
    "build_scenes",
    "precache_voiceovers",
    "final_render",
    "assemble",
    "complete",
    "error",
}

SCENE_ID_RE = re.compile(r"^scene_(\d{2})_([a-z0-9_]+)$")


def _add_error_unique(state: dict, msg: str) -> None:
    errors = state.setdefault("errors", [])
    if not isinstance(errors, list):
        state["errors"] = errors = []
    if msg not in errors:
        errors.append(msg)


def _clear_errors_matching(state: dict, predicate) -> None:
    errors = state.get("errors")
    if not isinstance(errors, list) or not errors:
        return
    state["errors"] = [e for e in errors if not (isinstance(e, str) and predicate(e))]


def utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_str(x: Any) -> str | None:
    if x is None:
        return None
    if isinstance(x, str):
        return x
    return str(x)


def _ensure_list(x: Any) -> list:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def _ensure_dict(x: Any) -> dict:
    if x is None:
        return {}
    if isinstance(x, dict):
        return x
    return {}


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    slug = re.sub(r"_+", "_", slug)
    return slug


def _canonical_scene_id(
    index: int,
    title: str,
    raw_id: str | None,
    used_ids: set[str],
) -> str:
    slug = ""
    if isinstance(raw_id, str):
        m = SCENE_ID_RE.match(raw_id)
        if m:
            slug = m.group(2)

    if not slug:
        slug = _slugify(title)
    if not slug and isinstance(raw_id, str):
        slug = _slugify(raw_id)
    if not slug:
        slug = "scene"

    base = f"scene_{index:02d}_{slug}"
    candidate = base
    suffix = 2
    while candidate in used_ids:
        candidate = f"{base}_{suffix}"
        suffix += 1

    used_ids.add(candidate)
    return candidate


def read_json_best_effort(path: Path) -> dict:
    """Read JSON; if trailing garbage exists, parse first JSON object."""
    raw = path.read_text(encoding="utf-8")
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
        return {}
    except json.JSONDecodeError:
        pass

    # Try: locate first '{' and decode a single JSON value.
    start = raw.find("{")
    if start < 0:
        return {}
    try:
        obj, _end = json.JSONDecoder().raw_decode(raw[start:])
    except json.JSONDecodeError:
        return {}
    return obj if isinstance(obj, dict) else {}


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def normalize_state(project_dir: Path, state: dict) -> dict:
    """Coerce state to the required schema, dropping unknown garbage."""
    project_name = _safe_str(state.get("project_name"))
    if not project_name:
        project_name = project_dir.name

    topic = state.get("topic", None)
    if topic is not None and not isinstance(topic, str):
        topic = _safe_str(topic)

    phase = _safe_str(state.get("phase")) or "plan"
    if phase not in VALID_PHASES:
        phase = "plan"

    created_at = _safe_str(state.get("created_at")) or utc_now()
    updated_at = _safe_str(state.get("updated_at")) or utc_now()

    run_count = state.get("run_count", 0)
    try:
        run_count = int(run_count)
    except Exception:
        run_count = 0

    flags_in = _ensure_dict(state.get("flags"))
    flags = {
        "needs_human_review": bool(flags_in.get("needs_human_review", False)),
        "dry_run": bool(flags_in.get("dry_run", False)),
        "force_replan": bool(flags_in.get("force_replan", False)),
    }

    scenes_in = state.get("scenes")
    scenes_list = scenes_in if isinstance(scenes_in, list) else []
    scenes: list[dict] = []
    for s in scenes_list:
        if not isinstance(s, dict):
            continue
        scene_id = _safe_str(s.get("id"))
        if not scene_id:
            continue
        scene = {
            "id": scene_id,
            "title": _safe_str(s.get("title")) or scene_id,
            "narration_key": _safe_str(s.get("narration_key")) or scene_id,
            "narration_summary": _safe_str(s.get("narration_summary")) or "",
            "estimated_words": int(s.get("estimated_words") or 0),
            "estimated_duration": _safe_str(s.get("estimated_duration")) or "0s",
            "animations": s.get("animations")
            if isinstance(s.get("animations"), list)
            else _ensure_list(s.get("animations")),
            "complexity": _safe_str(s.get("complexity")) or "low",
            "risk_flags": s.get("risk_flags")
            if isinstance(s.get("risk_flags"), list)
            else _ensure_list(s.get("risk_flags")),
        }
        # Optional render metadata
        if "status" in s and isinstance(s.get("status"), str):
            scene["status"] = s["status"]
        if "file" in s and isinstance(s.get("file"), str):
            scene["file"] = s["file"]
        if "class_name" in s and isinstance(s.get("class_name"), str):
            scene["class_name"] = s["class_name"]
        if "video_file" in s and isinstance(s.get("video_file"), str):
            scene["video_file"] = s["video_file"]
        if "verification" in s and isinstance(s.get("verification"), dict):
            scene["verification"] = s["verification"]
        scenes.append(scene)

    current_scene_index = state.get("current_scene_index", 0)
    try:
        current_scene_index = int(current_scene_index)
    except Exception:
        current_scene_index = 0
    if current_scene_index < 0:
        current_scene_index = 0

    errors_in = state.get("errors") if isinstance(state.get("errors"), list) else []
    if errors_in is None:
        errors_in = []
    # Dedupe errors to prevent infinite growth across retries.
    errors = []
    seen_err = set()
    for e in errors_in:
        if e is None:
            continue
        try:
            key = json.dumps(e, sort_keys=True)
        except Exception:
            key = str(e)
        if key in seen_err:
            continue
        seen_err.add(key)
        errors.append(e)

    history = state.get("history") if isinstance(state.get("history"), list) else []

    out = {
        "project_name": project_name,
        "topic": topic,
        "phase": phase,
        "created_at": created_at,
        "updated_at": updated_at,
        "run_count": run_count,
        "plan_file": state.get("plan_file", None),
        "narration_file": state.get("narration_file", None),
        "voice_config_file": state.get("voice_config_file", None),
        "scenes": scenes,
        "current_scene_index": current_scene_index,
        "errors": errors,
        "history": history,
        "flags": flags,
    }

    # Normalize plan/narration file names to null/str
    for k in ("plan_file", "narration_file", "voice_config_file"):
        if out[k] is not None and not isinstance(out[k], str):
            out[k] = _safe_str(out[k])

    # Clamp current_scene_index
    if out["scenes"]:
        if out["current_scene_index"] > len(out["scenes"]):
            out["current_scene_index"] = len(out["scenes"])
    else:
        out["current_scene_index"] = 0

    return out


def load_plan(project_dir: Path) -> dict:
    plan_path = project_dir / "plan.json"
    if not plan_path.exists():
        raise FileNotFoundError("plan.json not found")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if not isinstance(plan, dict):
        raise ValueError("plan.json must be an object")
    scenes = plan.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("plan.json.scenes missing/empty")
    return plan


def scenes_from_plan(plan: dict) -> list[dict]:
    out = []
    used_ids: set[str] = set()
    for index, s in enumerate(plan.get("scenes", []), start=1):
        if not isinstance(s, dict):
            continue
        scene_title = _safe_str(s.get("title")) or f"Scene {index:02d}"
        scene_id = _canonical_scene_id(
            index=index,
            title=scene_title,
            raw_id=_safe_str(s.get("id")),
            used_ids=used_ids,
        )
        narration_key = _safe_str(s.get("narration_key")) or scene_id
        out.append(
            {
                "id": scene_id,
                "title": scene_title,
                "narration_key": narration_key,
                "narration_summary": _safe_str(s.get("narration_summary")) or "",
                "estimated_words": int(s.get("estimated_words") or 0),
                "estimated_duration": _safe_str(s.get("estimated_duration")) or "0s",
                "animations": s.get("animations")
                if isinstance(s.get("animations"), list)
                else _ensure_list(s.get("animations")),
                "complexity": _safe_str(s.get("complexity")) or "low",
                "risk_flags": s.get("risk_flags")
                if isinstance(s.get("risk_flags"), list)
                else _ensure_list(s.get("risk_flags")),
                "status": "pending",
            }
        )
    if not out:
        raise ValueError("plan.json contained no usable scenes")
    return out


def infer_class_name(scene_path: Path) -> str | None:
    try:
        txt = scene_path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(
        r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*VoiceoverScene\s*\)\s*:\s*$",
        txt,
        re.M,
    )
    if m:
        return m.group(1)
    m = re.search(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(.*\)\s*:\s*$", txt, re.M)
    if m:
        return m.group(1)
    return None


def apply_phase(project_dir: Path, state: dict, phase: str) -> dict:
    state = normalize_state(project_dir, state)
    state["updated_at"] = utc_now()

    if phase == "plan":
        plan = load_plan(project_dir)
        state["plan_file"] = "plan.json"
        state["scenes"] = scenes_from_plan(plan)
        state["current_scene_index"] = 0
        state["phase"] = "review"
        state["flags"]["needs_human_review"] = False
        state.setdefault("history", []).append(
            {
                "timestamp": utc_now(),
                "phase": "plan",
                "action": "Applied plan.json to project_state.json (deterministic)",
            }
        )
        return state

    if phase == "review":
        # Deterministically advance to training examples before narration.
        state["phase"] = "training"
        state["flags"]["needs_human_review"] = False
        state.setdefault("history", []).append(
            {
                "timestamp": utc_now(),
                "phase": "review",
                "action": "Advanced to training (deterministic)",
            }
        )
        return state

    if phase == "training":
        ack_path = project_dir / "training_ack.md"
        if ack_path.exists() and ack_path.stat().st_size > 0:
            ack_text = (
                ack_path.read_text(encoding="utf-8").strip().lower().rstrip(".!? ")
            )
            if ack_text != "understood":
                state["phase"] = "training"
                _add_error_unique(
                    state,
                    "training incomplete: training_ack.md must contain exactly 'understood'",
                )
                return state

            state["phase"] = "narration"
            state["flags"]["needs_human_review"] = False
            _clear_errors_matching(
                state,
                lambda e: e.startswith("training incomplete:")
                or e.startswith("training failed:"),
            )
            state.setdefault("history", []).append(
                {
                    "timestamp": utc_now(),
                    "phase": "training",
                    "action": "Detected training_ack.md; advanced to narration (deterministic)",
                }
            )
            return state

        state["phase"] = "training"
        _add_error_unique(
            state,
            "training incomplete: training_ack.md missing or empty",
        )
        return state

    if phase == "narration":
        narration_path = project_dir / "narration_script.py"
        if not narration_path.exists():
            _add_error_unique(state, "narration failed: narration_script.py missing")
            state["flags"]["needs_human_review"] = True
            return state
        state["narration_file"] = "narration_script.py"
        state["phase"] = "build_scenes"
        state["flags"]["needs_human_review"] = False
        _clear_errors_matching(state, lambda e: e.startswith("narration failed:"))
        state.setdefault("history", []).append(
            {
                "timestamp": utc_now(),
                "phase": "narration",
                "action": "Detected narration_script.py; advanced to build_scenes (deterministic)",
            }
        )
        return state

    if phase == "precache_voiceovers":
        # Deterministically advance once Qwen cache index exists.
        cache_index = project_dir / "media" / "voiceovers" / "qwen" / "cache.json"
        if cache_index.exists():
            state["phase"] = "final_render"
            state["flags"]["needs_human_review"] = False
            _clear_errors_matching(
                state,
                lambda e: e.startswith("precache_voiceovers incomplete:")
                or e.startswith("precache_voiceovers failed:"),
            )
            state.setdefault("history", []).append(
                {
                    "timestamp": utc_now(),
                    "phase": "precache_voiceovers",
                    "action": "Detected media/voiceovers/qwen/cache.json; advanced to final_render (deterministic)",
                }
            )
            return state

        # Keep the phase so the pipeline can retry.
        state["phase"] = "precache_voiceovers"
        _add_error_unique(
            state,
            "precache_voiceovers incomplete: media/voiceovers/qwen/cache.json missing",
        )
        return state

    if phase == "build_scenes":
        idx = int(state.get("current_scene_index") or 0)
        scenes = state.get("scenes") or []
        if not isinstance(scenes, list) or not scenes:
            _add_error_unique(
                state,
                "build_scenes failed: no scenes in state (did plan.json apply run?)",
            )
            state["flags"]["needs_human_review"] = True
            return state
        if idx >= len(scenes):
            state["phase"] = "precache_voiceovers"
            _clear_errors_matching(
                state, lambda e: e.startswith("build_scenes incomplete:")
            )
            return state

        scene = scenes[idx]
        scene_id = _safe_str(scene.get("id"))
        if not scene_id:
            _add_error_unique(
                state, f"build_scenes failed: scene at index {idx} missing id"
            )
            return state

        scene_file = f"{scene_id}.py"
        scene_path = project_dir / scene_file
        if not scene_path.exists():
            _add_error_unique(
                state, f"build_scenes incomplete: expected {scene_file} not found"
            )
            # Let the loop retry without human review.
            return state

        class_name = infer_class_name(scene_path)
        if not class_name:
            _add_error_unique(
                state,
                f"build_scenes incomplete: could not infer class name from {scene_file}",
            )
            return state

        scene["status"] = "built"
        scene["file"] = scene_file
        scene["class_name"] = class_name
        state["current_scene_index"] = idx + 1

        # Clear retryable errors once the scene exists and is parseable.
        _clear_errors_matching(
            state,
            lambda e: e.startswith("build_scenes incomplete: expected")
            or e.startswith("build_scenes incomplete: could not infer class name"),
        )

        if state["current_scene_index"] >= len(scenes):
            state["phase"] = "precache_voiceovers"
        else:
            state["phase"] = "build_scenes"

        state.setdefault("history", []).append(
            {
                "timestamp": utc_now(),
                "phase": "build_scenes",
                "action": f"Marked built: {scene_file} ({class_name}); advanced index to {state['current_scene_index']}",
            }
        )
        return state

    return state


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--project-dir", required=True)
    p.add_argument("--state-file", default="project_state.json")
    p.add_argument(
        "--mode",
        choices=["normalize", "apply"],
        required=True,
        help="normalize: repair/schema-coerce only; apply: advance based on phase artifacts",
    )
    p.add_argument("--phase", default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()
    state_path = Path(args.state_file)
    if not state_path.is_absolute():
        state_path = (project_dir / state_path).resolve()

    if not state_path.exists():
        print(f"State file missing: {state_path}", file=sys.stderr)
        return 2

    state_raw = read_json_best_effort(state_path)
    state = normalize_state(project_dir, state_raw)

    if args.mode == "normalize":
        state["updated_at"] = utc_now()
        write_json(state_path, state)
        return 0

    phase = args.phase
    if not phase:
        phase = _safe_str(state.get("phase")) or "plan"
    if phase not in VALID_PHASES:
        phase = "plan"

    new_state = apply_phase(project_dir, state, phase)
    new_state["updated_at"] = utc_now()
    write_json(state_path, new_state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
