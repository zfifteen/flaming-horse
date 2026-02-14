from manim import *
import numpy as np
import colorsys  # New: For harmonious_color

# Python 3.13 Compatibility Patch
import manim_voiceover_plus.services.base as base
original_set_transcription = base.SpeechService.set_transcription

def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self._whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs or {})

base.SpeechService.set_transcription = patched_set_transcription

# Voiceover Imports
from pathlib import Path
from manim_voiceover_plus import VoiceoverScene

from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

# For Qwen caching: Precache check (New)
ref_path = Path("assets/voice_ref/ref.wav")
if not ref_path.exists():
    raise FileNotFoundError("Run precache_voice.sh before building.")

# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560


def safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2):
    """Enhanced: Adjusts vertically with buffer to prevent edge clipping."""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * ((min_y + buff) - bottom))
    return mobject

def harmonious_color(base_color, variations=3, lightness_shift=0.1):
    if hasattr(base_color, 'rgb'):
        rgb_vals = base_color.rgb[:3]
    else:
        rgb_vals = np.array(base_color[:3])
    h, l, s = colorsys.rgb_to_hls(*[float(c) for c in rgb_vals])
    palette = []
    for i in range(variations):
        h_shift = i * (360 / variations) / 360.0
        new_h = (h + h_shift) % 1
        new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, l, s + lightness_shift * i)
        palette.append(ManimColor([new_r, new_g, new_b, 1.0]))
    return palette

def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.1, glow=False):
    if glow:
        mobject.set_stroke(width=3, opacity=0.5)
    return AnimationGroup(
        FadeIn(mobject, lag_ratio=lag_ratio),
        mobject.animate.scale(scale_factor).set_run_time(0.5).set_rate_func(there_and_back_with_pause),
        rate_func=there_and_back_with_pause
    )

def adaptive_title_position(title, content_group, max_shift=0.5):
    content_height = content_group.height if content_group else 0
    shift_y = min(max_shift, max(0, content_height - 2.0))
    title.move_to(UP * (3.8 + shift_y))
    return title

def safe_layout(*mobjects, min_horizontal_spacing=0.5, max_y=4.0, min_y=-4.0):
    """Ensure multiple mobjects don't overlap and stay within safe bounds."""
    for mob in mobjects:
        top = mob.get_top()[1]
        bottom = mob.get_bottom()[1]
        if top > max_y:
            mob.shift(DOWN * (top - max_y))
        elif bottom < min_y:
            mob.shift(UP * (min_y - bottom))

    for i, mob_a in enumerate(mobjects):
        for mob_b in mobjects[i + 1:]:
            a_left = mob_a.get_left()[0]
            a_right = mob_a.get_right()[0]
            b_left = mob_b.get_left()[0]
            b_right = mob_b.get_right()[0]
            if not (a_right < b_left or b_right < a_left):
                overlap = (a_right - b_left) if a_right > b_left else (b_right - a_left)
                mob_b.shift(RIGHT * (overlap + min_horizontal_spacing))

    return VGroup(*mobjects)

# Timing Helpers
class BeatPlan:
    '''Deterministic timing allocator for one voiceover block.

    Use integer-ish weights for each visual beat and consume slots in order.
    Agents should avoid manual wait/run_time math and use this plan instead.
    '''

    def __init__(self, total_duration, weights):
        self.total_duration = max(0.0, float(total_duration))
        cleaned = [max(0.0, float(w)) for w in weights]
        if not cleaned:
            raise ValueError("BeatPlan requires at least one weight")
        weight_sum = sum(cleaned)
        if weight_sum <= 0:
            cleaned = [1.0 for _ in cleaned]
            weight_sum = float(len(cleaned))

        slots = []
        consumed = 0.0
        for idx, weight in enumerate(cleaned):
            if idx == len(cleaned) - 1:
                slot = max(0.0, self.total_duration - consumed)
            else:
                slot = self.total_duration * (weight / weight_sum)
                consumed += slot
            slots.append(slot)
        self._slots = slots
        self._cursor = 0

    def next_slot(self):
        if self._cursor >= len(self._slots):
            return 0.0
        slot = self._slots[self._cursor]
        self._cursor += 1
        return slot


def play_in_slot(scene, slot, *animations, max_run_time=None, min_run_time=0.3, **play_kwargs):
    '''Play one or more animations in a fixed slot and fill remainder with wait.'''
    if not animations:
        return

    slot = max(0.0, float(slot))
    if slot <= 0:
        return

    # Support multiple animations by grouping them into a single animation.
    animation = (
        animations[0]
        if len(animations) == 1
        else LaggedStart(*animations, lag_ratio=0.15)
    )

    run_time = slot
    if max_run_time is not None:
        run_time = min(run_time, float(max_run_time))
    run_time = max(float(min_run_time), run_time)
    run_time = min(run_time, slot)

    scene.play(animation, run_time=run_time, **play_kwargs)
    remaining = slot - run_time
    if remaining > 1e-6:
        scene.wait(remaining)


def play_text_in_slot(scene, slot, *animations, max_text_seconds=2.0, min_run_time=0.3, **play_kwargs):
    '''Text animations must complete quickly; fill the rest with waits.'''
    return play_in_slot(
        scene,
        slot,
        *animations,
        max_run_time=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )


def play_next(scene, beats, *animations, max_run_time=None, min_run_time=0.3, **play_kwargs):
    '''Play next deterministic beat slot from BeatPlan.'''
    return play_in_slot(
        scene,
        beats.next_slot(),
        *animations,
        max_run_time=max_run_time,
        min_run_time=min_run_time,
        **play_kwargs,
    )


def play_text_next(scene, beats, *animations, max_text_seconds=2.0, min_run_time=0.3, **play_kwargs):
    '''Play next beat slot with text reveal cap.'''
    return play_text_in_slot(
        scene,
        beats.next_slot(),
        *animations,
        max_text_seconds=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )

# Scene Class
class Scene02Setup(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        # Palette for cohesion
        blues = harmonious_color(BLUE, variations=3)
        
        # Animation Sequence
        with self.voiceover(text=SCRIPT["setup"]) as tracker:
            beats = BeatPlan(tracker.duration, [3, 3, 3, 3, 2])
            
            # Title
            title = Text("Example Setup", font_size=48, weight=BOLD, color=blues[0])
            title = adaptive_title_position(title, None)
            play_text_next(self, beats, Write(title))
            
            # Subtitle
            subtitle = Text("Division Bracket Structure", font_size=32, color=blues[1])
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            play_text_next(self, beats, polished_fade_in(subtitle, lag_ratio=0.1))
            
            # Divisor (outside left)
            divisor = MathTex(r"x + 1", font_size=42, color=blues[2])
            divisor.move_to(LEFT * 4 + ORIGIN)
            divisor_label = Text("Divisor", font_size=28, color=blues[0], weight=BOLD)
            divisor_label.next_to(divisor, UP, buff=0.15)
            safe_position(divisor_label)
            play_next(self, beats, Write(VGroup(divisor, divisor_label)), rate_func=smooth)
            
            # Division bracket
            top_bar = Line(LEFT * 1, RIGHT * 3.5).move_to(UP * 1.2)
            left_vert = Line(UP * 1.2 + LEFT * 1, DOWN * 2.5 + LEFT * 1)
            bracket = VGroup(top_bar, left_vert).set_stroke(width=4, color=GREY_A)
            play_next(self, beats, Create(bracket))
            
            # Dividend (inside bracket)
            dividend = MathTex(r"x^{3} + 3x^{2} + x - 3", font_size=42, color=blues[2])
            dividend.move_to(ORIGIN)
            dividend_label = Text("Dividend", font_size=28, color=blues[0], weight=BOLD)
            dividend_label.next_to(dividend, UP, buff=0.15)
            safe_position(dividend_label)
            play_next(self, beats, Write(VGroup(dividend, dividend_label)), rate_func=smooth)
            
            # Ensure no overlaps
            all_content = VGroup(divisor, divisor_label, bracket, dividend, dividend_label)
            safe_layout(*all_content)
            
            # Buffer
            self.wait(tracker.duration * 0.05)