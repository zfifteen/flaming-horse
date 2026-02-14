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
class Scene03TrialDivision(VoiceoverScene):
    def construct(self):
        # Qwen cached voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing is deterministic: define beat weights, then consume slots in order.
        with self.voiceover(text=SCRIPT["trial_division"]) as tracker:
            beats = BeatPlan(tracker.duration, [1.5, 4.5, 3])

            # Title group
            title = Text("Basic Factoring:", font_size=44, weight=BOLD)
            title.move_to(UP * 3.8)
            subtitle = Text("Trial Division", font_size=36)
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            title_group = VGroup(title, subtitle)
            play_text_next(self, beats, Write(title_group))

            # N=143 and trial divisions
            n_display = MathTex(r"N = 143", font_size=72, color=BLUE)
            n_display.move_to(ORIGIN)

            trial_strings = [
                r"2 \nmid 143",
                r"3 \nmid 143",
                r"5 \nmid 143",
                r"7 \nmid 143",
                r"11 \mid 143 = 13",
            ]
            trial_colors = [GRAY, GRAY, GRAY, GRAY, GREEN]
            trial_texts = VGroup(
                *[
                    MathTex(s, font_size=42, color=c).move_to(
                        LEFT * 4.2 + DOWN * (i - 2) * 0.65
                    )
                    for i, (s, c) in enumerate(zip(trial_strings, trial_colors))
                ]
            )
            safe_layout(*trial_texts)

            play_next(
                self,
                beats,
                FadeIn(n_display),
                LaggedStart(
                    *[FadeIn(trial, scale=1.1) for trial in trial_texts], lag_ratio=0.2
                ),
            )

            # Sqrt optimization arrow and time complexity graph
            sqrt_tex = MathTex(r"\sqrt{143} \approx 11.96", font_size=48, color=ORANGE)
            sqrt_tex.next_to(ORIGIN, DOWN, buff=1.8)
            safe_position(sqrt_tex)

            sqrt_arrow = Arrow(
                sqrt_tex.get_right(),
                trial_texts[-1].get_left(),
                color=ORANGE,
                stroke_width=6,
            )

            # Graph
            graph_axis = Axes(
                x_range=[0, 150, 25],
                y_range=[0, 13, 3],
                x_length=5,
                y_length=2.2,
                axis_config={"color": GRAY},
            ).move_to(RIGHT * 3.2)

            graph_curve = graph_axis.plot(np.sqrt, color=YELLOW, stroke_width=6)

            n_dot = Dot(
                graph_axis.coords_to_point(143, np.sqrt(143)), color=BLUE, radius=0.08
            )

            complexity_label = MathTex(
                r"O(\sqrt{N})", font_size=36, color=YELLOW
            ).next_to(graph_axis, UP, buff=0.15)
            safe_position(complexity_label)

            graph_group = VGroup(graph_axis, graph_curve, n_dot, complexity_label)

            play_next(
                self,
                beats,
                Succession(
                    FadeOut(VGroup(n_display, trial_texts)),
                    LaggedStart(
                        Write(sqrt_tex),
                        Create(sqrt_arrow),
                        FadeIn(graph_group),
                        lag_ratio=0.15,
                    ),
                ),
            )
