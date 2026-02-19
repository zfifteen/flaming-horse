# Visual Helpers

## Enhanced Visual Helpers

Always include these functions in scene files for polished aesthetics:

```python
import colorsys

def harmonious_color(base_color, variations=3, lightness_shift=0.1):
    """Generate a palette from base for visual cohesion (e.g., blues: #007BFF -> variants)."""
    rgb = np.array(base_color.to_rgb())
    h, l, s = colorsys.rgb_to_hls(*rgb)
    palette = []
    for i in range(variations):
        h_shift = i * (360 / variations) / 360  # Hue wheel shift
        new_h = (h + h_shift) % 1
        new_l = min(1.0, max(0.0, l + lightness_shift * i))
        new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, new_l, s)
        palette.append([new_r, new_g, new_b, 1.0])  # RGBA
    return palette

def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.1, glow=False):
    """Smooth reveal with initial scale pop and optional glow."""
    if glow:
        mobject.set_stroke(width=3, opacity=0.5)  # Subtle outline
    return LaggedStart(
        FadeIn(mobject),
        mobject.animate.scale(scale_factor).set_run_time(0.5).scale(1/scale_factor),  # Quick scale effect
        lag_ratio=lag_ratio,
    )

def adaptive_title_position(title, content_group, max_shift=0.5):
    """Shift title based on content height to avoid crowding."""
    content_height = content_group.height if content_group else 0
    shift_y = min(max_shift, max(0, content_height - 2.0))
    title.move_to(UP * (3.8 + shift_y))
    return title

# Usage examples:
# blues = harmonious_color(BLUE)
# title.color = blues[0]
# self.play(polished_fade_in(subtitle))
# title = adaptive_title_position(title, VGroup(subtitle, diagram))
```

- 3D Guidelines: Prefer for spatial topics (e.g., geometry); limit to 1-2 moving objects. Use `self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)` in a `ThreeDScene` for subtle depth without complexity.
- Text Rules: Cap `Write()` at 1.5s; for staggered reveals use `LaggedStart(*[FadeIn(b) for b in bullets], lag_ratio=0.15)`.
- For transitions: Mandate 0.5-1s crossfades between elements using `FadeTransform` or `polished_fade_in()`.
- Timing Rule: Never pass `run_time=` to `play_next(...)` / `play_text_next(...)`; those helpers must own slot timing.
- Cleanup Rule: Before dense visuals begin, fade out prior bullets/subtitle to keep <=2 simultaneous content layers.
- Positioning Rule: If labels are created via loop/comprehension with `.next_to(...)`, call `safe_position(...)` for each label explicitly.
