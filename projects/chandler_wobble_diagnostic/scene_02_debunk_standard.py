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
config.frame_width = 10 * 16/9
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
class Scene02DebunkStandard(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
        # Timing budget: 0.15 + 0.25 + 0.20 + 0.25 + 0.15 = 1.0
        
        with self.voiceover(text=SCRIPT["debunk_standard"]) as tracker:
            # Header
            header = Text("Standard Explanation", font_size=44, weight=BOLD, color=WHITE)
            header.move_to(UP * 3.8)
            self.play(Write(header), run_time=tracker.duration * 0.15)
            
            # Random atmospheric and oceanic vectors
            vectors = VGroup()
            np.random.seed(42)
            for _ in range(15):
                start = np.random.uniform(-6, 6, size=2).tolist() + [0]
                angle = np.random.uniform(0, 2*PI)
                direction = np.array([np.cos(angle), np.sin(angle), 0]) * 0.8
                end = np.add(start, direction).tolist()
                arrow = Arrow(start=start, end=end, buff=0, color=BLUE, stroke_width=3)
                vectors.add(arrow)
            
            label = Text("Random Atmospheric & Oceanic Forcing", font_size=28, color=BLUE)
            label.next_to(header, DOWN, buff=0.8)
            safe_position(label)
            
            self.play(
                FadeIn(label),
                *[GrowArrow(v) for v in vectors],
                run_time=tracker.duration * 0.25
            )
            
            # Vectors converge to center (cancellation)
            center_point = ORIGIN
            self.play(
                *[v.animate.scale(0.1).move_to(center_point) for v in vectors],
                run_time=tracker.duration * 0.20
            )
            
            # Three ghost spirals with random phases
            spiral_group = VGroup()
            phases = [0, 47, 203]
            colors = ["#666666", "#777777", "#888888"]
            
            for i, (phase_deg, color) in enumerate(zip(phases, colors)):
                phase_rad = phase_deg * DEGREES
                points = []
                for t in np.linspace(0, 2*PI, 40):
                    x = 0.8 * np.cos(t + phase_rad) + (i - 1) * 2.5
                    y = 0.8 * np.sin(t + phase_rad)
                    points.append([x, y, 0])
                spiral = VMobject(color=color, stroke_width=2)
                spiral.set_points_as_corners(points)
                phase_text = Text(f"{phase_deg}°", font_size=20, color=color)
                phase_text.next_to(spiral, UP, buff=0.2)
                spiral_group.add(VGroup(spiral, phase_text))
            
            self.play(
                FadeOut(vectors),
                FadeOut(label),
                *[FadeIn(s) for s in spiral_group],
                run_time=tracker.duration * 0.25
            )
            
            # Only 180-degree spiral remains, red X over explanation
            inverted_spiral_points = []
            for t in np.linspace(0, 2*PI, 40):
                x = 1.2 * np.cos(t + PI)  # 180-degree phase shift
                y = 1.2 * np.sin(t + PI)
                inverted_spiral_points.append([x, y, 0])
            
            final_spiral = VMobject(color="#FFC857", stroke_width=4)
            final_spiral.set_points_as_corners(inverted_spiral_points)
            final_label = Text("180°", font_size=32, color="#FFC857", weight=BOLD)
            final_label.next_to(final_spiral, UP, buff=0.3)
            
            red_x = Text("✗", font_size=120, color=RED, weight=BOLD)
            red_x.move_to(UP * 3)
            
            annotation = Text("Precise phase inversion ≠ Random outcome", 
                            font_size=28, color="#FFC857")
            annotation.move_to(DOWN * 3.5)
            safe_position(annotation)
            
            self.play(
                FadeOut(spiral_group),
                FadeIn(final_spiral),
                FadeIn(final_label),
                FadeIn(red_x),
                FadeIn(annotation),
                run_time=tracker.duration * 0.15
            )