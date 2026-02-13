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
class Scene05Analysis(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────

        with self.voiceover(text=SCRIPT["analysis"]) as tracker:
            # 1. High Confidence Wexner
            # Duration allocation: ~30%

            gauge_bg = Arc(radius=2, start_angle=PI, angle=-PI, color=WHITE).shift(
                UP * 1
            )
            gauge_ticks = VGroup()
            for i in range(11):
                angle = PI - i * (PI / 10)
                tick = Line(
                    UP * 1.8, UP * 2, color=GREY
                ).rotate(
                    angle - PI / 2, about_point=UP * 1
                )  # Correction: rotation center is origin relative to line, need to shift
                # Easier: just place lines
                p1 = UP * 1 + np.array([np.cos(angle) * 1.8, np.sin(angle) * 1.8, 0])
                p2 = UP * 1 + np.array([np.cos(angle) * 2.0, np.sin(angle) * 2.0, 0])
                gauge_ticks.add(Line(p1, p2, color=GREY))

            needle = Line(UP * 1, UP * 2.8, color=RED, stroke_width=4).rotate(
                PI / 2, about_point=UP * 1
            )  # Start pointing left (0)
            pivot = Dot(point=UP * 1, color=RED)

            label = Text("Wexner Redaction Certainty", font_size=32).next_to(
                gauge_bg, DOWN
            )

            self.play(
                Create(gauge_bg),
                Create(gauge_ticks),
                Create(needle),
                FadeIn(pivot),
                Write(label),
                run_time=tracker.duration * 0.1,
            )

            # Needle to Max
            self.play(
                Rotate(needle, angle=-PI, about_point=UP * 1),
                run_time=tracker.duration * 0.1,
            )

            max_text = Text(
                "HIGHEST CONFIDENCE", color=RED, font_size=40, weight=BOLD
            ).move_to(DOWN * 1)
            self.play(Write(max_text), run_time=tracker.duration * 0.1)

            # Clear
            self.play(
                FadeOut(gauge_bg),
                FadeOut(gauge_ticks),
                FadeOut(needle),
                FadeOut(pivot),
                FadeOut(label),
                FadeOut(max_text),
                run_time=tracker.duration * 0.05,
            )

            # 2. The Machine (System)
            # Duration allocation: ~35%

            machine = Rectangle(
                width=4, height=3, color=BLUE, fill_opacity=0.2
            ).move_to(ORIGIN)
            machine_label = Text("The System", font_size=36).move_to(
                machine.get_top() + DOWN * 0.5
            )
            gears = VGroup(
                Circle(radius=0.5, color=WHITE).shift(LEFT * 1 + DOWN * 0.5),
                Circle(radius=0.5, color=WHITE).shift(RIGHT * 1 + DOWN * 0.5),
            )  # Simplified gears

            input_arrow = Arrow(LEFT * 6, machine.get_left(), color=WHITE)
            input_text = Text("Evidence", font_size=24).next_to(input_arrow, UP)

            top_out = Arrow(
                machine.get_right() + UP * 0.5, RIGHT * 6 + UP * 0.5, color=GOLD
            )
            bot_out = Arrow(
                machine.get_right() + DOWN * 0.5, RIGHT * 6 + DOWN * 2, color=RED
            )  # Chute

            elite_res = Text("Shielded Power", color=GOLD, font_size=24).next_to(
                top_out, UP
            )
            victim_res = Text("Exposed Victims", color=RED, font_size=24).next_to(
                bot_out, DOWN
            )

            self.play(
                Create(machine),
                Write(machine_label),
                Create(gears),
                run_time=tracker.duration * 0.1,
            )
            self.play(
                GrowArrow(input_arrow),
                Write(input_text),
                run_time=tracker.duration * 0.05,
            )
            self.play(
                Rotate(gears[0], angle=2 * PI),
                Rotate(gears[1], angle=-2 * PI),
                GrowArrow(top_out),
                GrowArrow(bot_out),
                run_time=tracker.duration * 0.1,
            )
            self.play(
                Write(elite_res), Write(victim_res), run_time=tracker.duration * 0.05
            )

            # Clear
            self.play(
                FadeOut(machine),
                FadeOut(machine_label),
                FadeOut(gears),
                FadeOut(input_arrow),
                FadeOut(input_text),
                FadeOut(top_out),
                FadeOut(bot_out),
                FadeOut(elite_res),
                FadeOut(victim_res),
                run_time=tracker.duration * 0.05,
            )

            # 3. Reforms Fork
            # Duration allocation: ~35%

            start_point = DOWN * 3
            fork_point = ORIGIN
            left_end = UP * 3 + LEFT * 3
            right_end = UP * 3 + RIGHT * 3

            road_main = Line(start_point, fork_point, color=WHITE, stroke_width=8)
            road_left = Line(fork_point, left_end, color=WHITE, stroke_width=8)
            road_right = Line(fork_point, right_end, color=WHITE, stroke_width=8)

            needed_text = Text("Reforms Needed", font_size=36).move_to(DOWN * 2)

            self.play(
                Create(road_main),
                Create(road_left),
                Create(road_right),
                Write(needed_text),
                run_time=tracker.duration * 0.1,
            )

            intent_label = Text("If Intentional:", font_size=24, color=RED).move_to(
                LEFT * 3 + UP * 1.5
            )
            account_box = Rectangle(width=2.5, height=1, color=RED).move_to(left_end)
            account_text = Text("Accountability", font_size=24).move_to(account_box)

            struct_label = Text("If Structural:", font_size=24, color=BLUE).move_to(
                RIGHT * 3 + UP * 1.5
            )
            laws_box = Rectangle(width=2.5, height=1, color=BLUE).move_to(right_end)
            laws_text = Text("Better Laws", font_size=24).move_to(laws_box)

            self.play(
                Write(intent_label),
                Create(account_box),
                Write(account_text),
                Write(struct_label),
                Create(laws_box),
                Write(laws_text),
                run_time=tracker.duration * 0.2,
            )

            # FBI/DOJ Pipeline opacity
            pipeline_text = Text("Opaque Pipeline", font_size=40, color=GREY).move_to(
                ORIGIN
            )
            self.play(FadeIn(pipeline_text), run_time=tracker.duration * 0.05)