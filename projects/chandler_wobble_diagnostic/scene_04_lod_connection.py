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
class Scene04LODConnection(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )
        
        # Timing budget: 0.15 + 0.20 + 0.25 + 0.25 + 0.15 = 1.0
        
        with self.voiceover(text=SCRIPT["lod_connection"]) as tracker:
            # Split screen: CW vs LOD
            cw_label = Text("Chandler Wobble\n(433-day)", font_size=32, color="#00F5FF")
            cw_label.move_to(LEFT * 5 + UP * 3.2)
            
            lod_label = Text("6-Year LOD\nOscillation", font_size=32, color="#FFC857")
            lod_label.move_to(RIGHT * 5 + UP * 3.2)
            
            # CW wave (fast)
            cw_axes = Axes(x_range=[0, 6, 1], y_range=[-1, 1, 1],
                          x_length=4, y_length=2, tips=False).move_to(LEFT * 5 + UP * 1)
            cw_wave = cw_axes.plot(lambda x: np.sin(10 * x), color="#00F5FF", stroke_width=3)
            
            # LOD wave (slow)
            lod_axes = Axes(x_range=[0, 6, 1], y_range=[-1, 1, 1],
                           x_length=4, y_length=2, tips=False).move_to(RIGHT * 5 + UP * 1)
            lod_wave = lod_axes.plot(lambda x: np.sin(1.5 * x), color="#FFC857", stroke_width=3)
            
            self.play(
                FadeIn(cw_label),
                FadeIn(lod_label),
                Create(cw_axes),
                Create(lod_axes),
                Create(cw_wave),
                Create(lod_wave),
                run_time=tracker.duration * 0.15
            )
            
            # Earth cross-section with Alfven waves
            earth_core = Circle(radius=0.6, color="#FF6B35", fill_opacity=0.6).move_to(DOWN * 1.5)
            earth_mantle = Annulus(inner_radius=0.6, outer_radius=1.2, 
                                  color="#004E89", fill_opacity=0.4).move_to(DOWN * 1.5)
            
            # Torsional Alfven waves (concentric rings)
            alfven_rings = VGroup()
            for r in np.linspace(0.3, 1.1, 5):
                ring = Circle(radius=r, color="#FF6B35", stroke_width=2, stroke_opacity=0.6)
                ring.move_to(DOWN * 1.5)
                alfven_rings.add(ring)
            
            cmb_label = Text("Torsional Alfvén Waves\nat Core-Mantle Boundary",
                           font_size=24, color="#FF6B35")
            cmb_label.move_to(DOWN * 3.3)
            safe_position(cmb_label)
            
            self.play(
                FadeIn(earth_core),
                FadeIn(earth_mantle),
                *[Create(ring) for ring in alfven_rings],
                FadeIn(cmb_label),
                run_time=tracker.duration * 0.20
            )
            
            # Timeline with disruptions
            timeline = Line(LEFT * 7, RIGHT * 7, color=WHITE, stroke_width=2).move_to(UP * 0.5)
            
            year_labels = VGroup()
            for year in [2010, 2014, 2019, 2021, 2027]:
                x_pos = (year - 2010) / 17 * 14 - 7
                tick = Line(UP * 0.1, DOWN * 0.1, color=WHITE).move_to([x_pos, 0.5, 0])
                label = Text(str(year), font_size=20, color=WHITE)
                label.next_to(tick, DOWN, buff=0.15)
                year_labels.add(VGroup(tick, label))
            
            self.play(
                FadeOut(cw_axes), FadeOut(lod_axes),
                FadeOut(cw_wave), FadeOut(lod_wave),
                FadeOut(earth_core), FadeOut(earth_mantle),
                FadeOut(alfven_rings), FadeOut(cmb_label),
                Create(timeline),
                *[FadeIn(y) for y in year_labels],
                run_time=tracker.duration * 0.25
            )
            
            # Disruption regions
            lod_disruption = Rectangle(width=2.5, height=0.8, color=RED, 
                                      fill_opacity=0.3, stroke_width=2)
            lod_disruption.move_to([-5.3, 1.8, 0])
            lod_label_d = Text("LOD Disruption\n2010-2014", font_size=22, color=RED)
            lod_label_d.next_to(lod_disruption, UP, buff=0.2)
            safe_position(lod_label_d)
            
            cw_disruption = Rectangle(width=1.2, height=0.8, color=PURPLE,
                                     fill_opacity=0.3, stroke_width=2)
            cw_disruption.move_to([0.3, 1.8, 0])
            cw_label_d = Text("CW Flip\n2019-2021", font_size=22, color=PURPLE)
            cw_label_d.next_to(cw_disruption, UP, buff=0.2)
            safe_position(cw_label_d)
            
            # Offset arrow
            offset_arrow = DoubleArrow(start=lod_disruption.get_right(),
                                      end=cw_disruption.get_left(),
                                      buff=0.1, color="#FFC857", stroke_width=4)
            offset_label = Text("5-7 year offset", font_size=24, color="#FFC857", weight=BOLD)
            offset_label.next_to(offset_arrow, DOWN, buff=0.2)
            safe_position(offset_label)
            
            # 2027 projection
            projection = DashedLine(start=[4, 0.5, 0], end=[4, 3, 0], 
                                   color="#00F5FF", stroke_width=3)
            question = Text("?", font_size=48, color="#00F5FF", weight=BOLD)
            question.move_to([4, 3.3, 0])
            
            self.play(
                FadeIn(lod_disruption), FadeIn(lod_label_d),
                FadeIn(cw_disruption), FadeIn(cw_label_d),
                GrowArrow(offset_arrow), FadeIn(offset_label),
                Create(projection), FadeIn(question),
                run_time=tracker.duration * 0.25
            )
            
            self.wait(tracker.duration * 0.15)
