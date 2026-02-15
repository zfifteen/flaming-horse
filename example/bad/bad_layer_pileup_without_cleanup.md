# Bad Pattern: Layer Pileup (No FadeOut/FadeTransform)

```python
play_text_next(self, beats, FadeIn(subtitle))
play_next(self, beats, Create(diagram))
play_text_next(self, beats, FadeIn(bullets))
play_text_next(self, beats, FadeIn(another_big_text_block))
```

Why this is bad:

- Too many dense elements coexist.
- The viewer cannot track focus.
- Later text often overlaps the diagram and previous bullets.

Rule:

- Keep at most two non-persistent active layers.
- Remove or transform old content before introducing another dense block.
