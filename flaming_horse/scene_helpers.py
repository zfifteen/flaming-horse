from manim import *
import numpy as np
import colorsys  # New: For harmonious_color


# Public API - these are meant to be imported by scene files
__all__ = [
    "safe_position",
    "harmonious_color",
    "polished_fade_in",
    "adaptive_title_position",
    "safe_layout",
]


def safe_position(mobject, max_y=3.8, min_y=-3.8, max_x=7.5, min_x=-7.5, buff=0.2):
    """Enhanced: Adjusts vertically and horizontally with buffer to prevent edge clipping."""
    # Vertical clamping
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * ((min_y + buff) - bottom))
    # Horizontal clamping
    left = mobject.get_left()[0]
    right = mobject.get_right()[0]
    if right > max_x - buff:
        mobject.shift(LEFT * (right - (max_x - buff)))
    if left < min_x + buff:
        mobject.shift(RIGHT * ((min_x + buff) - left))
    return mobject


def harmonious_color(base_color, variations=3, lightness_shift=0.1):
    # Handle string names like "primary" -> GREEN
    if isinstance(base_color, str):
        color_map = {
            "primary": GREEN,
            "secondary": BLUE,
            "accent": YELLOW,
            "neutral": GRAY,
        }
        base_color = color_map.get(base_color, GREEN)
    rgb = np.array(base_color.to_rgb())
    h, l, s = colorsys.rgb_to_hls(*rgb)
    palette = []
    for i in range(variations):
        h_shift = i * (360 / variations) / 360
        new_h = (h + h_shift) % 1
        new_l = min(1.0, max(0.0, l + lightness_shift * i))
        new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, new_l, s)
        # Convert numpy.float64 to Python float for ManimColor compatibility
        palette.append([float(new_r), float(new_g), float(new_b), 1.0])
    return palette


def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.1, glow=False):
    if glow:
        mobject.set_stroke(width=3, opacity=0.5)
    return LaggedStart(
        FadeIn(mobject),
        mobject.animate.scale(scale_factor).set_run_time(0.5).scale(1 / scale_factor),
        lag_ratio=lag_ratio,
    )


def adaptive_title_position(title, content_group, max_shift=0.5):
    content_height = content_group.height if content_group else 0
    shift_y = min(max_shift, max(0, content_height - 2.0))
    title.move_to(UP * (3.8 + shift_y))
    return title


def safe_layout(
    *mobjects,
    alignment=ORIGIN,
    h_buff=0.5,
    v_buff=0.3,
    max_y=3.5,
    min_y=-3.5,
    max_x=7.5,
    min_x=-7.5,
):
    """Enhanced: Positions siblings horizontally/vertically without overlaps, with alignment and clamping."""
    group = VGroup(*mobjects)
    group.arrange(RIGHT, buff=h_buff, aligned_edge=UP if v_buff else alignment)
    for mob in mobjects:
        safe_position(mob, max_y=max_y, min_y=min_y, max_x=max_x, min_x=min_x)
    for i, mob_a in enumerate(mobjects):
        for j, mob_b in enumerate(mobjects[i + 1 :], i + 1):
            if mob_a.get_right()[0] > mob_b.get_left()[0] - h_buff:
                overlap = mob_a.get_right()[0] - mob_b.get_left()[0] + h_buff
                mob_b.shift(RIGHT * overlap)
    return VGroup(*mobjects)
