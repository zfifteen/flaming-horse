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
class Scene01Intro(VoiceoverScene):
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
        # Timing budget: 0.4 + 0.3 + 0.3 = 1.0

        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            # Title (ALWAYS use UP * 3.8, NEVER .to_edge(UP))
            title = Text(
                "Temporal Aliasing in COVID-19 Vaccine Mortality Data",
                font_size=48,
                weight=BOLD,
            )
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.4)

            # Radio wave image as overlay
            radio_image = ImageMobject("assets/radio_spectrum.svg", scale=0.3)
            radio_image.move_to(ORIGIN)
            safe_position(radio_image)
            self.play(FadeIn(radio_image), run_time=tracker.duration * 0.3)

            # Text waves as additional
            wave1 = Text("Blue Wave", color=BLUE, font_size=32)
            wave1.next_to(radio_image, DOWN, buff=0.5)
            safe_position(wave1)
            wave2 = Text("Red Wave", color=RED, font_size=32)
            wave2.next_to(wave1, DOWN, buff=0.5)
            safe_position(wave2)
            self.play(FadeIn(wave1), FadeIn(wave2), run_time=tracker.duration * 0.3)
