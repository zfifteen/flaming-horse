<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.polygram.Triangle.html -->

# Triangle

Qualified name: `manim.mobject.geometry.polygram.Triangle`

class Triangle(***kwargs*)[[source]](../_modules/manim/mobject/geometry/polygram.html#Triangle)
:   Bases: [`RegularPolygon`](manim.mobject.geometry.polygram.RegularPolygon.html#manim.mobject.geometry.polygram.RegularPolygon "manim.mobject.geometry.polygram.RegularPolygon")

    An equilateral triangle.

    Parameters:
    :   **kwargs** (*Any*) – Additional arguments to be passed to [`RegularPolygon`](manim.mobject.geometry.polygram.RegularPolygon.html#manim.mobject.geometry.polygram.RegularPolygon "manim.mobject.geometry.polygram.RegularPolygon")

    Examples

    Example: TriangleExample

    ```python
    from manim import *

    class TriangleExample(Scene):
        def construct(self):
            triangle_1 = Triangle()
            triangle_2 = Triangle().scale(2).rotate(60*DEGREES)
            tri_group = Group(triangle_1, triangle_2).arrange(buff=1)
            self.add(tri_group)
    ```

    ```python
    class TriangleExample(Scene):
        def construct(self):
            triangle_1 = Triangle()
            triangle_2 = Triangle().scale(2).rotate(60*DEGREES)
            tri_group = Group(triangle_1, triangle_2).arrange(buff=1)
            self.add(tri_group)
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

    _original__init__(***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   **kwargs** (*Any*)

        Return type:
        :   None
