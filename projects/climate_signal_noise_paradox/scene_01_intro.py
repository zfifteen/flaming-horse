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
class Scene01Intro(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: title 0.10 + diagram 0.25 + arrows 0.25 + label 0.10 + tropics 0.20 + wait 0.10 = 1.0

        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            # Title
            title = Text(
                "Why Climate Models Fail",
                font_size=48,
                weight=BOLD,
            )
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.10)

            # Atmosphere diagram: vertical layers
            layers = VGroup()
            layer_labels = []
            colors = [BLUE_E, BLUE_D, BLUE_C, BLUE_B, BLUE_A]
            names = [
                "Surface",
                "Lower Tropo.",
                "Mid Tropo.",
                "Upper Tropo.",
                "Stratosphere",
            ]
            for i in range(5):
                rect = Rectangle(
                    width=10,
                    height=1.0,
                    fill_color=colors[i],
                    fill_opacity=0.4,
                    stroke_color=WHITE,
                    stroke_width=1,
                )
                rect.move_to(DOWN * 2.5 + UP * i * 1.1)
                layers.add(rect)
                lbl = Text(names[i], font_size=16, color=WHITE)
                lbl.move_to(rect.get_left() + RIGHT * 1.2)
                layer_labels.append(lbl)

            layer_label_group = VGroup(*layer_labels)
            safe_position(layers)
            safe_position(layer_label_group)

            self.play(
                FadeIn(layers, shift=UP * 0.3, lag_ratio=0.15),
                FadeIn(layer_label_group, lag_ratio=0.15),
                run_time=tracker.duration * 0.25,
            )

            # Energy flow arrows: Signal (organized, left side) vs Noise (chaotic, right side)
            signal_arrow = Arrow(
                start=layers[0].get_center() + LEFT * 3,
                end=layers[4].get_center() + LEFT * 3,
                color=GREEN,
                stroke_width=6,
                buff=0.1,
            )
            signal_label = Text("Forced\nSignal", font_size=18, color=GREEN)
            signal_label.next_to(signal_arrow, LEFT, buff=0.3)
            safe_position(signal_label)

            noise_arrows = VGroup()
            np.random.seed(42)
            for _ in range(8):
                start_y = np.random.uniform(-2.5, 1.5)
                end_y = start_y + np.random.uniform(-0.8, 0.8)
                start_x = np.random.uniform(2.5, 4.5)
                end_x = start_x + np.random.uniform(-1.0, 1.0)
                arr = Arrow(
                    start=np.array([start_x, start_y, 0]),
                    end=np.array([end_x, end_y, 0]),
                    color=RED_C,
                    stroke_width=3,
                    buff=0.0,
                )
                noise_arrows.add(arr)

            noise_label = Text(
                "Internal\nVariability\n(Noise)", font_size=18, color=RED_C
            )
            noise_label.move_to(RIGHT * 5 + UP * 0.5)
            safe_position(noise_label)

            self.play(
                GrowArrow(signal_arrow),
                FadeIn(signal_label),
                LaggedStart(*[GrowArrow(a) for a in noise_arrows], lag_ratio=0.1),
                FadeIn(noise_label),
                run_time=tracker.duration * 0.25,
            )

            # Key insight label
            insight = Text(
                "Models: Too much noise, too little signal",
                font_size=24,
                color=YELLOW,
            )
            insight.move_to(UP * 3.0)
            safe_position(insight)
            self.play(Write(insight), run_time=tracker.duration * 0.10)

            # Highlight tropics with a glowing band
            tropics_band = Rectangle(
                width=10,
                height=1.0,
                fill_color=ORANGE,
                fill_opacity=0.3,
                stroke_color=ORANGE,
                stroke_width=2,
            )
            tropics_band.move_to(layers[1].get_center())
            tropics_label = Text(
                "Tropical Latent Heat Redistribution",
                font_size=20,
                color=ORANGE,
            )
            tropics_label.next_to(tropics_band, DOWN, buff=0.15)
            safe_position(tropics_label)

            self.play(
                FadeIn(tropics_band),
                Write(tropics_label),
                run_time=tracker.duration * 0.20,
            )

            self.wait(tracker.duration * 0.10)