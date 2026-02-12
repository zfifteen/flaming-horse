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
class Scene03Disagree(VoiceoverScene):
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

        with self.voiceover(text=SCRIPT["disagreements"]) as tracker:
            # 1. Three Interpretations
            # Duration allocation: ~50%

            # Setup columns
            col_width = config.frame_width / 3

            # Claude (Left)
            claude_title = Text(
                "Claude: Intentional", font_size=32, color="#D97757"
            ).move_to(LEFT * col_width + UP * 3)
            claude_gear = VGroup(
                Gear(teeth=12, fill_color=GREY).scale(0.8),
                Gear(teeth=8, fill_color=WHITE)
                .scale(0.5)
                .shift(RIGHT * 1 + DOWN * 0.5),
            ).move_to(LEFT * col_width)
            claude_quote = Text(
                "'Not Dysfunction'", font_size=20, slant=ITALIC
            ).next_to(claude_gear, DOWN)

            # Kimi (Center)
            kimi_title = Text("Kimi: Targeted", font_size=32, color="#5CA5F2").move_to(
                UP * 3
            )
            kimi_scope = Cross(Circle(radius=1, color=RED), stroke_color=RED).move_to(
                ORIGIN
            )
            kimi_weight = Square(side_length=1, color=GREY, fill_opacity=0.5).move_to(
                DOWN * 1.5
            )
            kimi_label = Text("Inertia", font_size=20).move_to(kimi_weight)

            # Grok (Right)
            grok_title = Text("Grok: Structural", font_size=32, color=GREEN).move_to(
                RIGHT * col_width + UP * 3
            )
            grok_building = Rectangle(width=2, height=3, color=WHITE).move_to(
                RIGHT * col_width
            )
            # Add cracks
            cracks = VGroup(
                Line(
                    grok_building.get_bottom(), grok_building.get_center(), color=GREY
                ),
                Line(
                    grok_building.get_corner(DL), grok_building.get_right(), color=GREY
                ),
            )

            self.play(
                Write(claude_title),
                FadeIn(claude_gear),
                Write(claude_quote),
                Write(kimi_title),
                FadeIn(kimi_scope),
                FadeIn(kimi_weight),
                Write(kimi_label),
                Write(grok_title),
                Create(grok_building),
                Create(cracks),
                run_time=tracker.duration * 0.4,
            )

            # Rotate gears
            self.play(
                Rotate(claude_gear[0], angle=PI),
                Rotate(claude_gear[1], angle=-PI),
                run_time=tracker.duration * 0.1,
            )

            # 2. Specific Findings (Highlighting)
            # Duration allocation: ~50%

            # Claude: Oversight Capture
            # Focus on Left column, dim others
            self.play(
                kimi_title.animate.set_opacity(0.3),
                kimi_scope.animate.set_opacity(0.3),
                kimi_weight.animate.set_opacity(0.3),
                kimi_label.animate.set_opacity(0.3),
                grok_title.animate.set_opacity(0.3),
                grok_building.animate.set_opacity(0.3),
                cracks.animate.set_opacity(0.3),
                run_time=tracker.duration * 0.05,
            )

            handshake_icon = VGroup(
                Circle(radius=0.3, color=BLUE).shift(LEFT * 0.3),
                Circle(radius=0.3, color=RED).shift(RIGHT * 0.3),
            ).next_to(claude_quote, DOWN, buff=0.5)

            capture_text = Text("Oversight Capture", font_size=24, color=RED).next_to(
                handshake_icon, DOWN
            )

            self.play(
                FadeIn(handshake_icon),
                Write(capture_text),
                run_time=tracker.duration * 0.1,
            )

            # Grok: FBI Layer
            # Focus on Right column
            self.play(
                claude_title.animate.set_opacity(0.3),
                claude_gear.animate.set_opacity(0.3),
                claude_quote.animate.set_opacity(0.3),
                capture_text.animate.set_opacity(0.3),
                handshake_icon.animate.set_opacity(0.3),
                grok_title.animate.set_opacity(1),
                grok_building.animate.set_opacity(1),
                cracks.animate.set_opacity(1),
                run_time=tracker.duration * 0.05,
            )

            fbi_box = Rectangle(width=1, height=0.6, color=BLUE).move_to(
                grok_building.get_center() + UP * 0.5 + LEFT * 0.5
            )
            fbi_lbl = Text("FBI", font_size=16).move_to(fbi_box)

            doj_box = Rectangle(width=1, height=0.6, color=GREY).move_to(
                grok_building.get_center() + DOWN * 0.5 + RIGHT * 0.5
            )
            doj_lbl = Text("DOJ", font_size=16).move_to(doj_box)

            # Document moves
            doc = Rectangle(width=0.2, height=0.3, color=WHITE, fill_opacity=1).move_to(
                fbi_box
            )

            self.play(
                FadeIn(fbi_box),
                Write(fbi_lbl),
                FadeIn(doj_box),
                Write(doj_lbl),
                FadeIn(doc),
                run_time=tracker.duration * 0.05,
            )

            # Doc turns black (redacted) IN FBI box
            self.play(doc.animate.set_color(BLACK), run_time=tracker.duration * 0.05)

            # Move to DOJ
            self.play(doc.animate.move_to(doj_box), run_time=tracker.duration * 0.1)

            # Label
            suppress_text = Text("Pre-Redaction", font_size=20, color=RED).next_to(
                doj_box, DOWN
            )
            self.play(Write(suppress_text), run_time=tracker.duration * 0.05)


# ── Helper Class for Gear ──────────────────────────────────────────
class Gear(VMobject):
    def __init__(self, teeth=12, **kwargs):
        super().__init__(**kwargs)
        self.teeth = teeth
        self.inner_radius = 0.5
        self.outer_radius = 0.7
        self.add_teeth()

    def add_teeth(self):
        angle = TAU / self.teeth
        points = []
        for i in range(self.teeth):
            theta = i * angle
            # Inner point
            points.append(
                np.array(
                    [
                        np.cos(theta) * self.inner_radius,
                        np.sin(theta) * self.inner_radius,
                        0,
                    ]
                )
            )
            # Outer points (tooth)
            theta_tooth_start = theta + angle * 0.2
            theta_tooth_end = theta + angle * 0.8
            points.append(
                np.array(
                    [
                        np.cos(theta_tooth_start) * self.outer_radius,
                        np.sin(theta_tooth_start) * self.outer_radius,
                        0,
                    ]
                )
            )
            points.append(
                np.array(
                    [
                        np.cos(theta_tooth_end) * self.outer_radius,
                        np.sin(theta_tooth_end) * self.outer_radius,
                        0,
                    ]
                )
            )

        self.set_points_as_corners(points)
        self.close_path()
