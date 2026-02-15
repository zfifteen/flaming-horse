# Foundation Pattern: Recap With Clean Exit

Use this for concluding scenes.

```python
beats = BeatPlan(tracker.duration, [2, 2, 2, 2, 2])

title = Text("Key Takeaways", font_size=48, weight=BOLD).move_to(UP * 3.8)
subtitle = Text("What to remember", font_size=32)
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)

panel = RoundedRectangle(corner_radius=0.2, width=6.2, height=3.0, color=GREEN, fill_opacity=0.2)
panel.move_to(DOWN * 0.6)
bullet_a = Text("Area gives factor intuition.", font_size=30).move_to(panel.get_center() + UP * 0.5)
bullet_b = Text("Grouping reveals binomial factors.", font_size=30).move_to(panel.get_center() + DOWN * 0.2)

play_text_next(self, beats, Write(title))
play_text_next(self, beats, FadeIn(subtitle))
play_next(self, beats, FadeIn(panel))
play_text_next(self, beats, LaggedStart(FadeIn(bullet_a), FadeIn(bullet_b), lag_ratio=0.2))
play_next(self, beats, FadeOut(VGroup(panel, bullet_a, bullet_b)))
```
