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
class Scene06WaveFunction(VoiceoverScene):
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
        # Timing budget: 0.20 + 0.05 + 0.20 + 0.05 + 0.15 + 0.05 + 0.15 + 0.10 + 0.05 = 1.00

        with self.voiceover(text=SCRIPT["wave_function"]) as tracker:
            # ── Stage A: Complex Wave Components (0.20) ───────────
            # Title
            psi_title = MathTex(
                "\\psi(x) = ",
                "\\text{Re}",
                " + i\\,",
                "\\text{Im}",
                font_size=42,
            )
            psi_title[1].set_color(BLUE)
            psi_title[3].set_color(YELLOW)
            psi_title.move_to(UP * 3.8)
            safe_position(psi_title)

            # Real part (blue sine)
            real_wave = FunctionGraph(
                lambda x: 0.8 * np.sin(2 * PI * x),
                x_range=(-3, 3),
                color=BLUE,
                stroke_width=3,
            )
            real_wave.move_to(UP * 0.8)

            real_label = Text("Real part", font_size=22, color=BLUE)
            real_label.next_to(real_wave, RIGHT, buff=0.3)

            # Imaginary part (yellow cosine)
            imag_wave = FunctionGraph(
                lambda x: 0.8 * np.cos(2 * PI * x),
                x_range=(-3, 3),
                color=YELLOW,
                stroke_width=3,
            )
            imag_wave.move_to(DOWN * 1.5)

            imag_label = Text("Imaginary part", font_size=22, color=YELLOW)
            imag_label.next_to(imag_wave, RIGHT, buff=0.3)

            wave_group = VGroup(psi_title, real_wave, real_label, imag_wave, imag_label)

            self.play(
                Write(psi_title),
                Create(real_wave),
                FadeIn(real_label),
                Create(imag_wave),
                FadeIn(imag_label),
                run_time=2,
            )

            # ── Stage B: Fade Wave Components (0.05) ──────────────
            self.play(
                FadeOut(real_label),
                FadeOut(imag_label),
                FadeOut(psi_title),
                run_time=tracker.duration * 0.05,
            )

            # ── Stage C: Magnitude Squared → Probability (0.20) ──
            mag_label = MathTex(
                "|\\psi|^{2}",
                font_size=54,
                color=PURPLE,
            )
            mag_label.move_to(UP * 3.8)
            safe_position(mag_label)

            arrow = MathTex("\\Rightarrow", font_size=48, color=WHITE)
            arrow.next_to(mag_label, RIGHT, buff=0.3)

            prob_text = Text("Probability", font_size=32, color=PURPLE)
            prob_text.next_to(arrow, RIGHT, buff=0.3)

            header_group = VGroup(mag_label, arrow, prob_text)
            header_group.move_to(UP * 3.8)
            safe_position(header_group)

            # Probability density curve (always positive)
            prob_curve = FunctionGraph(
                lambda x: 0.5 + 0.4 * np.sin(PI * x) ** 2,
                x_range=(-3, 3),
                color=PURPLE,
                stroke_width=4,
                fill_opacity=0.2,
            )
            prob_curve.move_to(ORIGIN)

            self.play(
                FadeIn(header_group),
                ReplacementTransform(real_wave, prob_curve),
                FadeOut(imag_wave),
                run_time=2,
            )

            # ── Stage D: Fade Probability Curve (0.05) ───────────
            self.play(
                FadeOut(prob_curve),
                FadeOut(header_group),
                run_time=tracker.duration * 0.05,
            )

            # ── Stage E: Electron Probability Cloud (0.15) ───────
            cloud_title = Text(
                "Electron Probability Cloud",
                font_size=36,
                color=PURPLE,
                weight=BOLD,
            )
            cloud_title.move_to(UP * 3.8)

            nucleus = Dot(color=YELLOW, radius=0.15)
            nucleus.move_to(ORIGIN)
            nuc_label = MathTex("+", font_size=24, color=YELLOW)
            nuc_label.move_to(nucleus.get_center())

            # Probability cloud: dots distributed radially with varying opacity
            electron_cloud = VGroup()
            np.random.seed(42)
            for i in range(40):
                angle = i * TAU / 40 + np.random.uniform(-0.2, 0.2)
                radius = 0.8 + 0.6 * np.random.random()
                opacity = max(0.2, 1.0 - radius / 1.8)
                dot = Dot(
                    color=PURPLE,
                    radius=0.04,
                    fill_opacity=opacity,
                )
                dot.move_to(
                    ORIGIN + radius * np.array([np.cos(angle), np.sin(angle), 0])
                )
                electron_cloud.add(dot)

            cloud_group = VGroup(cloud_title, nucleus, nuc_label, electron_cloud)

            self.play(
                Write(cloud_title),
                FadeIn(nucleus),
                FadeIn(nuc_label),
                FadeIn(electron_cloud, lag_ratio=0.05),
                run_time=tracker.duration * 0.15,
            )

            # ── Stage F: Fade Cloud (0.05) ───────────────────────
            self.play(
                FadeOut(cloud_group),
                run_time=tracker.duration * 0.05,
            )

            # ── Stage G: Final Statement (0.15) ──────────────────
            final = Text(
                "Complex Numbers → Quantum Reality",
                font_size=44,
                color=GOLD,
                weight=BOLD,
            )
            final.move_to(UP * 0.5)

            subtitle = Text(
                "Without them, the atomic world\nwould still be a mystery.",
                font_size=28,
                color=WHITE,
            )
            subtitle.next_to(final, DOWN, buff=0.8)
            safe_position(subtitle)

            self.play(
                Write(final),
                run_time=2,
            )
            self.play(
                FadeIn(subtitle, shift=UP * 0.2),
                run_time=tracker.duration * 0.05,
            )

            # ── Stage H: Fade to Black (0.10) ───────────────────
            all_remaining = VGroup(final, subtitle)
            self.play(
                FadeOut(all_remaining),
                run_time=tracker.duration * 0.10,
            )

            # ── Buffer (0.05) ────────────────────────────────────
            self.wait(tracker.duration * 0.05)
