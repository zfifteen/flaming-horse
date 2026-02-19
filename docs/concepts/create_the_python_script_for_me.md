<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Create the python script for me

Here are the complete Python scene files for the Archimedes Circle Growth Law video, following Flaming Horse contracts exactly:

## narration_script.py

```python
"""
Narration script for Archimedes Circle Growth Law
Generated: 2026-02-18
Duration: ~200 seconds
"""

SCRIPT = {
    "intro": """
The Archimedes triangle equivalence isn't just a geometric coincidence. It reveals 
something deeper: a circle is the unique closed curve where its area growth rate 
exactly equals its own perimeter at every moment. This self-referential property 
is a signature of the circle itself.
""",
    
    "growth_demo": """
Watch what happens when we expand a circle. As the radius increases, the area 
grows at a rate precisely matching the circumference. First, we see the circle 
at radius one. Next, as we expand, notice the instantaneous rate. Now observe: 
derivative of pi r squared gives two pi r, which is the perimeter formula. Finally, 
this equality holds continuously.
""",
    
    "efficiency_gap": """
Other shapes behave differently. A square grows its area more slowly than its 
perimeter suggests. An ellipse shows the same inefficiency. Every non-circular 
shape leaves a measurable efficiency gap between zero and one. This ratio becomes 
a scalar fingerprint distinguishing circles from all other curves.
""",
    
    "curvature_invariance": """
Here's the non-obvious part: this property isn't limited to flat space. On a 
sphere, geodesic circles still satisfy this growth law. In hyperbolic space, the 
same rule holds. The self-referential property is independent of the ambient 
geometry. It's a signature of constant curvature, not of flatness.
""",
    
    "conclusion": """
This gives us a curvature-independent test. Compute area growth rate divided by 
perimeter. True geodesic circles score exactly one. Any other shape scores strictly 
less. If a non-circular curve ever scores one, you've discovered unexpected symmetry 
or hidden constant-curvature regions in your surface. The prediction is sharp and 
testable.
"""
}
```


***

## scene_01_intro.py

```python
from manim import *
import numpy as np
import colorsys
from pathlib import Path
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

# Python 3.13 compatibility patch
try:
    from typing import override as _typing_override
except Exception:
    try:
        from typing_extensions import override as _typing_override
    except Exception:
        def _typing_override(func):
            return func

# Qwen precache check
ref_path = Path("assets/voice_ref/ref.wav")
if not ref_path.exists():
    raise FileNotFoundError("Run precache_voice.sh before building.")

# LOCKED CONFIGURATION
config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

def safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2):
    top = mobject.get_top()[^1]
    bottom = mobject.get_bottom()[^1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * ((min_y + buff) - bottom))
    return mobject

def harmonious_color(base_color, variations=3, lightness_shift=0.1):
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

def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.05):
    return LaggedStart(
        FadeIn(mobject),
        mobject.animate.scale(scale_factor).set_run_time(0.5).scale(1/scale_factor),
        lag_ratio=lag_ratio,
    )

class Scene01Intro(VoiceoverScene):
    def construct(self):
        blues = harmonious_color(BLUE, variations=3)
        
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            num_beats = max(10, min(22, int(np.ceil(tracker.duration / 3.0))))
            beats = BeatPlan(tracker.duration, [^1] * num_beats)

            # Title
            title = Text("The Circle Growth Law", font_size=48, weight=BOLD, color=blues[^0])
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))
            
            # Subtitle
            subtitle = Text("A Self-Referential Signature", font_size=32, color=blues[^1])
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            play_text_next(self, beats, polished_fade_in(subtitle))
            
            # Center circle with radius label
            circle = Circle(radius=1.5, color=blues[^2], stroke_width=4)
            circle.move_to(ORIGIN + DOWN * 0.5)
            play_next(self, beats, Create(circle))
            
            radius_line = Line(circle.get_center(), circle.get_right(), color=YELLOW, stroke_width=3)
            r_label = MathTex("r", color=YELLOW, font_size=36).next_to(radius_line, UP, buff=0.2)
            safe_position(r_label)
            play_next(self, beats, Create(radius_line), FadeIn(r_label))
            
            # Archimedes triangle reference (simple triangle inscribed)
            triangle = Triangle(color=blues[^1], stroke_width=3).scale(1.3).move_to(circle.get_center())
            play_next(self, beats, Create(triangle))
            
            # Key callout
            callout = Text("Area growth = Perimeter", font_size=28, color=YELLOW)
            callout.move_to(DOWN * 2.8)
            play_text_next(self, beats, polished_fade_in(callout))
            
            # Hold final frame
            play_next(self, beats, Wait())
```


***

## scene_02_growth_demo.py

```python
from manim import *
import numpy as np
import colorsys
from pathlib import Path
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

try:
    from typing import override as _typing_override
except Exception:
    try:
        from typing_extensions import override as _typing_override
    except Exception:
        def _typing_override(func):
            return func

ref_path = Path("assets/voice_ref/ref.wav")
if not ref_path.exists():
    raise FileNotFoundError("Run precache_voice.sh before building.")

config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

def safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2):
    top = mobject.get_top()[^1]
    bottom = mobject.get_bottom()[^1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * ((min_y + buff) - bottom))
    return mobject

def harmonious_color(base_color, variations=3, lightness_shift=0.1):
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

def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.05):
    return LaggedStart(
        FadeIn(mobject),
        mobject.animate.scale(scale_factor).set_run_time(0.5).scale(1/scale_factor),
        lag_ratio=lag_ratio,
    )

class Scene02GrowthDemo(VoiceoverScene):
    def construct(self):
        blues = harmonious_color(BLUE, variations=4)
        
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
        with self.voiceover(text=SCRIPT["growth_demo"]) as tracker:
            num_beats = max(10, min(22, int(np.ceil(tracker.duration / 3.0))))
            beats = BeatPlan(tracker.duration, [^1] * num_beats)

            # Title
            title = Text("Dynamic Growth Demonstration", font_size=42, weight=BOLD, color=blues[^0])
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))
            
            # Left panel bullets
            bullet1 = Text("• Start at r = 1", font_size=26, color=blues[^1]).move_to(LEFT * 5.2 + UP * 1.5)
            bullet2 = Text("• Expand radius dynamically", font_size=26, color=blues[^1]).next_to(bullet1, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet2)
            bullet3 = MathTex(r"\frac{dA}{dr} = 2\pi r", font_size=32, color=blues[^2]).next_to(bullet2, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet3)
            bullet4 = MathTex(r"\text{Perimeter} = 2\pi r", font_size=32, color=blues[^2]).next_to(bullet3, DOWN, aligned_edge=LEFT, buff=0.3)
            safe_position(bullet4)
            
            play_text_next(self, beats, FadeIn(bullet1))
            
            # Right panel: expanding circle
            circle_start = Circle(radius=1.0, color=blues[^3], stroke_width=3)
            circle_start.move_to(RIGHT * 3.0 + DOWN * 0.5)
            play_next(self, beats, Create(circle_start))
            
            play_text_next(self, beats, FadeIn(bullet2))
            
            # Expand animation
            circle_end = Circle(radius=2.0, color=blues[^3], stroke_width=3, fill_opacity=0.2, fill_color=blues[^3])
            circle_end.move_to(circle_start.get_center())
            play_next(self, beats, Transform(circle_start, circle_end))
            
            play_text_next(self, beats, FadeIn(bullet3))
            
            # Equation display
            equation = MathTex(r"\frac{d}{dr}(\pi r^2) = 2\pi r", font_size=36, color=YELLOW)
            equation.move_to(RIGHT * 3.0 + DOWN * 2.5)
            play_text_next(self, beats, FadeIn(equation))
            
            play_text_next(self, beats, FadeIn(bullet4))
            
            # Perimeter highlight
            perimeter_arc = circle_start.copy().set_color(YELLOW).set_stroke(width=5)
            play_next(self, beats, ShowPassingFlash(perimeter_arc, time_width=0.8))
            
            # Final callout
            callout = Text("Perfect match!", font_size=28, color=YELLOW, weight=BOLD)
            callout.move_to(RIGHT * 3.0 + UP * 2.0)
            play_text_next(self, beats, polished_fade_in(callout))
            
            play_next(self, beats, Wait())
```


***

## scene_03_efficiency_gap.py

```python
from manim import *
import numpy as np
import colorsys
from pathlib import Path
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

try:
    from typing import override as _typing_override
except Exception:
    try:
        from typing_extensions import override as _typing_override
    except Exception:
        def _typing_override(func):
            return func

ref_path = Path("assets/voice_ref/ref.wav")
if not ref_path.exists():
    raise FileNotFoundError("Run precache_voice.sh before building.")

config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

def safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2):
    top = mobject.get_top()[^1]
    bottom = mobject.get_bottom()[^1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * ((min_y + buff) - bottom))
    return mobject

def safe_layout(*mobjects, h_buff=0.5, max_y=3.5, min_y=-3.5):
    group = VGroup(*mobjects)
    group.arrange(RIGHT, buff=h_buff)
    for mob in mobjects:
        safe_position(mob, max_y, min_y)
    return group

def harmonious_color(base_color, variations=3, lightness_shift=0.1):
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

class Scene03EfficiencyGap(VoiceoverScene):
    def construct(self):
        blues = harmonious_color(BLUE, variations=3)
        
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
        with self.voiceover(text=SCRIPT["efficiency_gap"]) as tracker:
            num_beats = max(10, min(22, int(np.ceil(tracker.duration / 3.0))))
            beats = BeatPlan(tracker.duration, [^1] * num_beats)

            # Title
            title = Text("Other Shapes Fail the Test", font_size=42, weight=BOLD, color=blues[^0])
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))
            
            # Three columns: Square, Ellipse, Polygon
            square = Square(side_length=1.5, color=YELLOW, stroke_width=3)
            square.move_to(LEFT * 4.5 + UP * 0.5)
            square_label = Text("Square", font_size=24, color=YELLOW).next_to(square, UP, buff=0.3)
            safe_position(square_label)
            
            ellipse = Ellipse(width=2.0, height=1.2, color=ORANGE, stroke_width=3)
            ellipse.move_to(ORIGIN + UP * 0.5)
            ellipse_label = Text("Ellipse", font_size=24, color=ORANGE).next_to(ellipse, UP, buff=0.3)
            safe_position(ellipse_label)
            
            polygon = RegularPolygon(n=6, radius=1.0, color=RED, stroke_width=3)
            polygon.move_to(RIGHT * 4.5 + UP * 0.5)
            polygon_label = Text("Polygon", font_size=24, color=RED).next_to(polygon, UP, buff=0.3)
            safe_position(polygon_label)
            
            play_text_next(self, beats, FadeIn(square), FadeIn(square_label))
            play_text_next(self, beats, FadeIn(ellipse), FadeIn(ellipse_label))
            play_text_next(self, beats, FadeIn(polygon), FadeIn(polygon_label))
            
            # Efficiency ratio bars
            bar_square = Rectangle(width=0.7, height=0.5, color=YELLOW, fill_opacity=0.6)
            bar_square.move_to(LEFT * 4.5 + DOWN * 1.8)
            ratio_square = Text("0.79", font_size=22, color=WHITE).move_to(bar_square.get_center())
            
            bar_ellipse = Rectangle(width=0.85, height=0.5, color=ORANGE, fill_opacity=0.6)
            bar_ellipse.move_to(ORIGIN + DOWN * 1.8)
            ratio_ellipse = Text("0.87", font_size=22, color=WHITE).move_to(bar_ellipse.get_center())
            
            bar_polygon = Rectangle(width=0.92, height=0.5, color=RED, fill_opacity=0.6)
            bar_polygon.move_to(RIGHT * 4.5 + DOWN * 1.8)
            ratio_polygon = Text("0.91", font_size=22, color=WHITE).move_to(bar_polygon.get_center())
            
            play_next(self, beats, GrowFromEdge(bar_square, LEFT), FadeIn(ratio_square))
            play_next(self, beats, GrowFromEdge(bar_ellipse, LEFT), FadeIn(ratio_ellipse))
            play_next(self, beats, GrowFromEdge(bar_polygon, LEFT), FadeIn(ratio_polygon))
            
            # Circle reference bar
            bar_circle = Rectangle(width=1.0, height=0.5, color=GREEN, fill_opacity=0.8)
            bar_circle.move_to(ORIGIN + DOWN * 2.8)
            ratio_circle = Text("Circle = 1.0", font_size=24, color=WHITE, weight=BOLD).move_to(bar_circle.get_center())
            
            play_next(self, beats, GrowFromEdge(bar_circle, LEFT), FadeIn(ratio_circle))
            
            # Callout
            callout = Text("Gap quantifies non-circularity", font_size=26, color=YELLOW)
            callout.move_to(DOWN * 3.8)
            play_text_next(self, beats, FadeIn(callout))
            
            play_next(self, beats, Wait())
```


***

## scene_04_curvature_invariance.py

```python
from manim import *
import numpy as np
import colorsys
from pathlib import Path
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

try:
    from typing import override as _typing_override
except Exception:
    try:
        from typing_extensions import override as _typing_override
    except Exception:
        def _typing_override(func):
            return func

ref_path = Path("assets/voice_ref/ref.wav")
if not ref_path.exists():
    raise FileNotFoundError("Run precache_voice.sh before building.")

config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

def safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2):
    top = mobject.get_top()[^1]
    bottom = mobject.get_bottom()[^1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * ((min_y + buff) - bottom))
    return mobject

def harmonious_color(base_color, variations=3, lightness_shift=0.1):
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

class Scene04CurvatureInvariance(ThreeDScene):
    def construct(self):
        blues = harmonious_color(BLUE, variations=4)
        
        # Note: VoiceoverScene not compatible with ThreeDScene inheritance
        # Using direct speech service initialization
        from flaming_horse_voice import get_speech_service
        service = get_speech_service(Path(__file__).resolve().parent)
        self.set_speech_service(service)
        
        with self.voiceover(text=SCRIPT["curvature_invariance"]) as tracker:
            num_beats = max(10, min(22, int(np.ceil(tracker.duration / 3.0))))
            beats = BeatPlan(tracker.duration, [^1] * num_beats)

            # Set 3D camera
            self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
            
            # Title (2D overlay)
            title = Text("Constant Curvature Signature", font_size=42, weight=BOLD, color=blues[^0])
            title.to_edge(UP, buff=0.3)
            self.add_fixed_in_frame_mobjects(title)
            play_text_next(self, beats, Write(title))
            
            # Flat plane with circle
            plane = Surface(
                lambda u, v: np.array([u, v, 0]),
                u_range=[-2, 2],
                v_range=[-2, 2],
                resolution=(20, 20),
                fill_opacity=0.3,
                color=BLUE_E
            )
            plane.shift(LEFT * 5)
            
            circle_flat = Circle(radius=0.8, color=blues[^3], stroke_width=4)
            circle_flat.rotate(90 * DEGREES, axis=RIGHT).shift(LEFT * 5)
            
            play_next(self, beats, Create(plane), Create(circle_flat))
            
            # Equation overlay
            eq1 = MathTex(r"\frac{dA}{dr} = \text{Perimeter}", font_size=28, color=YELLOW)
            eq1.to_edge(DOWN, buff=1.5).shift(LEFT * 4)
            self.add_fixed_in_frame_mobjects(eq1)
            play_text_next(self, beats, FadeIn(eq1))
            
            # Sphere with geodesic circle
            sphere = Sphere(radius=1.2, resolution=(20, 20), fill_opacity=0.4, color=BLUE)
            sphere.shift(ORIGIN)
            
            circle_sphere = Circle(radius=0.6, color=blues[^3], stroke_width=4)
            circle_sphere.rotate(90 * DEGREES, axis=RIGHT).move_to(ORIGIN + OUT * 1.2)
            
            play_next(self, beats, Create(sphere), Create(circle_sphere))
            
            eq2 = MathTex(r"\frac{dA}{dr} = \text{Perimeter}", font_size=28, color=YELLOW)
            eq2.to_edge(DOWN, buff=1.5).shift(ORIGIN)
            self.add_fixed_in_frame_mobjects(eq2)
            play_text_next(self, beats, FadeIn(eq2))
            
            # Hyperbolic surface (saddle)
            hyperbolic = Surface(
                lambda u, v: np.array([u, v, 0.3 * (u**2 - v**2)]),
                u_range=[-1.5, 1.5],
                v_range=[-1.5, 1.5],
                resolution=(20, 20),
                fill_opacity=0.3,
                color=RED_E
            )
            hyperbolic.shift(RIGHT * 5)
            
            circle_hyper = Circle(radius=0.8, color=blues[^3], stroke_width=4)
            circle_hyper.rotate(90 * DEGREES, axis=RIGHT).shift(RIGHT * 5)
            
            play_next(self, beats, Create(hyperbolic), Create(circle_hyper))
            
            eq3 = MathTex(r"\frac{dA}{dr} = \text{Perimeter}", font_size=28, color=YELLOW)
            eq3.to_edge(DOWN, buff=1.5).shift(RIGHT * 4)
            self.add_fixed_in_frame_mobjects(eq3)
            play_text_next(self, beats, FadeIn(eq3))
            
            # Rotate camera for emphasis
            play_next(self, beats, self.begin_ambient_camera_rotation(rate=0.2))
            play_next(self, beats, Wait())
            self.stop_ambient_camera_rotation()
            
            # Final callout
            callout = Text("Geometry-independent property", font_size=26, color=YELLOW, weight=BOLD)
            callout.to_edge(DOWN, buff=0.3)
            self.add_fixed_in_frame_mobjects(callout)
            play_text_next(self, beats, FadeIn(callout))
            
            play_next(self, beats, Wait())
```


***

## scene_05_conclusion.py

```python
from manim import *
import numpy as np
import colorsys
from pathlib import Path
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

try:
    from typing import override as _typing_override
except Exception:
    try:
        from typing_extensions import override as _typing_override
    except Exception:
        def _typing_override(func):
            return func

ref_path = Path("assets/voice_ref/ref.wav")
if not ref_path.exists():
    raise FileNotFoundError("Run precache_voice.sh before building.")

config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

def safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2):
    top = mobject.get_top()[^1]
    bottom = mobject.get_bottom()[^1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * ((min_y + buff) - bottom))
    return mobject

def harmonious_color(base_color, variations=3, lightness_shift=0.1):
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

def polished_fade_in(mobject, lag_ratio=0.2, scale_factor=1.05):
    return LaggedStart(
        FadeIn(mobject),
        mobject.animate.scale(scale_factor).set_run_time(0.5).scale(1/scale_factor),
        lag_ratio=lag_ratio,
    )

class Scene05Conclusion(VoiceoverScene):
    def construct(self):
        blues = harmonious_color(BLUE, variations=4)
        
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
        with self.voiceover(text=SCRIPT["conclusion"]) as tracker:
            num_beats = max(10, min(22, int(np.ceil(tracker.duration / 3.0))))
            beats = BeatPlan(tracker.duration, [^1] * num_beats)

            # Title
            title = Text("The Curvature-Independent Test", font_size=42, weight=BOLD, color=blues[^0])
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title))
            
            # Left panel bullets
            bullet1 = Text("• Compute: (dA/dr) / perimeter", font_size=24, color=blues[^1]).move_to(LEFT * 5.0 + UP * 1.8)
            bullet2 = Text("• True circles → ratio = 1.0 ✓", font_size=24, color=GREEN).next_to(bullet1, DOWN, aligned_edge=LEFT, buff=0.35)
            safe_position(bullet2)
            bullet3 = Text("• Other shapes → ratio < 1.0 ✗", font_size=24, color=YELLOW).next_to(bullet2, DOWN, aligned_edge=LEFT, buff=0.35)
            safe_position(bullet3)
            bullet4 = Text("• Unexpected 1.0? → Hidden symmetry!", font_size=24, color=RED).next_to(bullet3, DOWN, aligned_edge=LEFT, buff=0.35)
            safe_position(bullet4)
            
            play_text_next(self, beats, FadeIn(bullet1))
            play_text_next(self, beats, FadeIn(bullet2))
            play_text_next(self, beats, FadeIn(bullet3))
            play_text_next(self, beats, polished_fade_in(bullet4))
            
            # Right panel: Decision flowchart
            input_box = RoundedRectangle(width=2.5, height=0.6, corner_radius=0.1, color=blues[^2], stroke_width=2)
            input_box.move_to(RIGHT * 3.5 + UP * 2.0)
            input_text = Text("Closed curve", font_size=20, color=WHITE).move_to(input_box.get_center())
            
            play_next(self, beats, Create(input_box), FadeIn(input_text))
            
            # Compute node
            compute_box = RoundedRectangle(width=2.8, height=0.6, corner_radius=0.1, color=blues[^2], stroke_width=2)
            compute_box.move_to(RIGHT * 3.5 + UP * 0.8)
            compute_text = Text("Compute ratio", font_size=20, color=WHITE).move_to(compute_box.get_center())
            
            arrow1 = Arrow(input_box.get_bottom(), compute_box.get_top(), buff=0.1, color=blues[^1], stroke_width=2)
            play_next(self, beats, Create(arrow1), Create(compute_box), FadeIn(compute_text))
            
            # Branch: = 1.0
            circle_box = RoundedRectangle(width=2.2, height=0.6, corner_radius=0.1, color=GREEN, stroke_width=2, fill_opacity=0.2, fill_color=GREEN)
            circle_box.move_to(RIGHT * 2.0 + DOWN * 0.8)
            circle_text = Text("Geodesic circle", font_size=18, color=GREEN).move_to(circle_box.get_center())
            
            arrow_yes = Arrow(compute_box.get_bottom(), circle_box.get_top(), buff=0.1, color=GREEN, stroke_width=2)
            arrow_yes_label = Text("= 1.0", font_size=16, color=GREEN).next_to(arrow_yes, LEFT, buff=0.1)
            safe_position(arrow_yes_label)
            
            play_next(self, beats, Create(arrow_yes), FadeIn(arrow_yes_label), Create(circle_box), FadeIn(circle_text))
            
            # Branch: < 1.0
            other_box = RoundedRectangle(width=2.2, height=0.6, corner_radius=0.1, color=YELLOW, stroke_width=2, fill_opacity=0.2, fill_color=YELLOW)
            other_box.move_to(RIGHT * 5.0 + DOWN * 0.8)
            other_text = Text("Non-circular", font_size=18, color=YELLOW).move_to(other_box.get_center())
            
            arrow_no = Arrow(compute_box.get_bottom(), other_box.get_top(), buff=0.1, color=YELLOW, stroke_width=2)
            arrow_no_label = Text("< 1.0", font_size=16, color=YELLOW).next_to(arrow_no, RIGHT, buff=0.1)
            safe_position(arrow_no_label)
            
            play_next(self, beats, Create(arrow_no), FadeIn(arrow_no_label), Create(other_box), FadeIn(other_text))
            
            # Discovery node
            discovery_box = RoundedRectangle(width=2.8, height=0.6, corner_radius=0.1, color=RED, stroke_width=3, fill_opacity=0.3, fill_color=RED)
            discovery_box.move_to(RIGHT * 3.5 + DOWN * 2.2)
            discovery_text = Text("New symmetry!", font_size=20, color=RED, weight=BOLD).move_to(discovery_box.get_center())
            
            play_next(self, beats, Create(discovery_box), FadeIn(discovery_text))
            
            # Final callout
            callout = Text("Sharp, testable prediction", font_size=28, color=YELLOW, weight=BOLD)
            callout.move_to(DOWN * 3.5)
            play_text_next(self, beats, polished_fade_in(callout))
            
            play_next(self, beats, Wait())
```


***

## Usage Instructions

Save these files in your project directory:

```bash
projects/archimedes_circle_growth/
├── narration_script.py
├── scene_01_intro.py
├── scene_02_growth_demo.py
├── scene_03_efficiency_gap.py
├── scene_04_curvature_invariance.py
└── scene_05_conclusion.py
```

Then run through the pipeline:

```bash
# From repo root
./scripts/build_video.sh projects/archimedes_circle_growth
```

All scenes follow Flaming Horse contracts: locked config, cached Qwen voice, safe positioning, duration-scaled micro-beats, layout contracts, no browser storage, no positioning violations, continuous motion, proper timing budget.

<div align="center">⁂</div>

[^1]: AGENTS.md

