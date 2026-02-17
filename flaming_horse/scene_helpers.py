from manim import *
import numpy as np
import colorsys  # New: For harmonious_color


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
        palette.append([new_r, new_g, new_b, 1.0])
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


class BeatPlan:
    def __init__(self, total_duration, weights=None):
        self.total_duration = max(0.0, float(total_duration))
        if weights is None:
            # Default: uniform weights for num_beats
            num_beats = max(12, min(30, int(np.ceil(self.total_duration / 1.8))))
            weights = [1] * num_beats
        cleaned = [max(0.0, float(w)) for w in weights]
        if not cleaned:
            raise ValueError("BeatPlan requires at least one weight")
        weight_sum = sum(cleaned)
        if weight_sum <= 0:
            cleaned = [1.0 for _ in cleaned]
            weight_sum = float(len(cleaned))

        slots = []
        consumed = 0.0
        for idx, weight in enumerate(cleaned):
            if idx == len(cleaned) - 1:
                slot = max(0.0, self.total_duration - consumed)
            else:
                slot = self.total_duration * (weight / weight_sum)
                consumed += slot
            slots.append(slot)
        self._slots = slots
        self._cursor = 0

    def next_slot(self):
        if self._cursor >= len(self._slots):
            return 0.0
        slot = self._slots[self._cursor]
        self._cursor += 1
        return slot


def play_in_slot(
    scene, slot, *animations, max_run_time=None, min_run_time=0.3, **play_kwargs
):
    if not animations:
        return

    if "run_time" in play_kwargs:
        raise ValueError(
            "Do not pass run_time to play_next/play_text_next; slot helpers own timing."
        )

    slot = max(0.0, float(slot))
    if slot <= 0:
        return

    animation = (
        animations[0]
        if len(animations) == 1
        else LaggedStart(*animations, lag_ratio=0.15)
    )

    run_time = slot
    if max_run_time is not None:
        run_time = min(run_time, float(max_run_time))
    run_time = max(float(min_run_time), run_time)
    run_time = min(run_time, slot)

    scene.play(animation, run_time=run_time, **play_kwargs)
    remaining = slot - run_time
    if remaining > 1e-6:
        scene.wait(remaining)


def play_text_in_slot(
    scene, slot, *animations, max_text_seconds=1.5, min_run_time=0.3, **play_kwargs
):
    return play_in_slot(
        scene,
        slot,
        *animations,
        max_run_time=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )


def play_next(
    scene, beats, *animations, max_run_time=None, min_run_time=0.3, **play_kwargs
):
    return play_in_slot(
        scene,
        beats.next_slot(),
        *animations,
        max_run_time=max_run_time,
        min_run_time=min_run_time,
        **play_kwargs,
    )


def play_text_next(
    scene, beats, *animations, max_text_seconds=999, min_run_time=0.3, **play_kwargs
):
    return play_text_in_slot(
        scene,
        beats.next_slot(),
        *animations,
        max_text_seconds=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )
