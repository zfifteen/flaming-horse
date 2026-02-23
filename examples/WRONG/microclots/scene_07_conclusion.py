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


class Scene07Conclusion(VoiceoverScene):
    def construct(self):
        ref_path = Path("assets/voice_ref/ref.wav")
        if not ref_path.exists():
            raise FileNotFoundError("Run precache_voice.sh before building.")

        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["scene_07_conclusion"]) as tracker:
            # SLOT_START:scene_body
            pass  # TEMP scaffold stub: Agent replaces entire block from here to SLOT_END
            # PROMPT: Output ONLY the indented Python code (12 spaces) to replace from SLOT_START to SLOT_END. NO ```python fences, NO full class/imports/config. Start with num_beats = ...
            # PROMPT: Use structurally different patterns (e.g., progressive bullets + evolving diagram or timeline/staged reveal).
            # PROMPT: Position bullets at LEFT * 3.5 with set_max_width(6.0); derive content from narration_script.py, not plan.json.
            # PROMPT: Ensure layout contracts: title at UP * 3.8, subtitle next_to(title, DOWN, buff=0.4), visuals below subtitle.
            # PROMPT: Use BeatPlan with num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8)))).
            # PROMPT: Set max_text_seconds=999 in play_text_next to avoid micro-pauses.
            # SLOT_END:scene_body
