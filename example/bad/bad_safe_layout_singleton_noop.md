# Bad Pattern: Calling safe_layout() with One Object

```python
bullets = BulletedList(...)
bullets.next_to(rectangle, RIGHT, buff=1.0)
safe_layout(bullets)
```

Why this is bad:

- `safe_layout` is intended for sibling collision management.
- With one object, it does not resolve interactions with other active objects.
- This gives false confidence while overlaps remain.

Do this instead:

```python
safe_layout(rectangle, bullets, labels_group)
```
