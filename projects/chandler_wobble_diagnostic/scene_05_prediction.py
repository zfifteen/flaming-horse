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
class Scene05Prediction(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
        # Timing budget: 0.20 + 0.30 + 0.30 + 0.20 = 1.0
        
        with self.voiceover(text=SCRIPT["prediction"]) as tracker:
            # Two overlaid sine waves
            title = Text("Falsifiable Prediction", font_size=44, weight=BOLD, color=WHITE)
            title.move_to(UP * 3.8)
            
            axes = Axes(
                x_range=[0, 10, 1],
                y_range=[-1.5, 1.5, 0.5],
                x_length=10,
                y_length=3,
                tips=False
            ).move_to(UP * 1.2)
            
            # Pre-2010 phase (blue solid)
            pre_2010 = axes.plot(
                lambda x: np.sin(2 * x),
                color=BLUE,
                stroke_width=4
            )
            pre_label = Text("Pre-2010 LOD Phase", font_size=28, color=BLUE)
            pre_label.next_to(axes, LEFT, buff=0.5).shift(UP * 0.8)
            safe_position(pre_label)
            
            self.play(
                Write(title),
                Create(axes),
                Create(pre_2010),
                FadeIn(pre_label),
                run_time=tracker.duration * 0.20
            )
            
            # Post-2027 phase (cyan dashed) - initially in phase
            post_2027_initial = axes.plot(
                lambda x: np.sin(2 * x),
                color="#00F5FF",
                stroke_width=4
            ).set_stroke(opacity=0.7)
            
            # Make it dashed by creating segments
            post_2027 = DashedVMobject(post_2027_initial, num_dashes=30)
            
            post_label = Text("Predicted Post-2027 Phase", font_size=28, color="#00F5FF")
            post_label.next_to(axes, LEFT, buff=0.5).shift(DOWN * 0.8)
            safe_position(post_label)
            
            self.play(
                Create(post_2027),
                FadeIn(post_label),
                run_time=tracker.duration * 0.30
            )
            
            # Phase shift transformation
            phase_shift = 1.0  # 60 degrees approximately
            post_2027_shifted_curve = axes.plot(
                lambda x: np.sin(2 * x + phase_shift),
                color="#00F5FF",
                stroke_width=4
            )
            post_2027_shifted = DashedVMobject(post_2027_shifted_curve, num_dashes=30)
            
            phase_annotation = Text("Phase Offset: 30-180°", font_size=28, 
                                  color="#FFC857", weight=BOLD)
            phase_annotation.next_to(axes, RIGHT, buff=0.5)
            safe_position(phase_annotation)
            
            self.play(
                Transform(post_2027, post_2027_shifted),
                FadeIn(phase_annotation),
                run_time=tracker.duration * 0.30
            )
            
            # Correlation plot
            self.play(
                FadeOut(axes), FadeOut(pre_2010), FadeOut(post_2027),
                FadeOut(pre_label), FadeOut(post_label), FadeOut(phase_annotation),
                run_time=0.3
            )
            
            corr_axes = Axes(
                x_range=[-2, 2, 1],
                y_range=[-2, 2, 1],
                x_length=5,
                y_length=5,
                axis_config={"include_numbers": False},
                tips=True
            ).move_to(DOWN * 0.5)
            
            x_label = Text("LOD Anomaly", font_size=24, color=WHITE)
            x_label.next_to(corr_axes.x_axis, DOWN, buff=0.3)
            safe_position(x_label)
            
            y_label = Text("AAM Anomaly", font_size=24, color=WHITE)
            y_label.next_to(corr_axes.y_axis, LEFT, buff=0.3).rotate(PI/2)
            safe_position(y_label)
            
            # Tight anti-phase correlation (r = -0.6)
            np.random.seed(42)
            points_tight = []
            for i in range(25):
                x = np.random.uniform(-1.5, 1.5)
                y = -0.7 * x + np.random.normal(0, 0.3)
                point = Dot(corr_axes.c2p(x, y), radius=0.05, color=BLUE)
                points_tight.append(point)
            
            tight_line = corr_axes.plot(lambda x: -0.7 * x, color=BLUE, stroke_width=3)
            corr_label = Text("r = -0.6 (tight anti-phase)", font_size=24, color=BLUE)
            corr_label.move_to(UP * 3.3)
            safe_position(corr_label)
            
            self.play(
                Create(corr_axes),
                FadeIn(x_label),
                FadeIn(y_label),
                *[FadeIn(p) for p in points_tight],
                Create(tight_line),
                FadeIn(corr_label),
                run_time=tracker.duration * 0.15
            )
            
            # Correlation weakens
            points_weak = []
            for p_tight in points_tight:
                old_pos = p_tight.get_center()
                noise_x = np.random.normal(0, 0.4)
                noise_y = np.random.normal(0, 0.4)
                new_pos = old_pos + np.array([noise_x, noise_y, 0])
                p_weak = Dot(new_pos, radius=0.05, color="#FFC857")
                points_weak.append(p_weak)
            
            weak_label = Text("r = -0.3 (weakened)", font_size=24, color="#FFC857")
            weak_label.move_to(UP * 3.3)
            safe_position(weak_label)
            
            prediction_text = Text("Falsifiable Prediction: Phase offset detectable by late 2027",
                                 font_size=26, color="#FFC857", weight=BOLD)
            prediction_text.move_to(DOWN * 3.5)
            safe_position(prediction_text)
            
            self.play(
                *[Transform(points_tight[i], points_weak[i]) for i in range(len(points_tight))],
                FadeOut(tight_line),
                Transform(corr_label, weak_label),
                FadeIn(prediction_text),
                run_time=tracker.duration * 0.05
            )