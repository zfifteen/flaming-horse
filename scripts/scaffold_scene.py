#!/usr/bin/env python3
"""Generate a new Manim scene file scaffold."""

import argparse
from pathlib import Path
import sys


TEMPLATE = """from manim import *
import numpy as np

# Python 3.13 Compatibility Patch
import manim_voiceover_plus.services.base as base
original_set_transcription = base.SpeechService.set_transcription

def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self.whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs)

base.SpeechService.set_transcription = patched_set_transcription

# Voiceover Imports
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

# Safe Positioning Helper
def safe_position(mobject, max_y=4.0, min_y=-4.0):
    \"\"\"Ensure mobject stays within safe bounds after positioning\"\"\"
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject

def safe_layout(*mobjects, min_horizontal_spacing=0.5, max_y=4.0, min_y=-4.0):
    \"\"\"Ensure multiple mobjects don't overlap and stay within safe bounds.\"\"\"
    for mob in mobjects:
        top = mob.get_top()[1]
        bottom = mob.get_bottom()[1]
        if top > max_y:
            mob.shift(DOWN * (top - max_y))
        elif bottom < min_y:
            mob.shift(UP * (min_y - bottom))

    for i, mob_a in enumerate(mobjects):
        for mob_b in mobjects[i + 1:]:
            a_left = mob_a.get_left()[0]
            a_right = mob_a.get_right()[0]
            b_left = mob_b.get_left()[0]
            b_right = mob_b.get_right()[0]
            if not (a_right < b_left or b_right < a_left):
                overlap = (a_right - b_left) if a_right > b_left else (b_right - a_left)
                mob_b.shift(RIGHT * (overlap + min_horizontal_spacing))

    return list(mobjects)

# Timing Helpers
def play_in_slot(scene, animation, slot, *, max_run_time=None, min_run_time=0.3, **play_kwargs):
    '''Play an animation, then wait to fill the remaining slot time.

    Args:
        scene: The Manim scene (typically `self`)
        animation: A Manim Animation instance (e.g., Write(title))
        slot: Total time budget for this beat (seconds)
        max_run_time: Optional cap for the animation portion (seconds)
        min_run_time: Minimum perceptible animation time (seconds)
        **play_kwargs: Passed to scene.play(...)
    '''
    slot = float(slot)
    if slot <= 0:
        return

    run_time = slot
    if max_run_time is not None:
        run_time = min(run_time, float(max_run_time))
    run_time = max(float(min_run_time), run_time)
    run_time = min(run_time, slot)

    scene.play(animation, run_time=run_time, **play_kwargs)
    remaining = slot - run_time
    if remaining > 1e-6:
        scene.wait(remaining)


def play_text_in_slot(scene, animation, slot, *, max_text_seconds=2.0, min_run_time=0.3, **play_kwargs):
    '''Text animations must complete quickly; fill the rest with waits.'''
    return play_in_slot(
        scene,
        animation,
        slot,
        max_run_time=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )

# Scene Class
class {class_name}(VoiceoverScene):
    def construct(self):
        # Qwen cached voiceover (precache required)
        self.set_speech_service(get_speech_service())

        # Animation Sequence
        # Timing budget: Calculate BEFORE writing animations
        # Example: 0.4 + 0.3 + 0.3 = 1.0 ✓
        with self.voiceover(text=SCRIPT["{narration_key}"]) as tracker:
            # TODO: Add animations here
            # NOTE: Text must never take longer than 2 seconds to appear.
            # Use play_text_in_slot(...) to cap text reveal time, and let waits
            # (or later non-text animations) consume the remaining narration slot.
            #
            # Example pattern:
            # title = Text("Title", font_size=48, weight=BOLD)
            # title.move_to(UP * 3.8)
            # play_text_in_slot(self, Write(title), tracker.duration * 0.3)
            #
            # box = Rectangle(width=4, height=2.2, color=BLUE)
            # box.move_to(ORIGIN)
            # play_in_slot(self, Create(box), tracker.duration * 0.7)
            self.wait(tracker.duration)
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
    print(f"✅ Created scene scaffold: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
