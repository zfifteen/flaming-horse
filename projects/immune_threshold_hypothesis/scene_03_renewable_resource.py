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
class Scene03RenewableResource(VoiceoverScene):
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
        # Timing budget: Pool 0.1, Cancer 0.1, Neutralize 0.1, Regen 0.1, Label 0.1, Threshold 0.1, Split left 0.1, Split right 0.1, Decline left 0.1, Deplete right 0.1, Below 0.05, Survive 0.05 = 1.0

        with self.voiceover(text=SCRIPT["renewable_resource"]) as tracker:
            # Pool and particles
            pool = (
                Circle(radius=2, color=BLUE).set_fill(BLUE, opacity=0.5).move_to(ORIGIN)
            )
            particles = VGroup(
                *[
                    Dot(radius=0.05, color=WHITE).move_to(
                        pool.get_center() + np.random.uniform(-1.5, 1.5, 3)
                    )
                    for _ in range(50)
                ]
            )
            self.play(Create(pool), FadeIn(particles), run_time=tracker.duration * 0.1)

            # Precancerous cells neutralized
            cancer_cell = Dot(radius=0.1, color=BLACK).move_to(
                pool.get_center() + RIGHT * 1
            )
            self.play(FadeIn(cancer_cell), run_time=tracker.duration * 0.1)
            self.play(cancer_cell.animate.scale(0), run_time=tracker.duration * 0.1)

            # Regeneration
            new_particles = VGroup(
                *[
                    Dot(radius=0.05, color=WHITE).move_to(pool.get_bottom() + UP * 0.1)
                    for _ in range(10)
                ]
            )
            self.play(FadeIn(new_particles), run_time=tracker.duration * 0.1)

            # Label
            label = Text("Renewable Resource Model", font_size=28).move_to(UP * 3.8)
            self.play(Write(label), run_time=tracker.duration * 0.1)

            # Threshold line
            threshold_line = Line(
                start=pool.get_left(), end=pool.get_right(), color=RED
            ).move_to(pool.get_center() + DOWN * 0.8)
            threshold_text = Text("SURVEILLANCE THRESHOLD", font_size=20).next_to(
                threshold_line, RIGHT
            )
            safe_position(threshold_text)
            self.play(
                Create(threshold_line),
                Write(threshold_text),
                run_time=tracker.duration * 0.1,
            )

            # Split screen
            left_pool = pool.copy().move_to(LEFT * 3)
            left_particles = particles.copy().move_to(LEFT * 3)
            left_label = Text("Age 70: Gradual decline", font_size=24).next_to(
                left_pool, UP
            )
            safe_position(left_label)
            self.play(
                Transform(pool, left_pool),
                Transform(particles, left_particles),
                Write(left_label),
                run_time=tracker.duration * 0.1,
            )

            right_pool = pool.copy().move_to(RIGHT * 3)
            right_particles = particles.copy().move_to(RIGHT * 3)
            right_label = Text("Age 40: Rapid depletion", font_size=24).next_to(
                right_pool, UP
            )
            safe_position(right_label)
            self.play(
                FadeIn(right_pool),
                FadeIn(right_particles),
                Write(right_label),
                run_time=tracker.duration * 0.1,
            )

            # Gradual decline left
            self.play(
                left_particles.animate.shift(DOWN * 0.5),
                run_time=tracker.duration * 0.1,
            )

            # Rapid depletion right
            self.play(
                right_particles.animate.shift(DOWN * 1.5),
                run_time=tracker.duration * 0.1,
            )

            # Below threshold
            self.play(
                right_particles.animate.set_color(RED), run_time=tracker.duration * 0.05
            )

            # Cancer cells survive
            surviving_cancer = VGroup(
                *[
                    Dot(radius=0.1, color=BLACK).move_to(
                        right_pool.get_center() + np.random.uniform(-1, 1, 3)
                    )
                    for _ in range(5)
                ]
            )
            self.play(FadeIn(surviving_cancer), run_time=tracker.duration * 0.05)
