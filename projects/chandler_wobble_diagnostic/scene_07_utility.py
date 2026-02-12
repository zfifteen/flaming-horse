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
class Scene07Utility(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )
        
        # Timing budget: 0.25 + 0.30 + 0.25 + 0.20 = 1.0
        
        with self.voiceover(text=SCRIPT["utility"]) as tracker:
            # Earth globe
            earth = Sphere(radius=1.5, resolution=(20, 20))
            earth.set_color("#004E89").set_opacity(0.7)
            earth.move_to(LEFT * 5 + UP * 0.5)
            
            # Rotation animation
            earth.rotate(PI/4, axis=UP)
            
            self.play(
                FadeIn(earth),
                run_time=tracker.duration * 0.25
            )
            
            # Monitoring dashboard
            dashboard_bg = Rectangle(
                width=8,
                height=6,
                color="#1A1A2E",
                fill_opacity=0.9,
                stroke_color=WHITE,
                stroke_width=2
            ).move_to(RIGHT * 3.5)
            
            dashboard_title = Text("Chandler Wobble Phase Monitor",
                                 font_size=32, color="#00F5FF", weight=BOLD)
            dashboard_title.move_to(RIGHT * 3.5 + UP * 2.5)
            
            # Live phase trace
            trace_axes = Axes(
                x_range=[0, 10, 1],
                y_range=[-1, 1, 0.5],
                x_length=6,
                y_length=2,
                tips=False,
                axis_config={"stroke_width": 1, "stroke_opacity": 0.5}
            ).move_to(RIGHT * 3.5 + UP * 0.8)
            
            phase_trace = trace_axes.plot(
                lambda x: np.sin(3 * x),
                color="#00F5FF",
                stroke_width=3
            )
            
            # Phase angle readout
            phase_readout = Text("Phase: 0°", font_size=28, color="#00F5FF")
            phase_readout.next_to(trace_axes, DOWN, buff=0.5)
            safe_position(phase_readout)
            
            self.play(
                FadeIn(dashboard_bg),
                FadeIn(dashboard_title),
                Create(trace_axes),
                Create(phase_trace),
                FadeIn(phase_readout),
                run_time=tracker.duration * 0.30
            )
            
            # Phase angle shifts and triggers alert
            phase_90 = Text("Phase: 90°", font_size=28, color="#FFC857")
            phase_90.move_to(phase_readout.get_center())
            
            phase_180 = Text("Phase: 180°", font_size=28, color=RED, weight=BOLD)
            phase_180.move_to(phase_readout.get_center())
            
            # Alert icon
            alert_triangle = Triangle(color="#FFC857", fill_opacity=0.8, stroke_width=3)
            alert_triangle.scale(0.6).move_to(RIGHT * 3.5 + DOWN * 1.5)
            alert_exclaim = Text("!", font_size=48, color="#1A1A2E", weight=BOLD)
            alert_exclaim.move_to(alert_triangle.get_center())
            
            alert_text = Text("Coupling Regime\nTransition Detected",
                            font_size=26, color="#FFC857", weight=BOLD)
            alert_text.next_to(alert_triangle, DOWN, buff=0.4)
            safe_position(alert_text)
            
            self.play(
                Transform(phase_readout, phase_90),
                run_time=0.2
            )
            
            self.play(
                Transform(phase_readout, phase_180),
                FadeIn(alert_triangle),
                FadeIn(alert_exclaim),
                FadeIn(alert_text),
                run_time=tracker.duration * 0.25
            )
            
            # Timeline projection
            projection_box = Rectangle(
                width=7,
                height=1.5,
                color="#FFC857",
                stroke_width=2,
                fill_opacity=0.1
            ).move_to(RIGHT * 3.5 + DOWN * 3.2)
            
            projection_text = Text("Predicted 6-Year LOD Disruption",
                                 font_size=24, color="#FFC857")
            projection_text.move_to(projection_box.get_center() + UP * 0.4)
            
            projection_years = Text("2026-2028 (±2 years)",
                                  font_size=28, color="#FFC857", weight=BOLD)
            projection_years.move_to(projection_box.get_center() + DOWN * 0.3)
            
            # Final lead time annotation
            lead_time = Text("Lead Time: ~5 years for climate oscillation forecasts",
                           font_size=26, color=WHITE, weight=BOLD)
            lead_time.move_to(DOWN * 4.3)
            safe_position(lead_time)
            
            self.play(
                FadeIn(projection_box),
                FadeIn(projection_text),
                FadeIn(projection_years),
                FadeIn(lead_time),
                run_time=tracker.duration * 0.20
            )
