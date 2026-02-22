<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.growing.GrowFromPoint.html -->

# GrowFromPoint

Qualified name: `manim.animation.growing.GrowFromPoint`

class GrowFromPoint(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/growing.html#GrowFromPoint)
:   Bases: [`Transform`](manim.animation.transform.Transform.html#manim.animation.transform.Transform "manim.animation.transform.Transform")

    Introduce an [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") by growing it from a point.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobjects to be introduced.
        - **point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike")) – The point from which the mobject grows.
        - **point_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*) – Initial color of the mobject before growing to its full size. Leave empty to match mobject’s color.
        - **kwargs** (*Any*)

    Examples

    Example: GrowFromPointExample

    [
    ](./GrowFromPointExample-1.mp4)

    ```python
    from manim import *

    class GrowFromPointExample(Scene):
        def construct(self):
            dot = Dot(3 * UR, color=GREEN)
            squares = [Square() for _ in range(4)]
            VGroup(*squares).set_x(0).arrange(buff=1)
            self.add(dot)
            self.play(GrowFromPoint(squares[0], ORIGIN))
            self.play(GrowFromPoint(squares[1], [-2, 2, 0]))
            self.play(GrowFromPoint(squares[2], [3, -2, 0], RED))
            self.play(GrowFromPoint(squares[3], dot, dot.get_color()))
    ```

    ```python
    class GrowFromPointExample(Scene):
        def construct(self):
            dot = Dot(3 * UR, color=GREEN)
            squares = [Square() for _ in range(4)]
            VGroup(*squares).set_x(0).arrange(buff=1)
            self.add(dot)
            self.play(GrowFromPoint(squares[0], ORIGIN))
            self.play(GrowFromPoint(squares[1], [-2, 2, 0]))
            self.play(GrowFromPoint(squares[2], [3, -2, 0], RED))
            self.play(GrowFromPoint(squares[3], dot, dot.get_color()))
    ```

    Methods

    |  |  |
    | --- | --- |
    | `create_starting_mobject` |  |
    | `create_target` |  |

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    _original__init__(*mobject*, *point*, *point_color=None*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike"))
            - **point_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*)
            - **kwargs** (*Any*)
