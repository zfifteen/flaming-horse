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
class Scene02ResonanceMechanism(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        with self.voiceover(text=SCRIPT["resonance"]) as tracker:
            # Sphere
            sphere = Sphere(radius=2, color=GREY_E)
            sphere.shading = [0.1, 0.1, 0.3]
            self.play(Create(sphere), run_time=tracker.duration * 0.4)

            # Vectors for ionic oscillations
            vectors = VGroup()
            for i in range(20):
                direction = np.random.random(3) - 0.5
                direction /= np.linalg.norm(direction)
                vec = Arrow(ORIGIN, direction * 0.5, color=BLUE, buff=0)
                vec.move_to(sphere.get_center() + direction * 2)
                vectors.add(vec)

            self.play(FadeIn(vectors), run_time=tracker.duration * 0.3)

            # Amplification text
            amp = Text("10-50× Amplification", font_size=36, color=YELLOW)
            amp.to_edge(DOWN)
            safe_position(amp)
            self.play(Write(amp), run_time=tracker.duration * 0.3)