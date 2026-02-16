#!/usr/bin/env python3
"""Generate a new Manim scene file scaffold."""

import argparse
from pathlib import Path
import sys


TEMPLATE = """from pathlib import Path
import colorsys

from manim import *
import numpy as np
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


def harmonious_color(base_color, variations=3, lightness_shift=0.1):
    rgb = np.array(base_color.to_rgb())
    h, l, s = colorsys.rgb_to_hls(*rgb)
    palette = []
    for i in range(variations):
        h_shift = i * (360 / variations) / 360
        new_h = (h + h_shift) % 1
        new_l = min(1.0, max(0.0, l + lightness_shift * i))
        new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, new_l, s)
        palette.append([new_r, new_g, new_b, 1.0])
    return palette


def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.1, glow=False):
    if glow:
        mobject.set_stroke(width=3, opacity=0.5)
    return LaggedStart(
        FadeIn(mobject),
        mobject.animate.scale(scale_factor).set_run_time(0.5).scale(1 / scale_factor),
        lag_ratio=lag_ratio,
    )


def adaptive_title_position(title, content_group, max_shift=0.5):
    content_height = content_group.height if content_group else 0
    shift_y = min(max_shift, max(0, content_height - 2.0))
    title.move_to(UP * (3.8 + shift_y))
    return title


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

    if "run_time" in play_kwargs:
        raise ValueError("Do not pass run_time to play_next/play_text_next; slot helpers own timing.")

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
            num_beats = max(10, min(22, int(np.ceil(tracker.duration / 3.0))))
            beats = BeatPlan(tracker.duration, [1] * num_beats)
            blues = harmonious_color(BLUE, variations=3)

            title = Text("{{{{TITLE}}}}", font_size=48, weight=BOLD, color=blues[0])
            title = adaptive_title_position(title, None)
            play_text_next(self, beats, Write(title))

            subtitle = Text("{{{{SUBTITLE}}}}", font_size=32, color=blues[1])
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            play_text_next(self, beats, polished_fade_in(subtitle, lag_ratio=0.1))

            bullet_1 = Text("{{{{KEY_POINT_1}}}}", font_size=28).move_to(LEFT * 4.8 + UP * 1.6)
            bullet_2 = Text("{{{{KEY_POINT_2}}}}", font_size=28).next_to(bullet_1, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_2)
            bullet_3 = Text("{{{{KEY_POINT_3}}}}", font_size=28).next_to(bullet_2, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_3)

            play_text_next(self, beats, FadeIn(bullet_1))
            play_text_next(self, beats, FadeIn(bullet_2))
            play_text_next(self, beats, FadeIn(bullet_3))

            # Before dense visuals, remove previous text layer (keep title if desired).
            play_next(self, beats, FadeOut(subtitle), FadeOut(bullet_1), FadeOut(bullet_2), FadeOut(bullet_3))

            # Evolving right-panel visual (replace with topic-specific diagram).
            panel = RoundedRectangle(width=5.2, height=3.2, corner_radius=0.2, color=blues[2]).move_to(RIGHT * 3.2 + DOWN * 0.6)
            marker = Dot(panel.get_center(), color=YELLOW)
            marker_label = Text("Visual Focus", font_size=22, color=YELLOW)
            marker_label.next_to(panel, UP, buff=0.2)
            safe_position(marker_label)

            play_next(self, beats, Create(panel, rate_func=smooth))
            play_next(self, beats, FadeIn(marker), FadeIn(marker_label))
            play_next(self, beats, marker.animate.shift(RIGHT * 1.2))

            # Pattern for labels attached via next_to in loops.
            node_left = Dot(LEFT * 1.0 + DOWN * 1.8, color=RED)
            node_right = Dot(RIGHT * 1.0 + DOWN * 1.8, color=RED)
            node_labels = []
            for node in [node_left, node_right]:
                label = Text("Node", font_size=20)
                label.next_to(node, DOWN, buff=0.2)
                safe_position(label)
                node_labels.append(label)
            safe_layout(node_left, node_right)
            safe_layout(*node_labels)
            play_next(self, beats, FadeIn(node_left), FadeIn(node_right))
            play_text_next(self, beats, LaggedStart(*[FadeIn(label) for label in node_labels], lag_ratio=0.15))

            play_next(self, beats, FadeOut(marker), FadeOut(marker_label), FadeOut(panel), FadeOut(node_left), FadeOut(node_right), FadeOut(*node_labels))

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
