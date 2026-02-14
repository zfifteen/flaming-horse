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
def play_in_slot(scene, *args, max_run_time=None, min_run_time=0.3, **play_kwargs):
    """Play one or more animations, then wait to fill the remaining slot.

    Compatible with both call styles:
      - play_in_slot(self, Create(obj), tracker.duration * 0.3)
      - play_in_slot(self, *[Write(m) for m in mobs], tracker.duration * 0.3)

    The last positional argument is interpreted as the time slot in seconds.
    """
    if len(args) < 2:
        return

    *animations, slot = args
    try:
        slot = float(slot)
    except (TypeError, ValueError) as e:
        raise TypeError(
            "play_in_slot(...): last positional argument must be a numeric slot (seconds)"
        ) from e

    if slot <= 0 or not animations:
        return

    # Support multiple animations by grouping them into a single animation.
    animation = (
        animations[0]
        if len(animations) == 1
        else LaggedStart(*animations, lag_ratio=0.15)
    )

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
    scene, *args, max_text_seconds=2.0, min_run_time=0.3, **play_kwargs
):
    """Text animations must complete quickly; fill the rest with waits."""
    return play_in_slot(
        scene,
        *args,
        max_run_time=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )


# Scene Class
class Scene03Visualization(VoiceoverScene):
    def construct(self):
        # Qwen cached voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing budget: 0.2 + 0.4 + 0.4 = 1.0 ✓
        with self.voiceover(text=SCRIPT["visualization"]) as tracker:
            # Section title
            title = Text("Visualizing Square Roots", font_size=36, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_in_slot(self, Write(title), tracker.duration * 0.2)

            # Create square and show area
            square = Square(side_length=4, color=BLUE, fill_opacity=0.2)
            square.move_to(ORIGIN)
            area_label = MathTex("16", font_size=36, color=BLUE)
            area_label.move_to(square.get_center())
            play_in_slot(self, Create(square), tracker.duration * 0.4)
            self.add(area_label)  # Add area label after square creation

            # Show sqrt calculation and side lengths
            sqrt_eq = MathTex(r"\sqrt{16} = 4", font_size=48, color=GOLD)
            sqrt_eq.next_to(square, DOWN, buff=0.5)
            safe_position(sqrt_eq)

            # Side labels
            side_labels = []
            for i, pos in enumerate([UP, RIGHT, DOWN, LEFT]):
                label = MathTex("4", font_size=24, color=GREEN)
                label.move_to(square.get_center() + pos * 2)
                side_labels.append(label)

            play_text_in_slot(self, Write(sqrt_eq), tracker.duration * 0.4)
            for label in side_labels:
                self.add(label)
