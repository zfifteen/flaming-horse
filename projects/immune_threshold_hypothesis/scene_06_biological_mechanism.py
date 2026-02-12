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
class Scene06BiologicalMechanism(VoiceoverScene):
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
        # Timing budget: 0.1 + 0.1 + 0.2 + 0.1 + 0.05 + 0.05 + 0.1 + 0.1 + 0.2 = 1.0 ✓

        with self.voiceover(text=SCRIPT["biological_mechanism"]) as tracker:
            # T cells
            t_cell = Circle(radius=0.3, color=BLUE).move_to(LEFT * 2)
            t_label = Text("T Cell", font_size=16).next_to(t_cell, DOWN)
            safe_position(t_label)
            cancer_cell = Circle(radius=0.2, color=BLACK).move_to(RIGHT * 2)
            cancer_label = Text("Cancer Cell", font_size=16).next_to(cancer_cell, DOWN)
            safe_position(cancer_label)
            self.play(
                Create(t_cell),
                Write(t_label),
                Create(cancer_cell),
                Write(cancer_label),
                run_time=tracker.duration * 0.1,
            )

            # Normal elimination
            self.play(
                t_cell.animate.move_to(cancer_cell.get_center()),
                cancer_cell.animate.scale(0),
                run_time=tracker.duration * 0.1,
            )

            # After stimulation
            exhausted_t = Circle(radius=0.3, color=GRAY).move_to(LEFT * 2)
            regulatory_t = Circle(radius=0.25, color=PURPLE).move_to(LEFT * 1)
            igg4 = Triangle(color=YELLOW).move_to(ORIGIN)
            igg4_label = Text("IgG4 Antibody", font_size=16).next_to(igg4, DOWN)
            safe_position(igg4_label)
            self.play(
                Transform(t_cell, exhausted_t),
                FadeIn(regulatory_t),
                FadeIn(igg4),
                Write(igg4_label),
                run_time=tracker.duration * 0.2,
            )

            # Tolerance mode
            tolerance_text = Text(
                "Tolerance Mode: Immune evasion enabled", font_size=24
            ).move_to(UP * 2)
            safe_position(tolerance_text)
            self.play(Write(tolerance_text), run_time=tracker.duration * 0.1)

            # Cancer survives
            new_cancer = Circle(radius=0.2, color=BLACK).move_to(RIGHT * 2)
            self.play(FadeIn(new_cancer), run_time=tracker.duration * 0.05)
            self.play(new_cancer.animate.scale(1.5), run_time=tracker.duration * 0.05)

            # Citation
            citation = Text(
                "Elevated IgG4 ↔ worse outcomes in pancreatic cancer patients (2025 study)",
                font_size=18,
            ).move_to(DOWN * 2)
            safe_position(citation)
            self.play(Write(citation), run_time=tracker.duration * 0.1)

            # Transition to macro
            incidence_curve = (
                VMobject()
                .set_points_as_corners(
                    [LEFT * 3 + DOWN * 1, ORIGIN + DOWN * 1, RIGHT * 3 + UP * 1]
                )
                .set_stroke(RED, 4)
            )
            self.play(Create(incidence_curve), run_time=tracker.duration * 0.1)
            self.wait(tracker.duration * 0.2)
