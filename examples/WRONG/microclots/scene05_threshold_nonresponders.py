from pathlib import Path

from manim import *
import numpy as np
from manim_voiceover_plus import VoiceoverScene

from flaming_horse_voice import get_speech_service
from flaming_horse.scene_helpers import (
    safe_position,
    harmonious_color,
    polished_fade_in,
    adaptive_title_position,
    safe_layout,
    BeatPlan,
    play_next,
    play_text_next,
)
from narration_script import SCRIPT


# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560


class Scene05ThresholdNonresponders(VoiceoverScene):
    def construct(self):
        ref_path = Path("assets/voice_ref/ref.wav")
        if not ref_path.exists():
            raise FileNotFoundError("Run precache_voice.sh before building.")

        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["scene_05_threshold_nonresponders"]) as tracker:
            # SLOT_START:scene_body
            num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
            beats = BeatPlan(tracker.duration, [1] * num_beats)

            reds = harmonious_color(RED, variations=4)

            title = Text("The Critical Threshold and Non-Responders", font_size=48, color=reds[0])
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))

            subtitle = Text("NET Density Threshold and Treatment Non-Responders", font_size=32, color=reds[1])
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            play_text_next(self, beats, polished_fade_in(subtitle))

            bullet_1 = Text("NET >40% threshold", font_size=28, color=reds[2]).move_to(LEFT * 3.5 + UP * 1.6).set_max_width(6.0)
            bullet_2 = Text("Fibrinolysis self-defeating", font_size=28, color=reds[2]).next_to(bullet_1, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_2)
            bullet_3 = Text("20% non-responders", font_size=28, color=reds[2]).next_to(bullet_2, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_3)
            bullet_4 = Text("High MPO markers", font_size=28, color=reds[2]).next_to(bullet_3, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_4)

            axes = Axes(x_range=[0, 100, 10], y_range=[0, 1, 0.1], axis_config={"color": RED}, x_axis_config={"numbers_to_include": [0, 40, 100]}, y_axis_config={"numbers_to_include": [0, 0.5, 1]}).move_to(RIGHT * 3.2 + DOWN * 0.6)
            axes.scale(0.8)
            sigmoid = axes.plot(lambda x: 1 / (1 + np.exp(-(x - 40) / 5)), color=RED, stroke_width=4)
            threshold_line = axes.get_vertical_line(axes.c2p(40, 0), color=YELLOW, stroke_width=3, line_config={"dashed_ratio": 0.5})
            threshold_label = Text("40% Threshold", font_size=18, color=YELLOW).next_to(threshold_line.get_top(), RIGHT, buff=0.2)
            safe_position(threshold_label)

            bars = VGroup()
            responders_bar = Rectangle(width=1.5, height=2.5, color=GREEN).move_to(RIGHT * 2.5 + DOWN * 2.5)
            nonresponders_bar = Rectangle(width=1.5, height=0.5, color=RED).next_to(responders_bar, RIGHT, buff=0.5)
            safe_position(nonresponders_bar)
            bars.add(responders_bar, nonresponders_bar)
            responders_label = Text("Responders (80%)", font_size=20, color=GREEN).next_to(responders_bar, DOWN, buff=0.2)
            nonresponders_label = Text("Non-Responders (20%)", font_size=20, color=RED).next_to(nonresponders_bar, DOWN, buff=0.2)
            safe_position(responders_label)
            safe_position(nonresponders_label)
            bars.add(responders_label, nonresponders_label)
            bars.move_to(RIGHT * 3.2 + DOWN * 2.8)

            play_text_next(self, beats, FadeIn(bullet_1))
            play_text_next(self, beats, FadeIn(bullet_2))
            play_text_next(self, beats, FadeIn(bullet_3))
            play_text_next(self, beats, FadeIn(bullet_4))

            play_next(self, beats, FadeOut(subtitle), FadeOut(bullet_1), FadeOut(bullet_2), FadeOut(bullet_3), FadeOut(bullet_4))
            play_next(self, beats, Create(axes))
            play_next(self, beats, Create(sigmoid))
            play_next(self, beats, Create(threshold_line), FadeIn(threshold_label))
            play_next(self, beats, FadeIn(bars))
            play_next(self, beats, FadeOut(axes), FadeOut(sigmoid), FadeOut(threshold_line), FadeOut(threshold_label), FadeOut(bars))
            # SLOT_END:scene_body