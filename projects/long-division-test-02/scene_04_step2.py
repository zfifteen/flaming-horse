from manim import *
import numpy as np
import colorsys  # New: For harmonious_color
from manim.utils.color import color_to_rgb

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
    r, g, b = colorsys.rgb_to_hls(*color_to_rgb(base_color))
    palette = []
    for i in range(variations):
        h_shift = i * (360 / variations) / 360
        new_h = (r + h_shift) % 1
        new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, g, b + lightness_shift * i)
        palette.append("#%02x%02x%02x" % (int(float(new_r)*255 + 0.5), int(float(new_g)*255 + 0.5), int(float(new_b)*255 + 0.5)))
    return palette

def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.1, glow=False):
    if glow:
        mobject.set_stroke(width=3, opacity=0.5)
    return FadeIn(mobject, lag_ratio=lag_ratio, rate_func=there_and_back_with_pause)

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
class Scene04Step2(VoiceoverScene):
    def construct(self):
        # Palette for cohesion (New)
        blues = harmonious_color(BLUE, variations=3)
        
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
        # Animation Sequence
        # Timing is deterministic via BeatPlan helper slots.
        
        with self.voiceover(text=SCRIPT["step2"]) as tracker:
            beats = BeatPlan(tracker.duration, [2, 2, 2, 2, 2, 2, 2, 2])
            
            # Title (ALWAYS use UP * 3.8, NEVER .to_edge(UP)); Adaptive (New)
            title = Text("Step 2: Bring Down and Repeat", font_size=48, weight=BOLD, color=blues[0])
            title = adaptive_title_position(title, None)  # No content yet
            play_text_next(self, beats, Write(title, run_time=1.5))  # Cap at 1.5s (New)
            
            # Subtitle with safe positioning
            subtitle = Text("Next Quotient Term", font_size=32, color=blues[1])
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)  # ALWAYS call after .next_to()
            play_text_next(self, beats, polished_fade_in(subtitle, lag_ratio=0.1))  # Polished (New)
            
            # Current state from previous: divisor, bracket, partial remainder
            divisor = MathTex(r"x + 1", font_size=42, color=blues[2])
            divisor.move_to(LEFT * 4 + ORIGIN)
            bracket_top = Line(LEFT * 1, RIGHT * 3.5).move_to(UP * 1.2)
            bracket_left = Line(UP * 1.2 + LEFT * 1, DOWN * 2.5 + LEFT * 1)
            bracket = VGroup(bracket_top, bracket_left).set_stroke(width=4, color=GREY_A)
            partial_remainder = MathTex(r"2x^{2} + x - 3", font_size=42, color=blues[2])
            partial_remainder.move_to(ORIGIN)
            # Previous quotient
            prev_quotient = MathTex(r"x^{2}", font_size=42, color=GREEN)
            prev_quotient.next_to(bracket_top.get_left(), UP, buff=0.4, aligned_edge=LEFT)
            safe_position(prev_quotient)
            current_state = VGroup(divisor, bracket, partial_remainder, prev_quotient)
            play_next(self, beats, polished_fade_in(current_state, lag_ratio=0.1), rate_func=smooth)
            
            # Highlight leading terms
            lead_anims = LaggedStart(
                Indicate(partial_remainder[0], color=YELLOW, scale_factor=1.2),
                Indicate(divisor[0], color=YELLOW, scale_factor=1.2),
                lag_ratio=0.5
            )
            play_next(self, beats, lead_anims)
            
            # Next quotient term: 2x
            next_quotient = MathTex(r"+ 2x", font_size=42, color=GREEN)
            next_quotient.next_to(prev_quotient, RIGHT, buff=0.1, aligned_edge=LEFT)
            safe_position(next_quotient)
            play_next(self, beats, Write(next_quotient, run_time=1.5), rate_func=smooth)
            
            # Product: 2x² + 2x
            product = MathTex(r"2x^{2} + 2x", font_size=42, color=RED)
            product.next_to(partial_remainder, DOWN, buff=0.15)
            product.align_to(partial_remainder, LEFT)
            safe_position(product)
            play_next(self, beats, Write(product, run_time=2.0), rate_func=smooth)
            
            # Subtract animation
            subtract_group = AnimationGroup(
                partial_remainder.animate.set_color(YELLOW),
                product.animate.set_stroke(width=6, opacity=0.8),
                lag_ratio=0.2
            )
            play_next(self, beats, subtract_group, rate_func=there_and_back_with_pause)
            
            # New partial remainder: -x - 3
            new_remainder = MathTex(r"-x - 3", font_size=42, color=blues[2])
            new_remainder.move_to(ORIGIN)
            full_quotient = MathTex(r"x^{2} + 2x", font_size=42, color=GREEN)
            full_quotient.next_to(bracket_top.get_left(), UP, buff=0.4, aligned_edge=LEFT)
            safe_position(full_quotient)
            play_next(self, beats, ReplacementTransform(partial_remainder, new_remainder), FadeOut(product), Transform(prev_quotient, full_quotient), rate_func=smooth)
            
            # Ensure no overlaps
            all_content = VGroup(title, subtitle, divisor, bracket, full_quotient, new_remainder)
            safe_layout(*all_content)
            
            # Always end with buffer (New)
            self.wait(tracker.duration * 0.1)