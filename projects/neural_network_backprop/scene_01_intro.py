from manim import *
import numpy as np

import manim_voiceover_plus.services.base as base

original_set_transcription = base.SpeechService.set_transcription


def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self.whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs)


base.SpeechService.set_transcription = patched_set_transcription

from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS
from narration_script import SCRIPT

config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560


def safe_position(mobject, max_y=4.0, min_y=-4.0):
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject


def safe_layout(*mobjects, min_horizontal_spacing=0.5, max_y=4.0, min_y=-4.0):
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


class Scene01Intro(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )

        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            # Timing budget: 0.20 + 0.10 + 0.25 + 0.25 + 0.20 = 1.00
            title = Text("How Neural Networks Learn", font_size=56, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.20)

            subtitle = Text("Backpropagation Explained", font_size=36, color=BLUE)
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            self.play(FadeIn(subtitle), run_time=tracker.duration * 0.10)

            hook = Text(
                '"How does a computer learn to recognize\na cat when no one programmed the rules?"',
                font_size=28,
            )
            hook.move_to(ORIGIN)
            self.play(FadeIn(hook), run_time=tracker.duration * 0.25)

            icon_group = VGroup()
            photo = RoundedRectangle(
                width=1.5, height=1.2, corner_radius=0.1, color=WHITE, fill_opacity=0.1
            )
            cat_ears = VGroup(
                Line(
                    photo.get_top() + LEFT * 0.2 + DOWN * 0.1,
                    photo.get_top() + LEFT * 0.35 + UP * 0.15,
                ),
                Line(
                    photo.get_top() + LEFT * 0.35 + UP * 0.15,
                    photo.get_top() + LEFT * 0.35 + DOWN * 0.05,
                ),
                Line(
                    photo.get_top() + RIGHT * 0.2 + DOWN * 0.1,
                    photo.get_top() + RIGHT * 0.35 + UP * 0.15,
                ),
                Line(
                    photo.get_top() + RIGHT * 0.35 + UP * 0.15,
                    photo.get_top() + RIGHT * 0.35 + DOWN * 0.05,
                ),
            )
            cat_ears.set_color(WHITE)
            icon_group.add(photo, cat_ears)
            icon_group.move_to(hook.get_bottom() + DOWN * 1.5)
            self.play(FadeIn(icon_group), run_time=tracker.duration * 0.25)

            self.wait(tracker.duration * 0.20)
