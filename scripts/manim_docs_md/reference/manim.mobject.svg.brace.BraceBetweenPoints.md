<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.svg.brace.BraceBetweenPoints.html -->

# BraceBetweenPoints

Qualified name: `manim.mobject.svg.brace.BraceBetweenPoints`

class BraceBetweenPoints(*point_1*, *point_2*, *direction=array([0., 0., 0.])*, ***kwargs*)[[source]](../_modules/manim/mobject/svg/brace.html#BraceBetweenPoints)
:   Bases: [`Brace`](manim.mobject.svg.brace.Brace.html#manim.mobject.svg.brace.Brace "manim.mobject.svg.brace.Brace")

    Similar to Brace, but instead of taking a mobject it uses 2
    points to place the brace.

    A fitting direction for the brace is
    computed, but it still can be manually overridden.
    If the points go from left to right, the brace is drawn from below.
    Swapping the points places the brace on the opposite side.

    Parameters:
    :   - **point_1** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike")) – The first point.
        - **point_2** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike")) – The second point.
        - **direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The direction from which the brace faces towards the points.
        - **kwargs** (*Any*)

    Examples

    Example: BraceBPExample

    [
    ](./BraceBPExample-1.mp4)

    ```python
    from manim import *

    class BraceBPExample(Scene):
        def construct(self):
            p1 = [0,0,0]
            p2 = [1,2,0]
            brace = BraceBetweenPoints(p1,p2)
            self.play(Create(NumberPlane()))
            self.play(Create(brace))
            self.wait(2)
    ```

    ```python
    class BraceBPExample(Scene):
        def construct(self):
            p1 = [0,0,0]
            p2 = [1,2,0]
            brace = BraceBetweenPoints(p1,p2)
            self.play(Create(NumberPlane()))
            self.play(Create(brace))
            self.wait(2)
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

    _original__init__(*point_1*, *point_2*, *direction=array([0., 0., 0.])*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **point_1** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike"))
            - **point_2** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike"))
            - **direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
            - **kwargs** (*Any*)
