from manim import *
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
from pathlib import Path
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560


# Safe Positioning Helper
def safe_position(mobject, max_y=4.0, min_y=-4.0):
    """Ensure mobject stays within safe bounds after positioning"""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject


def safe_layout(*mobjects, min_horizontal_spacing=0.5, max_y=4.0, min_y=-4.0):
    """Ensure multiple mobjects don't overlap and stay within safe bounds."""
    for mob in mobjects:
        top = mob.get_top()[1]
        bottom = mob.get_bottom()[1]
        if top > max_y:
            mob.shift(DOWN * (top - max_y))
        elif bottom < min_y:
            mob.shift(UP * (min_y - bottom))

    for i, mob_a in enumerate(mobjects):
        for mob_b in mobjects[i + 1 :]:
            a_left = mob_a.get_left()[0]
            a_right = mob_a.get_right()[0]
            b_left = mob_b.get_left()[0]
            b_right = mob_b.get_right()[0]
            if not (a_right < b_left or b_right < a_left):
                overlap = (a_right - b_left) if a_right > b_left else (b_right - a_left)
                mob_b.shift(RIGHT * (overlap + min_horizontal_spacing))

    return list(mobjects)


# Timing Helpers
def play_in_slot(
    scene, animation, slot, *, max_run_time=None, min_run_time=0.3, **play_kwargs
):
    """Play an animation, then wait to fill the remaining slot time.

    Args:
        scene: The Manim scene (typically `self`)
        animation: A Manim Animation instance (e.g., Write(title))
        slot: Total time budget for this beat (seconds)
        max_run_time: Optional cap for the animation portion (seconds)
        min_run_time: Minimum perceptible animation time (seconds)
        **play_kwargs: Passed to scene.play(...)
    """
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


def play_text_in_slot(
    scene, animation, slot, *, max_text_seconds=2.0, min_run_time=0.3, **play_kwargs
):
    """Text animations must complete quickly; fill the rest with waits."""
    return play_in_slot(
        scene,
        animation,
        slot,
        max_run_time=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )


# Scene Class
class Scene06Regimes(VoiceoverScene):
    def construct(self):
        # Qwen cached voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing budget: 0.2 + 0.4 + 0.4 = 1.0 ✓
        with self.voiceover(text=SCRIPT["regimes"]) as tracker:
            # Title
            title = Text("Two Regimes of Color Processing", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_in_slot(self, Write(title), tracker.duration * 0.2)

            # Regime diagrams
            regime1 = Rectangle(width=3, height=2, color=GREEN, fill_opacity=0.2)
            regime1_label = Text(
                "Cortical Amplification\n(High η, k ≤ 4)", font_size=24, color=GREEN
            )
            regime1_group = VGroup(regime1, regime1_label).arrange(DOWN, buff=0.2)
            regime1_group.move_to(LEFT * 3)

            regime2 = Rectangle(width=3, height=2, color=RED, fill_opacity=0.2)
            regime2_label = Text(
                "Interval Decoding\n(Low η, k > 6)", font_size=24, color=RED
            )
            regime2_group = VGroup(regime2, regime2_label).arrange(DOWN, buff=0.2)
            regime2_group.move_to(RIGHT * 3)

            regimes = VGroup(regime1_group, regime2_group)
            safe_layout(regime1_group, regime2_group)
            play_in_slot(self, FadeIn(regimes), tracker.duration * 0.4)

            # Scaling plot (resource mismatch)
            axes = Axes(
                x_range=[0.5, 15, 1],
                y_range=[0.01, 50, 10],
                x_length=6,
                y_length=4,
                axis_config={"include_tip": False},
                x_axis_config={"numbers_to_include": [1, 2, 3, 5, 10]},
                y_axis_config={"numbers_to_include": [0.1, 1, 10]},
            )
            axes_labels = axes.get_axis_labels(x_label="k", y_label="\\eta")
            plot = axes.plot(lambda x: 100 * (x**-2.83), x_range=[1, 12], color=BLUE)
            points = [
                axes.coords_to_point(2, 10),
                axes.coords_to_point(3, 6.7),
                axes.coords_to_point(3, 21.7),
                axes.coords_to_point(5, 5),
                axes.coords_to_point(4, 12.5),
                axes.coords_to_point(12, 0.09),
            ]
            dots = VGroup(*[Dot(point, color=RED) for point in points])
            plot_group = VGroup(axes, axes_labels, plot, dots)
            plot_group.move_to(ORIGIN)
            safe_position(plot_group)
            play_in_slot(self, FadeIn(plot_group), tracker.duration * 0.4)
