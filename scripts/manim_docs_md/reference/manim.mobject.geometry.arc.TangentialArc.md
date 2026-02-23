<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.arc.TangentialArc.html -->

# TangentialArc

Qualified name: `manim.mobject.geometry.arc.TangentialArc`

class TangentialArc(*line1*, *line2*, *radius*, *corner=(1, 1)*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/arc.html#TangentialArc)
:   Bases: [`ArcBetweenPoints`](manim.mobject.geometry.arc.ArcBetweenPoints.html#manim.mobject.geometry.arc.ArcBetweenPoints "manim.mobject.geometry.arc.ArcBetweenPoints")

    Construct an arc that is tangent to two intersecting lines.
    You can choose any of the 4 possible corner arcs via the corner tuple.
    corner = (s1, s2) where each si is ±1 to control direction along each line.

    Examples

    Example: TangentialArcExample

    ```python
    from manim import *

    class TangentialArcExample(Scene):
        def construct(self):
            line1 = DashedLine(start=3 * LEFT, end=3 * RIGHT)
            line1.rotate(angle=31 * DEGREES, about_point=ORIGIN)
            line2 = DashedLine(start=3 * UP, end=3 * DOWN)
            line2.rotate(angle=12 * DEGREES, about_point=ORIGIN)

            arc = TangentialArc(line1, line2, radius=2.25, corner=(1, 1), color=TEAL)
            self.add(arc, line1, line2)
    ```

    ```python
    class TangentialArcExample(Scene):
        def construct(self):
            line1 = DashedLine(start=3 * LEFT, end=3 * RIGHT)
            line1.rotate(angle=31 * DEGREES, about_point=ORIGIN)
            line2 = DashedLine(start=3 * UP, end=3 * DOWN)
            line2.rotate(angle=12 * DEGREES, about_point=ORIGIN)

            arc = TangentialArc(line1, line2, radius=2.25, corner=(1, 1), color=TEAL)
            self.add(arc, line1, line2)
    ```

    The following example shows all four possible corner configurations:

    Example: TangentialArcCorners

    ```python
    from manim import *

    class TangentialArcCorners(Scene):
        def construct(self):
            # Create two intersecting lines
            line1 = DashedLine(start=3 * LEFT, end=3 * RIGHT, color=GREY)
            line2 = DashedLine(start=3 * UP, end=3 * DOWN, color=GREY)

            # All four corner configurations with different colors
            arc_pp = TangentialArc(line1, line2, radius=1.5, corner=(1, 1), color=RED)
            arc_pn = TangentialArc(line1, line2, radius=1.5, corner=(1, -1), color=GREEN)
            arc_np = TangentialArc(line1, line2, radius=1.5, corner=(-1, 1), color=BLUE)
            arc_nn = TangentialArc(line1, line2, radius=1.5, corner=(-1, -1), color=YELLOW)

            # Labels for each arc
            label_pp = Text("(1,1)", font_size=24, color=RED).next_to(arc_pp, UR, buff=0.1)
            label_pn = Text("(1,-1)", font_size=24, color=GREEN).next_to(arc_pn, DR, buff=0.1)
            label_np = Text("(-1,1)", font_size=24, color=BLUE).next_to(arc_np, UL, buff=0.1)
            label_nn = Text("(-1,-1)", font_size=24, color=YELLOW).next_to(arc_nn, DL, buff=0.1)

            self.add(line1, line2, arc_pp, arc_pn, arc_np, arc_nn)
            self.add(label_pp, label_pn, label_np, label_nn)
    ```

    ```python
    class TangentialArcCorners(Scene):
        def construct(self):
            # Create two intersecting lines
            line1 = DashedLine(start=3 * LEFT, end=3 * RIGHT, color=GREY)
            line2 = DashedLine(start=3 * UP, end=3 * DOWN, color=GREY)

            # All four corner configurations with different colors
            arc_pp = TangentialArc(line1, line2, radius=1.5, corner=(1, 1), color=RED)
            arc_pn = TangentialArc(line1, line2, radius=1.5, corner=(1, -1), color=GREEN)
            arc_np = TangentialArc(line1, line2, radius=1.5, corner=(-1, 1), color=BLUE)
            arc_nn = TangentialArc(line1, line2, radius=1.5, corner=(-1, -1), color=YELLOW)

            # Labels for each arc
            label_pp = Text("(1,1)", font_size=24, color=RED).next_to(arc_pp, UR, buff=0.1)
            label_pn = Text("(1,-1)", font_size=24, color=GREEN).next_to(arc_pn, DR, buff=0.1)
            label_np = Text("(-1,1)", font_size=24, color=BLUE).next_to(arc_np, UL, buff=0.1)
            label_nn = Text("(-1,-1)", font_size=24, color=YELLOW).next_to(arc_nn, DL, buff=0.1)

            self.add(line1, line2, arc_pp, arc_pn, arc_np, arc_nn)
            self.add(label_pp, label_pn, label_np, label_nn)
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `always` | Call a method on a mobject every frame. |
    | `animate` | Used to animate the application of any method of `self`. |
    | `animation_overrides` |  |
    | `color` |  |
    | `depth` | The depth of the mobject. |
    | `fill_color` | If there are multiple colors (for gradient) this returns the first one |
    | `height` | The height of the mobject. |
    | `n_points_per_curve` |  |
    | `sheen_factor` |  |
    | `stroke_color` |  |
    | `width` | The width of the mobject. |

    Parameters:
    :   - **line1** ([*Line*](manim.mobject.geometry.line.Line.html#manim.mobject.geometry.line.Line "manim.mobject.geometry.line.Line"))
        - **line2** ([*Line*](manim.mobject.geometry.line.Line.html#manim.mobject.geometry.line.Line "manim.mobject.geometry.line.Line"))
        - **radius** (*float*)
        - **corner** (*Any*)
        - **kwargs** (*Any*)

    _original__init__(*line1*, *line2*, *radius*, *corner=(1, 1)*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **line1** ([*Line*](manim.mobject.geometry.line.Line.html#manim.mobject.geometry.line.Line "manim.mobject.geometry.line.Line"))
            - **line2** ([*Line*](manim.mobject.geometry.line.Line.html#manim.mobject.geometry.line.Line "manim.mobject.geometry.line.Line"))
            - **radius** (*float*)
            - **corner** (*Any*)
            - **kwargs** (*Any*)
