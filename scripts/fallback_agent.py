#!/usr/bin/env python3
"""Fallback artifact generator for when the LLM agent (opencode) is unavailable.

Generates deterministic plan.json, narration_script.py, and scene files
from the project topic so the pipeline can produce a video end-to-end.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from textwrap import dedent


def generate_plan(topic: str) -> dict:
    """Generate a minimal 3-scene plan from the topic."""
    return {
        "title": topic,
        "topic_summary": topic,
        "target_audience": "General audience",
        "estimated_duration_seconds": 60,
        "total_estimated_words": 150,
        "scenes": [
            {
                "id": "scene_01_intro",
                "title": "Introduction",
                "narration_key": "intro",
                "narration_summary": f"Introduction to {topic}",
                "estimated_words": 50,
                "estimated_duration": "20s",
                "animations": ["Write title", "FadeIn subtitle"],
                "complexity": "low",
                "risk_flags": [],
            },
            {
                "id": "scene_02_main",
                "title": "Main Content",
                "narration_key": "main",
                "narration_summary": f"Core content about {topic}",
                "estimated_words": 50,
                "estimated_duration": "20s",
                "animations": ["Show content"],
                "complexity": "low",
                "risk_flags": [],
            },
            {
                "id": "scene_03_recap",
                "title": "Summary and Recap",
                "narration_key": "recap",
                "narration_summary": "Final summary restating the key points",
                "estimated_words": 50,
                "estimated_duration": "20s",
                "animations": ["FadeIn summary points"],
                "complexity": "low",
                "risk_flags": [],
            },
        ],
    }


def generate_narration(topic: str, plan: dict) -> str:
    """Generate narration_script.py content from the plan."""
    scripts = {}
    for scene in plan["scenes"]:
        key = scene["narration_key"]
        summary = scene.get("narration_summary", key)
        if key == "intro":
            scripts[key] = f"Welcome. Today we will explore the topic of {topic}. This is an important and fascinating subject that we will break down step by step."
        elif key == "recap":
            scripts[key] = f"To summarize what we have covered, {topic} is a rich subject with many interesting aspects. Thank you for watching."
        else:
            scripts[key] = f"Now let us dive deeper into {topic}. {summary}. There is a lot to uncover here, so let us get started."

    lines = [
        '"""',
        f"Narration script for: {plan.get('title', topic)}",
        '"""',
        "",
        "SCRIPT = {",
    ]
    for key, text in scripts.items():
        lines.append(f'    "{key}": """{text}""",')
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def generate_scene(
    project_dir: Path, scene: dict, scaffold_script: Path
) -> None:
    """Generate a scene file using the scaffold script."""
    scene_id = scene["id"]
    narration_key = scene["narration_key"]
    # Convert scene_id to CamelCase class name
    class_name = "".join(part.capitalize() for part in scene_id.split("_"))

    scene_file = project_dir / f"{scene_id}.py"
    if scene_file.exists():
        print(f"  ✓ Scene already exists: {scene_file.name}")
        return

    cmd = [
        sys.executable,
        str(scaffold_script),
        "--project", str(project_dir),
        "--scene-id", scene_id,
        "--class-name", class_name,
        "--narration-key", narration_key,
        "--force",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ Failed to scaffold {scene_id}: {result.stderr}", file=sys.stderr)
        raise SystemExit(1)
    print(f"  ✓ Scaffolded: {scene_file.name}")


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "Usage: fallback_agent.py <phase> <project_dir> [scaffold_script]",
            file=sys.stderr,
        )
        return 1

    phase = sys.argv[1]
    project_dir = Path(sys.argv[2]).resolve()
    scaffold_script = (
        Path(sys.argv[3]).resolve()
        if len(sys.argv) > 3
        else (Path(__file__).parent / "scaffold_scene.py").resolve()
    )

    state_path = project_dir / "project_state.json"
    if not state_path.exists():
        print(f"ERROR: {state_path} not found", file=sys.stderr)
        return 1

    state = json.loads(state_path.read_text(encoding="utf-8"))
    topic = state.get("topic") or "an interesting topic"

    if phase == "plan":
        plan = generate_plan(topic)
        plan_path = project_dir / "plan.json"
        plan_path.write_text(
            json.dumps(plan, indent=2) + "\n", encoding="utf-8"
        )
        print(f"✓ Generated plan.json ({len(plan['scenes'])} scenes)")
        return 0

    if phase == "narration":
        plan_path = project_dir / "plan.json"
        if not plan_path.exists():
            print("ERROR: plan.json not found", file=sys.stderr)
            return 1
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        narration = generate_narration(topic, plan)
        narration_path = project_dir / "narration_script.py"
        narration_path.write_text(narration, encoding="utf-8")
        print("✓ Generated narration_script.py")
        return 0

    if phase == "build_scenes":
        plan_path = project_dir / "plan.json"
        if not plan_path.exists():
            print("ERROR: plan.json not found", file=sys.stderr)
            return 1
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        idx = state.get("current_scene_index", 0)
        scenes = plan.get("scenes", [])
        if idx >= len(scenes):
            print("✓ All scenes already built")
            return 0
        scene = scenes[idx]
        print(f"→ Building scene {idx + 1}/{len(scenes)}: {scene['id']}")
        generate_scene(project_dir, scene, scaffold_script)
        return 0

    print(f"⚠ Fallback agent: no handler for phase '{phase}' (skipping)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
