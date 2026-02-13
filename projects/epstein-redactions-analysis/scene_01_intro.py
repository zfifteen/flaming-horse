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
class Scene01Intro(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────

        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            # 1. Title Sequence (Glitch/Redaction Effect)
            # Duration allocation: ~15%
            title_text = Text("Epstein Files Analysis", font_size=60, weight=BOLD)
            title_text.move_to(UP * 2)

            # Create redaction bars covering the text
            redaction_bars = VGroup()
            for char in title_text:
                bar = Rectangle(
                    width=char.width + 0.1,
                    height=char.height + 0.1,
                    color=BLACK,
                    fill_opacity=1,
                )
                bar.move_to(char.get_center())
                redaction_bars.add(bar)

            # Background for title to make redaction visible
            title_bg = Rectangle(width=12, height=3, color=WHITE, fill_opacity=0.1)
            title_bg.move_to(title_text.get_center())

            self.play(FadeIn(title_bg), run_time=tracker.duration * 0.05)
            self.add(title_text, redaction_bars)  # Text hidden by bars

            # Reveal text by sliding bars away
            self.play(
                redaction_bars.animate.shift(RIGHT * 0.2).set_opacity(0),
                run_time=tracker.duration * 0.1,
            )

            # 2. The Act & Failure (Timeline)
            # Duration allocation: ~30%
            act_label = Text("Transparency Act 2025", font_size=36, color=BLUE)
            act_label.next_to(title_bg, DOWN, buff=1.0)

            timeline = Line(start=LEFT * 4, end=RIGHT * 4, color=GREY)
            timeline.next_to(act_label, DOWN, buff=0.5)

            deadline_tick = Line(UP * 0.2, DOWN * 0.2, color=RED).move_to(
                timeline.get_end()
            )
            deadline_text = Text("30 Days", font_size=24, color=RED).next_to(
                deadline_tick, UP
            )

            self.play(
                FadeIn(act_label), Create(timeline), run_time=tracker.duration * 0.1
            )

            # Animate a dot moving to the deadline
            progress_dot = Dot(color=YELLOW).move_to(timeline.get_start())
            self.play(
                progress_dot.animate.move_to(timeline.get_end()),
                FadeIn(deadline_tick),
                Write(deadline_text),
                run_time=tracker.duration * 0.15,
            )

            # Stamp "FAILED"
            fail_stamp = Text("FAILED", font_size=72, color=RED, weight=BOLD).rotate(
                15 * DEGREES
            )
            fail_stamp.move_to(timeline.get_center())
            self.play(FadeIn(fail_stamp, scale=2.0), run_time=tracker.duration * 0.05)

            # Clear for next section
            self.play(
                FadeOut(title_text),
                FadeOut(title_bg),
                FadeOut(redaction_bars),
                FadeOut(act_label),
                FadeOut(timeline),
                FadeOut(progress_dot),
                FadeOut(deadline_tick),
                FadeOut(deadline_text),
                FadeOut(fail_stamp),
                run_time=tracker.duration * 0.05,
            )

            # 3. Contrast: Elites vs Victims
            # Duration allocation: ~30%

            # Left side: Elites (Shielded)
            elite_group = VGroup()
            shield = Annulus(inner_radius=1.2, outer_radius=1.4, color=GOLD).shift(
                LEFT * 3
            )
            shield_cross = Cross(
                shield, stroke_color=GOLD, stroke_width=5
            )  # Stylized shield interior
            # Simple "Suits" icons (Circles + Squares)
            for i in range(3):
                head = Circle(radius=0.2, color=WHITE, fill_opacity=1).shift(
                    LEFT * 3 + LEFT * (i - 1) * 0.6 + UP * 0.2
                )
                body = Square(side_length=0.4, color=WHITE, fill_opacity=1).next_to(
                    head, DOWN, buff=0
                )
                elite_group.add(head, body)

            elite_label = Text("Protected", font_size=32, color=GOLD).next_to(
                shield, DOWN
            )

            # Right side: Victims (Exposed)
            victim_group = VGroup()
            spotlight = Circle(
                radius=1.5, color=WHITE, fill_opacity=0.2, stroke_opacity=0
            ).shift(RIGHT * 3)
            # Simple people icons
            for i in range(5):
                head = Circle(radius=0.15, color=GREY_B, fill_opacity=0.5).shift(
                    RIGHT * 3 + RIGHT * (i - 2) * 0.5 + UP * 0.1
                )
                body = Rectangle(
                    width=0.3, height=0.4, color=GREY_B, fill_opacity=0.5
                ).next_to(head, DOWN, buff=0)
                victim_group.add(head, body)

            victim_label = Text("Exposed", font_size=32, color=RED).next_to(
                spotlight, DOWN
            )

            self.play(
                Create(shield),
                FadeIn(elite_group),
                Write(elite_label),
                FadeIn(spotlight),
                FadeIn(victim_group),
                Write(victim_label),
                run_time=tracker.duration * 0.15,
            )

            # 4. The Models
            # Duration allocation: ~20%

            # Clear previous
            self.play(
                FadeOut(shield),
                FadeOut(elite_group),
                FadeOut(elite_label),
                FadeOut(spotlight),
                FadeOut(victim_group),
                FadeOut(victim_label),
                run_time=tracker.duration * 0.05,
            )

            # Three nodes
            claude = Circle(radius=0.8, color="#D97757", fill_opacity=0.3).move_to(
                UP * 2 + LEFT * 3
            )
            claude_lbl = Text("Claude", font_size=24).move_to(claude)

            kimi = Circle(radius=0.8, color="#5CA5F2", fill_opacity=0.3).move_to(
                UP * 2 + RIGHT * 3
            )
            kimi_lbl = Text("Kimi", font_size=24).move_to(kimi)

            grok = Circle(radius=0.8, color="#333333", fill_opacity=0.3).move_to(
                DOWN * 2
            )
            grok_lbl = Text("Grok", font_size=24).move_to(grok)

            # Connecting to center "Analysis"
            center_node = Circle(radius=1.0, color=WHITE).move_to(ORIGIN)
            center_lbl = Text("Analysis", font_size=28).move_to(center_node)

            lines = VGroup(
                Line(claude.get_center(), center_node.get_center()),
                Line(kimi.get_center(), center_node.get_center()),
                Line(grok.get_center(), center_node.get_center()),
            )

            self.play(
                GrowFromCenter(center_node),
                Write(center_lbl),
                run_time=tracker.duration * 0.05,
            )

            self.play(
                FadeIn(claude),
                Write(claude_lbl),
                Create(lines[0]),
                FadeIn(kimi),
                Write(kimi_lbl),
                Create(lines[1]),
                FadeIn(grok),
                Write(grok_lbl),
                Create(lines[2]),
                run_time=tracker.duration * 0.1,
            )