from manim import *
import numpy as np

# ── Python 3.13 Compatibility Patch ─────────────────────────────────
import manim_voiceover_plus.services.base as base
original_set_transcription = base.SpeechService.set_transcription

def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self.whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs)

base.SpeechService.set_transcription = patched_set_transcription

# ── Voiceover Imports ──────────────────────────────────────
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

# ── Import Shared Configuration ────────────────────────────────
from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS
from narration_script import SCRIPT

# ── LOCKED CONFIGURATION (DO NOT MODIFY) ─────────────────────────
config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

# ── Safe Positioning Helper ──────────────────────────────────
def safe_position(mobject, max_y=4.0, min_y=-4.0):
    """Ensure mobject stays within safe bounds after positioning"""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject

# ── Scene Class ─────────────────────────────────────────
class Scene01PhaseFlip(VoiceoverScene):
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
        # Timing budget: 0.15 + 0.15 + 0.20 + 0.10 + 0.25 + 0.15 = 1.0
        
        with self.voiceover(text=SCRIPT["phase_flip"]) as tracker:
            # Title (ALWAYS use UP * 3.8)
            title = Text("Chandler Wobble's Hidden Message", font_size=48, weight=BOLD, color=WHITE)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.15)
            
            # Subtitle
            subtitle = Text("A Core-Mantle Coupling Diagnostic", font_size=32, color="#00F5FF")
            subtitle.next_to(title, DOWN, buff=0.5)
            safe_position(subtitle)
            self.play(FadeIn(subtitle), run_time=tracker.duration * 0.15)
            
            # Earth wireframe with rotation axis
            earth = Sphere(radius=1.2, resolution=(20, 20)).set_color("#004E89").set_opacity(0.3)
            earth.move_to(ORIGIN)
            rotation_axis = Arrow(start=DOWN*2, end=UP*2, color=CYAN, buff=0, stroke_width=4)
            
            self.play(
                Create(earth),
                GrowArrow(rotation_axis),
                run_time=tracker.duration * 0.20
            )
            
            # Chandler wobble spiral (clockwise)
            spiral_points = []
            for t in np.linspace(0, 4*PI, 80):
                x = 0.15 * np.cos(t)
                y = 2.0 + 0.15 * np.sin(t)  # Near pole
                z = 0
                spiral_points.append([x, y, z])
            
            cw_spiral = VMobject(color="#00F5FF", stroke_width=3)
            cw_spiral.set_points_as_corners(spiral_points)
            
            self.play(Create(cw_spiral), run_time=tracker.duration * 0.10)
            
            # Spiral disappears
            self.play(FadeOut(cw_spiral), run_time=tracker.duration * 0.25)
            
            # Spiral reappears inverted (counterclockwise)
            spiral_points_inv = []
            for t in np.linspace(0, 4*PI, 80):
                x = 0.15 * np.cos(-t)  # Negative t for counterclockwise
                y = 2.0 + 0.15 * np.sin(-t)
                z = 0
                spiral_points_inv.append([x, y, z])
            
            cw_spiral_inv = VMobject(color="#FFC857", stroke_width=3)
            cw_spiral_inv.set_points_as_corners(spiral_points_inv)
            
            # Phase arrow
            phase_arrow = CurvedArrow(
                start_point=RIGHT * 0.8 + UP * 2.5,
                end_point=LEFT * 0.8 + UP * 2.5,
                angle=-PI,
                color="#FFC857",
                stroke_width=6
            )
            phase_label = Text("180° PHASE FLIP", font_size=28, color="#FFC857", weight=BOLD)
            phase_label.next_to(phase_arrow, UP, buff=0.3)
            safe_position(phase_label)
            
            # Core-mantle boundary glow
            cmb_glow = Circle(radius=0.6, color="#FF6B35", fill_opacity=0.4, stroke_width=0)
            cmb_glow.move_to(ORIGIN)
            
            self.play(
                Create(cw_spiral_inv),
                Create(phase_arrow),
                FadeIn(phase_label),
                FadeIn(cmb_glow),
                run_time=tracker.duration * 0.15
            )
