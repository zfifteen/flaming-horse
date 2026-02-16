#!/usr/bin/env python3
"""Generate a new Manim scene file scaffold."""

import argparse
from pathlib import Path
import sys


TEMPLATE = """from pathlib import Path

from manim import *
from manim_voiceover_plus import VoiceoverScene

from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT


# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560


def safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2):
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * ((min_y + buff) - bottom))
    return mobject


def safe_layout(*mobjects, h_buff=0.5, max_y=3.5, min_y=-3.5):
    group = VGroup(*mobjects)
    group.arrange(RIGHT, buff=h_buff)
    for mob in mobjects:
        safe_position(mob, max_y=max_y, min_y=min_y)
    for i, mob_a in enumerate(mobjects):
        for mob_b in mobjects[i + 1 :]:
            if mob_a.get_right()[0] > mob_b.get_left()[0] - h_buff:
                overlap = mob_a.get_right()[0] - mob_b.get_left()[0] + h_buff
                mob_b.shift(RIGHT * overlap)
    return VGroup(*mobjects)


class BeatPlan:
    def __init__(self, total_duration, weights):
        self.total_duration = max(0.0, float(total_duration))
        cleaned = [max(0.0, float(w)) for w in weights]
        if not cleaned:
            raise ValueError("BeatPlan requires at least one weight")
        weight_sum = sum(cleaned)
        if weight_sum <= 0:
            cleaned = [1.0 for _ in cleaned]
            weight_sum = float(len(cleaned))

        slots = []
        consumed = 0.0
        for idx, weight in enumerate(cleaned):
            if idx == len(cleaned) - 1:
                slot = max(0.0, self.total_duration - consumed)
            else:
                slot = self.total_duration * (weight / weight_sum)
                consumed += slot
            slots.append(slot)
        self._slots = slots
        self._cursor = 0

    def next_slot(self):
        if self._cursor >= len(self._slots):
            return 0.0
        slot = self._slots[self._cursor]
        self._cursor += 1
        return slot


def play_in_slot(scene, slot, *animations, max_run_time=None, min_run_time=0.3, **play_kwargs):
    if not animations:
        return

    slot = max(0.0, float(slot))
    if slot <= 0:
        return

    animation = animations[0] if len(animations) == 1 else LaggedStart(*animations, lag_ratio=0.15)

    run_time = slot
    if max_run_time is not None:
        run_time = min(run_time, float(max_run_time))
    run_time = max(float(min_run_time), run_time)
    run_time = min(run_time, slot)

    scene.play(animation, run_time=run_time, **play_kwargs)
    remaining = slot - run_time
    if remaining > 1e-6:
        scene.wait(remaining)


def play_text_in_slot(scene, slot, *animations, max_text_seconds=1.5, min_run_time=0.3, **play_kwargs):
    return play_in_slot(
        scene,
        slot,
        *animations,
        max_run_time=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )


def play_next(scene, beats, *animations, max_run_time=None, min_run_time=0.3, **play_kwargs):
    return play_in_slot(
        scene,
        beats.next_slot(),
        *animations,
        max_run_time=max_run_time,
        min_run_time=min_run_time,
        **play_kwargs,
    )


def play_text_next(scene, beats, *animations, max_text_seconds=1.5, min_run_time=0.3, **play_kwargs):
    return play_text_in_slot(
        scene,
        beats.next_slot(),
        *animations,
        max_text_seconds=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )


class {class_name}(VoiceoverScene):
    def construct(self):
        ref_path = Path("assets/voice_ref/ref.wav")
        if not ref_path.exists():
            raise FileNotFoundError("Run precache_voice.sh before building.")

        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["{narration_key}"]) as tracker:
            # SLOT_START:scene_body
            # MANDATORY: replace with duration-scaled micro-beats during scene authoring.
            # Coarse 3-slot timing causes sparse scenes and late animation clustering.
            beats = BeatPlan(tracker.duration, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

            title = Text("{{{{TITLE}}}}", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))

            subtitle = Text("{{{{SUBTITLE}}}}", font_size=32)
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            play_text_next(self, beats, FadeIn(subtitle))

            bullet_1 = Text("{{{{KEY_POINT_1}}}}", font_size=28).move_to(LEFT * 4.8 + UP * 1.6)
            bullet_2 = Text("{{{{KEY_POINT_2}}}}", font_size=28).next_to(bullet_1, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_2)
            bullet_3 = Text("{{{{KEY_POINT_3}}}}", font_size=28).next_to(bullet_2, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_3)

            play_text_next(self, beats, FadeIn(bullet_1))
            play_text_next(self, beats, FadeIn(bullet_2))
            play_text_next(self, beats, FadeIn(bullet_3))

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
