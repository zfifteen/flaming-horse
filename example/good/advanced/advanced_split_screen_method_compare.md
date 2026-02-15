# Advanced Pattern: Split-Screen Method Comparison

Use this when comparing two valid factorization strategies in one scene.

```python
beats = BeatPlan(tracker.duration, [2, 2, 2, 2, 2, 2, 2, 2, 2])

title = Text("Two Paths to the Same Factors", font_size=46, weight=BOLD)
title.move_to(UP * 3.8)
subtitle = Text("Area tiles vs coefficient pairing", font_size=30)
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)

divider = Line(UP * 2.8 + ORIGIN, DOWN * 3.4 + ORIGIN).set_color(GRAY_B)

left_panel = RoundedRectangle(width=6.3, height=4.6, corner_radius=0.2, color=BLUE, fill_opacity=0.12)
left_panel.move_to(LEFT * 3.7 + DOWN * 0.7)
left_header = Text("Geometric Tiles", font_size=28).next_to(left_panel, UP, buff=0.2)

right_panel = RoundedRectangle(width=6.3, height=4.6, corner_radius=0.2, color=GREEN, fill_opacity=0.12)
right_panel.move_to(RIGHT * 3.7 + DOWN * 0.7)
right_header = Text("Coefficient Pairing", font_size=28).next_to(right_panel, UP, buff=0.2)

tile_block = Rectangle(width=2.2, height=1.4, color=BLUE, fill_opacity=0.3).move_to(left_panel.get_center() + LEFT * 1.0)
tile_note = MathTex(r"x^2,\ 5x,\ 6", font_size=34).next_to(tile_block, RIGHT, buff=0.3)

sum_product = VGroup(
    MathTex(r"a+b=5", font_size=34),
    MathTex(r"ab=6", font_size=34),
).arrange(DOWN, buff=0.3).move_to(right_panel.get_center() + LEFT * 0.7)
pair_result = MathTex(r"(a,b)=(2,3)", font_size=34).next_to(sum_product, DOWN, buff=0.45)

final_left = MathTex(r"(x+2)(x+3)", font_size=40).move_to(left_panel.get_center() + DOWN * 1.55)
final_right = MathTex(r"(x+2)(x+3)", font_size=40).move_to(right_panel.get_center() + DOWN * 1.55)

play_text_next(self, beats, Write(title))
play_text_next(self, beats, FadeIn(subtitle))
play_next(self, beats, Create(divider))
play_next(self, beats, LaggedStart(FadeIn(left_panel), FadeIn(right_panel), lag_ratio=0.2))
play_text_next(self, beats, LaggedStart(FadeIn(left_header), FadeIn(right_header), lag_ratio=0.2))
play_next(self, beats, FadeIn(tile_block), FadeIn(tile_note))
play_next(self, beats, FadeIn(sum_product))
play_text_next(self, beats, FadeIn(pair_result))
play_next(self, beats, LaggedStart(FadeIn(final_left), FadeIn(final_right), lag_ratio=0.2))
```

Why this is advanced:

- Manages two synchronized visual narratives.
- Demonstrates complex mid-scene composition while remaining readable.
