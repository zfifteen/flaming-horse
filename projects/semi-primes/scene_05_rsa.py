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
class Scene05RSA(VoiceoverScene):
    def construct(self):
        # Qwen cached voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing is deterministic: define beat weights, then consume slots in order.
        with self.voiceover(text=SCRIPT["rsa"]) as tracker:
            beats = BeatPlan(tracker.duration, [3, 3, 4])

            # Title
            title = Text("RSA Cryptography", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))

            # Key generation
            key_box = Rectangle(
                width=4.5, height=1.8, color=GREEN, fill_opacity=0.1
            ).move_to(UP * 0.8)
            key_text = MathTex(
                r"p,q \\to n=p\\times q \\\\ \\phi(n)=(p-1)(q-1), (e,d)", font_size=34
            ).move_to(key_box)
            play_next(self, beats, Create(key_box), Write(key_text))

            # Enc/Dec flow
            enc_box = Rectangle(width=3.5, height=1.2, color=BLUE).move_to(LEFT * 1.8)
            enc_text = MathTex(r"m^e \\mod n", font_size=32).move_to(enc_box)
            dec_box = Rectangle(width=3.5, height=1.2, color=ORANGE).move_to(
                RIGHT * 1.8
            )
            dec_text = MathTex(r"c^d \\mod n = m", font_size=32).move_to(dec_box)
            flow_group = VGroup(enc_box, enc_text, dec_box, dec_text)
            safe_layout(*[enc_box, dec_box])
            play_next(
                self,
                beats,
                Succession(
                    FadeOut(VGroup(key_box, key_text)),
                    LaggedStart(
                        Create(enc_box),
                        Write(enc_text),
                        Create(dec_box),
                        Write(dec_text),
                        lag_ratio=0.25,
                    ),
                ),
            )

            # Security
            sec_text = Text(
                "Factoring large semi-primes\\nis computationally infeasible\\\\n(2048-bit RSA secure)",
                font_size=38,
                color=RED,
            ).move_to(ORIGIN)
            safe_position(sec_text)
            play_text_next(
                self, beats, Succession(FadeOut(flow_group), FadeIn(sec_text))
            )
