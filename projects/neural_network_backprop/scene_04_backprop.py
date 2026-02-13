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


class Scene04Backprop(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )

        with self.voiceover(text=SCRIPT["backprop"]) as tracker:
            # Timing budget: 0.07 + 0.10 + 0.08 + 0.06 + 0.07 + 0.14 + 0.06 + 0.14 + 0.07 + 0.06 + 0.06 + 0.05 + 0.04 = 1.00
            title = Text("Backpropagation", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.07)

            error_banner = Rectangle(width=8, height=1.2, color=RED, fill_opacity=0.2)
            error_banner.move_to(UP * 2.2)

            error_text = Text(
                "ERROR: Said 'Cat' but it was a 'Dog'", font_size=24, color=RED
            )
            error_text.move_to(UP * 2.2)

            self.play(FadeIn(error_banner), run_time=tracker.duration * 0.10)
            self.play(Write(error_text), run_time=tracker.duration * 0.08)

            question = Text(
                '"How much did each connection contribute?"', font_size=22, color=YELLOW
            )
            question.next_to(error_banner, DOWN, buff=0.3)
            safe_position(question)
            self.play(FadeIn(question), run_time=tracker.duration * 0.06)

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

            connections_l2 = VGroup()
            for n1 in input_layer:
                for n2 in hidden_layer:
                    line = Line(n1.get_right(), n2.get_left(), color=GRAY)
                    line.set_stroke(opacity=0.4)
                    connections_l2.add(line)

            connections_l3 = VGroup()
            for n2 in hidden_layer:
                for n3 in output_layer:
                    line = Line(n2.get_right(), n3.get_left(), color=GRAY)
                    line.set_stroke(opacity=0.4)
                    connections_l3.add(line)

            network.add(
                input_layer, hidden_layer, output_layer, connections_l2, connections_l3
            )
            safe_layout(input_layer, hidden_layer, output_layer)

            self.play(FadeIn(network), run_time=tracker.duration * 0.07)

            backward_arrows = VGroup()
            for n3 in output_layer:
                for n2 in hidden_layer:
                    arrow = Arrow(n3.get_left(), n2.get_right(), color=RED, buff=0.1)
                    backward_arrows.add(arrow)

            self.play(FadeIn(backward_arrows), run_time=tracker.duration * 0.14)

            self.play(
                backward_arrows.animate.set_opacity(0.3),
                run_time=tracker.duration * 0.06,
            )

            backward_arrows2 = VGroup()
            for n2 in hidden_layer:
                for n1 in input_layer:
                    arrow = Arrow(n2.get_left(), n1.get_right(), color=RED, buff=0.1)
                    backward_arrows2.add(arrow)

            self.play(FadeIn(backward_arrows2), run_time=tracker.duration * 0.14)

            wrong_connections = VGroup()
            for line in connections_l3:
                wrong_connections.add(line)
            self.play(
                wrong_connections.animate.set_color(RED).set_opacity(0.6),
                run_time=tracker.duration * 0.07,
            )

            reduce_label = Text("Reduce weight", font_size=18, color=RED)
            reduce_label.next_to(connections_l3, DOWN, buff=0.3)
            safe_position(reduce_label)
            self.play(FadeIn(reduce_label), run_time=tracker.duration * 0.06)

            strengthen_connections = VGroup()
            for line in connections_l2:
                strengthen_connections.add(line)
            self.play(
                strengthen_connections.animate.set_color(GREEN).set_opacity(0.6),
                run_time=tracker.duration * 0.06,
            )

            strengthen_label = Text("Strengthen", font_size=18, color=GREEN)
            strengthen_label.next_to(connections_l2, LEFT, buff=0.3)
            safe_position(strengthen_label)
            self.play(FadeIn(strengthen_label), run_time=tracker.duration * 0.05)

            thousands = Text("Repeat thousands of times...", font_size=26, color=BLUE)
            thousands.move_to(DOWN * 3.5)
            self.play(FadeIn(thousands), run_time=tracker.duration * 0.04)
