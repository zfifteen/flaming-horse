# Advanced Pattern: Graph Build + Highlight + Replacement

Inspiration: Manim CE `GraphAreaPlot` and `SinAndCosFunctionPlot`.

```python
beats = BeatPlan(tracker.duration, [2, 2, 2, 2, 2, 2, 2, 2])

title = Text("Factor Pair Search on Axes", font_size=46, weight=BOLD)
title.move_to(UP * 3.8)
subtitle = Text("Visualize valid pairs (a, b)", font_size=30)
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)

axes = Axes(x_range=[0, 8, 1], y_range=[0, 8, 1], x_length=6.5, y_length=4.0, tips=False)
axes.move_to(DOWN * 0.8)
labels = axes.get_axis_labels(x_label=MathTex("a"), y_label=MathTex("b"))

pair_curve = axes.plot(lambda x: 6 / x, x_range=[1, 6], color=BLUE)
dot_1 = Dot(axes.c2p(2, 3), color=YELLOW)
dot_2 = Dot(axes.c2p(3, 2), color=YELLOW)

panel = VGroup(axes, labels, pair_curve, dot_1, dot_2)
safe_layout(subtitle, panel)

play_text_next(self, beats, Write(title))
play_text_next(self, beats, FadeIn(subtitle))
play_next(self, beats, Create(axes, rate_func=smooth))
play_next(self, beats, FadeIn(labels))
play_next(self, beats, Create(pair_curve, rate_func=smooth))
play_next(self, beats, LaggedStart(FadeIn(dot_1), FadeIn(dot_2), lag_ratio=0.2))
play_next(self, beats, Circumscribe(VGroup(dot_1, dot_2), color=YELLOW, time_width=0.7))

result_old = MathTex(r"a+b=5", font_size=38).move_to(RIGHT * 4.2 + DOWN * 0.5)
result_new = MathTex(r"(x+2)(x+3)", font_size=38).move_to(result_old.get_center())
play_text_next(self, beats, FadeIn(result_old))
play_next(self, beats, FadeTransform(result_old, result_new))
```

Why this is advanced:

- Uses axes, function plot, markers, and symbolic replacement in one scene.
- Keeps concept flow active instead of one-shot reveal.
