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
class Scene05Implications(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: Calculate BEFORE writing animations
        # Example: 0.4 + 0.3 + 0.3 = 1.0 ✓

        with self.voiceover(text=SCRIPT["implications"]) as tracker:
            # Title (ALWAYS use UP * 3.8, NEVER .to_edge(UP))
            title = Text("Broader Implications", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.2)

            # Ecological networks
            ecology_title = Text("Disease Ecology", font_size=36, color=GREEN)
            ecology_title.next_to(title, DOWN, buff=0.8)
            safe_position(ecology_title)
            ecology_icon = Circle(radius=1.0, color=GREEN).next_to(
                ecology_title, DOWN, buff=0.3
            )
            ecology_group = VGroup(ecology_title, ecology_icon)
            safe_position(ecology_group)
            self.play(FadeIn(ecology_group), run_time=tracker.duration * 0.3)

            # Conservation scenarios
            conservation_title = Text("Conservation Biology", font_size=36, color=BLUE)
            conservation_title.next_to(ecology_group, DOWN, buff=0.8)
            safe_position(conservation_title)
            conservation_icon = Square(side_length=1.5, color=BLUE).next_to(
                conservation_title, DOWN, buff=0.3
            )
            conservation_group = VGroup(conservation_title, conservation_icon)
            safe_position(conservation_group)
            self.play(FadeIn(conservation_group), run_time=tracker.duration * 0.25)

            # Medical applications
            medical_title = Text("Medical Applications", font_size=36, color=RED)
            medical_title.next_to(conservation_group, DOWN, buff=0.8)
            safe_position(medical_title)
            medical_icon = (
                Triangle(color=RED).scale(0.8).next_to(medical_title, DOWN, buff=0.3)
            )
            medical_group = VGroup(medical_title, medical_icon)
            safe_position(medical_group)
            self.play(FadeIn(medical_group), run_time=tracker.duration * 0.25)