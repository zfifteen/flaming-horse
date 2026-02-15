# Good Pattern: Title -> Subtitle -> Diagram

Source inspiration: Manim CE `MobjectPlacement` and `OpeningManim` examples.

```python
title = Text("Geometric Factorization", font_size=48, weight=BOLD)
title.move_to(UP * 3.8)

subtitle = Text("Area model overview", font_size=32)
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)

diagram = Rectangle(width=4.6, height=2.8, color=BLUE)
diagram.move_to(DOWN * 0.9)

safe_layout(subtitle, diagram)

play_text_next(self, beats, Write(title))
play_text_next(self, beats, FadeIn(subtitle))
play_next(self, beats, Create(diagram, rate_func=smooth))
```

Why this is good:

- Title stays in safe top zone.
- Subtitle is anchored to title, then safety-adjusted.
- Diagram is intentionally lowered to avoid text collisions.
