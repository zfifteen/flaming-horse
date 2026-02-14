from manim import *
import numpy as np
import colorsys
from manim.utils.color import rgb_to_color

# Python 3.13 Compatibility Patch
import manim_voiceover_plus.services.base as base
original_set_transcription = base.SpeechService.set_transcription

def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self.whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs or {})

base.SpeechService.set_transcription = patched_set_transcription

from pathlib import Path

from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

# For Qwen caching: Precache check
ref_path = Path("assets/voice_ref/ref.wav")
if not ref_path.exists():
    raise FileNotFoundError("Run precache_voice.sh before building.")

# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

# Safe Positioning Helper (Enhanced)
def safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2):
    """Enhanced: Adjusts vertically with buffer to prevent edge clipping."""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * ((min_y + buff) - bottom))
    return mobject

# Enhanced Visual Helpers
def harmonious_color(base_color, variations=3, lightness_shift=0.1):
    r, g, b = colorsys.rgb_to_hls(*base_color[:3])
    palette = []
    for i in range(variations):
        h_shift = i * (360 / variations) / 360
        new_h = (r + h_shift) % 1
        new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, g, b + lightness_shift * i)
        palette.append(rgb_to_color(np.array([new_r, new_g, new_b])))
    return palette

def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.1, glow=False):
    if glow:
        mobject.set_stroke(width=3, opacity=0.5)
    return AnimationGroup(
        FadeIn(mobject, lag_ratio=lag_ratio),
        Succession(mobject.animate.scale(scale_factor), mobject.animate.scale(1 / scale_factor)).set_run_time(0.5),
        rate_func=there_and_back_with_pause
    )

def adaptive_title_position(title, content_group, max_shift=0.5):
    content_height = content_group.height if content_group else 0
    shift_y = min(max_shift, max(0, content_height - 2.0))
    title.move_to(UP * (3.8 + shift_y))
    return title

def safe_layout(*mobjects, alignment=ORIGIN, h_buff=0.5, v_buff=0.3, max_y=3.5, min_y=-3.5):
    """Enhanced: Positions siblings horizontally/vertically without overlaps, with alignment."""
    group = VGroup(*mobjects)
    group.arrange(RIGHT, buff=h_buff, aligned_edge=UP if v_buff else alignment)
    for mob in mobjects:
        safe_position(mob, max_y, min_y)
    for i, mob_a in enumerate(mobjects):
        for j, mob_b in enumerate(mobjects[i+1:], i+1):
            if mob_a.get_right()[0] > mob_b.get_left()[0] - h_buff:
                overlap = mob_a.get_right()[0] - mob_b.get_left()[0] + h_buff
                mob_b.shift(RIGHT * overlap)
    return VGroup(*mobjects)

class Scene01Intro(VoiceoverScene):
    def construct(self):
        # Palette for cohesion
        blues = harmonious_color(BLUE, variations=3)
        
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
        # Animation Sequence with timing budget
        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            # Title
            title = Text("Introduction to Long Division", font_size=48, weight=BOLD, color=blues[0])
            title = adaptive_title_position(title, None)
            self.play(Write(title), run_time=min(1.5, tracker.duration * 0.3))
            
            # Subtitle
            subtitle = Text("Efficient Way for Large Numbers", font_size=32, color=blues[1])
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            self.play(polished_fade_in(subtitle, lag_ratio=0.1), run_time=min(1.5, tracker.duration * 0.3))
            
            # Simple division graphic
            div_example = MathTex(r"12\,345 \\div 23", font_size=48, color=blues[2])
            div_example.move_to(DOWN * 0.6)
            safe_position(div_example)
            self.play(Write(div_example), run_time=min(2.0, tracker.duration * 0.3), rate_func=smooth)
            
            # Buffer
            self.wait(max(0, tracker.duration * 0.1))
        
        # Fade out for next scene transition if needed
        self.play(FadeOut(VGroup(title, subtitle, div_example)), run_time=1.0)