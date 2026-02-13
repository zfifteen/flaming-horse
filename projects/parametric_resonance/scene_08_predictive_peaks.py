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
class Scene08PredictivePeaks(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        with self.voiceover(text=SCRIPT["peaks"]) as tracker:
            # Plot with peaks
            axes = Axes(x_range=(0, 1), y_range=(0, 1), x_length=8, y_length=4)
            x_label = Text("f_mod/f_ci", font_size=24).next_to(axes.x_axis, DOWN)
            safe_position(x_label)

            def peaks(x):
                if 0.45 < x < 0.55:
                    return 1
                elif 0.3 < x < 0.36:
                    return 0.8
                elif 0.22 < x < 0.28:
                    return 0.6
                else:
                    return 0.1

            graph = axes.plot(peaks, color=BLUE)

            labels = VGroup(
                Text("1/2", font_size=20).move_to(axes.c2p(0.5, 1.1)),
                Text("1/3", font_size=20).move_to(axes.c2p(0.33, 0.9)),
                Text("1/4", font_size=20).move_to(axes.c2p(0.25, 0.7)),
            )

            comparison = Text(
                "vs Broadband Resonance", font_size=24, color=RED
            ).to_edge(DOWN)
            safe_position(comparison)

            self.play(
                Create(axes),
                Write(x_label),
                Create(graph),
                run_time=tracker.duration * 0.6,
            )
            self.play(FadeIn(labels), run_time=tracker.duration * 0.2)
            self.play(Write(comparison), run_time=tracker.duration * 0.2)