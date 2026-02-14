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
class Scene06Recap(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence with 4 beats: title, bullets, timeline, fadeout
        with self.voiceover(text=SCRIPT["recap"]) as tracker:
            beats = BeatPlan(tracker.duration, [2, 3, 3, 2])

            # Title (ALWAYS use UP * 3.8)
            title = Text("Recap & Challenges", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))

            # Key takeaways bullets
            bullet_texts = [
                r"Semi-primes: $p \times q$",
                r"Trial division: $O(\sqrt{N})$",
                r"Advanced: Pollard's $\rho$, Quadratic Sieve",
                r"RSA: factoring hardness",
                r"Quantum: Shor's algorithm",
            ]
            bullets = VGroup(*[Tex(tex, font_size=26) for tex in bullet_texts])
            bullets.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
            bullets.next_to(title, DOWN, buff=0.9)
            safe_position(bullets)
            play_text_next(
                self, beats, LaggedStart(*[Write(b) for b in bullets], lag_ratio=0.12)
            )

            # Timeline of methods
            timeline_line = Line(
                LEFT * 4.8 + DOWN * 1.9,
                RIGHT * 4.8 + DOWN * 1.9,
                stroke_width=8,
                color=BLUE,
            )
            pos_x = np.linspace(-4.4, 4.4, 4)
            dots = VGroup(
                *[Dot(np.array([x, -1.9, 0]), radius=0.12, color=YELLOW) for x in pos_x]
            )
            methods = ["Trial", "Rho", "Sieve", "RSA"]
            labels = VGroup()
            for i, (x, m) in enumerate(zip(pos_x, methods)):
                label = Text(m, font_size=28, weight=BOLD)
                label.move_to(UP * 0.3 + RIGHT * x + DOWN * 1.9)
                safe_position(label)
                labels.add(label)
            safe_layout(*labels)

            timeline_group_anim = AnimationGroup(
                Create(timeline_line),
                LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.25),
                LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.15),
            )
            play_next(self, beats, timeline_group_anim)

            # Fade out
            all_elements = VGroup(title, bullets, timeline_line, dots, labels)
            play_next(self, beats, FadeOut(all_elements))
