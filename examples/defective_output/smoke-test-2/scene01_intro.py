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


class Scene01Intro(VoiceoverScene):
    def construct(self):
        ref_path = Path("assets/voice_ref/ref.wav")
        if not ref_path.exists():
            raise FileNotFoundError("Run precache_voice.sh before building.")

        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["scene_01_intro"]) as tracker:
            # SLOT_START:scene_body
            pass  # Placeholder - will be replaced by generated code
            # PROMPT: Design unique visual flow per scene, incorporating ≥1 unique visual from topic_visual_patterns.md.
            # PROMPT: Use structurally different patterns (e.g., progressive bullets + evolving diagram or timeline/staged reveal).
            # PROMPT: Position bullets at LEFT * 3.5 with set_max_width(6.0); derive content from narration_script.py, not plan.json.
            # PROMPT: Ensure layout contracts: title at UP * 3.8, subtitle next_to(title, DOWN, buff=0.4), visuals below subtitle.
            # PROMPT: Use BeatPlan with num_beats = max(10, min(22, int(np.ceil(tracker.duration / 3.0)))).
            # PROMPT: Set max_text_seconds=999 in play_text_next to avoid micro-pauses.
            # SLOT_END:scene_body