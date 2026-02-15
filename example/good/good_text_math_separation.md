# Good Pattern: Prose Text + Separate MathTex

Source inspiration: Manim CE examples that keep equations as dedicated math mobjects.

```python
point_1 = Text("1. Represent the quadratic as area.", font_size=30)
point_2 = Text("2. Read side lengths as factor terms.", font_size=30)

bullets_group = VGroup(point_1, point_2).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
bullets_group.move_to(LEFT * 3 + DOWN * 0.3)

equation = MathTex(r"x^2 + (a+b)x + ab = (x+a)(x+b)", font_size=40)
equation.next_to(bullets_group, RIGHT, buff=0.8)
safe_position(equation)

safe_layout(bullets_group, equation)

play_text_next(self, beats, FadeIn(bullets_group))
play_text_next(self, beats, Write(equation, run_time=1.2))
```

Why this is good:

- Prose and formulas are rendered with the right object types.
- Formula placement is explicit and collision-aware.
