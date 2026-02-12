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
class Scene07OperationalWindow(VoiceoverScene):
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
        with self.voiceover(text=SCRIPT["window"]) as tracker:
            # Phase diagram
            axes = Axes(x_range=(0, 0.2), y_range=(0, 1), x_length=6, y_length=4)
            x_label = Text("Parameter Value", font_size=24).next_to(axes.x_axis, DOWN)
            safe_position(x_label)

            # Operational window band
            band = Rectangle(
                width=axes.x_axis.get_length() * 0.1 / 0.2,
                height=axes.y_axis.get_length(),
                color=GREEN,
                fill_opacity=0.5,
            )
            band.move_to(axes.c2p(0.075, 0.5))
            label = Text("Operational Window", font_size=24, color=GREEN).next_to(
                band, UP
            )
            safe_position(label)

            # Instabilities
            instability = Text("Plasma Instabilities", font_size=24, color=RED).move_to(
                axes.c2p(0.15, 0.8)
            )

            self.play(Create(axes), Write(x_label), run_time=tracker.duration * 0.3)
            self.play(FadeIn(band), Write(label), run_time=tracker.duration * 0.4)
            self.play(Write(instability), run_time=tracker.duration * 0.3)
