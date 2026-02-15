# Advanced Pattern: Table-to-Geometry Transition

Use this when narration starts from numeric pair search, then shifts into area geometry.

```python
beats = BeatPlan(tracker.duration, [2, 2, 2, 2, 2, 2, 2, 2, 2])

title = Text("From Pair Table to Area Model", font_size=46, weight=BOLD)
title.move_to(UP * 3.8)
subtitle = Text("Connect numeric reasoning to geometric layout", font_size=30)
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)

table = MathTable(
    [["1", "6", "7"], ["2", "3", "5"]],
    row_labels=[MathTex("a"), MathTex("b")],
    col_labels=[MathTex("p_1"), MathTex("p_2"), MathTex("a+b")],
    include_outer_lines=True,
)
table.scale(0.58).move_to(LEFT * 3.6 + DOWN * 0.7)

table_box = SurroundingRectangle(table.get_entries((3, 3)), color=YELLOW, buff=0.08)

area_model = Rectangle(width=3.6, height=2.4, color=BLUE, fill_opacity=0.22).move_to(RIGHT * 3.2 + DOWN * 0.8)
area_v = Line(area_model.get_top() + LEFT * 1.1, area_model.get_bottom() + LEFT * 1.1, color=GREEN)
area_h = Line(area_model.get_left() + DOWN * 0.8, area_model.get_right() + DOWN * 0.8, color=GREEN)
side_labels = VGroup(
    MathTex("x+2", font_size=32).next_to(area_model, LEFT, buff=0.25),
    MathTex("x+3", font_size=32).next_to(area_model, UP, buff=0.2),
)

result = MathTex(r"x^2+5x+6=(x+2)(x+3)", font_size=38).move_to(DOWN * 2.7)

play_text_next(self, beats, Write(title))
play_text_next(self, beats, FadeIn(subtitle))
play_next(self, beats, FadeIn(table))
play_next(self, beats, Create(table_box))
play_next(self, beats, FadeIn(area_model))
play_next(self, beats, LaggedStart(Create(area_v), Create(area_h), lag_ratio=0.2))
play_text_next(self, beats, FadeIn(side_labels))
play_next(self, beats, FadeOut(VGroup(table, table_box)))
play_text_next(self, beats, Write(result, run_time=1.2))
```

Why this is advanced:

- Bridges two representational modes in one coherent sequence.
- Uses explicit transition/cleanup between dense sections.
