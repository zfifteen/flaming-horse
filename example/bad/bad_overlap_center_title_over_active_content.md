# Bad Pattern: Center Title Over Active Bullets/Diagram

Observed in generated scene: `copilot-test-video-2/scene_04_recap.py`.

```python
bullets = BulletedList(...)
bullets.next_to(rectangle, RIGHT, buff=1.0)
safe_layout(bullets)  # no-op for overlap prevention in this case
play_text_next(self, beats, FadeIn(bullets))

title_card = Text("Geometric Factorization Explained Visually", font_size=48, weight=BOLD)
title_card.move_to(ORIGIN)
play_text_next(self, beats, FadeIn(title_card))
```

Why this is bad:

- Adds a large center headline while bullets and diagram are still visible.
- Creates direct visual collision and unreadable content.

Never do this. Clear or transform prior content first.
