from manim import *
import numpy as np

# Python 3.13 Compatibility Patch
import manim_voiceover_plus.services.base as base

original_set_transcription = base.SpeechService.set_transcription


def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self.whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs)


base.SpeechService.set_transcription = patched_set_transcription

# Voiceover Imports
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

# Import Shared Configuration
from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS
from narration_script import SCRIPT

# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560


# Safe Positioning Helper
def safe_position(mobject, max_y=4.0, min_y=-4.0):
    """Ensure mobject stays within safe bounds after positioning"""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject


# Scene Class
class Scene04Examples(VoiceoverScene):
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

        # Animation Sequence
        # Timing budget: 0.5 + 0.5 = 1.0

        with self.voiceover(text=SCRIPT["examples"]) as tracker:
            # Password hashing example
            password = Text("password123", font_size=28)
            password.move_to(LEFT * 3 + UP * 1)
            arrow1 = Arrow(LEFT * 1.5 + UP * 1, RIGHT * 0.5 + UP * 1, buff=0)
            hash_result = Text("a665a459...", font_size=28, color=GREEN)
            hash_result.move_to(RIGHT * 2 + UP * 1)

            slot = tracker.duration * 0.5
            self.play(Write(password), run_time=min(2.0, max(0.3, slot * 0.3)))
            self.play(GrowArrow(arrow1), run_time=min(2.0, max(0.3, slot * 0.3)))
            self.play(Write(hash_result), run_time=min(2.0, max(0.3, slot * 0.4)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))

            # File integrity example
            file_icon = Rectangle(width=1, height=1.5, color=BLUE)
            file_icon.move_to(LEFT * 3 + DOWN * 1)
            arrow2 = Arrow(LEFT * 1.5 + DOWN * 1, RIGHT * 0.5 + DOWN * 1, buff=0)
            checksum = Text("SHA256: abc123...", font_size=24, color=GREEN)
            checksum.move_to(RIGHT * 2 + DOWN * 1)

            slot = tracker.duration * 0.5
            self.play(Create(file_icon), run_time=min(2.0, max(0.3, slot * 0.3)))
            self.play(GrowArrow(arrow2), run_time=min(2.0, max(0.3, slot * 0.3)))
            self.play(Write(checksum), run_time=min(2.0, max(0.3, slot * 0.4)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))
