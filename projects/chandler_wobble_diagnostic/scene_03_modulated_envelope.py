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
class Scene03ModulatedEnvelope(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
        # Timing budget: 0.25 + 0.25 + 0.30 + 0.20 = 1.0
        
        with self.voiceover(text=SCRIPT["modulated_envelope"]) as tracker:
            # Fast sinusoidal wave (433-day Chandler period)
            axes = Axes(
                x_range=[0, 12, 1],
                y_range=[-2, 2, 1],
                x_length=12,
                y_length=4,
                tips=False
            ).move_to(UP * 0.5)
            
            # High frequency carrier (Chandler wobble)
            fast_wave = axes.plot(
                lambda x: np.sin(8 * x),
                color="#00F5FF",
                stroke_width=3
            )
            
            label = Text("Chandler Wobble (433-day period)", font_size=28, color="#00F5FF")
            label.move_to(UP * 3.8)
            
            self.play(
                Create(axes),
                Create(fast_wave),
                FadeIn(label),
                run_time=tracker.duration * 0.25
            )
            
            # Slow envelope wave
            envelope = axes.plot(
                lambda x: np.cos(0.5 * x),
                color="#004E89",
                stroke_width=6
            ).set_opacity(0.6)
            
            envelope_label = Text("Modulating Envelope", font_size=28, color="#004E89")
            envelope_label.next_to(label, DOWN, buff=0.5)
            safe_position(envelope_label)
            
            self.play(
                Create(envelope),
                FadeIn(envelope_label),
                run_time=tracker.duration * 0.25
            )
            
            # Modulated wave (carrier * envelope) with node crossing
            modulated_wave = axes.plot(
                lambda x: np.sin(8 * x) * np.cos(0.5 * x),
                color="#FFC857",
                stroke_width=4
            )
            
            # Node point indicator
            node_x = PI  # First zero crossing of envelope
            node_point = Dot(axes.c2p(node_x, 0), color=RED, radius=0.15)
            node_label = Text("Node Crossing", font_size=24, color=RED, weight=BOLD)
            node_label.next_to(node_point, UP, buff=0.3)
            safe_position(node_label)
            
            arrow = Arrow(
                start=node_label.get_bottom(),
                end=node_point.get_top(),
                buff=0.1,
                color=RED,
                stroke_width=4
            )
            
            self.play(
                Transform(fast_wave, modulated_wave),
                FadeIn(node_point),
                FadeIn(node_label),
                GrowArrow(arrow),
                run_time=tracker.duration * 0.30
            )
            
            # Zoom out to show Earth core-mantle connection
            earth_section = VGroup(
                Circle(radius=0.8, color="#FF6B35", fill_opacity=0.6, stroke_width=2),  # Core
                Annulus(inner_radius=0.8, outer_radius=1.4, color="#004E89", 
                       fill_opacity=0.4, stroke_width=2)  # Mantle
            ).scale(0.8).move_to(DOWN * 2.5)
            
            connection_arrow = Arrow(
                start=axes.c2p(6, -2.5),
                end=earth_section.get_top(),
                buff=0.1,
                color="#FF6B35",
                stroke_width=4
            )
            
            cmb_label = Text("Core-Mantle Boundary", font_size=24, color="#FF6B35")
            cmb_label.next_to(earth_section, DOWN, buff=0.3)
            safe_position(cmb_label)
            
            self.play(
                FadeIn(earth_section),
                GrowArrow(connection_arrow),
                FadeIn(cmb_label),
                run_time=tracker.duration * 0.20
            )