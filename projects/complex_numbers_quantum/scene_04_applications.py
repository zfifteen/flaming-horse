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
class Scene04Applications(VoiceoverScene):
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

        # ── Pre-calculate Layout ───────────────────────────────────
        # 5 icons in a row, evenly spaced
        icon_y = UP * 0.5
        icon_positions = [
            LEFT * 6 + icon_y,
            LEFT * 3 + icon_y,
            ORIGIN + icon_y,
            RIGHT * 3 + icon_y,
            RIGHT * 6 + icon_y,
        ]
        label_colors = [BLUE, YELLOW, GREEN, RED, TEAL]
        label_texts = [
            "Smartphone",
            "Fiber Optics",
            "Power Grid",
            "Airplane",
            "Skyscraper",
        ]

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: 0.12 + 5*0.12 + 0.05 + 0.18 + 0.05 = 1.00

        with self.voiceover(text=SCRIPT["applications"]) as tracker:
            # ── Stage A: Title (0.12) ─────────────────────────────
            title = Text(
                "Real-World Applications",
                font_size=44,
                color=WHITE,
                weight=BOLD,
            )
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=2)

            # ── Stage B: Icons One By One (5 * 0.12 = 0.60) ──────
            all_icons = VGroup()
            all_labels = VGroup()

            for idx in range(5):
                pos = icon_positions[idx]
                color = label_colors[idx]

                # Create icon based on type
                if idx == 0:
                    # Smartphone: sine wave + phone rectangle
                    wave = FunctionGraph(
                        lambda x: 0.3 * np.sin(3 * PI * x),
                        x_range=(-0.5, 0.5),
                        color=color,
                        stroke_width=3,
                    )
                    phone = Rectangle(
                        width=0.6,
                        height=1.0,
                        color=GRAY,
                        fill_opacity=0.3,
                        stroke_width=2,
                    )
                    icon = VGroup(phone, wave)
                elif idx == 1:
                    # Fiber optics: line with glowing dot
                    fiber = Line(LEFT * 0.6, RIGHT * 0.6, color=WHITE, stroke_width=3)
                    glow = Dot(color=color, radius=0.08)
                    glow.move_to(fiber.get_center())
                    icon = VGroup(fiber, glow)
                elif idx == 2:
                    # Power grid: simple grid pattern
                    h_lines = VGroup(
                        *[
                            Line(
                                LEFT * 0.5, RIGHT * 0.5, color=color, stroke_width=2
                            ).shift(UP * d)
                            for d in [-0.3, 0, 0.3]
                        ]
                    )
                    v_lines = VGroup(
                        *[
                            Line(
                                DOWN * 0.4, UP * 0.4, color=color, stroke_width=2
                            ).shift(RIGHT * d)
                            for d in [-0.3, 0, 0.3]
                        ]
                    )
                    icon = VGroup(h_lines, v_lines)
                elif idx == 3:
                    # Airplane: simple triangle shape
                    body = Polygon(
                        [-0.5, 0, 0],
                        [0.5, 0, 0],
                        [0, 0.4, 0],
                        color=color,
                        fill_opacity=0.4,
                        stroke_width=2,
                    )
                    wing = Line(LEFT * 0.7, RIGHT * 0.7, color=color, stroke_width=2)
                    wing.shift(DOWN * 0.1)
                    icon = VGroup(body, wing)
                else:
                    # Skyscraper: tall rectangle
                    building = Rectangle(
                        width=0.4,
                        height=1.2,
                        color=color,
                        fill_opacity=0.3,
                        stroke_width=2,
                    )
                    # Windows
                    windows = VGroup()
                    for row in range(4):
                        for col in range(2):
                            w = Square(side_length=0.08, color=YELLOW, fill_opacity=0.8)
                            w.move_to(
                                building.get_center()
                                + UP * (0.35 - row * 0.25)
                                + RIGHT * (col * 0.15 - 0.075)
                            )
                            windows.add(w)
                    icon = VGroup(building, windows)

                icon.move_to(pos)

                label = Text(label_texts[idx], font_size=20, color=color)
                label.next_to(icon, DOWN, buff=0.3)
                safe_position(label)

                all_icons.add(icon)
                all_labels.add(label)

                self.play(
                    FadeIn(icon, scale=0.7),
                    FadeIn(label),
                    run_time=tracker.duration * 0.12,
                )

            # ── Stage C: Fade Title (0.05) ────────────────────────
            self.play(FadeOut(title), run_time=tracker.duration * 0.05)

            # ── Stage D: Final Statement (0.18) ──────────────────
            final_text = Text(
                "No Complex Numbers = No Modern Technology",
                font_size=36,
                color=RED,
                weight=BOLD,
            )
            final_text.move_to(DOWN * 2.5)
            safe_position(final_text)

            # Underline for emphasis
            underline = Underline(final_text, color=RED, buff=0.1)

            self.play(
                Write(final_text),
                Create(underline),
                run_time=2,
            )

            # ── Stage E: Hold (0.05) ─────────────────────────────
            self.wait(tracker.duration * 0.05)
