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


class Scene05Conclusion(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )

        with self.voiceover(text=SCRIPT["conclusion"]) as tracker:
            # Timing budget: 0.12 + 0.10 + 0.16 + 0.13 + 0.20 + 0.12 + 0.07 + 0.10 = 1.00
            title = Text("Key Insight", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.12)

            insight_box = Rectangle(width=9, height=4, color=BLUE, fill_opacity=0.15)
            insight_box.move_to(UP * 0.5)

            main_point = Text(
                "The network discovers patterns", font_size=32, color=BLUE
            )
            main_point.move_to(UP * 1.2)

            through_feedback = Text(
                "through feedback, not programming.", font_size=28, color=GREEN
            )
            through_feedback.next_to(main_point, DOWN, buff=0.4)
            safe_position(through_feedback)

            self.play(FadeIn(insight_box), run_time=tracker.duration * 0.10)
            self.play(Write(main_point), run_time=tracker.duration * 0.16)
            self.play(Write(through_feedback), run_time=tracker.duration * 0.13)

            comparison = VGroup()

            old_way = VGroup()
            old_label = Text("Traditional Programming:", font_size=20, color=RED)
            old_label.move_to(LEFT * 3 + UP * 1.5)
            old_way.add(old_label)

            rule1 = Text("If ear=pointed AND whisker=long", font_size=16, color=GRAY)
            rule1.next_to(old_label, DOWN, buff=0.2)
            rule2 = Text("THEN cat = true", font_size=16, color=GRAY)
            rule2.next_to(rule1, DOWN, buff=0.1)
            old_way.add(rule1, rule2)

            new_way = VGroup()
            new_label = Text("Neural Networks:", font_size=20, color=GREEN)
            new_label.move_to(RIGHT * 3 + UP * 1.5)
            new_way.add(new_label)

            rule1n = Text("See thousands of examples", font_size=16, color=GRAY)
            rule1n.next_to(new_label, DOWN, buff=0.2)
            rule2n = Text("Adjust weights from errors", font_size=16, color=GRAY)
            rule2n.next_to(rule1n, DOWN, buff=0.1)
            rule3n = Text("Discover patterns yourself", font_size=16, color=GRAY)
            rule3n.next_to(rule2n, DOWN, buff=0.1)
            new_way.add(rule1n, rule2n, rule3n)

            comparison.add(old_way, new_way)
            comparison.move_to(DOWN * 2)
            safe_layout(old_way, new_way, max_y=-1.5)

            self.play(FadeIn(comparison), run_time=tracker.duration * 0.20)

            summary = Text(
                "Backpropagation: Learning from mistakes",
                font_size=26,
                color=YELLOW,
            )
            summary.move_to(DOWN * 3.5)
            self.play(FadeIn(summary), run_time=tracker.duration * 0.12)

            self.wait(tracker.duration * 0.07)
