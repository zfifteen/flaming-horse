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


class Scene03ForwardPass(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["forward_pass"]) as tracker:
            # Timing budget: 0.07 + 0.12 + 0.07 + 0.12 + 0.23 + 0.10 + 0.13 + 0.06 + 0.10 = 1.00
            title = Text("The Forward Pass", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.07)

            network = VGroup()

            input_layer = VGroup()
            for i in range(4):
                node = Square(side_length=0.5, color=BLUE, fill_opacity=0.8)
                node.move_to(np.array([-5, 1.5 - i * 1.0, 0]))
                input_layer.add(node)

            hidden_layer = VGroup()
            for i in range(3):
                node = Circle(radius=0.25, color=GREEN, fill_opacity=0.8)
                node.move_to(np.array([0, 0.9 - i * 0.9, 0]))
                hidden_layer.add(node)

            output_layer = VGroup()
            for i in range(2):
                node = Circle(radius=0.3, color=ORANGE, fill_opacity=0.8)
                node.move_to(np.array([5, 0.3 - i * 0.6, 0]))
                output_layer.add(node)

            for n1 in input_layer:
                for n2 in hidden_layer:
                    line = Line(n1.get_right(), n2.get_left(), color=GRAY)
                    line.set_stroke(opacity=0.4)
                    network.add(line)

            for n2 in hidden_layer:
                for n3 in output_layer:
                    line = Line(n2.get_right(), n3.get_left(), color=GRAY)
                    line.set_stroke(opacity=0.4)
                    network.add(line)

            network.add(input_layer, hidden_layer, output_layer)
            safe_layout(input_layer, hidden_layer, output_layer)

            self.play(FadeIn(network), run_time=tracker.duration * 0.12)

            input_data = Text("Input: Image Pixels", font_size=20, color=BLUE)
            input_data.next_to(input_layer, LEFT, buff=0.3)
            safe_position(input_data)
            self.play(FadeIn(input_data), run_time=tracker.duration * 0.07)

            pixel_animation = []
            for node in input_layer:
                pixel = RoundedRectangle(
                    width=0.3, height=0.3, fill_opacity=0.9, color=BLUE_E
                )
                pixel.move_to(node.get_left() + LEFT * 1.5)
                pixel_animation.append(FadeIn(pixel))

            self.play(*pixel_animation, run_time=tracker.duration * 0.12)

            flow_anim = []
            for n1 in input_layer:
                for n2 in hidden_layer:
                    pulse = Circle(radius=0.1, color=YELLOW, fill_opacity=0.9)
                    pulse.move_to(n1.get_right())
                    flow_anim.append(FadeIn(pulse))
                    flow_anim.append(
                        pulse.animate.move_to(n2.get_left()).set_opacity(0)
                    )

            self.play(*flow_anim, run_time=tracker.duration * 0.23)

            for node in hidden_layer:
                node.set_fill(GREEN, 1.0)
            self.play(
                *[Flash(node, color=WHITE, flash_radius=0.5) for node in hidden_layer],
                run_time=tracker.duration * 0.10,
            )

            flow_anim2 = []
            for n2 in hidden_layer:
                for n3 in output_layer:
                    pulse = Circle(radius=0.1, color=YELLOW, fill_opacity=0.9)
                    pulse.move_to(n2.get_right())
                    flow_anim2.append(FadeIn(pulse))
                    flow_anim2.append(
                        pulse.animate.move_to(n3.get_left()).set_opacity(0)
                    )

            self.play(*flow_anim2, run_time=tracker.duration * 0.13)

            prediction = Text('Prediction: "90% Cat"', font_size=28, color=GREEN)
            prediction.next_to(output_layer, RIGHT, buff=0.5)
            safe_position(prediction)
            self.play(FadeIn(prediction), run_time=tracker.duration * 0.06)

            self.wait(tracker.duration * 0.10)