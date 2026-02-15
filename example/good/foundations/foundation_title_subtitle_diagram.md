# Foundation Pattern: Title + Subtitle + Single Diagram

Use this for intro and recap scenes where clarity matters more than complexity.

```python
beats = BeatPlan(tracker.duration, [2, 2, 2, 2])

title = Text("Geometric Factorization", font_size=48, weight=BOLD)
title.move_to(UP * 3.8)

subtitle = Text("A visual way to factor", font_size=32)
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)

diagram = Rectangle(width=4.6, height=2.8, color=BLUE, fill_opacity=0.25)
diagram.move_to(DOWN * 0.8)

play_text_next(self, beats, Write(title))
play_text_next(self, beats, FadeIn(subtitle))
play_next(self, beats, Create(diagram, rate_func=smooth))
```
