# Advanced Pattern: Algebra Tiles Rearrangement Sequence

Use this for middle scenes that must demonstrate a geometric reconfiguration into factors.

```python
beats = BeatPlan(tracker.duration, [2, 2, 2, 2, 2, 2, 2, 2, 2, 2])

title = Text("Rearrange Tiles Into Factors", font_size=46, weight=BOLD)
title.move_to(UP * 3.8)
subtitle = Text("From x^2 + 5x + 6 to side lengths", font_size=30)
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)

x2 = Square(side_length=1.9, color=BLUE, fill_opacity=0.35).move_to(LEFT * 2.2 + DOWN * 0.8)
x2_label = MathTex(r"x^2", font_size=32).move_to(x2.get_center())

x_rect_1 = Rectangle(width=1.9, height=0.7, color=GREEN, fill_opacity=0.35).next_to(x2, DOWN, buff=0)
x_rect_2 = Rectangle(width=0.7, height=1.9, color=GREEN, fill_opacity=0.35).next_to(x2, RIGHT, buff=0)
x_rect_3 = Rectangle(width=1.9, height=0.35, color=YELLOW, fill_opacity=0.35).next_to(x_rect_1, DOWN, buff=0)
x_rect_4 = Rectangle(width=0.35, height=1.9, color=YELLOW, fill_opacity=0.35).next_to(x_rect_2, RIGHT, buff=0)
const_6 = Rectangle(width=1.05, height=0.7, color=RED, fill_opacity=0.35).next_to(x_rect_3, RIGHT, buff=0)

raw_tiles = VGroup(x2, x_rect_1, x_rect_2, x_rect_3, x_rect_4, const_6, x2_label)

target_group = raw_tiles.copy().arrange_in_grid(rows=2, cols=3, buff=(0.05, 0.05))
target_group.move_to(RIGHT * 2.2 + DOWN * 0.9)

left_form = MathTex(r"x^2 + 5x + 6", font_size=38).move_to(LEFT * 4.7 + DOWN * 2.0)
right_form = MathTex(r"(x+2)(x+3)", font_size=38).move_to(RIGHT * 4.7 + DOWN * 2.0)

play_text_next(self, beats, Write(title))
play_text_next(self, beats, FadeIn(subtitle))
play_next(self, beats, LaggedStart(*[Create(m) for m in raw_tiles[:-1]], lag_ratio=0.12))
play_text_next(self, beats, FadeIn(x2_label))
play_text_next(self, beats, FadeIn(left_form))
play_next(self, beats, Indicate(VGroup(x_rect_1, x_rect_2), scale_factor=1.05))
play_next(self, beats, Indicate(VGroup(x_rect_3, x_rect_4), scale_factor=1.05))
play_next(self, beats, Transform(raw_tiles, target_group))
play_text_next(self, beats, FadeTransform(left_form, right_form))
play_next(self, beats, Circumscribe(right_form, color=BLUE, time_width=0.8))
```

Why this is advanced:

- Long multi-beat progression with clear symbolic payoff.
- Uses transform + emphasis + symbolic swap.
- Matches geometric factorization storytelling for middle scenes.
