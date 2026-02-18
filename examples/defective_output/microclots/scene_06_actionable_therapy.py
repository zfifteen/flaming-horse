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


class Scene06ActionableTherapy(VoiceoverScene):
    def construct(self):
        ref_path = Path("assets/voice_ref/ref.wav")
        if not ref_path.exists():
            raise FileNotFoundError("Run precache_voice.sh before building.")

        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["scene_06_actionable_therapy"]) as tracker:
            # SLOT_START:scene_body
            num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
            beats = BeatPlan(tracker.duration, [1] * num_beats)

            # Harmonious colors - using built-in colors to avoid numpy issues
            blues = [BLUE, BLUE_B, BLUE_C, BLUE_D]

            # Title
            title = Text("Actionable Therapy: Sequential Protocol", font_size=48, weight=BOLD, color=blues[0])
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))

            # Subtitle
            subtitle = Text("DNase First, Then Fibrinolytics", font_size=32, color=blues[1])
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            play_text_next(self, beats, polished_fade_in(subtitle, lag_ratio=0.1))

            # Bullets (left side, progressive reveal)
            bullet_1 = Text("• Degrade NETs with DNase first", font_size=28, color=blues[2]).move_to(LEFT * 4.5 + UP * 1.5)
            bullet_2 = Text("• Monitor markers below threshold", font_size=28, color=blues[2]).next_to(bullet_1, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_2)
            bullet_3 = Text("• Prevents rebound NETosis", font_size=28, color=blues[2]).next_to(bullet_2, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_3)
            bullet_4 = Text("• Falsifiable: Better with DNase pre-treatment", font_size=28, color=blues[2]).next_to(bullet_3, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet_4)

            play_text_next(self, beats, FadeIn(bullet_1))
            play_text_next(self, beats, FadeIn(bullet_2))
            play_text_next(self, beats, FadeIn(bullet_3))
            play_text_next(self, beats, FadeIn(bullet_4))

            # Cleanup bullets and subtitle
            play_next(self, beats, FadeOut(subtitle), FadeOut(bullet_1), FadeOut(bullet_2), FadeOut(bullet_3), FadeOut(bullet_4))

            # Right-side flowchart
            flowchart_group = VGroup()

            # Step 1: DNase
            step1_box = Rectangle(width=3, height=1, color=blues[1])
            step1_box.move_to(RIGHT * 3.5 + UP * 1.5)
            step1_text = Text("Step 1: DNase", font_size=24, color=WHITE).move_to(step1_box.get_center())
            step1_icon = Circle(radius=0.2, color=YELLOW).next_to(step1_box, LEFT, buff=0.3)
            step1_icon_label = Text("Syringe", font_size=16, color=YELLOW).next_to(step1_icon, DOWN, buff=0.1)
            safe_position(step1_icon_label)
            flowchart_group.add(step1_box, step1_text, step1_icon, step1_icon_label)

            # Arrow to check
            arrow1 = Arrow(step1_box.get_bottom(), step1_box.get_bottom() + DOWN * 0.8, color=blues[2])
            check_box = Rectangle(width=3, height=0.8, color=GREEN)
            check_box.next_to(arrow1, DOWN, buff=0.1)
            check_text = Text("Check Markers < Threshold", font_size=20, color=WHITE).move_to(check_box.get_center())
            flowchart_group.add(arrow1, check_box, check_text)

            # Arrow to Step 2: Fibrinolytics
            arrow2 = Arrow(check_box.get_bottom(), check_box.get_bottom() + DOWN * 0.8, color=blues[2])
            step2_box = Rectangle(width=3, height=1, color=blues[1])
            step2_box.next_to(arrow2, DOWN, buff=0.1)
            step2_text = Text("Step 2: Fibrinolytics", font_size=24, color=WHITE).move_to(step2_box.get_center())
            step2_icon = Circle(radius=0.2, color=YELLOW).next_to(step2_box, LEFT, buff=0.3)
            step2_icon_label = Text("tPA", font_size=16, color=YELLOW).next_to(step2_icon, DOWN, buff=0.1)
            safe_position(step2_icon_label)
            flowchart_group.add(arrow2, step2_box, step2_text, step2_icon, step2_icon_label)

            # Position flowchart below title area
            flowchart_group.move_to(DOWN * 0.6)
            safe_position(flowchart_group)

            # Animate flowchart build
            play_next(self, beats, FadeIn(step1_box), FadeIn(step1_text), FadeIn(step1_icon), FadeIn(step1_icon_label))
            play_next(self, beats, GrowArrow(arrow1), FadeIn(check_box), FadeIn(check_text))
            play_next(self, beats, GrowArrow(arrow2), FadeIn(step2_box), FadeIn(step2_text), FadeIn(step2_icon), FadeIn(step2_icon_label))

            # Final cleanup
            play_next(self, beats, FadeOut(title), FadeOut(flowchart_group))
            # SLOT_END:scene_body
