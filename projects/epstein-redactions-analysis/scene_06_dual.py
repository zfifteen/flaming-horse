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
class Scene06Dual(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────

        with self.voiceover(text=SCRIPT["dual"]) as tracker:
            # 1. The Pre-Redaction Process
            # Duration allocation: ~40%

            fbi_box = Rectangle(
                width=3, height=2, color=BLUE, fill_opacity=0.2
            ).move_to(LEFT * 3)
            fbi_label = Text("FBI Layer", font_size=24).next_to(fbi_box, UP)

            doj_box = Rectangle(
                width=3, height=2, color=GREY, fill_opacity=0.2
            ).move_to(RIGHT * 3)
            doj_label = Text("DOJ Layer", font_size=24).next_to(doj_box, UP)

            # Document
            doc = VGroup(
                Rectangle(width=1, height=1.4, color=WHITE, fill_opacity=1),
                Text("Secret", color=BLACK, font_size=16),
            ).move_to(LEFT * 6)

            self.play(
                Create(fbi_box),
                Write(fbi_label),
                Create(doj_box),
                Write(doj_label),
                FadeIn(doc),
                run_time=tracker.duration * 0.1,
            )

            # Enter FBI
            self.play(
                doc.animate.move_to(fbi_box.get_center()),
                run_time=tracker.duration * 0.1,
            )

            # Redact inside
            redaction = Rectangle(
                width=0.8, height=0.2, color=BLACK, fill_opacity=1
            ).move_to(doc.get_center())
            self.play(FadeIn(redaction), run_time=tracker.duration * 0.05)
            doc.add(redaction)

            # Move to DOJ
            self.play(
                doc.animate.move_to(doj_box.get_center()),
                run_time=tracker.duration * 0.1,
            )

            # DOJ Stamping
            stamp = (
                Text("REVIEWED", color=GREEN, font_size=20)
                .rotate(15 * DEGREES)
                .move_to(doc.get_center())
            )
            self.play(FadeIn(stamp), run_time=tracker.duration * 0.05)

            # 2. Partitioned System (Blame Shift)
            # Duration allocation: ~40%

            # Investigator
            investigator = Circle(radius=0.5, color=YELLOW).move_to(DOWN * 2)
            inv_label = Text("Investigator", font_size=20).next_to(investigator, DOWN)
            q_mark = Text("?", font_size=36, color=YELLOW).move_to(investigator)

            self.play(
                FadeIn(investigator),
                Write(inv_label),
                Write(q_mark),
                run_time=tracker.duration * 0.05,
            )

            # Arrows
            arrow_inv_doj = Arrow(
                investigator.get_top(), doj_box.get_bottom(), color=YELLOW
            )
            self.play(GrowArrow(arrow_inv_doj), run_time=tracker.duration * 0.05)

            arrow_doj_fbi = Arrow(doj_box.get_left(), fbi_box.get_right(), color=GREY)
            label_shift = Text("Not Us", font_size=16).next_to(arrow_doj_fbi, UP)
            self.play(
                GrowArrow(arrow_doj_fbi),
                Write(label_shift),
                run_time=tracker.duration * 0.05,
            )

            arrow_fbi_void = Arrow(fbi_box.get_left(), LEFT * 6, color=BLUE)
            label_void = Text("Sources & Methods", font_size=16).next_to(
                arrow_fbi_void, UP
            )
            self.play(
                GrowArrow(arrow_fbi_void),
                Write(label_void),
                run_time=tracker.duration * 0.05,
            )

            # 3. Plausible Deniability
            # Duration allocation: ~20%

            denial_text = Text(
                "PLAUSIBLE DENIABILITY", color=RED, font_size=40, weight=BOLD
            ).move_to(UP * 2.5)
            self.play(Write(denial_text), run_time=tracker.duration * 0.1)