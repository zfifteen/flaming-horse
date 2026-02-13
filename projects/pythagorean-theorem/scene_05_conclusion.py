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
class Scene05Conclusion(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing budget: 0.18 + 0.22 + 0.18 + 0.34 + 0.08 = 1.0

        with self.voiceover(text=SCRIPT["conclusion"]) as tracker:
            # Title
            title = Text("It Works for Any Triangle!", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.18)

            # Triangle 5-12-13 (scaled to frame; keep everything on-screen)
            # Keep the triangle well below the title and fully in-frame.
            corner = np.array([-3.3, -3.6, 0.0])
            base_len = 2.6
            height_len = 6.24
            base_pt = corner + RIGHT * base_len
            top_pt = corner + UP * height_len

            triangle = Polygon(corner, base_pt, top_pt, color=BLUE)
            # Extra guard: keep a clear margin under the title.
            if triangle.get_top()[1] > 2.9:
                triangle.shift(DOWN * (triangle.get_top()[1] - 2.9))
            self.play(Create(triangle), run_time=tracker.duration * 0.22)

            # Labels (placed on segments, not via next_to(triangle) which is ambiguous)
            label_5 = Text("5", font_size=32)
            label_5.move_to((corner + base_pt) / 2 + DOWN * 0.35)

            label_12 = Text("12", font_size=32)
            label_12.move_to((corner + top_pt) / 2 + LEFT * 0.4)

            # Use the actual rendered points (triangle may have shifted).
            hyp = Line(triangle.get_vertices()[1], triangle.get_vertices()[2])
            label_13 = Text("13", font_size=32)
            label_13.move_to((hyp.get_start() + hyp.get_end()) / 2 + RIGHT * 0.45)
            angle = hyp.get_angle()
            if angle > PI / 2 or angle < -PI / 2:
                angle -= PI
            label_13.rotate(angle)

            safe_position(label_5)
            safe_position(label_12)
            safe_position(label_13)

            self.play(
                Write(label_5),
                Write(label_12),
                Write(label_13),
                run_time=tracker.duration * 0.18,
            )

            # Verification (grouped; keep within safe area)
            eq = MathTex(r"5^2 + 12^2 = 13^2", font_size=40)
            calc = MathTex(r"25 + 144 = 169", font_size=40)
            check = Text("OK", font_size=40, color=GREEN)

            verify = VGroup(eq, calc, check).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
            verify.move_to(RIGHT * 2.9 + DOWN * 0.4)
            safe_position(verify)

            self.play(Write(eq), run_time=tracker.duration * 0.10)
            self.play(Write(calc), run_time=tracker.duration * 0.10)
            self.play(FadeIn(check), run_time=tracker.duration * 0.14)

            self.wait(tracker.duration * 0.08)