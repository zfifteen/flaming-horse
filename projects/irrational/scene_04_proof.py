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
class BeatPlan:
    """Deterministic timing allocator for one voiceover block.

    Use integer-ish weights for each visual beat and consume slots in order.
    Agents should avoid manual wait/run_time math and use this plan instead.
    """

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


def play_in_slot(
    scene, slot, *animations, max_run_time=None, min_run_time=0.3, **play_kwargs
):
    """Play one or more animations in a fixed slot and fill remainder with wait."""
    if not animations:
        return

    slot = max(0.0, float(slot))
    if slot <= 0:
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
    scene, slot, *animations, max_text_seconds=2.0, min_run_time=0.3, **play_kwargs
):
    """Text animations must complete quickly; fill the rest with waits."""
    return play_in_slot(
        scene,
        slot,
        *animations,
        max_run_time=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )


def play_next(
    scene, beats, *animations, max_run_time=None, min_run_time=0.3, **play_kwargs
):
    """Play next deterministic beat slot from BeatPlan."""
    return play_in_slot(
        scene,
        beats.next_slot(),
        *animations,
        max_run_time=max_run_time,
        min_run_time=min_run_time,
        **play_kwargs,
    )


def play_text_next(
    scene, beats, *animations, max_text_seconds=2.0, min_run_time=0.3, **play_kwargs
):
    """Play next beat slot with text reveal cap."""
    return play_text_in_slot(
        scene,
        beats.next_slot(),
        *animations,
        max_text_seconds=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )


# Scene Class
class Scene04Proof(VoiceoverScene):
    def construct(self):
        # Qwen cached voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing is deterministic: define beat weights, then consume slots in order.
        with self.voiceover(text=SCRIPT["proof"]) as tracker:
            beats = BeatPlan(tracker.duration, [3, 2, 3, 2, 3, 2, 3, 2, 3, 3])

            # Title
            title = Text("Proof by Contradiction", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))

            # Assume sqrt(2) = p/q
            assume = MathTex(r"\sqrt{2} = \frac{p}{q}", font_size=36)
            assume.next_to(title, DOWN, buff=0.5)
            safe_position(assume)
            play_text_next(self, beats, Write(assume))

            # Square both sides: 2 = p^2 / q^2
            step1 = MathTex(r"2 = \frac{p^{2}}{q^{2}}", font_size=36)
            step1.next_to(assume, DOWN, buff=0.5)
            safe_position(step1)
            play_text_next(self, beats, Write(step1))

            # 2 q^2 = p^2
            step2 = MathTex(r"2 q^{2} = p^{2}", font_size=36)
            step2.next_to(step1, DOWN, buff=0.5)
            safe_position(step2)
            play_text_next(self, beats, Write(step2))

            # p^2 even => p even
            even_note = Text("p² is even, so p is even", font_size=28, color=BLUE)
            even_note.next_to(step2, DOWN, buff=0.5)
            safe_position(even_note)
            play_text_next(self, beats, Write(even_note))

            # p = 2r
            sub = MathTex(r"p = 2r", font_size=36)
            sub.next_to(even_note, DOWN, buff=0.5)
            safe_position(sub)
            play_text_next(self, beats, Write(sub))

            # Substitute: q^2 = 2 r^2
            step3 = MathTex(r"q^{2} = 2 r^{2}", font_size=36)
            step3.next_to(sub, DOWN, buff=0.5)
            safe_position(step3)
            play_text_next(self, beats, Write(step3))

            # q^2 even => q even
            even_q = Text("q² is even, so q is even", font_size=28, color=BLUE)
            even_q.next_to(step3, DOWN, buff=0.5)
            safe_position(even_q)
            play_text_next(self, beats, Write(even_q))

            # Contradiction
            contradiction = Text(
                "Contradiction: both p and q are even!", font_size=32, color=RED
            )
            contradiction.next_to(even_q, DOWN, buff=0.5)
            safe_position(contradiction)
            play_text_next(self, beats, Write(contradiction))

            # Fade out previous steps to reduce clutter
            self.play(
                FadeOut(VGroup(assume, step1, step2, even_note, sub, step3, even_q)),
                run_time=0.5,
            )

            # Conclusion
            conclusion = Text(
                "Therefore, √2 is irrational", font_size=36, weight=BOLD, color=GOLD
            )
            conclusion.move_to(DOWN * 3.5)
            play_text_next(self, beats, Write(conclusion))
