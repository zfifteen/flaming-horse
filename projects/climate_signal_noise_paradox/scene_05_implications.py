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
class Scene05Implications(VoiceoverScene):
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
        # Timing budget: title 0.10 + anomaly_boxes 0.25 + root_cause 0.25 + novel 0.25 + wait 0.15 = 1.0

        with self.voiceover(text=SCRIPT["implications"]) as tracker:
            # Title
            title = Text(
                "Two Anomalies, One Root Cause",
                font_size=44,
                weight=BOLD,
            )
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.10)

            # Anomaly 1: Tropical Hotspot Gap
            box1 = RoundedRectangle(
                width=5,
                height=2.0,
                corner_radius=0.3,
                fill_color=RED_E,
                fill_opacity=0.5,
                stroke_color=RED,
                stroke_width=3,
            )
            box1.move_to(LEFT * 3.5 + UP * 1.0)
            box1_title = Text(
                "Tropical Hotspot\nGap", font_size=24, weight=BOLD, color=RED_B
            )
            box1_title.move_to(box1.get_center() + UP * 0.3)
            box1_desc = Text(
                "Models overpredict\ntropospheric warming", font_size=16, color=WHITE
            )
            box1_desc.move_to(box1.get_center() + DOWN * 0.4)

            # Anomaly 2: Signal-to-Noise Paradox
            box2 = RoundedRectangle(
                width=5,
                height=2.0,
                corner_radius=0.3,
                fill_color=BLUE_E,
                fill_opacity=0.5,
                stroke_color=BLUE,
                stroke_width=3,
            )
            box2.move_to(RIGHT * 3.5 + UP * 1.0)
            box2_title = Text(
                "Signal-to-Noise\nParadox", font_size=24, weight=BOLD, color=BLUE_B
            )
            box2_title.move_to(box2.get_center() + UP * 0.3)
            box2_desc = Text(
                "Models underpredict\npredictable modes", font_size=16, color=WHITE
            )
            box2_desc.move_to(box2.get_center() + DOWN * 0.4)

            self.play(
                FadeIn(box1),
                Write(box1_title),
                Write(box1_desc),
                FadeIn(box2),
                Write(box2_title),
                Write(box2_desc),
                run_time=tracker.duration * 0.25,
            )

            # Root cause box below, connecting both
            root_box = RoundedRectangle(
                width=6,
                height=1.8,
                corner_radius=0.3,
                fill_color=YELLOW_E,
                fill_opacity=0.5,
                stroke_color=YELLOW,
                stroke_width=3,
            )
            root_box.move_to(DOWN * 2.0)
            root_text = Text(
                "Convective Parameterization\nEnergy Misallocation",
                font_size=22,
                weight=BOLD,
                color=YELLOW,
            )
            root_text.move_to(root_box.get_center())

            # Connecting arrows from root to both anomalies
            arrow1 = Arrow(
                root_box.get_top() + LEFT * 1.5,
                box1.get_bottom(),
                color=YELLOW,
                stroke_width=4,
            )
            arrow2 = Arrow(
                root_box.get_top() + RIGHT * 1.5,
                box2.get_bottom(),
                color=YELLOW,
                stroke_width=4,
            )

            self.play(
                FadeIn(root_box),
                Write(root_text),
                GrowArrow(arrow1),
                GrowArrow(arrow2),
                run_time=tracker.duration * 0.25,
            )

            # Novel connection label
            novel_label = Text(
                "First explicit connection in the literature",
                font_size=22,
                color=GREEN_B,
                weight=BOLD,
            )
            novel_label.move_to(DOWN * 3.5)
            safe_position(novel_label)

            # Pulsing highlight on root cause
            highlight = SurroundingRectangle(root_box, color=YELLOW, buff=0.15)

            self.play(
                Write(novel_label),
                Create(highlight),
                run_time=tracker.duration * 0.25,
            )

            self.wait(tracker.duration * 0.15)
