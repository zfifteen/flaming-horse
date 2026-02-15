from pathlib import Path
import colorsys
import numpy as np

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


def safe_layout(*mobjects, alignment=ORIGIN, h_buff=0.5, v_buff=0.3, max_y=3.5, min_y=-3.5):
    group = VGroup(*mobjects)
    group.arrange(RIGHT, buff=h_buff, aligned_edge=UP if v_buff else alignment)
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


class Scene01Intro(VoiceoverScene):
    def construct(self):
        ref_path = Path("assets/voice_ref/ref.wav")
        if not ref_path.exists():
            raise FileNotFoundError("Run precache_voice.sh before building.")

        palette = harmonious_color(BLUE, variations=3)

        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            beats = BeatPlan(tracker.duration, [4, 3, 5])

            title = Text(
                "Novel Insights from the Guthrie Case",
                font_size=42,
                weight=BOLD,
                color=palette[0],
            )
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title, run_time=1.2))

            subtitle = Text(
                "What if one detail changes everything?",
                font_size=32,
                color=palette[1],
            )
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            play_text_next(self, beats, polished_fade_in(subtitle, lag_ratio=0.1))

            timeline_line = Line(LEFT * 4.2, RIGHT * 4.2, stroke_width=6, color=palette[2])
            timeline_line.move_to(DOWN * 1.0)
            positions = [-3.8, -1.9, 0.0, 1.9, 3.8]
            label_texts = [
                "Background",
                "Key Facts",
                "Trad. Analysis",
                "Novel Insights",
                "Conclusion",
            ]
            dots = VGroup()
            labels = VGroup()
            for idx, pos in enumerate(positions):
                dot = Circle(radius=0.15, color=palette[2], fill_opacity=1.0)
                dot.move_to(pos * RIGHT + DOWN * 1.0)
                dots.add(dot)

                label = Text(label_texts[idx], font_size=24, color=palette[1])
                label.next_to(dot, DOWN, buff=0.15)
                safe_position(label)
                labels.add(label)

            safe_layout(*labels)

            line_anim = Create(timeline_line, rate_func=smooth)
            dots_anim = LaggedStart(*[Create(d) for d in dots], lag_ratio=0.12)
            labels_anim = LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.12)
            play_next(self, beats, line_anim, dots_anim, labels_anim)

            self.wait(tracker.duration * 0.1)
*** End Patch
