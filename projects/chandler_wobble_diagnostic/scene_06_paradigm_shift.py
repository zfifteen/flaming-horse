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
class Scene06ParadigmShift(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )
        
        # Timing budget: 0.20 + 0.25 + 0.30 + 0.25 = 1.0
        
        with self.voiceover(text=SCRIPT["paradigm_shift"]) as tracker:
            # Three vertical panels
            panel_width = 4.5
            separator1 = Line(UP * 4.5, DOWN * 4.5, color=WHITE, stroke_width=1, stroke_opacity=0.3)
            separator1.move_to(LEFT * 4.5)
            separator2 = Line(UP * 4.5, DOWN * 4.5, color=WHITE, stroke_width=1, stroke_opacity=0.3)
            separator2.move_to(RIGHT * 4.5)
            
            # Panel labels
            cmb_label = Text("Core-Mantle\nBoundary", font_size=28, color="#FF6B35", weight=BOLD)
            cmb_label.move_to(LEFT * 7.5 + UP * 3.8)
            
            cw_label = Text("Chandler\nWobble", font_size=28, color="#00F5FF", weight=BOLD)
            cw_label.move_to(ORIGIN + UP * 3.8)
            
            lod_label = Text("6-Year LOD\n→ Climate", font_size=28, color="#FFC857", weight=BOLD)
            lod_label.move_to(RIGHT * 7.5 + UP * 3.8)
            
            self.play(
                Create(separator1),
                Create(separator2),
                FadeIn(cmb_label),
                FadeIn(cw_label),
                FadeIn(lod_label),
                run_time=tracker.duration * 0.20
            )
            
            # CMB with pulsing glow
            cmb_circle = Circle(radius=1.2, color="#FF6B35", fill_opacity=0.6, stroke_width=3)
            cmb_circle.move_to(LEFT * 7.5 + UP * 0.5)
            
            cmb_glow = Circle(radius=1.5, color="#FF6B35", fill_opacity=0.2, stroke_width=0)
            cmb_glow.move_to(LEFT * 7.5 + UP * 0.5)
            
            self.play(
                FadeIn(cmb_circle),
                FadeIn(cmb_glow),
                run_time=tracker.duration * 0.25
            )
            
            # Wave pulse emanates
            wave_pulse = Circle(radius=0.2, color=WHITE, stroke_width=6)
            wave_pulse.move_to(LEFT * 7.5 + UP * 0.5)
            
            # Chandler wobble spiral (dormant)
            cw_spiral_points = []
            for t in np.linspace(0, 3*PI, 50):
                x = 0.4 * np.cos(t)
                y = 0.5 + 0.4 * np.sin(t)
                cw_spiral_points.append([x, y, 0])
            
            cw_spiral = VMobject(color="#00F5FF", stroke_width=3, stroke_opacity=0.3)
            cw_spiral.set_points_as_corners(cw_spiral_points)
            
            # LOD waveform (dormant)
            lod_wave_dormant = VGroup()
            for i in range(3):
                wave = FunctionGraph(
                    lambda x: 0.3 * np.sin(3 * x),
                    x_range=[0, 2],
                    color="#FFC857",
                    stroke_width=2,
                    stroke_opacity=0.3
                ).move_to(RIGHT * 7.5 + DOWN * (1.5 - i))
                lod_wave_dormant.add(wave)
            
            self.play(
                Create(cw_spiral),
                Create(lod_wave_dormant),
                run_time=0.2
            )
            
            # Wave reaches CW panel
            self.play(
                wave_pulse.animate.scale(15).set_stroke(opacity=0.1),
                run_time=tracker.duration * 0.30
            )
            
            # CW spiral flips (becomes bright and inverted)
            cw_spiral_flipped_points = []
            for t in np.linspace(0, 3*PI, 50):
                x = 0.4 * np.cos(-t)  # Inverted
                y = 0.5 + 0.4 * np.sin(-t)
                cw_spiral_flipped_points.append([x, y, 0])
            
            cw_spiral_flipped = VMobject(color="#00F5FF", stroke_width=4, stroke_opacity=1.0)
            cw_spiral_flipped.set_points_as_corners(cw_spiral_flipped_points)
            
            cw_timestamp = Text("2019-2021", font_size=24, color="#00F5FF")
            cw_timestamp.move_to(DOWN * 2.5)
            safe_position(cw_timestamp)
            
            self.play(
                Transform(cw_spiral, cw_spiral_flipped),
                FadeIn(cw_timestamp),
                run_time=0.3
            )
            
            # Wave continues to LOD panel (slower)
            wave_pulse2 = Circle(radius=0.2, color=WHITE, stroke_width=6)
            wave_pulse2.move_to(ORIGIN + UP * 0.5)
            
            self.play(
                wave_pulse2.animate.scale(25).move_to(RIGHT * 7.5).set_stroke(opacity=0.1),
                run_time=tracker.duration * 0.20
            )
            
            # LOD wave distorts (becomes bright and shifted)
            lod_wave_active = VGroup()
            for i in range(3):
                wave = FunctionGraph(
                    lambda x: 0.3 * np.sin(3 * x + 0.8),  # Phase shifted
                    x_range=[0, 2],
                    color="#FFC857",
                    stroke_width=3,
                    stroke_opacity=1.0
                ).move_to(RIGHT * 7.5 + DOWN * (1.5 - i))
                lod_wave_active.add(wave)
            
            lod_timestamp = Text("~2026-2027", font_size=24, color="#FFC857")
            lod_timestamp.move_to(RIGHT * 7.5 + DOWN * 2.5)
            safe_position(lod_timestamp)
            
            self.play(
                Transform(lod_wave_dormant, lod_wave_active),
                FadeIn(lod_timestamp),
                run_time=0.2
            )
            
            # Leading indicator arrow
            indicator_arrow = Arrow(
                start=LEFT * 9,
                end=RIGHT * 9,
                buff=0,
                color=WHITE,
                stroke_width=6
            ).move_to(DOWN * 3.8)
            
            indicator_label = Text("Leading Indicator: ~5-7 year advance warning",
                                 font_size=28, color=WHITE, weight=BOLD)
            indicator_label.next_to(indicator_arrow, UP, buff=0.3)
            safe_position(indicator_label)
            
            self.play(
                GrowArrow(indicator_arrow),
                FadeIn(indicator_label),
                run_time=tracker.duration * 0.05
            )
