from pathlib import Path

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


class Scene03Regression(VoiceoverScene):
    def construct(self):
        ref_path = Path("assets/voice_ref/ref.wav")
        if not ref_path.exists():
            raise FileNotFoundError("Run precache_voice.sh before building.")

        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["regression_analysis"]) as tracker:
            # SLOT_START:scene_body
            beats = BeatPlan(tracker.duration, [1, 2, 2, 1])

            palette = [BLUE, PURPLE, GREEN]

            title = Text("Regression Analysis", font_size=48, weight=BOLD, color=palette[0])
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))

            subtitle = Text("Linear Model Fit", font_size=36, color=palette[1])
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            play_text_next(self, beats, FadeIn(subtitle))

            sizes = [1.0, 1.5, 2.0, 2.5, 3.0]
            defects = [0.02, 0.03, 0.045, 0.065, 0.04]
            points = VGroup(*[Dot([sizes[i], defects[i]*10, 0], color=palette[0]) for i in range(5)])
            points.scale(0.8).move_to(DOWN * 0.6)
            safe_position(points)

            line = Line(LEFT * 2 + DOWN * 0.6, RIGHT * 2 + UP * 0.2, color=palette[1], stroke_width=6)
            equation = MathTex(r"y = 0.018\, x + 0.002", font_size=36, color=palette[2])
            equation.next_to(line, UP, buff=0.3)
            safe_position(equation)

            preds = VGroup(*[Dot([sizes[i], 0.018*sizes[i] + 0.002*10, 0], color=palette[2]) for i in range(5)])
            preds.scale(0.6).set_stroke(width=3, opacity=0.8)
            residuals = VGroup()
            for i in range(5):
                res_line = Line(preds[i].get_center(), points[i].get_center(), stroke_width=2, color=YELLOW if i==3 else GRAY)
                residuals.add(res_line)

            model_group = VGroup(line, equation, preds, residuals)
            model_group.move_to(DOWN * 0.6)
            safe_position(model_group)

            play_next(self, beats, LaggedStart(*[Create(p) for p in points], lag_ratio=0.15))

            play_next(self, beats, Create(line), Write(equation))

            play_next(self, beats, LaggedStart(*[FadeIn(p) for p in preds], lag_ratio=0.1), LaggedStart(*[Create(r) for r in residuals], lag_ratio=0.1))

            self.wait(tracker.duration * 0.1)
            # SLOT_END:scene_body
