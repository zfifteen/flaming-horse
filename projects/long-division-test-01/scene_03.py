from manim import *
import numpy as np
import colorsys

# Python 3.13 Compatibility Patch
import manim_voiceover_plus.services.base as base
original_set_transcription = base.SpeechService.set_transcription

def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self.whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs)

base.SpeechService.set_transcription = patched_set_transcription

# Voiceover Imports
from pathlib import Path
from manim_voiceover_plus import VoiceoverScene
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from flaming_horse_voice import get_speech_service

from narration_script import SCRIPT

# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

# For Qwen caching: Precache check (New)
ref_path = Path("assets/voice_ref/ref.wav")
if not ref_path.exists():
    raise FileNotFoundError("Run precache_voice.sh before building.")

# Safe Positioning Helper
def safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2):
    """Enhanced: Adjusts vertically with buffer to prevent edge clipping."""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * ((min_y + buff) - bottom))
    return mobject


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

def harmonious_color(base_color, variations=3, lightness_shift=0.1):
    rgb = base_color.get_rgb()
    r, g, b = colorsys.rgb_to_hls(*rgb)
    palette = []
    for i in range(variations):
        h_shift = i * (360 / variations) / 360
        new_h = (r + h_shift) % 1
        new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, g, b + lightness_shift * i)
        palette.append([new_r, new_g, new_b, 1.0])
    return palette

def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.1, glow=False):
    if glow:
        mobject.set_stroke(width=3, opacity=0.5)
    return AnimationGroup(
        FadeIn(mobject, lag_ratio=lag_ratio),
        mobject.animate.scale(scale_factor).set_run_time(0.5).rate_func(there_and_back_with_pause),
        rate_func=there_and_back_with_pause
    )

def adaptive_title_position(title, content_group, max_shift=0.5):
    content_height = content_group.height if content_group else 0
    shift_y = min(max_shift, max(0, content_height - 2.0))
    title.move_to(UP * (3.8 + shift_y))
    return title


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
class Scene03Step1(VoiceoverScene):
    def construct(self):
        # Palette for cohesion (New)
        blues = harmonious_color(BLUE, variations=3)
        
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing is deterministic: define beat weights, then consume slots in order.
        with self.voiceover(text=SCRIPT["step1"]) as tracker:
                        # Define beats for timing (adjust weights to fit narration rhythm)
            beats = BeatPlan(tracker.duration, [3, 2, 2, 2, 2, 1, 1])

            # Title
            title = Text("Step 1: First Division", font_size=48, weight=BOLD, color=blues[0])
            title = adaptive_title_position(title, None)  # No content yet
            play_text_next(self, beats, Write(title, run_time=1.5))  # Cap at 1.5s (New)

            # Subtitle
            subtitle = Text("23 into 123?", font_size=32, color=blues[1])
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)  # ALWAYS call after .next_to()
            play_text_next(self, beats, polished_fade_in(subtitle, lag_ratio=0.1))  # Polished (New)

            # Diagram setup
            divisor = MathTex(r"23", font_size=48, color=blues[0]).move_to(LEFT * 3)
            partial_dividend = MathTex(r"123", font_size=48, color=blues[1]).next_to(divisor, RIGHT, buff=1.0)
            safe_position(partial_dividend)
            diagram = VGroup(divisor, partial_dividend)
            play_next(self, beats, Create(diagram, run_time=2.0, rate_func=smooth))  # Smooth (New)

            # Quotient digit
            quotient_digit = MathTex(r"5", font_size=48, color=blues[2]).move_to(partial_dividend.get_center() + UP * 0.8)
            safe_position(quotient_digit)
            play_text_next(self, beats, Write(quotient_digit))

            # Product 115
            product = MathTex(r"115", font_size=48, color=YELLOW).move_to(partial_dividend.get_bottom() + DOWN * 0.3)
            safe_position(product)
            play_next(self, beats, Write(product))

            # Subtraction line
            sub_line = Line(product.get_top(), partial_dividend.get_bottom(), color=RED, stroke_width=6)
            safe_position(sub_line)
            play_next(self, beats, Create(sub_line, rate_func=smooth))

            # Remainder 8
            remainder = MathTex(r"8", font_size=48, color=ORANGE).move_to(product.get_bottom() + DOWN * 0.5)
            safe_position(remainder)
            play_text_next(self, beats, polished_fade_in(remainder, lag_ratio=0.1))



            # Small buffer
            self.wait(tracker.duration * 0.1)
