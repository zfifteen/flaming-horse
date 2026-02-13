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
class Scene06Paradoxes(VoiceoverScene):
    def construct(self):
        # Qwen cached voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing budget: Calculate BEFORE writing animations
        # Example: 0.4 + 0.3 + 0.3 = 1.0 ✓
        with self.voiceover(text=SCRIPT["paradoxes"]) as tracker:
            # Title for the scene
            title = Text("Paradoxes and Applications", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_in_slot(self, Write(title), tracker.duration * 0.15)

            # Subtitle: Hilbert's Hotel
            subtitle = Text("Hilbert's Hotel Paradox", font_size=32, color=BLUE)
            subtitle.next_to(title, DOWN, buff=0.5)
            safe_position(subtitle)
            play_text_in_slot(self, FadeIn(subtitle), tracker.duration * 0.1)

            # Represent infinite hotel: line of rooms (simplified, show 5-6 rooms with ...)
            rooms = VGroup()
            guests = VGroup()
            for i in range(5):
                room = Rectangle(width=0.8, height=0.6, color=WHITE, fill_opacity=0.1)
                room.move_to(LEFT * 3 + RIGHT * (i * 1))
                rooms.add(room)
                guest = Circle(radius=0.15, color=GREEN, fill_opacity=0.8)
                guest.move_to(room.get_center())
                guests.add(guest)
            dots = Text("...", font_size=36).next_to(rooms[-1], RIGHT, buff=0.2)
            hotel = VGroup(rooms, guests, dots).move_to(ORIGIN + DOWN * 1)
            safe_position(hotel)

            # Animate hotel appearing
            play_in_slot(self, FadeIn(hotel), tracker.duration * 0.2)

            # New guest arrives: show arrow to room 1
            new_guest = Circle(radius=0.15, color=RED, fill_opacity=0.8)
            new_guest.next_to(rooms[0], LEFT, buff=0.5)
            arrow = Arrow(new_guest.get_right(), rooms[0].get_left(), color=RED)
            new_group = VGroup(new_guest, arrow)
            play_in_slot(self, FadeIn(new_group), tracker.duration * 0.05)

            # Shift guests: animate moving to n+1
            shift_animations = []
            for i, guest in enumerate(guests):
                shift_animations.append(guest.animate.shift(RIGHT * 1))
            play_in_slot(self, *shift_animations, tracker.duration * 0.1)

            # New guest moves to room 1
            play_in_slot(
                self,
                new_guest.animate.move_to(rooms[0].get_center()),
                tracker.duration * 0.05,
            )

            # Fade out hotel and new elements
            play_in_slot(self, FadeOut(hotel, new_group), tracker.duration * 0.05)

            # Real-world applications
            apps_title = Text("Real-World Applications", font_size=36, color=YELLOW)
            apps_title.next_to(title, DOWN, buff=0.5)
            safe_position(apps_title)
            play_text_in_slot(self, Write(apps_title), tracker.duration * 0.05)

            # Geometric series: 1 + 1/2 + 1/4 + ... = 2
            series = MathTex(
                r"1 + \frac{1}{2} + \frac{1}{4} + \cdots = 2", font_size=36, color=GOLD
            )
            series.move_to(LEFT * 3 + DOWN * 1)
            safe_position(series)
            play_in_slot(self, Write(series), tracker.duration * 0.1)

            # Fractal: simple triangle for Sierpinski hint
            triangle = Polygon(
                np.array([-1, -1, 0]),
                np.array([1, -1, 0]),
                np.array([0, 1, 0]),
                color=BLUE,
                fill_opacity=0.5,
            )
            triangle.move_to(RIGHT * 3 + DOWN * 1)
            safe_position(triangle)
            play_in_slot(self, Create(triangle), tracker.duration * 0.1)

            # Calculus: harmonic series sum ~ ln(n)
            calculus = MathTex(
                r"\sum_{n=1}^{\infty} \frac{1}{n} \approx \ln(n)",
                font_size=36,
                color=PURPLE,
            )
            calculus.move_to(ORIGIN + DOWN * 2)
            safe_position(calculus)
            play_in_slot(self, Write(calculus), tracker.duration * 0.1)

            # Fade out all
            play_in_slot(
                self,
                FadeOut(apps_title, series, triangle, calculus),
                tracker.duration * 0.05,
            )
