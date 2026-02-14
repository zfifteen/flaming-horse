from manim import *
import colorsys

def harmonious_color(base_color, variations=3, lightness_shift=0.1):
    rgb = base_color.get_rgb()
    r, g, b = colorsys.rgb_to_hls(*rgb)
    palette = []
    for i in range(variations):
        h_shift = i * (360 / variations) / 360
        new_h = (r + h_shift) % 1
        new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, g, b + lightness_shift * i)
        palette.append([new_r, new_g, new_b, 1.0])
    return palette

print(harmonious_color(BLUE))
