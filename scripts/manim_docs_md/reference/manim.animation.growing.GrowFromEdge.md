<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.growing.GrowFromEdge.html -->

# GrowFromEdge

Qualified name: `manim.animation.growing.GrowFromEdge`

class GrowFromEdge(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/growing.html#GrowFromEdge)
:   Bases: [`GrowFromPoint`](manim.animation.growing.GrowFromPoint.html#manim.animation.growing.GrowFromPoint "manim.animation.growing.GrowFromPoint")

    Introduce an [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") by growing it from one of its bounding box edges.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobjects to be introduced.
        - **edge** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The direction to seek bounding box edge of mobject.
        - **point_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*) – Initial color of the mobject before growing to its full size. Leave empty to match mobject’s color.
        - **kwargs** (*Any*)

    Examples

    Example: GrowFromEdgeExample

    [
    ](./GrowFromEdgeExample-1.mp4)

    ```python
    from manim import *

    class GrowFromEdgeExample(Scene):
        def construct(self):
            squares = [Square() for _ in range(4)]
            VGroup(*squares).set_x(0).arrange(buff=1)
            self.play(GrowFromEdge(squares[0], DOWN))
            self.play(GrowFromEdge(squares[1], RIGHT))
            self.play(GrowFromEdge(squares[2], UR))
            self.play(GrowFromEdge(squares[3], UP, point_color=RED))
    ```

    ```python
    class GrowFromEdgeExample(Scene):
        def construct(self):
            squares = [Square() for _ in range(4)]
            VGroup(*squares).set_x(0).arrange(buff=1)
            self.play(GrowFromEdge(squares[0], DOWN))
            self.play(GrowFromEdge(squares[1], RIGHT))
            self.play(GrowFromEdge(squares[2], UR))
            self.play(GrowFromEdge(squares[3], UP, point_color=RED))
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    _original__init__(*mobject*, *edge*, *point_color=None*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **edge** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
            - **point_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*)
            - **kwargs** (*Any*)
