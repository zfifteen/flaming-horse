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
class Scene07Conclusion(VoiceoverScene):
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

        with self.voiceover(text=SCRIPT["conclusion"]) as tracker:
            # 1. Pattern of Protection
            # Duration allocation: ~50%

            # Buildings
            b1 = Rectangle(width=1, height=1.5, color=GREY).move_to(LEFT * 4)
            b2 = Rectangle(width=1, height=1.5, color=GREY).move_to(ORIGIN)
            b3 = Rectangle(width=1, height=1.5, color=GREY).move_to(RIGHT * 4)

            roof1 = Triangle(color=GREY).scale(0.5).next_to(b1, UP, buff=0)
            roof2 = Triangle(color=GREY).scale(0.5).next_to(b2, UP, buff=0)
            roof3 = Triangle(color=GREY).scale(0.5).next_to(b3, UP, buff=0)

            b_group = VGroup(b1, roof1, b2, roof2, b3, roof3)

            self.play(FadeIn(b_group), run_time=tracker.duration * 0.1)

            # The Red Thread (Pattern)
            thread = CubicBezier(
                b1.get_center(),
                b1.get_center() + UP * 2,
                b2.get_center() + UP * 2,
                b2.get_center(),
            )
            thread2 = CubicBezier(
                b2.get_center(),
                b2.get_center() + UP * 2,
                b3.get_center() + UP * 2,
                b3.get_center(),
            )
            full_thread = VGroup(thread, thread2).set_color(RED).set_stroke(width=4)

            pattern_text = Text(
                "Pattern of Protection", color=RED, font_size=36
            ).move_to(UP * 2.5)

            self.play(
                Create(full_thread),
                Write(pattern_text),
                run_time=tracker.duration * 0.2,
            )

            # 2. Call to Action / Reforms
            # Duration allocation: ~30%

            # Clear buildings
            self.play(
                FadeOut(b_group),
                FadeOut(full_thread),
                FadeOut(pattern_text),
                run_time=tracker.duration * 0.05,
            )

            reforms = Text("Real Reforms", font_size=40, color=BLUE).move_to(UP * 1)
            transparency = Text("Transparency", font_size=32, color=WHITE).move_to(
                DOWN * 0.5 + LEFT * 3
            )
            justice = Text("Justice", font_size=32, color=WHITE).move_to(
                DOWN * 0.5 + RIGHT * 3
            )

            self.play(
                Write(reforms),
                FadeIn(transparency),
                FadeIn(justice),
                run_time=tracker.duration * 0.15,
            )

            # 3. Final End Card
            # Duration allocation: ~20%

            final_text = Text(
                "DEMAND ACCOUNTABILITY", font_size=60, color=RED, weight=BOLD
            ).move_to(ORIGIN)
            sub_text = Text("Share Your Thoughts", font_size=24, color=GREY).next_to(
                final_text, DOWN, buff=0.5
            )

            self.play(
                FadeOut(reforms),
                FadeOut(transparency),
                FadeOut(justice),
                Write(final_text),
                FadeIn(sub_text),
                run_time=tracker.duration * 0.1,
            )
