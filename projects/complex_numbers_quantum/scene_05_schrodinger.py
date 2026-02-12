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
class Scene05Schrodinger(VoiceoverScene):
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
        # Timing budget: 0.12 + 0.15 + 0.05 + 0.20 + 0.05 + 0.18 + 0.05 + 0.15 + 0.05 = 1.00

        with self.voiceover(text=SCRIPT["schrodinger"]) as tracker:
            # ── Stage A: Year 1926 (0.12) ─────────────────────────
            year = Text("1926", font_size=96, color=YELLOW, weight=BOLD)
            year.move_to(ORIGIN)
            self.play(Write(year), run_time=2)

            # ── Stage B: Shrink Year + Show Name (0.15) ──────────
            year.generate_target()
            year.target.scale(0.4).move_to(UP * 3.8 + LEFT * 5)

            name = Text("Erwin Schrödinger", font_size=44, color=WHITE)
            name.move_to(UP * 1.5)

            self.play(
                MoveToTarget(year),
                FadeIn(name, shift=UP * 0.3),
                run_time=tracker.duration * 0.15,
            )

            # ── Stage C: Fade Name (0.05) ────────────────────────
            self.play(FadeOut(name), run_time=tracker.duration * 0.05)

            # ── Stage D: Classical Orbit (0.20) ──────────────────
            nucleus = Dot(color=YELLOW, radius=0.15)
            nucleus.move_to(ORIGIN)
            nucleus_label = Text("Nucleus", font_size=18, color=YELLOW)
            nucleus_label.next_to(nucleus, DOWN, buff=0.3)

            orbit_path = Circle(radius=1.5, color=BLUE_C, stroke_width=2)
            orbit_path.move_to(nucleus.get_center())

            electron = Dot(color=BLUE, radius=0.1)
            electron.move_to(orbit_path.point_from_proportion(0))

            orbit_group = VGroup(nucleus, nucleus_label, orbit_path, electron)

            self.play(
                FadeIn(nucleus),
                FadeIn(nucleus_label),
                Create(orbit_path),
                run_time=tracker.duration * 0.10,
            )

            # Animate electron along the orbit (explicit Rotate, NOT always_rotate)
            self.play(
                MoveAlongPath(electron, orbit_path),
                run_time=tracker.duration * 0.10,
            )

            # ── Stage E: Transition Orbit → Wave (0.05 fade + 0.18 wave) ─
            # Fade out orbit
            self.play(
                FadeOut(orbit_path),
                FadeOut(electron),
                FadeOut(nucleus_label),
                run_time=tracker.duration * 0.05,
            )

            # Create wave replacing the orbit area
            wave = FunctionGraph(
                lambda x: 0.5 * np.sin(4 * PI * x),
                x_range=(-2.5, 2.5),
                color=PURPLE,
                stroke_width=4,
            )
            wave.move_to(ORIGIN)

            wave_label = Text("Wave behavior", font_size=24, color=PURPLE)
            wave_label.next_to(wave, DOWN, buff=0.5)
            safe_position(wave_label)

            wave_group = VGroup(wave, wave_label)

            self.play(
                FadeOut(nucleus),
                Create(wave),
                FadeIn(wave_label),
                run_time=tracker.duration * 0.18,
            )

            # ── Stage F: Fade Wave (0.05) ────────────────────────
            self.play(
                FadeOut(wave_group),
                run_time=tracker.duration * 0.05,
            )

            # ── Stage G: Schrödinger Equation (0.15) ─────────────
            equation = MathTex(
                "i\\hbar",
                "\\frac{\\partial \\psi}{\\partial t}",
                "=",
                "\\hat{H}",
                "\\psi",
                font_size=54,
            )
            equation.move_to(ORIGIN)
            equation[0].set_color(GOLD)  # i*hbar
            equation[1].set_color(BLUE)  # dpsi/dt
            equation[3].set_color(GREEN)  # H hat
            equation[4].set_color(BLUE)  # psi

            eq_box = SurroundingRectangle(equation, color=GOLD, buff=0.3)

            eq_label = Text(
                "Schrödinger's Wave Equation",
                font_size=28,
                color=GOLD,
            )
            eq_label.next_to(eq_box, DOWN, buff=0.4)
            safe_position(eq_label)

            self.play(
                Write(equation),
                run_time=2,
            )
            self.play(
                Create(eq_box),
                FadeIn(eq_label),
                run_time=tracker.duration * 0.05,
            )

            # ── Stage H: Hold (0.05) ─────────────────────────────
            self.wait(tracker.duration * 0.05)
