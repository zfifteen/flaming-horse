# Good Pattern: Cleanup Before New Headline

Source inspiration: Manim CE `OpeningManim` (`Transform` + `LaggedStart(FadeOut...)`).

```python
bullets = BulletedList(
    "Model the expression as area.",
    "Match side lengths to factors.",
    font_size=30,
)
bullets.move_to(RIGHT * 2 + DOWN * 0.2)

play_text_next(self, beats, FadeIn(bullets))

# Clear previous dense content before introducing a centered title card.
play_next(
    self,
    beats,
    FadeOut(VGroup(bullets, diagram, labels_group)),
)

title_card = Text("Systematic Factoring", font_size=52, weight=BOLD)
title_card.move_to(ORIGIN)
play_text_next(self, beats, FadeIn(title_card))
```

Why this is good:

- No overlap between old dense content and new center headline.
- Layer count stays controlled during transitions.
