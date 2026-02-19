# Manim CE Kitchen Sink (Static Agent Reference)

Use this document as direct implementation guidance when generating Manim scene code.
This file is designed for system-prompt injection and contains concrete examples from official Manim CE documentation.

---

## Source Policy (Official Manim CE Docs Only)

Use only these official Manim Community Edition docs:

- [Docs Home](https://docs.manim.community/en/stable/index.html)
- [Reference Manual](https://docs.manim.community/en/stable/reference.html)
- [Tutorials & Guides](https://docs.manim.community/en/stable/tutorials_guides.html)
- [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)
- [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
- [Scenes Index](https://docs.manim.community/en/stable/reference_index/scenes.html)
- [Cameras Index](https://docs.manim.community/en/stable/reference_index/cameras.html)
- [Utilities Index](https://docs.manim.community/en/stable/reference_index/utilities_misc.html)
- [Building Blocks Tutorial](https://docs.manim.community/en/stable/tutorials/building_blocks.html)
- [Using Text and LaTeX](https://docs.manim.community/en/stable/guides/using_text.html)

---

## Core Contract (Doc-Backed Assertions)

- Scenes are implemented through `construct()` in `Scene`/scene subclasses.  
  Source: [Scenes Index](https://docs.manim.community/en/stable/reference_index/scenes.html)
- Animation progression is controlled via scene animation APIs (`play`, animation classes, composition).  
  Source: [Scene Reference](https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html), [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)
- Mobjects are the primary object model for visual elements and transformations.  
  Source: [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
- Use only documented stable APIs for compatibility.  
  Source: [Reference Manual](https://docs.manim.community/en/stable/reference.html)

---

## Pattern Family A: Scene Lifecycle and `self.play(...)`

Doc-backed assertions:
- Scene lifecycle is centered around `construct()` and staged animation calls.  
  Source: [Scene Reference](https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html), [Building Blocks Tutorial](https://docs.manim.community/en/stable/tutorials/building_blocks.html)
- Progressive sequencing (create -> animate -> remove/replace) is a standard tutorial pattern.  
  Source: [Building Blocks Tutorial](https://docs.manim.community/en/stable/tutorials/building_blocks.html)

```python
from manim import *

class SceneLifecycleBaseline(Scene):
    """
    Demonstrates the standard scene lifecycle pattern with progressive sequencing.
    Source: https://docs.manim.community/en/stable/tutorials/building_blocks.html
    """
    def construct(self):
        # Object setup
        circle = Circle(radius=1.5, color=BLUE)
        square = Square(side_length=2, color=GREEN)
        
        # Reveal sequence
        self.play(Create(circle))
        self.wait(0.5)
        
        # Transform sequence
        self.play(Transform(circle, square))
        self.wait(0.5)
        
        # Cleanup before scene end
        self.play(FadeOut(circle))
        self.wait(0.3)
```

---

## Pattern Family B: 2D Geometry, Grouping, and Layout Composition

Doc-backed assertions:
- 2D primitives (for example `Circle`, `Rectangle`, `Polygon`, `Line`, `Arrow`) are part of documented mobject families.  
  Source: [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
- Grouping classes such as `VGroup` are provided for composition of multiple mobjects.  
  Source: [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)

```python
from manim import *

class GeometryGallery2D(Scene):
    """
    Demonstrates 2D primitives composed into a coherent concept using VGroup.
    Source: https://docs.manim.community/en/stable/reference_index/mobjects.html
    """
    def construct(self):
        # Multiple primitives composed into one concept
        circle = Circle(radius=0.8, color=BLUE)
        square = Square(side_length=1.5, color=GREEN).shift(RIGHT * 2.5)
        triangle = Triangle(color=RED).shift(LEFT * 2.5)
        
        # VGroup-based organization
        shapes = VGroup(circle, square, triangle)
        shapes.arrange(RIGHT, buff=1.0)
        
        # Staged animation sequence with clear visual intent
        self.play(Create(circle))
        self.wait(0.3)
        self.play(Create(square))
        self.wait(0.3)
        self.play(Create(triangle))
        self.wait(0.5)
        
        # Group transformation
        self.play(shapes.animate.scale(0.7))
        self.wait(0.5)
```

```python
from manim import *

class LayoutAndLabelAnchoring2D(Scene):
    """
    Demonstrates explicit and relative placement with label anchoring.
    Source: https://docs.manim.community/en/stable/reference/manim.mobject.mobject.Mobject.html
    """
    def construct(self):
        # Explicit placement
        circle = Circle(radius=1.0, color=BLUE).move_to(LEFT * 3)
        
        # Relative placement with spacing
        square = Square(side_length=1.5, color=GREEN)
        square.next_to(circle, RIGHT, buff=1.5)
        
        # Label anchoring to nearby objects
        circle_label = Text("Circle", font_size=28).next_to(circle, DOWN, buff=0.3)
        square_label = Text("Square", font_size=28).next_to(square, DOWN, buff=0.3)
        
        # Staged reveal preserving readability
        self.play(Create(circle), Write(circle_label))
        self.wait(0.5)
        self.play(Create(square), Write(square_label))
        self.wait(0.5)
```

---

## Pattern Family C: Text and Math Typesetting (`Text`, `Tex`, `MathTex`)

Doc-backed assertions:
- Text and formula objects are documented separately and have distinct usage patterns.  
  Source: [Using Text and LaTeX](https://docs.manim.community/en/stable/guides/using_text.html), [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
- LaTeX rendering for formulas is covered in official text/formula guidance.  
  Source: [Using Text and LaTeX](https://docs.manim.community/en/stable/guides/using_text.html)

```python
from manim import *

class TextHierarchyAndCallouts(Scene):
    """
    Demonstrates title/subtitle structure with annotation labels and staged reveals.
    Source: https://docs.manim.community/en/stable/guides/using_text.html
    """
    def construct(self):
        # Title/subtitle structure
        title = Text("Main Concept", font_size=48, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        
        subtitle = Text("Supporting Details", font_size=32, color=GRAY)
        subtitle.next_to(title, DOWN, buff=0.3)
        
        # Annotation labels
        point_1 = Text("• Key Point 1", font_size=28).shift(UP * 0.5)
        point_2 = Text("• Key Point 2", font_size=28).next_to(point_1, DOWN, buff=0.3, aligned_edge=LEFT)
        point_3 = Text("• Key Point 3", font_size=28).next_to(point_2, DOWN, buff=0.3, aligned_edge=LEFT)
        
        # Staged text reveal timing
        self.play(Write(title))
        self.wait(0.3)
        self.play(FadeIn(subtitle))
        self.wait(0.5)
        self.play(FadeIn(point_1))
        self.wait(0.3)
        self.play(FadeIn(point_2))
        self.wait(0.3)
        self.play(FadeIn(point_3))
        self.wait(0.5)
```

```python
from manim import *

class MathTexDerivationPattern(Scene):
    """
    Demonstrates equation introduction, transformation, and emphasis patterns.
    Source: https://docs.manim.community/en/stable/guides/using_text.html
    """
    def construct(self):
        # Equation introduction with MathTex
        eq1 = MathTex(r"a^2 + b^2 = c^2")
        eq1.scale(1.5)
        
        self.play(Write(eq1))
        self.wait(0.5)
        
        # Transformation between equation states
        eq2 = MathTex(r"c = \sqrt{a^2 + b^2}")
        eq2.scale(1.5)
        
        self.play(TransformMatchingTex(eq1, eq2))
        self.wait(0.5)
        
        # Emphasis on key terms/parts
        # Highlight specific parts by color
        eq3 = MathTex(r"c = \sqrt{", r"a^2", r" + ", r"b^2", r"}")
        eq3.scale(1.5)
        eq3[1].set_color(YELLOW)  # Highlight a^2
        eq3[3].set_color(BLUE)     # Highlight b^2
        
        self.play(TransformMatchingTex(eq2, eq3))
        self.wait(0.5)
```

---

## Pattern Family D: Transition Choreography and Animation Composition

Doc-backed assertions:
- Transform variants (`Transform`, `ReplacementTransform`, `FadeTransform`) are documented animation classes.  
  Source: [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)
- Composition helpers (`AnimationGroup`, `LaggedStart`, `Succession`) are documented composition tools.  
  Source: [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)

```python
from manim import *

class TransitionPatternsCore(Scene):
    """
    Demonstrates Transform, ReplacementTransform, and FadeTransform usage.
    Source: https://docs.manim.community/en/stable/reference_index/animations.html
    """
    def construct(self):
        # Transform: morphs the original object visually
        # Use when you want to keep the original object reference
        circle = Circle(color=BLUE).shift(LEFT * 3)
        square = Square(color=GREEN).shift(LEFT * 3)
        
        self.play(Create(circle))
        self.wait(0.3)
        self.play(Transform(circle, square))  # circle now looks like square
        self.wait(0.5)
        self.play(FadeOut(circle))  # removes the transformed object
        
        # ReplacementTransform: replaces one object with another
        # Use when you want to replace the object in the scene
        triangle = Triangle(color=RED).shift(RIGHT * 0)
        pentagon = RegularPolygon(5, color=ORANGE).shift(RIGHT * 0)
        
        self.play(Create(triangle))
        self.wait(0.3)
        self.play(ReplacementTransform(triangle, pentagon))  # pentagon replaces triangle
        self.wait(0.5)
        
        # FadeTransform: smooth transition with fade effect
        # Use when emphasizing a semantic change between objects
        hex1 = RegularPolygon(6, color=PURPLE).shift(RIGHT * 3)
        hex2 = RegularPolygon(6, color=YELLOW).shift(RIGHT * 3).scale(1.5)
        
        self.play(Create(hex1))
        self.wait(0.3)
        self.play(FadeTransform(hex1, hex2))  # smooth fade transition
        self.wait(0.5)
```

```python
from manim import *

class GroupedTimingPatterns(Scene):
    """
    Demonstrates AnimationGroup, LaggedStart, and Succession for timing control.
    Source: https://docs.manim.community/en/stable/reference_index/animations.html
    """
    def construct(self):
        # AnimationGroup: play multiple animations simultaneously
        circles = VGroup(*[Circle(radius=0.5, color=BLUE).shift(LEFT * 4 + UP * i) for i in range(-1, 2)])
        
        self.play(AnimationGroup(*[Create(c) for c in circles]))
        self.wait(0.5)
        
        # LaggedStart: stagger animations with a time lag
        squares = VGroup(*[Square(side_length=0.8, color=GREEN).shift(ORIGIN + UP * i) for i in range(-1, 2)])
        
        self.play(LaggedStart(*[Create(s) for s in squares], lag_ratio=0.3))
        self.wait(0.5)
        
        # Succession: play animations one after another
        triangles = VGroup(*[Triangle(color=RED).scale(0.6).shift(RIGHT * 4 + UP * i) for i in range(-1, 2)])
        
        self.play(Succession(*[Create(t) for t in triangles]))
        self.wait(0.5)
        
        # Practical pacing for readability: combine techniques
        all_shapes = VGroup(circles, squares, triangles)
        self.play(LaggedStart(*[FadeOut(group) for group in all_shapes], lag_ratio=0.2))
        self.wait(0.3)
```

---

## Pattern Family E: Graphing and Coordinate Systems

Doc-backed assertions:
- Graphing coordinate systems (for example `Axes`, `NumberPlane`) are documented mobject families.  
  Source: [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html), [Reference Manual](https://docs.manim.community/en/stable/reference.html)
- Plotting-oriented scene patterns are part of official tutorials and reference content.  
  Source: [Building Blocks Tutorial](https://docs.manim.community/en/stable/tutorials/building_blocks.html), [Reference Manual](https://docs.manim.community/en/stable/reference.html)

```python
from manim import *

class AxesAndFunctionPlot(Scene):
    """
    Demonstrates axis setup with function plotting and instructional labels.
    Source: https://docs.manim.community/en/stable/reference_index/mobjects.html
    """
    def construct(self):
        # Axis setup
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 6, 1],
            x_length=8,
            y_length=6,
            axis_config={"color": BLUE},
        )
        
        # Add axis labels
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")
        labels = VGroup(x_label, y_label)
        
        self.play(Create(axes), Write(labels))
        self.wait(0.5)
        
        # Function plot
        graph = axes.plot(lambda x: x**2, color=YELLOW)
        graph_label = axes.get_graph_label(graph, label=r"f(x) = x^2")
        
        self.play(Create(graph))
        self.wait(0.3)
        self.play(Write(graph_label))
        self.wait(0.5)
        
        # Highlights tied to instructional intent
        dot = Dot(axes.c2p(1, 1), color=RED)
        dot_label = Text("(1, 1)", font_size=24).next_to(dot, UP + RIGHT, buff=0.2)
        
        self.play(FadeIn(dot), Write(dot_label))
        self.wait(0.5)
```

```python
from manim import *

class DataNarrativeGraphing(Scene):
    """
    Demonstrates progressive data reveal with visual comparison and cleanup.
    Source: https://docs.manim.community/en/stable/reference_index/mobjects.html
    """
    def construct(self):
        # Setup axes for comparison
        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 10, 2],
            x_length=7,
            y_length=5,
            axis_config={"color": GRAY},
        )
        
        self.play(Create(axes))
        self.wait(0.3)
        
        # Progressive data/curve reveal - first dataset
        graph1 = axes.plot(lambda x: x, color=BLUE)
        label1 = Text("Linear", font_size=28, color=BLUE).to_edge(UP).shift(LEFT * 3)
        
        self.play(Create(graph1), Write(label1))
        self.wait(0.5)
        
        # Second dataset for visual comparison pattern
        graph2 = axes.plot(lambda x: x**1.5, color=RED)
        label2 = Text("Power", font_size=28, color=RED).to_edge(UP).shift(RIGHT * 3)
        
        self.play(Create(graph2), Write(label2))
        self.wait(0.8)
        
        # Cleanup between narrative beats
        self.play(
            FadeOut(graph1),
            FadeOut(label1),
            graph2.animate.set_color(YELLOW),
            label2.animate.set_color(YELLOW)
        )
        self.wait(0.5)
```

---

## Pattern Family F: 3D Scenes and Camera Control

Doc-backed assertions:
- 3D scene behavior is documented through `ThreeDScene` and camera APIs.  
  Source: [ThreeDScene Reference](https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html), [Cameras Index](https://docs.manim.community/en/stable/reference_index/cameras.html)
- Camera orientation/movement controls are explicit parts of the 3D scene API surface.  
  Source: [ThreeDScene Reference](https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html)

```python
from manim import *

class ThreeDOrientationBaseline(ThreeDScene):
    """
    Demonstrates ThreeDScene setup with camera orientation and 3D object reveal.
    Source: https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html
    """
    def construct(self):
        # Camera orientation initialization
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        
        # Simple 3D object reveal with readable framing
        axes = ThreeDAxes()
        cube = Cube(side_length=2, fill_opacity=0.7, color=BLUE)
        
        self.play(Create(axes))
        self.wait(0.3)
        self.play(Create(cube))
        self.wait(0.5)
        
        # Demonstrate 3D rotation for spatial understanding
        self.play(Rotate(cube, angle=PI/2, axis=UP))
        self.wait(0.5)
```

```python
from manim import *

class CameraMotionAndFocus3D(ThreeDScene):
    """
    Demonstrates purposeful camera movement with object transformation.
    Source: https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html
    """
    def construct(self):
        # Initial camera setup
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        
        # Create 3D objects
        axes = ThreeDAxes()
        sphere = Sphere(radius=1.5, resolution=(20, 20), color=GREEN)
        sphere.set_opacity(0.8)
        
        self.play(Create(axes))
        self.play(Create(sphere))
        self.wait(0.5)
        
        # Purposeful camera movement for different view angles
        self.move_camera(phi=30 * DEGREES, theta=-60 * DEGREES, run_time=2)
        self.wait(0.3)
        
        # Object transformation under camera change
        self.play(sphere.animate.scale(0.5).shift(UP * 2))
        self.wait(0.5)
        
        # Readability-oriented camera choice: zoom in on transformed object
        self.move_camera(phi=45 * DEGREES, theta=-30 * DEGREES, zoom=1.5, run_time=2)
        self.wait(0.5)
```

---

## Pattern Family G: Dynamic Motion with Trackers and Updaters

Doc-backed assertions:
- `ValueTracker` is a documented mechanism for value-driven animation control.  
  Source: [ValueTracker Reference](https://docs.manim.community/en/stable/reference/manim.mobject.value_tracker.ValueTracker.html)
- Updater behavior is documented on mobject APIs and interacts with scene timing.  
  Source: [Mobject Reference](https://docs.manim.community/en/stable/reference/manim.mobject.mobject.Mobject.html), [Wait Reference](https://docs.manim.community/en/stable/reference/manim.animation.animation.Wait.html)

```python
from manim import *

class ValueTrackerDrivenMotion(Scene):
    """
    Demonstrates ValueTracker with updater lifecycle for controlled motion.
    Source: https://docs.manim.community/en/stable/reference/manim.mobject.value_tracker.ValueTracker.html
    """
    def construct(self):
        # ValueTracker-driven parameter updates
        tracker = ValueTracker(0)
        
        # Create objects that depend on tracker value
        circle = Circle(radius=1, color=BLUE)
        number = DecimalNumber(0).next_to(circle, DOWN, buff=0.5)
        
        # add_updater lifecycle
        def update_circle(mob):
            # Update circle position based on tracker value
            mob.move_to(RIGHT * tracker.get_value())
        
        def update_number(mob):
            # Update displayed number to match tracker value
            mob.set_value(tracker.get_value())
            mob.next_to(circle, DOWN, buff=0.5)
        
        circle.add_updater(update_circle)
        number.add_updater(update_number)
        
        self.add(circle, number)
        
        # Controlled motion window with clear start/stop behavior
        self.play(tracker.animate.set_value(3), run_time=2)
        self.wait(0.5)
        self.play(tracker.animate.set_value(-2), run_time=2)
        self.wait(0.5)
        
        # remove_updater to stop tracking
        circle.remove_updater(update_circle)
        number.remove_updater(update_number)
        
        # Demonstrate that updaters are removed
        self.play(tracker.animate.set_value(0), run_time=1)
        self.wait(0.5)
```

---

## Pattern Family H: Color, Fill, Stroke, and Palette Behavior

Doc-backed assertions:
- Manim color utilities are documented under `manim.utils.color`.  
  Source: [Color Utilities Reference](https://docs.manim.community/en/stable/reference/manim.utils.color.html), [Utilities Index](https://docs.manim.community/en/stable/reference_index/utilities_misc.html)
- Mobject/VMobject styling APIs provide documented color/fill/stroke controls.  
  Source: [Mobject Reference](https://docs.manim.community/en/stable/reference/manim.mobject.mobject.Mobject.html), [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
- Color-related animation transitions are part of documented animation APIs (for example transform/fade families).  
  Source: [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)

```python
from manim import *

class ColorSemanticPalette(Scene):
    """
    Demonstrates coherent color palette with semantic mapping.
    Source: https://docs.manim.community/en/stable/reference/manim.utils.color.html
    """
    def construct(self):
        # A small, coherent palette
        primary_color = BLUE
        secondary_color = GREEN
        highlight_color = YELLOW
        
        # Semantic color mapping: state A (blue), state B (green), highlight (yellow)
        state_a = Circle(radius=1.5, color=primary_color).shift(LEFT * 3)
        state_b = Square(side_length=2.5, color=secondary_color).shift(RIGHT * 3)
        
        label_a = Text("State A", font_size=28, color=primary_color).next_to(state_a, DOWN)
        label_b = Text("State B", font_size=28, color=secondary_color).next_to(state_b, DOWN)
        
        self.play(Create(state_a), Write(label_a))
        self.wait(0.3)
        self.play(Create(state_b), Write(label_b))
        self.wait(0.5)
        
        # Consistent color reuse across scene beats
        # Highlight important transition
        arrow = Arrow(state_a.get_right(), state_b.get_left(), color=highlight_color, buff=0.5)
        arrow_label = Text("Transition", font_size=24, color=highlight_color).next_to(arrow, UP)
        
        self.play(GrowArrow(arrow), Write(arrow_label))
        self.wait(0.5)
```

```python
from manim import *

class FillStrokeStyleTransitions(Scene):
    """
    Demonstrates fill, stroke, and opacity styling with emphasis transitions.
    Source: https://docs.manim.community/en/stable/reference/manim.mobject.mobject.Mobject.html
    """
    def construct(self):
        # Initial object with basic styling
        circle = Circle(radius=1.5)
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(WHITE, width=3)
        
        self.play(Create(circle))
        self.wait(0.5)
        
        # set_fill / set_stroke style changes
        self.play(
            circle.animate.set_fill(RED, opacity=0.8),
            circle.animate.set_stroke(YELLOW, width=6)
        )
        self.wait(0.5)
        
        # Opacity and emphasis transitions
        # Emphasize by increasing opacity and size
        self.play(
            circle.animate.set_fill(GREEN, opacity=1.0).scale(1.3)
        )
        self.wait(0.5)
        
        # Readability-preserving contrast choices
        # Add contrasting text that remains readable
        text = Text("Emphasis", font_size=36, color=WHITE, weight=BOLD)
        text.move_to(circle.get_center())
        
        self.play(Write(text))
        self.wait(0.5)
        
        # Fade out with opacity control
        self.play(
            circle.animate.set_opacity(0.3),
            text.animate.set_opacity(0.3)
        )
        self.wait(0.5)
```

---

## Agent-Facing Quality Checklist (Doc-Backed)

- Is scene construction/animation flow consistent with documented scene APIs?  
  Source: [Scene Reference](https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html), [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)
- Are used objects and methods documented in stable Manim CE references?  
  Source: [Reference Manual](https://docs.manim.community/en/stable/reference.html)
- Are text/math object choices aligned with official text/LaTeX guidance?  
  Source: [Using Text and LaTeX](https://docs.manim.community/en/stable/guides/using_text.html)
- Are 3D/camera choices aligned with documented 3D scene APIs (when applicable)?  
  Source: [ThreeDScene Reference](https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html), [Cameras Index](https://docs.manim.community/en/stable/reference_index/cameras.html)
- Are updater/tracker usages aligned with documented lifecycle behavior (when applicable)?  
  Source: [ValueTracker Reference](https://docs.manim.community/en/stable/reference/manim.mobject.value_tracker.ValueTracker.html), [Mobject Reference](https://docs.manim.community/en/stable/reference/manim.mobject.mobject.Mobject.html), [Wait Reference](https://docs.manim.community/en/stable/reference/manim.animation.animation.Wait.html)
- Are color/styling choices implemented through documented color/styling APIs?  
  Source: [Color Utilities Reference](https://docs.manim.community/en/stable/reference/manim.utils.color.html), [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
