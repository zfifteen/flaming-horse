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
class Scene04Evidence(VoiceoverScene):
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
        # Timing budget: Calculate BEFORE writing animations
        # Example: 0.4 + 0.3 + 0.3 = 1.0 ✓

        with self.voiceover(text=SCRIPT["evidence"]) as tracker:
            # Title (ALWAYS use UP * 3.8, NEVER .to_edge(UP))
            title = Text("Empirical Evidence", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.2)

            # Plot experimental data
            axes = (
                Axes(
                    x_range=[0, 10, 1],
                    y_range=[0, 100, 10],
                    axis_config={"color": WHITE},
                    tips=False,
                )
                .scale(0.6)
                .move_to(ORIGIN)
            )
            data_points = [
                Dot(axes.coords_to_point(x, 10 * x + np.random.uniform(-5, 5)))
                for x in range(1, 10)
            ]
            plot = VGroup(axes, *data_points)
            plot.next_to(title, DOWN, buff=0.5)
            safe_position(plot)
            self.play(Create(axes), run_time=tracker.duration * 0.2)
            self.play(
                *[Create(dot) for dot in data_points], run_time=tracker.duration * 0.2
            )

            # Animate study results
            bars = VGroup()
            for i in range(3):
                bar = Rectangle(
                    width=0.5, height=20 + i * 10, color=BLUE, fill_opacity=0.5
                )
                bar.move_to(axes.coords_to_point(2 + i, 10))
                bars.add(bar)
            self.play(*[Create(bar) for bar in bars], run_time=tracker.duration * 0.2)

            # Compare predictions vs observations
            pred_line = axes.plot(lambda x: 10 * x, color=GREEN)
            obs_points = [Dot(axes.coords_to_point(x, 10 * x + 15)) for x in [3, 5, 7]]
            self.play(Create(pred_line), run_time=tracker.duration * 0.1)
            self.play(
                *[Create(dot) for dot in obs_points], run_time=tracker.duration * 0.1
            )
