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
class Scene04AdvancedMethods(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence - single voiceover block with beat timing
        with self.voiceover(text=SCRIPT["advanced"]) as tracker:
            beats = BeatPlan(tracker.duration, [1, 4, 4, 4, 2])

            # Persistent title
            title = Text("Advanced Methods", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))

            # Pollard's Rho (slot 2)
            rho_label = Text("Pollard's Rho", font_size=36, color=BLUE)
            rho_label.next_to(title, DOWN, buff=0.5)
            safe_position(rho_label)

            rho_desc = Text("f(x) = x² + c mod N\nCycle detection", font_size=24)
            rho_desc.next_to(rho_label, DOWN, buff=0.3)
            safe_position(rho_desc)

            # Rho diagram: tail -> loop -> head
            rho_tail_start = LEFT * 2.2 + DOWN * 1.5
            rho_loop = Arc(
                radius=1.2,
                start_angle=PI + 0.3,
                angle=-1.8,
                stroke_width=14,
                color=BLUE,
            ).shift(LEFT * 0.2 + DOWN * 1.2)
            rho_tail = Line(
                rho_tail_start, rho_loop.get_start(), stroke_width=14, color=BLUE
            )
            rho_end = rho_loop.get_end()
            rho_head = Circle(radius=0.16, color=BLUE, fill_opacity=1).move_to(
                rho_end + RIGHT * 0.35 + UP * 0.08
            )
            rho_diagram = VGroup(rho_tail, rho_loop, rho_head).move_to(
                LEFT * 4.5 + DOWN * 0.8
            )

            rho_elements = [rho_label, rho_desc] + list(rho_diagram)
            safe_layout(*rho_elements)

            play_next(
                self,
                beats,
                LaggedStart(
                    Write(rho_label),
                    FadeIn(rho_desc),
                    Create(rho_tail),
                    Create(rho_loop),
                    Create(rho_head),
                    lag_ratio=0.2,
                ),
            )

            # Fermat slot 3: fade rho + show Fermat
            fermat_label = Text("Fermat's Method", font_size=36, color=GREEN)
            fermat_label.next_to(title, DOWN, buff=0.5)
            safe_position(fermat_label)

            fermat_eq = MathTex(
                r"N + k^{2} = a^{2} - b^{2} = (a-b)(a+b)", font_size=38, color=YELLOW
            )
            fermat_eq.next_to(fermat_label, DOWN, buff=0.4)
            safe_position(fermat_eq)

            fermat_group = VGroup(fermat_label, fermat_eq)
            safe_layout(*fermat_group)

            rho_group = VGroup(rho_label, rho_desc, rho_diagram)
            play_next(
                self,
                beats,
                Succession(
                    FadeOut(rho_group),
                    LaggedStart(Write(fermat_label), Write(fermat_eq), lag_ratio=0.1),
                ),
            )

            # Quadratic Sieve slot 4: fade Fermat + show QS
            qs_label = Text("Quadratic Sieve", font_size=36, color=ORANGE)
            qs_label.next_to(title, DOWN, buff=0.5)
            safe_position(qs_label)

            qs_desc = Text("Smooth numbers\nGF(2) matrix", font_size=24)
            qs_desc.next_to(qs_label, DOWN, buff=0.3)
            safe_position(qs_desc)

            qs_matrix = (
                IntegerMatrix(
                    [[1, 0, 1, 1], [0, 1, 1, 0], [1, 1, 0, 1], [1, 0, 1, 0]],
                    h_buff=1.2,
                    v_buff=1.2,
                )
                .scale(1.2)
                .set_color(PURPLE)
            )
            qs_matrix.move_to(DOWN * 1.3)

            qs_elements = [qs_label, qs_desc, qs_matrix]
            safe_layout(*qs_elements)

            play_next(
                self,
                beats,
                Succession(
                    FadeOut(fermat_group),
                    LaggedStart(
                        Write(qs_label),
                        FadeIn(qs_desc),
                        Create(qs_matrix),
                        lag_ratio=0.15,
                    ),
                ),
            )

            # Limits slot 5: fade QS + show limits
            limits_text = Text(
                "Classical limits:\nHeroic computation for RSA", font_size=32, color=RED
            )
            limits_text.next_to(title, DOWN * 1.3)
            safe_position(limits_text)

            qs_group = VGroup(qs_label, qs_desc, qs_matrix)
            play_text_next(
                self, beats, Succession(FadeOut(qs_group), FadeIn(limits_text))
            )
