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
class Scene05TraditionalVsParametric(VoiceoverScene):
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
        with self.voiceover(text=SCRIPT["traditional"]) as tracker:
            # Traditional plot
            axes1 = Axes(x_range=(0, 1), y_range=(0, 1), x_length=3, y_length=3)
            axes1.move_to(LEFT * 3)
            line1 = axes1.plot(lambda x: x, color=RED)
            label1 = Text("Traditional\nLinear", font_size=20, color=RED).next_to(
                axes1, DOWN
            )
            safe_position(label1)

            # Parametric plot
            axes2 = Axes(x_range=(0, 1), y_range=(0, 1), x_length=3, y_length=3)
            axes2.move_to(RIGHT * 3)

            def peak(x):
                return np.exp(-50 * (x - 0.05) ** 2)

            line2 = axes2.plot(peak, color=GREEN)
            label2 = Text("Parametric\nPeak", font_size=20, color=GREEN).next_to(
                axes2, DOWN
            )
            safe_position(label2)

            self.play(
                Create(axes1),
                Create(line1),
                Write(label1),
                run_time=tracker.duration * 0.5,
            )
            self.play(
                Create(axes2),
                Create(line2),
                Write(label2),
                run_time=tracker.duration * 0.5,
            )
