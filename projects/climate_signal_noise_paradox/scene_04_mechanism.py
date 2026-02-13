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
class Scene04Mechanism(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: title 0.08 + spencer 0.20 + model_lines 0.20 + diagram 0.25 + diagnosis 0.15 + wait 0.12 = 1.0

        with self.voiceover(text=SCRIPT["mechanism"]) as tracker:
            # Title
            title = Text(
                "Convective Heat Redistribution",
                font_size=44,
                weight=BOLD,
            )
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.08)

            # Spencer citation
            citation = Text(
                "Spencer (Jan 2026): All 39 CMIP6 models overpredict\n"
                "tropical tropospheric warming",
                font_size=20,
                color=YELLOW,
            )
            citation.move_to(UP * 2.8)
            safe_position(citation)
            self.play(Write(citation), run_time=tracker.duration * 0.05)

            # Model lines vs observation - tropical warming trends
            ax = Axes(
                x_range=[1980, 2025, 10],
                y_range=[0, 2.5, 0.5],
                x_length=10,
                y_length=4.5,
                axis_config={"include_numbers": True, "font_size": 16},
                x_axis_config={"numbers_to_include": [1980, 1990, 2000, 2010, 2020]},
                y_axis_config={"numbers_to_include": [0.0, 0.5, 1.0, 1.5, 2.0]},
            )
            ax.move_to(DOWN * 0.8)

            ax_ylabel = Text("Tropical Warming (K)", font_size=16, color=WHITE)
            ax_ylabel.next_to(ax, LEFT, buff=0.3).rotate(90 * DEGREES)
            safe_position(ax_ylabel)

            # Generate 39 model lines (red, overpredicting)
            model_lines = VGroup()
            np.random.seed(123)
            for i in range(39):
                slope = np.random.uniform(0.035, 0.055)
                offset = np.random.uniform(-0.1, 0.1)
                line = ax.plot(
                    lambda x, s=slope, o=offset: s * (x - 1980)
                    + o
                    + np.random.uniform(-0.05, 0.05),
                    x_range=[1980, 2024],
                    color=RED_C,
                    stroke_width=1.5,
                    stroke_opacity=0.4,
                )
                model_lines.add(line)

            # Observation line (lower trend)
            obs_line = ax.plot(
                lambda x: 0.018 * (x - 1980),
                x_range=[1980, 2024],
                color=GREEN,
                stroke_width=4,
            )

            obs_label = Text("Observations", font_size=18, color=GREEN)
            obs_label.next_to(obs_line, DOWN, buff=0.2).shift(RIGHT * 2)
            safe_position(obs_label)

            model_label = Text("39 CMIP6 Models", font_size=18, color=RED_C)
            model_label.next_to(ax, UP, buff=0.15).shift(RIGHT * 2)
            safe_position(model_label)

            self.play(
                Create(ax),
                Write(ax_ylabel),
                run_time=tracker.duration * 0.05,
            )
            self.play(
                LaggedStart(*[Create(m) for m in model_lines], lag_ratio=0.02),
                Write(model_label),
                run_time=tracker.duration * 0.10,
            )
            self.play(
                Create(obs_line),
                Write(obs_label),
                run_time=tracker.duration * 0.05,
            )

            # Fade out the trend chart and build the energy flow diagram
            self.play(
                FadeOut(ax),
                FadeOut(ax_ylabel),
                FadeOut(model_lines),
                FadeOut(obs_line),
                FadeOut(obs_label),
                FadeOut(model_label),
                FadeOut(citation),
                run_time=tracker.duration * 0.05,
            )

            # Energy misallocation diagram
            surface_box = Rectangle(
                width=4,
                height=1.2,
                fill_color=ORANGE,
                fill_opacity=0.5,
                stroke_color=WHITE,
            )
            surface_box.move_to(DOWN * 2.5)
            surface_text = Text("Surface Energy", font_size=22, color=WHITE)
            surface_text.move_to(surface_box.get_center())

            # Two pathways from surface
            # LEFT: Coherent forced response (what real atmosphere does more of)
            coherent_box = Rectangle(
                width=3.5,
                height=1.2,
                fill_color=GREEN_D,
                fill_opacity=0.5,
                stroke_color=GREEN,
            )
            coherent_box.move_to(LEFT * 3.5 + UP * 0.5)
            coherent_text = Text("Coherent Forced\nResponse", font_size=18, color=GREEN)
            coherent_text.move_to(coherent_box.get_center())

            # RIGHT: Disorganized noise (what models do too much of)
            noise_box = Rectangle(
                width=3.5,
                height=1.2,
                fill_color=RED_D,
                fill_opacity=0.5,
                stroke_color=RED,
            )
            noise_box.move_to(RIGHT * 3.5 + UP * 0.5)
            noise_text = Text("Disorganized\nNoise", font_size=18, color=RED)
            noise_text.move_to(noise_box.get_center())

            # Arrows
            arrow_coherent = Arrow(
                surface_box.get_top() + LEFT * 0.5,
                coherent_box.get_bottom(),
                color=GREEN,
                stroke_width=4,
            )
            arrow_noise = Arrow(
                surface_box.get_top() + RIGHT * 0.5,
                noise_box.get_bottom(),
                color=RED,
                stroke_width=8,  # thicker = models send more here
            )

            # Labels on arrows
            model_bias_label = Text("Models: Too much", font_size=16, color=RED)
            model_bias_label.next_to(arrow_noise, RIGHT, buff=0.15)
            safe_position(model_bias_label)

            real_label = Text("Reality: More here", font_size=16, color=GREEN)
            real_label.next_to(arrow_coherent, LEFT, buff=0.15)
            safe_position(real_label)

            self.play(
                FadeIn(surface_box),
                Write(surface_text),
                FadeIn(coherent_box),
                Write(coherent_text),
                FadeIn(noise_box),
                Write(noise_text),
                GrowArrow(arrow_coherent),
                GrowArrow(arrow_noise),
                FadeIn(model_bias_label),
                FadeIn(real_label),
                run_time=tracker.duration * 0.25,
            )

            # Diagnosis
            diagnosis = Text(
                "Convective parameterizations invert\nthe energy allocation",
                font_size=24,
                color=YELLOW,
                weight=BOLD,
            )
            diagnosis.move_to(UP * 2.5)
            safe_position(diagnosis)

            self.play(Write(diagnosis), run_time=tracker.duration * 0.15)

            self.wait(tracker.duration * 0.12)