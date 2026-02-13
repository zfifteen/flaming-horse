import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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
from flaming_horse_voice import get_speech_service

# ── Import Shared Configuration ────────────────────────────────────
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
class Scene01ThresholdIntro(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: surface 0.4, equation 0.1, contour 0.1, label 0.1, wait 0.3

        with self.voiceover(text=SCRIPT["threshold"]) as tracker:
            # 3D coordinate system
            axes = ThreeDAxes(
                x_range=(-0.2, 1.2, 0.2),
                y_range=(-0.2, 2.2, 0.5),
                z_range=(0, 1.5, 0.5),
                x_length=6,
                y_length=6,
                z_length=4,
            )
            axes.move_to(ORIGIN)

            # Labels
            x_label = axes.get_x_axis_label(
                "P_{ac}/q_{\\infty}", edge=RIGHT, direction=RIGHT
            ).set_color(YELLOW)
            y_label = axes.get_y_axis_label(
                "f_{mod}/f_{ci}", edge=UP, direction=UP
            ).set_color(BLUE)
            z_label = axes.get_z_axis_label("\\eta", edge=OUT, direction=OUT).set_color(
                WHITE
            )
            labels = VGroup(x_label, y_label, z_label)

            # Grid in xy plane
            grid = NumberPlane(
                x_range=(-0.2, 1.2, 0.2),
                y_range=(-0.2, 2.2, 0.5),
                background_line_style={
                    "stroke_color": GRAY,
                    "stroke_width": 1,
                    "stroke_opacity": 0.5,
                },
                faded_line_style={
                    "stroke_color": GRAY,
                    "stroke_width": 0.5,
                    "stroke_opacity": 0.25,
                },
            )

            # Parametric surface
            def surface_func(u, v):
                p = u  # 0 to 1
                f = v  # 0 to 2
                eta = p * f
                return axes.c2p(p, f, eta)

            surface = Surface(
                surface_func,
                u_range=(0, 1),
                v_range=(0, 2),
                resolution=(20, 20),
            )
            surface.set_color_by_func(
                lambda point: interpolate_color(BLUE_E, YELLOW, point[2])
            )
            surface.set_opacity(0.8)

            # Initial flat surface
            surface.save_state()
            surface.scale(np.array([1, 1, 0.01])).move_to(axes.c2p(0.5, 1, 0))

            # Frame tilt
            # self.camera.frame.set_euler_angles(phi=-20 * DEG, theta=65 * DEG, gamma=0)

            # Animate surface rising
            self.play(
                FadeIn(axes),
                FadeIn(labels),
                FadeIn(grid),
                Restore(surface),
                run_time=tracker.duration * 0.4,
            )

            # Equation
            equation = MathTex(
                "\\eta = (P_{ac}/q_{\\infty}) \\times (f_{mod}/f_{ci})", font_size=36
            )
            equation.to_edge(UL)
            equation.set_color_by_tex("P_{ac}/q_{\\infty}", YELLOW)
            equation.set_color_by_tex("f_{mod}/f_{ci}", BLUE)
            equation.set_color_by_tex("\\eta", WHITE)
            safe_position(equation)

            self.play(Write(equation), run_time=tracker.duration * 0.1)

            # Contour plane at z=0.075
            contour_plane = Rectangle(width=6, height=4, color=YELLOW, fill_opacity=0.3)
            contour_plane.rotate(PI / 2, axis=RIGHT)
            contour_plane.move_to(axes.c2p(0.5, 1, 0.075))

            # Glowing contour (simplified as pulsing plane)
            contour_plane.add_updater(
                lambda m, dt: m.set_opacity(0.3 + 0.2 * np.sin(2 * PI * self.time))
            )

            self.play(FadeIn(contour_plane), run_time=tracker.duration * 0.1)

            # Label with arrow
            label = Text("Parametric Threshold Zone", font_size=24, color=YELLOW)
            label.move_to(RIGHT * 6)
            arrow = Arrow(
                label.get_left(), contour_plane.get_right(), color=YELLOW, buff=0.1
            )
            label_group = VGroup(label, arrow)
            safe_position(label_group)

            self.play(FadeIn(label_group), run_time=tracker.duration * 0.1)

            # Wait
            self.wait(tracker.duration * 0.3)