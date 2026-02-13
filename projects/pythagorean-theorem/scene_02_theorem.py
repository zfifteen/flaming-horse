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
class Scene02Theorem(VoiceoverScene):
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
        # Timing budget: 0.3 + 0.3 + 0.3 + 0.1 = 1.0

        with self.voiceover(text=SCRIPT["theorem"]) as tracker:
            # Title
            title = Text("The Pythagorean Theorem", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.3)

            # Right triangle
            triangle = Polygon(
                np.array([0, 0, 0]),
                np.array([3, 0, 0]),
                np.array([0, 2, 0]),
                color=BLUE,
            )
            triangle.move_to(ORIGIN)
            self.play(Create(triangle), run_time=tracker.duration * 0.3)

            # Labels
            label_a = MathTex("a")
            label_a.next_to(triangle, DOWN, buff=0.1)
            safe_position(label_a)

            label_b = MathTex("b")
            label_b.next_to(triangle, LEFT, buff=0.1)
            safe_position(label_b)

            label_c = MathTex("c")
            label_c.move_to(triangle.get_center() + np.array([1.5, 1, 0]))
            safe_position(label_c)

            labels = VGroup(label_a, label_b, label_c)
            self.play(Write(labels), run_time=tracker.duration * 0.3)

            self.wait(tracker.duration * 0.1)
