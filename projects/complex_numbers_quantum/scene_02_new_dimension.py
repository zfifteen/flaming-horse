from manim import *
import numpy as np

# ── Python 3.13 Compatibility Patch ────────────────────────────────
import manim_voiceover_plus.services.base as base

original_set_transcription = base.SpeechService.set_transcription


def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self.whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs)


base.SpeechService.set_transcription = patched_set_transcription

# ── Voiceover Imports ──────────────────────────────────────────────
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

# ── Import Shared Configuration ────────────────────────────────────
from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS
from narration_script import SCRIPT

# ── LOCKED CONFIGURATION (DO NOT MODIFY) ───────────────────────────
config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560


# ── Safe Positioning Helper ────────────────────────────────────────
def safe_position(mobject, max_y=4.0, min_y=-4.0):
    """Ensure mobject stays within safe bounds after positioning"""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject


# ── Scene Class ────────────────────────────────────────────────────
class Scene02NewDimension(VoiceoverScene):
    def construct(self):
        # ELEVENLABS ONLY - NO FALLBACK - FAIL LOUD
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: 0.25 + 0.05 + 0.30 + 0.20 + 0.15 + 0.05 = 1.00

        with self.voiceover(text=SCRIPT["new_dimension"]) as tracker:
            # ── Stage A: Real Number Line (0.25) ───────────────────
            real_line = NumberLine(
                x_range=(-4, 4, 1),
                length=10,
                include_numbers=True,
                include_tip=True,
                label_direction=DOWN,
                color=BLUE,
            )
            real_line.move_to(ORIGIN)

            real_label = Text("Real Numbers", font_size=36, color=BLUE)
            real_label.next_to(real_line, UP, buff=0.5)
            safe_position(real_label)

            stage_a = VGroup(real_line, real_label)

            self.play(
                Write(real_line),
                FadeIn(real_label),
                run_time=2,
            )

            # ── Stage B: Fade Label, Expand to Complex Plane (0.30) ─
            self.play(
                FadeOut(real_label),
                run_time=tracker.duration * 0.05,
            )

            # Build the complex plane
            complex_plane = NumberPlane(
                x_range=(-4, 4, 1),
                y_range=(-4, 4, 1),
                background_line_style={
                    "stroke_color": GRAY,
                    "stroke_width": 1,
                    "stroke_opacity": 0.3,
                },
                faded_line_style={
                    "stroke_color": GRAY,
                    "stroke_width": 0.5,
                    "stroke_opacity": 0.15,
                },
            )

            # Imaginary axis
            imag_line = NumberLine(
                x_range=(-4, 4, 1),
                length=10,
                include_numbers=True,
                include_tip=True,
                label_direction=LEFT,
                color=YELLOW,
            )
            imag_line.rotate(PI / 2)
            imag_line.move_to(ORIGIN)

            # Axis labels
            re_label = Text("Re", font_size=28, color=BLUE)
            re_label.move_to(RIGHT * 5.5)
            safe_position(re_label)

            im_label = Text("Im", font_size=28, color=YELLOW)
            im_label.move_to(UP * 4.5 + LEFT * 0.5)
            safe_position(im_label)

            self.play(
                FadeIn(complex_plane, run_time=tracker.duration * 0.15),
                Create(imag_line, run_time=tracker.duration * 0.15),
                FadeIn(re_label),
                FadeIn(im_label),
                run_time=tracker.duration * 0.30,
            )

            # ── Stage C: Formula z = a + bi (0.20) ────────────────
            formula = MathTex("z = a + bi", font_size=54, color=WHITE)
            formula.move_to(UP * 3.8)
            safe_position(formula)

            self.play(Write(formula), run_time=2)

            # ── Stage D: Example Point (2, 3) (0.15) ──────────────
            example_point = Dot(color=GREEN, radius=0.12)
            example_point.move_to(complex_plane.c2p(2, 3))

            # Dashed projection lines
            h_line = DashedLine(
                complex_plane.c2p(0, 3),
                complex_plane.c2p(2, 3),
                color=GREEN,
                stroke_width=2,
            )
            v_line = DashedLine(
                complex_plane.c2p(2, 0),
                complex_plane.c2p(2, 3),
                color=GREEN,
                stroke_width=2,
            )

            # Component labels
            a_label = MathTex("2", font_size=28, color=BLUE)
            a_label.next_to(complex_plane.c2p(2, 0), DOWN, buff=0.3)
            bi_label = MathTex("3i", font_size=28, color=YELLOW)
            bi_label.next_to(complex_plane.c2p(0, 3), LEFT, buff=0.3)

            point_label = MathTex("2 + 3i", font_size=28, color=GREEN)
            point_label.next_to(example_point, UR, buff=0.2)

            example_group = VGroup(
                example_point, h_line, v_line, a_label, bi_label, point_label
            )

            self.play(
                FadeIn(example_point, scale=0.5),
                Create(h_line),
                Create(v_line),
                FadeIn(a_label),
                FadeIn(bi_label),
                FadeIn(point_label),
                run_time=tracker.duration * 0.15,
            )

            # ── Stage E: Hold (0.05) ──────────────────────────────
            self.wait(tracker.duration * 0.05)
