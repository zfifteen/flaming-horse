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
class Scene04DesignTradeoff(VoiceoverScene):
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
        with self.voiceover(text=SCRIPT["tradeoff"]) as tracker:
            # Optimization landscape
            axes = Axes(x_range=(0, 0.2), y_range=(0, 1), x_length=6, y_length=4)

            def landscape(x):
                return 0.1 if 0.04 < x < 0.06 else 0.01

            graph = axes.plot(landscape, color=BLUE)
            peak = Dot(axes.c2p(0.05, 0.1), color=YELLOW)
            label_peak = Text("Resonance Peak", font_size=24, color=YELLOW).next_to(
                peak, UP
            )
            safe_position(label_peak)

            penalty = Text("10x Penalty Zone", font_size=24, color=RED).to_edge(DOWN)
            safe_position(penalty)

            self.play(
                Create(axes),
                Create(graph),
                FadeIn(peak),
                run_time=tracker.duration * 0.5,
            )
            self.play(Write(label_peak), run_time=tracker.duration * 0.25)
            self.play(Write(penalty), run_time=tracker.duration * 0.25)
