import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service

# Import Shared Configuration
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


# Scene Class
class Scene04Application(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing budget: 0.18 + 0.26 + 0.16 + 0.32 + 0.08 = 1.0

        with self.voiceover(text=SCRIPT["application"]) as tracker:
            # Title
            title = Text("Ladder Problem", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.18)

            # Draw ladder scenario (scaled to fit and keep equations clear)
            corner = np.array([0.0, -1.2, 0.0])
            base_len = 3.0
            height_len = 4.0
            base_pt = corner + LEFT * base_len
            top_pt = corner + UP * height_len

            wall = Line(start=corner, end=corner + UP * (height_len + 1.2), color=BLUE)
            ground = Line(
                start=corner + LEFT * (base_len + 1.0),
                end=corner + RIGHT * 0.6,
                color=BLUE,
            )
            ladder = Line(start=base_pt, end=top_pt, color=RED)

            right_angle = Square(side_length=0.35, color=WHITE)
            right_angle.move_to(corner + np.array([-0.175, 0.175, 0]))
            right_angle.set_stroke(width=3)
            right_angle.set_fill(opacity=0)

            scenario = VGroup(wall, ground, ladder, right_angle)
            scenario.move_to(LEFT * 3.0)
            self.play(Create(scenario), run_time=tracker.duration * 0.26)

            # Labels
            base_label = Text("6 ft", font_size=32)
            base_label.move_to((base_pt + corner) / 2 + UP * 0.35)

            height_label = Text("h ft", font_size=32)
            height_label.move_to((corner + top_pt) / 2 + RIGHT * 0.45)

            ladder_label = Text("10 ft", font_size=32)
            ladder_mid = (base_pt + top_pt) / 2
            ladder_label.move_to(ladder_mid + RIGHT * 0.35)
            ladder_label.rotate(ladder.get_angle())

            safe_position(base_label)
            safe_position(height_label)
            safe_position(ladder_label)

            self.play(
                Write(base_label),
                Write(height_label),
                Write(ladder_label),
                run_time=tracker.duration * 0.16,
            )

            # Equations (kept away from diagram)
            eq1 = MathTex(r"6^2 + h^2 = 10^2", font_size=40)
            eq2 = MathTex(r"36 + h^2 = 100", font_size=40)
            eq3 = MathTex(r"h^2 = 64", font_size=40)
            eq4 = MathTex(r"h = 8\ \text{ft}", font_size=40)

            eqs = VGroup(eq1, eq2, eq3, eq4).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
            eqs.move_to(RIGHT * 3.2 + DOWN * 0.4)
            safe_position(eqs)

            self.play(Write(eq1), run_time=tracker.duration * 0.12)
            self.play(Write(eq2), run_time=tracker.duration * 0.08)
            self.play(Write(eq3), run_time=tracker.duration * 0.06)
            self.play(Write(eq4), run_time=tracker.duration * 0.06)

            self.wait(tracker.duration * 0.08)