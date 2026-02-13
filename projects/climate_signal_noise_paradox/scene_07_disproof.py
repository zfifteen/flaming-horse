import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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
from flaming_horse_voice import get_speech_service

# ── Import Shared Configuration ────────────────────────────────────
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
class Scene07Disproof(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: title 0.12 + scenario 0.40 + conclusion 0.25 + fadeout 0.13 + wait 0.10 = 1.0

        with self.voiceover(text=SCRIPT["disproof"]) as tracker:
            # Title
            title = Text(
                "How to Disprove This",
                font_size=44,
                weight=BOLD,
                color=RED_B,
            )
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.12)

            # Disproval scenario A: Resolve S/N paradox but KEEP hotspot bias
            scenario_a = RoundedRectangle(
                width=6.5,
                height=2.0,
                corner_radius=0.3,
                fill_color=PURPLE_E,
                fill_opacity=0.4,
                stroke_color=PURPLE,
                stroke_width=3,
            )
            scenario_a.move_to(LEFT * 0.0 + UP * 1.2)

            sa_header = Text(
                "Disproval Scenario", font_size=20, color=PURPLE_B, weight=BOLD
            )
            sa_header.move_to(scenario_a.get_top() + DOWN * 0.35)

            sa_line1 = Text(
                "A model resolves the signal-to-noise paradox",
                font_size=18,
                color=WHITE,
            )
            sa_line1.move_to(scenario_a.get_center() + UP * 0.05)

            sa_line2 = Text(
                "BUT retains full tropical hotspot bias",
                font_size=18,
                color=RED_C,
            )
            sa_line2.next_to(sa_line1, DOWN, buff=0.15)

            # OR vice versa
            or_text = Text("OR vice versa", font_size=22, color=YELLOW, weight=BOLD)
            or_text.next_to(scenario_a, DOWN, buff=0.4)

            scenario_b = RoundedRectangle(
                width=6.5,
                height=2.0,
                corner_radius=0.3,
                fill_color=PURPLE_E,
                fill_opacity=0.4,
                stroke_color=PURPLE,
                stroke_width=3,
            )
            scenario_b.move_to(DOWN * 2.0)

            sb_line1 = Text(
                "A model closes the tropical hotspot gap",
                font_size=18,
                color=WHITE,
            )
            sb_line1.move_to(scenario_b.get_center() + UP * 0.15)

            sb_line2 = Text(
                "BUT retains the signal-to-noise paradox",
                font_size=18,
                color=RED_C,
            )
            sb_line2.next_to(sb_line1, DOWN, buff=0.15)

            self.play(
                FadeIn(scenario_a),
                Write(sa_header),
                Write(sa_line1),
                Write(sa_line2),
                Write(or_text),
                FadeIn(scenario_b),
                Write(sb_line1),
                Write(sb_line2),
                run_time=tracker.duration * 0.40,
            )

            # Conclusion
            conclusion_box = RoundedRectangle(
                width=8,
                height=1.5,
                corner_radius=0.3,
                fill_color=GRAY_E,
                fill_opacity=0.5,
                stroke_color=WHITE,
                stroke_width=2,
            )
            conclusion_box.move_to(DOWN * 3.8)
            safe_position(conclusion_box)

            conclusion = Text(
                "Would prove the two anomalies are independent",
                font_size=22,
                color=WHITE,
                weight=BOLD,
            )
            conclusion.move_to(conclusion_box.get_center())
            safe_position(conclusion)

            self.play(
                FadeIn(conclusion_box),
                Write(conclusion),
                run_time=tracker.duration * 0.25,
            )

            # Gentle fade out everything
            all_objects = VGroup(
                title,
                scenario_a,
                sa_header,
                sa_line1,
                sa_line2,
                or_text,
                scenario_b,
                sb_line1,
                sb_line2,
                conclusion_box,
                conclusion,
            )
            self.play(
                FadeOut(all_objects),
                run_time=tracker.duration * 0.13,
            )

            self.wait(tracker.duration * 0.10)