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
class Scene04Metric(VoiceoverScene):
    def construct(self):
        # Qwen cached voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing budget: Calculate BEFORE writing animations
        # Slots: 0.15 (title) + 0.15 (eta eq) + 0.15 (k) + 0.15 (D) + 0.15 (B) + 0.25 (interpretations) = 1.0 ✓
        with self.voiceover(text=SCRIPT["metric"]) as tracker:
            # Title
            title = Text("Defining Perceptual Efficiency", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_in_slot(self, Write(title), tracker.duration * 0.15)

            # Main equation: η = B / D(k)
            eta_eq = MathTex(r"\eta = \frac{B}{D(k)}", font_size=72, color=GOLD)
            eta_eq.next_to(title, DOWN, buff=1.0)
            safe_position(eta_eq)
            play_text_in_slot(self, Write(eta_eq), tracker.duration * 0.15)

            # Explain k: number of photoreceptor classes
            k_text = Text(
                "k: functionally independent photoreceptor classes",
                font_size=28,
                color=BLUE,
            )
            k_text.next_to(eta_eq, DOWN, buff=0.8)
            safe_position(k_text)
            play_text_in_slot(self, FadeIn(k_text), tracker.duration * 0.15)

            # D formula: D = k(k-1)
            d_eq = MathTex(r"D = k(k-1)", font_size=48, color=GREEN)
            d_eq.next_to(k_text, DOWN, buff=0.6)
            safe_position(d_eq)
            play_text_in_slot(self, Write(d_eq), tracker.duration * 0.15)

            # B explanation
            b_text = Text("B: total spectral JND hue steps", font_size=28, color=RED)
            b_text.next_to(d_eq, DOWN, buff=0.6)
            safe_position(b_text)
            play_text_in_slot(self, FadeIn(b_text), tracker.duration * 0.15)

            # Interpretations: high vs low eta
            interpretations = VGroup(
                Text(
                    "High η: many distinctions via deep processing",
                    font_size=24,
                    color=YELLOW,
                ),
                Text(
                    "Low η: unexploited degrees of freedom", font_size=24, color=ORANGE
                ),
                Text("η ≈ 1: transition point", font_size=24, color=PURPLE),
            )
            interpretations.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
            interpretations.next_to(b_text, DOWN, buff=0.8)
            safe_position(interpretations)
            play_in_slot(
                self, FadeIn(interpretations, lag_ratio=0.2), tracker.duration * 0.25
            )
