<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.TangentLine.html -->

# TangentLine

Qualified name: `manim.mobject.geometry.line.TangentLine`

class TangentLine(*vmob*, *alpha*, *length=1*, *d_alpha=1e-06*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/line.html#TangentLine)
:   Bases: [`Line`](manim.mobject.geometry.line.Line.html#manim.mobject.geometry.line.Line "manim.mobject.geometry.line.Line")

    Constructs a line tangent to a [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") at a specific point.

    Parameters:
    :   - **vmob** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")) – The VMobject on which the tangent line is drawn.
        - **alpha** (*float*) – How far along the shape that the line will be constructed. range: 0-1.
        - **length** (*float*) – Length of the tangent line.
        - **d_alpha** (*float*) – The `dx` value
        - **kwargs** (*Any*) – Additional arguments to be passed to [`Line`](manim.mobject.geometry.line.Line.html#manim.mobject.geometry.line.Line "manim.mobject.geometry.line.Line")

    See also

    [`point_from_proportion()`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject.point_from_proportion "manim.mobject.types.vectorized_mobject.VMobject.point_from_proportion")

    Examples

    Example: TangentLineExample

    ```python
    from manim import *

    class TangentLineExample(Scene):
        def construct(self):
            circle = Circle(radius=2)
            line_1 = TangentLine(circle, alpha=0.0, length=4, color=BLUE_D) # right
            line_2 = TangentLine(circle, alpha=0.4, length=4, color=GREEN) # top left
            self.add(circle, line_1, line_2)
    ```

    ```python
    class TangentLineExample(Scene):
        def construct(self):
            circle = Circle(radius=2)
            line_1 = TangentLine(circle, alpha=0.0, length=4, color=BLUE_D) # right
            line_2 = TangentLine(circle, alpha=0.4, length=4, color=GREEN) # top left
            self.add(circle, line_1, line_2)
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

    _original__init__(*vmob*, *alpha*, *length=1*, *d_alpha=1e-06*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **vmob** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject"))
            - **alpha** (*float*)
            - **length** (*float*)
            - **d_alpha** (*float*)
            - **kwargs** (*Any*)

        Return type:
        :   None
