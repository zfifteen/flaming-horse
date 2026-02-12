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
class Scene02Agree(VoiceoverScene):
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

        with self.voiceover(text=SCRIPT["agreements"]) as tracker:
            # 1. Wexner Redaction (Surgical Precision)
            # Duration allocation: ~25%

            # Document graphic
            doc = Rectangle(width=6, height=8, color=WHITE, fill_opacity=0.1)
            lines = VGroup(
                *[
                    Line(
                        start=LEFT * 2.5, end=RIGHT * 2.5, color=GREY, stroke_width=2
                    ).shift(UP * (3 - i * 0.5))
                    for i in range(12)
                ]
            )
            doc_group = VGroup(doc, lines).move_to(LEFT * 3)

            wexner_count = Integer(0).scale(1.5).move_to(RIGHT * 3 + UP * 1)
            count_label = Text("Mentions Found", font_size=24).next_to(
                wexner_count, DOWN
            )

            self.play(
                FadeIn(doc_group),
                FadeIn(wexner_count),
                FadeIn(count_label),
                run_time=tracker.duration * 0.05,
            )

            # Count up quickly
            self.play(
                ChangeDecimalToValue(wexner_count, 4000),
                run_time=tracker.duration * 0.1,
            )

            # The "One" critical instance
            critical_text = Text(
                "CO-CONSPIRATOR", color=RED, font_size=36, weight=BOLD
            ).move_to(doc_group.get_center())
            self.play(Write(critical_text), run_time=tracker.duration * 0.05)

            # Redact it
            redaction_bar = Rectangle(
                width=critical_text.width + 0.2,
                height=critical_text.height + 0.2,
                color=BLACK,
                fill_opacity=1,
            )
            redaction_bar.move_to(critical_text)

            surgical_label = Text(
                "Surgically Precise", color=YELLOW, font_size=32
            ).next_to(redaction_bar, UP)

            self.play(
                FadeIn(redaction_bar),
                FadeOut(critical_text),  # Actually hide it
                Write(surgical_label),
                run_time=tracker.duration * 0.05,
            )

            # Clear
            self.play(
                FadeOut(doc_group),
                FadeOut(wexner_count),
                FadeOut(count_label),
                FadeOut(redaction_bar),
                FadeOut(surgical_label),
                run_time=tracker.duration * 0.05,
            )

            # 2. Massie vs Proactive
            # Duration allocation: ~25%

            timeline_line = Line(LEFT * 4, RIGHT * 4, color=GREY)

            massie_dot = Dot(color=BLUE).move_to(LEFT * 2)
            massie_label = Text("Rep. Massie", font_size=24, color=BLUE).next_to(
                massie_dot, UP
            )

            correction_dot = Dot(color=GREEN).move_to(RIGHT * 2)
            correction_label = Text("Correction", font_size=24, color=GREEN).next_to(
                correction_dot, UP
            )

            arrow = Arrow(
                massie_dot.get_center(),
                correction_dot.get_center(),
                color=WHITE,
                buff=0.1,
            )

            self.play(
                Create(timeline_line),
                FadeIn(massie_dot),
                Write(massie_label),
                run_time=tracker.duration * 0.05,
            )
            self.play(
                GrowArrow(arrow),
                FadeIn(correction_dot),
                Write(correction_label),
                run_time=tracker.duration * 0.05,
            )

            # Ghost "Proactive" path
            proactive_dot = Dot(color=GREY).move_to(LEFT * 4)  # Way earlier
            proactive_arrow = Arrow(
                proactive_dot.get_center(),
                correction_dot.get_center(),
                color=GREY,
                buff=0.1,
            )
            proactive_label = Text(
                "Proactive Review?", font_size=20, color=GREY
            ).next_to(proactive_arrow, DOWN)

            cross = Cross(proactive_arrow, color=RED)

            self.play(
                FadeIn(proactive_dot),
                Create(proactive_arrow),
                Write(proactive_label),
                run_time=tracker.duration * 0.05,
            )
            self.play(Create(cross), run_time=tracker.duration * 0.05)

            # Clear
            self.play(
                FadeOut(timeline_line),
                FadeOut(massie_dot),
                FadeOut(massie_label),
                FadeOut(correction_dot),
                FadeOut(correction_label),
                FadeOut(arrow),
                FadeOut(proactive_dot),
                FadeOut(proactive_arrow),
                FadeOut(proactive_label),
                FadeOut(cross),
                run_time=tracker.duration * 0.05,
            )

            # 3. Bondi Deflection
            # Duration allocation: ~20%

            bondi = Text("AG Bondi", font_size=32).move_to(LEFT * 3 + UP * 1)
            massie = Text("Rep. Massie", font_size=32).move_to(RIGHT * 3 + UP * 1)

            attack_arrow = Arrow(
                bondi.get_right(), massie.get_left(), color=RED, buff=0.2
            )
            attack_label = Text(
                "Trump Derangement Syndrome", font_size=20, color=RED
            ).next_to(attack_arrow, UP)

            accountability = Text(
                "Demand Accountability", font_size=24, color=WHITE
            ).move_to(DOWN * 1)
            deflection_label = Text(
                "DEFLECTION", font_size=48, color=RED, weight=BOLD
            ).move_to(ORIGIN)

            self.play(Write(bondi), Write(massie), run_time=tracker.duration * 0.05)
            self.play(
                GrowArrow(attack_arrow),
                Write(attack_label),
                run_time=tracker.duration * 0.05,
            )
            self.play(Write(accountability), run_time=tracker.duration * 0.05)
            self.play(
                Transform(attack_label, deflection_label),
                run_time=tracker.duration * 0.05,
            )

            # Clear
            self.play(
                FadeOut(bondi),
                FadeOut(massie),
                FadeOut(attack_arrow),
                FadeOut(accountability),
                FadeOut(attack_label),  # Transformed
                run_time=tracker.duration * 0.05,
            )

            # 4. Inversion of Priorities
            # Duration allocation: ~25%

            scale_base = Triangle(color=WHITE).scale(0.5).move_to(DOWN * 2)
            beam = Line(LEFT * 4, RIGHT * 4, color=WHITE).move_to(scale_base.get_top())
            # Tilt the beam: Left side LOW (heavy), Right side HIGH (light/protected)
            # Actually, "Priorities" usually means what you value more is held HIGH?
            # Or what is "heavier" sinks? Let's say Victims are exposed (low/mud), Elites are high (protected).
            beam.rotate(20 * DEGREES, about_point=scale_base.get_top())

            left_point = beam.get_start()
            right_point = beam.get_end()

            # Left: Victims (Exposed)
            victims = VGroup(*[Dot(radius=0.05, color=GREY) for _ in range(20)])
            victims.arrange_in_grid(4, 5, buff=0.1)
            victims.move_to(left_point + UP * 0.5)

            victim_label = Text("Victims Exposed", font_size=24, color=RED).next_to(
                victims, DOWN
            )

            # Right: Elites (Shielded)
            elites = Circle(radius=0.5, color=GOLD, fill_opacity=1).move_to(
                right_point + UP * 0.5
            )
            elite_label = Text("Elites Shielded", font_size=24, color=GOLD).next_to(
                elites, UP
            )

            title = Text("INVERSION OF PRIORITIES", font_size=40, color=RED).move_to(
                UP * 3
            )

            self.play(
                Create(scale_base),
                Create(beam),
                FadeIn(victims),
                Write(victim_label),
                FadeIn(elites),
                Write(elite_label),
                run_time=tracker.duration * 0.15,
            )

            self.play(Write(title), run_time=tracker.duration * 0.1)
