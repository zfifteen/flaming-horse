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
        # Timing budget: Calculate BEFORE writing animations
        # Estimated duration: 50s
        # 0.3 + 0.3 + 0.4 = 1.0 ✓

        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            # Title (ALWAYS use UP * 3.8, NEVER .to_edge(UP))
            title = Text("The Immune Threshold Hypothesis", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.3)

            # Subtitle with safe positioning
            subtitle = Text("Balancing Costs and Benefits in Immunity", font_size=32)
            subtitle.next_to(title, DOWN, buff=0.5)
            safe_position(subtitle)  # ALWAYS call after .next_to()
            self.play(FadeIn(subtitle), run_time=tracker.duration * 0.3)

            # Conceptual diagram: Simple threshold representation
            axis = NumberLine(x_range=[0, 10, 1], length=6, include_numbers=True)
            axis.move_to(ORIGIN)
            threshold_line = Line(axis.n2p(5), axis.n2p(5) + UP * 2, color=RED)
            threshold_label = Text("Threshold", font_size=24).next_to(
                threshold_line, UP
            )
            safe_position(threshold_label)
            diagram = VGroup(axis, threshold_line, threshold_label)
            self.play(Create(diagram), run_time=tracker.duration * 0.4)