from manim import *
import numpy as np

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
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

# Import Shared Configuration
from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS
from narration_script import SCRIPT

# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560


# Safe Positioning Helper
def safe_position(mobject, max_y=4.0, min_y=-4.0):
    """Ensure mobject stays within safe bounds after positioning"""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject


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
        for mob_b in mobjects[i + 1 :]:
            a_left = mob_a.get_left()[0]
            a_right = mob_a.get_right()[0]
            b_left = mob_b.get_left()[0]
            b_right = mob_b.get_right()[0]
            if not (a_right < b_left or b_right < a_left):
                overlap = (a_right - b_left) if a_right > b_left else (b_right - a_left)
                mob_b.shift(RIGHT * (overlap + min_horizontal_spacing))

    return list(mobjects)


# Timing Helpers
def play_in_slot(
    scene, animation, slot, *, max_run_time=None, min_run_time=0.3, **play_kwargs
):
    """Play an animation, then wait to fill the remaining slot time.

    Args:
        scene: The Manim scene (typically `self`)
        animation: A Manim Animation instance (e.g., Write(title))
        slot: Total time budget for this beat (seconds)
        max_run_time: Optional cap for the animation portion (seconds)
        min_run_time: Minimum perceptible animation time (seconds)
        **play_kwargs: Passed to scene.play(...)
    """
    slot = float(slot)
    if slot <= 0:
        return

    run_time = slot
    if max_run_time is not None:
        run_time = min(run_time, float(max_run_time))
    run_time = max(float(min_run_time), run_time)
    run_time = min(run_time, slot)

    scene.play(animation, run_time=run_time, **play_kwargs)
    remaining = slot - run_time
    if remaining > 1e-6:
        scene.wait(remaining)


def play_text_in_slot(
    scene, animation, slot, *, max_text_seconds=2.0, min_run_time=0.3, **play_kwargs
):
    """Text animations must complete quickly; fill the rest with waits."""
    return play_in_slot(
        scene,
        animation,
        slot,
        max_run_time=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )


# Scene Class
class Scene02Bottleneck(VoiceoverScene):
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

        # Animation Sequence
        # Timing budget: 0.2 + 0.3 + 0.5 = 1.0 ✓
        with self.voiceover(text=SCRIPT["bottleneck"]) as tracker:
            # Title
            title = Text("The Bottleneck Theorem", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_in_slot(self, Write(title), tracker.duration * 0.2)

            # Equation
            equation = Text(
                "Perceptual Dimensions ≤ min(Receptors, Neural Channels)",
                font_size=36,
                color=BLUE,
            )
            equation.next_to(title, DOWN, buff=0.5)
            safe_position(equation)
            play_text_in_slot(self, Write(equation), tracker.duration * 0.3)

            # Comparison
            comparison1 = Text(
                "Mantis Shrimp: 12 Receptors → Shallow Processing", font_size=32
            )
            comparison1.move_to(LEFT * 3 + DOWN * 1)
            comparison2 = Text("Humans: 3 Receptors → Deep Processing", font_size=32)
            comparison2.move_to(RIGHT * 3 + DOWN * 1)
            safe_layout(comparison1, comparison2)
            play_in_slot(
                self,
                AnimationGroup(Write(comparison1), Write(comparison2)),
                tracker.duration * 0.5,
            )
