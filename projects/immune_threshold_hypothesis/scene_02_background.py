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
config.frame_width = 10 * 16 / 9
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
class Scene02Background(VoiceoverScene):
    def construct(self):
        # ELEVENLABS ONLY - NO FALLBACK - FAIL LOUD
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: Calculate BEFORE writing animations
        # Total duration for background: ~60s, but fractions based on content

        with self.voiceover(text=SCRIPT["background"]) as tracker:
            # Immune cells animation (first part)
            title = Text("Immunological Background", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.2)

            # Animate immune cells
            cells = VGroup()
            for i in range(5):
                cell = Circle(radius=0.5, color=BLUE, fill_opacity=0.5).move_to(
                    np.array(
                        [np.cos(i * 2 * PI / 5) * 3, np.sin(i * 2 * PI / 5) * 3, 0]
                    )
                )
                cells.add(cell)
            cells_label = Text("Immune Cells", font_size=24).next_to(
                cells, DOWN, buff=0.5
            )
            safe_position(cells_label)

            self.play(
                Create(cells), Write(cells_label), run_time=tracker.duration * 0.3
            )

            # Cost-benefit graph
            axes = Axes(
                x_range=[0, 10, 1],
                y_range=[0, 10, 1],
                axis_config={"color": WHITE},
                x_length=6,
                y_length=4,
            ).move_to(ORIGIN)
            cost_curve = axes.plot(lambda x: 2 + 0.5 * x, color=RED, x_range=[0, 10])
            benefit_curve = axes.plot(
                lambda x: 8 - 0.3 * x**2, color=GREEN, x_range=[0, 10]
            )

            graph_label = Text("Cost-Benefit Analysis", font_size=24).next_to(
                axes, DOWN, buff=0.5
            )
            safe_position(graph_label)

            self.play(
                Create(axes),
                Create(cost_curve),
                Create(benefit_curve),
                Write(graph_label),
                run_time=tracker.duration * 0.3,
            )

            # Illustrate trade-offs
            balance = Text(
                "Trade-offs: Tolerance vs. Defense", font_size=32, color=YELLOW
            )
            balance.move_to(DOWN * 3)

            self.play(FadeIn(balance), run_time=tracker.duration * 0.2)
