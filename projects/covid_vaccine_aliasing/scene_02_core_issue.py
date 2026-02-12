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
class Scene02CoreIssue(VoiceoverScene):
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
        # Timing budget: 0.3 + 0.3 + 0.4 = 1.0

        with self.voiceover(text=SCRIPT["core_issue"]) as tracker:
            # Title
            title = Text("The Core Issue", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.3)

            # Timeline with wave and decay
            axes = Axes(
                x_range=[0, 12, 1],
                y_range=[0, 5, 1],
                axis_config={"include_numbers": True},
            )
            axes.move_to(ORIGIN)
            wave = axes.plot(lambda x: 2 + np.sin(x * 2), color=BLUE, x_range=[0, 12])
            decay = axes.plot(lambda x: 4 * np.exp(-x / 3), color=RED, x_range=[0, 12])
            self.play(
                Create(axes),
                Create(wave),
                Create(decay),
                run_time=tracker.duration * 0.3,
            )

            # Highlight overlap with label
            label = Text("Aliasing Overlap", color=YELLOW, font_size=32)
            label.next_to(axes, DOWN, buff=0.5)
            safe_position(label)
            self.play(FadeIn(label), run_time=tracker.duration * 0.4)
