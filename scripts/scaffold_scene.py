#!/usr/bin/env python3
"""Generate a new Manim scene file scaffold."""

import argparse
from pathlib import Path
import sys


TEMPLATE = """from pathlib import Path

from manim import *
import numpy as np
from manim_voiceover_plus import VoiceoverScene

from flaming_horse_voice import get_speech_service
from flaming_horse.scene_helpers import (
    safe_position,
    harmonious_color,
    polished_fade_in,
    adaptive_title_position,
    safe_layout,
)
from narration_script import SCRIPT


# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560


def clamp_text_width(text_obj, max_width=6.0):
    \"\"\"Clamp text width deterministically for scene readability.\"\"\"
    text_obj.set_max_width(max_width)
    if text_obj.width > max_width:
        text_obj.scale_to_fit_width(max_width)
    return text_obj


class {class_name}(VoiceoverScene):
    def construct(self):
        ref_path = Path("assets/voice_ref/ref.wav")
        if not ref_path.exists():
            raise FileNotFoundError("Run precache_voice.sh before building.")

        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["{narration_key}"]) as tracker:
            # SLOT_START:scene_body
            pass  # TEMP scaffold stub: Agent replaces entire block from here to SLOT_END
            # PROMPT: Output ONLY <scene_body>...</scene_body> body code. NO full class/imports/config wrappers.
            # PROMPT: Use structurally different patterns (e.g., progressive bullets + evolving diagram or timeline/staged reveal).
            # PROMPT: Position bullets at LEFT * 3.5 with set_max_width(6.0); derive content from narration_script.py, not plan.json.
            # PROMPT: Ensure layout contracts: title at UP * 3.8, subtitle next_to(title, DOWN, buff=0.4), visuals below subtitle.
            # SLOT_END:scene_body
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold a Manim scene file.")
    parser.add_argument("--project", required=True, help="Project directory path")
    parser.add_argument(
        "--scene-id", required=True, help="Scene id (file name without .py)"
    )
    parser.add_argument("--class-name", required=True, help="Scene class name")
    parser.add_argument(
        "--narration-key", required=True, help="SCRIPT key for narration"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing scene file"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project)
    scene_filename = (
        args.scene_id if args.scene_id.endswith(".py") else f"{args.scene_id}.py"
    )
    output_file = project_dir / scene_filename

    if not project_dir.exists():
        print(f"Error: project directory not found: {project_dir}", file=sys.stderr)
        return 1
    if output_file.exists() and not args.force:
        print(f"Error: scene file already exists: {output_file}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 1

    content = TEMPLATE.format(
        class_name=args.class_name,
        narration_key=args.narration_key,
    )
    output_file.write_text(content, encoding="utf-8")
    print(f"Created scene scaffold: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
