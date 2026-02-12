from manim import *
import numpy as np

# ── Python 3.13 Compatibility Patch ────────────────────────────────
import manim_voiceover_plus.services.base as base
original_set_transcription = base.SpeechService.set_transcription

def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self.whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs)

base.SpeechService.set_transcription = patched_set_transcription

# ── Voiceover Imports ──────────────────────────────────────────────
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

# ── Import Shared Configuration ────────────────────────────────────
from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS
from narration_script import SCRIPT

# ── LOCKED CONFIGURATION (DO NOT MODIFY) ───────────────────────────
config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

# ── Safe Positioning Helper ────────────────────────────────────────
def safe_position(mobject, max_y=4.0, min_y=-4.0):
    """Ensure mobject stays within safe bounds after positioning"""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject

# ── Scene Class ────────────────────────────────────────────────────
class Scene08Conclusion(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )
        
        # This scene is primarily silent with text
        # Brief pause at beginning, then animations
        
        with self.voiceover(text=SCRIPT["conclusion"]) as tracker:
            # Silent pause for 2-3 seconds
            self.wait(2.5)
            
            # Title card reappears
            title = Text("Chandler Wobble's Hidden Message",
                        font_size=48, weight=BOLD, color=WHITE)
            title.move_to(UP * 3.8)
            
            subtitle = Text("A Falsifiable Prediction",
                          font_size=36, color="#FFC857")
            subtitle.next_to(title, DOWN, buff=0.5)
            safe_position(subtitle)
            
            self.play(
                Write(title),
                FadeIn(subtitle),
                run_time=2.0
            )
            
            # Three bullet points
            bullet1 = Text("✓ Mechanism: Shared core-mantle coupling pathway",
                         font_size=32, color=WHITE)
            bullet1.move_to(UP * 1.0)
            
            bullet2 = Text("✓ Prediction: LOD phase offset by 2027",
                         font_size=32, color=WHITE)
            bullet2.move_to(ORIGIN)
            
            bullet3 = Text("✓ Disconfirmation: No phase offset → hypothesis falsified",
                         font_size=32, color=WHITE)
            bullet3.move_to(DOWN * 1.0)
            
            self.play(
                FadeIn(bullet1),
                run_time=1.5
            )
            
            self.play(
                FadeIn(bullet2),
                run_time=1.5
            )
            
            self.play(
                FadeIn(bullet3),
                run_time=1.5
            )
            
            self.wait(1.0)
            
            # Final message
            final_message = Text("Watch this space.\nThe core-mantle system is speaking.",
                               font_size=36, color="#00F5FF", weight=BOLD)
            final_message.move_to(DOWN * 2.8)
            safe_position(final_message)
            
            self.play(
                FadeIn(final_message),
                run_time=2.5
            )
            
            self.wait(2.0)
            
            # Fade to black
            self.play(
                *[FadeOut(mob) for mob in self.mobjects],
                run_time=2.5
            )
