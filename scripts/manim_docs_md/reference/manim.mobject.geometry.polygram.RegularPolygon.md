<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.polygram.RegularPolygon.html -->

# RegularPolygon

Qualified name: `manim.mobject.geometry.polygram.RegularPolygon`

class RegularPolygon(*n=6*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/polygram.html#RegularPolygon)
:   Bases: [`RegularPolygram`](manim.mobject.geometry.polygram.RegularPolygram.html#manim.mobject.geometry.polygram.RegularPolygram "manim.mobject.geometry.polygram.RegularPolygram")

    An n-sided regular [`Polygon`](manim.mobject.geometry.polygram.Polygon.html#manim.mobject.geometry.polygram.Polygon "manim.mobject.geometry.polygram.Polygon").

    Parameters:
    :   - **n** (*int*) – The number of sides of the [`RegularPolygon`](#manim.mobject.geometry.polygram.RegularPolygon "manim.mobject.geometry.polygram.RegularPolygon").
        - **kwargs** (*Any*) – Forwarded to the parent constructor.

    Examples

    Example: RegularPolygonExample

    ```python
    from manim import *

    class RegularPolygonExample(Scene):
        def construct(self):
            poly_1 = RegularPolygon(n=6)
            poly_2 = RegularPolygon(n=6, start_angle=30*DEGREES, color=GREEN)
            poly_3 = RegularPolygon(n=10, color=RED)

            poly_group = Group(poly_1, poly_2, poly_3).scale(1.5).arrange(buff=1)
            self.add(poly_group)
    ```

    ```python
    class RegularPolygonExample(Scene):
        def construct(self):
            poly_1 = RegularPolygon(n=6)
            poly_2 = RegularPolygon(n=6, start_angle=30*DEGREES, color=GREEN)
            poly_3 = RegularPolygon(n=10, color=RED)

            poly_group = Group(poly_1, poly_2, poly_3).scale(1.5).arrange(buff=1)
            self.add(poly_group)
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

    _original__init__(*n=6*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **n** (*int*)
            - **kwargs** (*Any*)

        Return type:
        :   None
