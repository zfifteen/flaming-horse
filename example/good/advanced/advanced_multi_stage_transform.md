# Advanced Pattern: Multi-Stage Transform Storyboard

Inspiration: Manim CE `OpeningManim`.

Use this pattern for a middle scene that must move through multiple ideas without static dead time.

```python
beats = BeatPlan(tracker.duration, [2, 2, 2, 2, 2, 2, 2, 2, 2])

title = Text("Factoring x^2 + 5x + 6", font_size=46, weight=BOLD)
title.move_to(UP * 3.8)
subtitle = Text("Build and regroup area tiles", font_size=30)
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)

tile_x2 = Square(1.8, color=BLUE, fill_opacity=0.35).move_to(LEFT * 2 + DOWN * 0.9)
tile_x2_label = MathTex(r"x^2", font_size=34).move_to(tile_x2.get_center())
tile_x2_group = VGroup(tile_x2, tile_x2_label)

tile_x3 = Rectangle(width=1.8, height=0.8, color=GREEN, fill_opacity=0.35).next_to(tile_x2, DOWN, buff=0)
tile_x2r = Rectangle(width=0.8, height=1.8, color=YELLOW, fill_opacity=0.35).next_to(tile_x2, RIGHT, buff=0)
tile_6 = Square(0.8, color=RED, fill_opacity=0.35).next_to(tile_x2r, DOWN, buff=0)
tiles = VGroup(tile_x2, tile_x3, tile_x2r, tile_6)

play_text_next(self, beats, Write(title))
play_text_next(self, beats, FadeIn(subtitle))
play_next(self, beats, Create(tile_x2_group, rate_func=smooth))
play_next(self, beats, LaggedStart(Create(tile_x3), Create(tile_x2r), Create(tile_6), lag_ratio=0.15))

equation_a = MathTex(r"x^2 + 5x + 6", font_size=40).move_to(RIGHT * 3 + DOWN * 0.6)
equation_b = MathTex(r"(x+2)(x+3)", font_size=40).move_to(RIGHT * 3 + DOWN * 0.6)
safe_layout(tiles, equation_a)

play_text_next(self, beats, FadeIn(equation_a))
play_next(self, beats, Indicate(tile_x3, scale_factor=1.05))
play_next(self, beats, Indicate(tile_x2r, scale_factor=1.05))
play_next(self, beats, FadeTransform(equation_a, equation_b))
play_next(self, beats, Circumscribe(equation_b, color=BLUE, time_width=0.8))
```

Why this is advanced:

- Continuous visual progression across 9 beats.
- Includes both transform and emphasis families.
- Keeps middle scene active and explanatory.
