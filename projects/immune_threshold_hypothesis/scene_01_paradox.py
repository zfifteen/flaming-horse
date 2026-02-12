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
class Scene01Paradox(VoiceoverScene):
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
        # Timing budget: Title 0.1, Labels 0.1, Glow expected 0.2, Glow observed 0.1, Numbers 0.3, Rotate 0.2 = 1.0

        with self.voiceover(text=SCRIPT["paradox"]) as tracker:
            # Title
            title = Text("The Immune Threshold Hypothesis", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.1)

            # Population pyramids (simplified as bars for age groups)
            age_groups = ["0-24", "25-44", "45-64", "65+"]
            expected_heights = [0.5, 1.0, 2.0, 3.0]  # Low in young, high in old
            observed_heights = [1.0, 3.0, 2.0, 1.5]  # High in 25-54

            expected_pyramid = VGroup()
            observed_pyramid = VGroup()

            for i, (age, h) in enumerate(zip(age_groups, expected_heights)):
                bar = Rectangle(width=0.8, height=h, color=BLUE).move_to(
                    LEFT * 3 + DOWN * (i * 1.2 - 1)
                )
                label = Text(age, font_size=20).next_to(bar, LEFT)
                safe_position(label)
                expected_pyramid.add(bar, label)

            for i, (age, h) in enumerate(zip(age_groups, observed_heights)):
                bar = Rectangle(width=0.8, height=h, color=RED).move_to(
                    RIGHT * 3 + DOWN * (i * 1.2 - 1)
                )
                label = Text(age, font_size=20).next_to(bar, RIGHT)
                safe_position(label)
                observed_pyramid.add(bar, label)

            expected_label = Text("Expected Trend", font_size=24).move_to(
                LEFT * 3 + UP * 2
            )
            observed_label = Text("Observed Trend 2021-2025", font_size=24).move_to(
                RIGHT * 3 + UP * 2
            )

            self.play(
                FadeIn(expected_label),
                FadeIn(observed_label),
                FadeIn(expected_pyramid),
                FadeIn(observed_pyramid),
                run_time=tracker.duration * 0.1,
            )

            # Glow expected 65+ (last bar)
            expected_65 = expected_pyramid[6]
            self.play(
                expected_65.animate.set_color(YELLOW).set_opacity(0.8),
                run_time=tracker.duration * 0.2,
            )

            # Glow observed 25-44 and 45-64
            observed_25_44 = observed_pyramid[2]  # bar for 25-44 (index 2)
            observed_45_64 = observed_pyramid[4]  # bar for 45-64 (index 4)

            self.play(
                observed_25_44.animate.set_color(YELLOW).set_opacity(0.8),
                observed_45_64.animate.set_color(YELLOW).set_opacity(0.8),
                run_time=tracker.duration * 0.1,
            )

            # Numbers
            women_text = Text("Women <50: +82% vs men", font_size=28)
            women_text.move_to(ORIGIN + DOWN * 2)
            safe_position(women_text)

            crc_text = Text("Ages 45-49 CRC: +17% (2018-2021)", font_size=28)
            crc_text.next_to(women_text, DOWN, buff=0.5)
            safe_position(crc_text)

            self.play(
                FadeIn(women_text), FadeIn(crc_text), run_time=tracker.duration * 0.3
            )

            # Rotate pyramids
            self.play(
                Rotate(expected_pyramid, PI / 6),
                Rotate(observed_pyramid, PI / 6),
                run_time=tracker.duration * 0.2,
            )
