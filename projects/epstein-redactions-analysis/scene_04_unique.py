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
class Scene04Unique(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────

        with self.voiceover(text=SCRIPT["unique"]) as tracker:
            # 1. Claude: Wexner Letter (Timing)
            # Duration allocation: ~35%

            claude_label = Text(
                "Claude: Timing", color="#D97757", font_size=32
            ).to_corner(UL)

            timeline = Line(LEFT * 3, RIGHT * 3, color=WHITE)

            death_mark = Line(UP * 0.3, DOWN * 0.3, color=RED).move_to(RIGHT * 2)
            death_label = Text("Epstein Death", font_size=20, color=RED).next_to(
                death_mark, UP
            )

            letter_mark = Line(UP * 0.3, DOWN * 0.3, color=YELLOW).move_to(
                RIGHT * 1
            )  # 2 days is close
            letter_label = (
                Text("Condemnation Letter", font_size=20, color=YELLOW)
                .next_to(letter_mark, UP)
                .shift(LEFT * 1.5)
            )

            gap_brace = Brace(
                Line(letter_mark.get_center(), death_mark.get_center()), DOWN
            )
            gap_text = gap_brace.get_text("2 Days")

            money_bag = Text("$", font_size=48, color=GREEN).move_to(DOWN * 2)
            ties_text = Text("Deep Financial Ties", font_size=24, color=GREEN).next_to(
                money_bag, DOWN
            )

            self.play(
                Write(claude_label),
                Create(timeline),
                FadeIn(death_mark),
                Write(death_label),
                run_time=tracker.duration * 0.1,
            )
            self.play(
                FadeIn(letter_mark),
                Write(letter_label),
                run_time=tracker.duration * 0.1,
            )
            self.play(
                GrowFromCenter(gap_brace),
                Write(gap_text),
                run_time=tracker.duration * 0.1,
            )
            self.play(
                FadeIn(money_bag), Write(ties_text), run_time=tracker.duration * 0.05
            )

            # Clear
            self.play(
                FadeOut(claude_label),
                FadeOut(timeline),
                FadeOut(death_mark),
                FadeOut(death_label),
                FadeOut(letter_mark),
                FadeOut(letter_label),
                FadeOut(gap_brace),
                FadeOut(gap_text),
                FadeOut(money_bag),
                FadeOut(ties_text),
                run_time=tracker.duration * 0.05,
            )

            # 2. Kimi: 40-Minute Fix
            # Duration allocation: ~30%

            kimi_label = Text(
                "Kimi: Capability", color="#5CA5F2", font_size=32
            ).to_corner(UL)

            stopwatch = Circle(radius=1.5, color=WHITE)
            hand = Line(stopwatch.get_center(), stopwatch.get_top(), color=RED)

            time_text = DecimalNumber(0, num_decimal_places=0).move_to(
                stopwatch.get_center() + DOWN * 0.5
            )
            min_label = Text("min", font_size=24).next_to(time_text, RIGHT, buff=0.1)
            # Group them to move together if needed, but for now just add label

            self.play(
                Write(kimi_label),
                Create(stopwatch),
                Create(hand),
                Write(min_label),  # Add label here
                run_time=tracker.duration * 0.05,
            )

            self.play(
                Rotate(
                    hand, angle=-240 * DEGREES, about_point=stopwatch.get_center()
                ),  # 40 mins = 2/3 circle roughly
                ChangeDecimalToValue(time_text, 40),
                run_time=tracker.duration * 0.1,
            )

            check = Text("✔", color=GREEN, font_size=60).move_to(stopwatch.get_center())
            self.play(FadeIn(check), run_time=tracker.duration * 0.05)

            choice_text = Text("Choice vs Ability", font_size=36).next_to(
                stopwatch, RIGHT, buff=1
            )
            self.play(Write(choice_text), run_time=tracker.duration * 0.1)

            # Clear
            self.play(
                FadeOut(kimi_label),
                FadeOut(stopwatch),
                FadeOut(hand),
                FadeOut(time_text),
                FadeOut(check),
                FadeOut(choice_text),
                run_time=tracker.duration * 0.05,
            )

            # 3. Grok: Untraceable Pipeline
            # Duration allocation: ~35%

            grok_label = Text(
                "Grok: The Pipeline", color=GREEN, font_size=32
            ).to_corner(UL)

            fbi = Text("FBI", font_size=24).move_to(LEFT * 4)
            doj = Text("DOJ", font_size=24).move_to(ORIGIN)
            public = Text("Public", font_size=24).move_to(RIGHT * 4)

            arrow1 = Arrow(fbi.get_right(), doj.get_left(), buff=0.2)
            arrow2 = Arrow(doj.get_right(), public.get_left(), buff=0.2)

            self.play(
                Write(grok_label),
                FadeIn(fbi),
                FadeIn(doj),
                FadeIn(public),
                run_time=tracker.duration * 0.05,
            )
            self.play(
                GrowArrow(arrow1), GrowArrow(arrow2), run_time=tracker.duration * 0.1
            )

            # The untraceable nature
            # Make the arrow from FBI to DOJ dashed or ghostly
            dashed_arrow = DashedLine(fbi.get_right(), doj.get_left(), color=GREY)

            self.play(
                ReplacementTransform(arrow1, dashed_arrow),
                run_time=tracker.duration * 0.05,
            )

            untraceable = Text("Untraceable Source", font_size=24, color=RED).next_to(
                dashed_arrow, UP
            )
            self.play(Write(untraceable), run_time=tracker.duration * 0.1)

            deniability = Text(
                "Plausible Deniability", font_size=30, weight=BOLD
            ).move_to(DOWN * 2)
            self.play(Write(deniability), run_time=tracker.duration * 0.05)