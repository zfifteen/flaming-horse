# Advanced Pattern: Updater-Driven Motion With Explainers

Inspiration: Manim CE `MovingAngle`.

```python
beats = BeatPlan(tracker.duration, [2, 2, 2, 2, 2, 2, 2, 2])

title = Text("Dynamic Side-Length Relationship", font_size=44, weight=BOLD)
title.move_to(UP * 3.8)
subtitle = Text("Track how dimensions preserve area", font_size=30)
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)

base = Rectangle(width=3.2, height=1.8, color=BLUE, fill_opacity=0.35).move_to(DOWN * 0.8)
width_tracker = ValueTracker(3.2)

dynamic_rect = always_redraw(
    lambda: Rectangle(
        width=width_tracker.get_value(),
        height=5.76 / width_tracker.get_value(),
        color=GREEN,
        fill_opacity=0.35,
    ).move_to(base.get_center())
)

area_tex = always_redraw(
    lambda: MathTex(
        rf"A={width_tracker.get_value():.1f}\times{(5.76/width_tracker.get_value()):.1f}=5.76",
        font_size=34,
    ).move_to(RIGHT * 4.1 + DOWN * 0.5)
)

play_text_next(self, beats, Write(title))
play_text_next(self, beats, FadeIn(subtitle))
play_next(self, beats, Create(base))
play_next(self, beats, FadeIn(dynamic_rect))
play_text_next(self, beats, FadeIn(area_tex))
play_next(self, beats, width_tracker.animate.set_value(2.4), rate_func=smooth)
play_next(self, beats, width_tracker.animate.set_value(1.8), rate_func=smooth)
play_next(self, beats, Circumscribe(area_tex, color=YELLOW, time_width=0.7))
```

Why this is advanced:

- Maintains motion continuity with updaters.
- Ties dynamic geometry directly to symbolic narration.
