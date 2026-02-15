# Advanced Pattern: Focus Shift and Context Swap

Inspiration: Manim CE `MovingFrameBox` and `OpeningManim`.

```python
beats = BeatPlan(tracker.duration, [2, 2, 2, 2, 2, 2, 2, 2])

title = Text("From Expansion to Factors", font_size=46, weight=BOLD)
title.move_to(UP * 3.8)
subtitle = Text("Track terms, then regroup", font_size=30)
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)

expansion = MathTex(r"x^2 + 5x + 6 = x^2 + 2x + 3x + 6", font_size=38)
expansion.move_to(DOWN * 0.5)

group_a = SurroundingRectangle(expansion[1:3], color=BLUE, buff=0.1)
group_b = SurroundingRectangle(expansion[3:5], color=GREEN, buff=0.1)

factored = MathTex(r"x(x+2) + 3(x+2)", font_size=38).move_to(expansion.get_center())
final_form = MathTex(r"(x+2)(x+3)", font_size=42).move_to(expansion.get_center())

play_text_next(self, beats, Write(title))
play_text_next(self, beats, FadeIn(subtitle))
play_text_next(self, beats, Write(expansion))
play_next(self, beats, Create(group_a))
play_next(self, beats, ReplacementTransform(group_a, group_b))
play_next(self, beats, FadeTransform(expansion, factored))
play_next(self, beats, FadeTransform(factored, final_form))
play_next(self, beats, Indicate(final_form, scale_factor=1.06))
```

Why this is advanced:

- Multiple guided focus shifts.
- Explicit symbolic progression with transform continuity.
