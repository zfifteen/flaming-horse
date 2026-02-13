import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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
from flaming_horse_voice import get_speech_service

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


class Scene02Basics(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["basics"]) as tracker:
            # Timing budget: 0.12 + 0.34 + 0.18 + 0.16 + 0.10 + 0.10 = 1.00
            title = Text("Neural Network Basics", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.12)

            network_group = VGroup()

            layer1 = VGroup()
            for i in range(4):
                node = Circle(radius=0.25, color=BLUE, fill_opacity=0.8)
                node.move_to(np.array([-5, 2 - i * 1.3, 0]))
                layer1.add(node)

            layer2 = VGroup()
            for i in range(3):
                node = Circle(radius=0.25, color=GREEN, fill_opacity=0.8)
                node.move_to(np.array([0, 1.95 - i * 1.95, 0]))
                layer2.add(node)

            layer3 = VGroup()
            for i in range(2):
                node = Circle(radius=0.25, color=ORANGE, fill_opacity=0.8)
                node.move_to(np.array([5, 2.6 - i * 5.2, 0]))
                layer3.add(node)

            network_group.add(layer1, layer2, layer3)
            safe_layout(layer1, layer2, layer3)

            for n1 in layer1:
                for n2 in layer2:
                    line = Line(n1.get_right(), n2.get_left(), color=GRAY)
                    line.set_stroke(opacity=0.5)
                    network_group.add(line)

            for n2 in layer2:
                for n3 in layer3:
                    line = Line(n2.get_right(), n3.get_left(), color=GRAY)
                    line.set_stroke(opacity=0.5)
                    network_group.add(line)

            self.play(FadeIn(network_group), run_time=tracker.duration * 0.34)

            weight_label = Text(
                "Weight = strength of connection", font_size=24, color=YELLOW
            )
            weight_label.move_to(DOWN * 2.5)
            self.play(FadeIn(weight_label), run_time=tracker.duration * 0.18)

            random_label = Text(
                "Start: Random weights = No knowledge", font_size=22, color=RED
            )
            random_label.next_to(weight_label, DOWN, buff=0.3)
            safe_position(random_label)
            self.play(FadeIn(random_label), run_time=tracker.duration * 0.16)

            adjust_label = Text(
                "Learning = Adjusting weights", font_size=22, color=GREEN
            )
            adjust_label.next_to(random_label, DOWN, buff=0.3)
            safe_position(adjust_label)
            self.play(FadeIn(adjust_label), run_time=tracker.duration * 0.10)

            self.wait(tracker.duration * 0.10)