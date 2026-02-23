<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.growing.GrowFromCenter.html -->

# GrowFromCenter

Qualified name: `manim.animation.growing.GrowFromCenter`

class GrowFromCenter(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/growing.html#GrowFromCenter)
:   Bases: [`GrowFromPoint`](manim.animation.growing.GrowFromPoint.html#manim.animation.growing.GrowFromPoint "manim.animation.growing.GrowFromPoint")

    Introduce an [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") by growing it from its center.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobjects to be introduced.
        - **point_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*) – Initial color of the mobject before growing to its full size. Leave empty to match mobject’s color.
        - **kwargs** (*Any*)

    Examples

    Example: GrowFromCenterExample

    [
    ](./GrowFromCenterExample-1.mp4)

    ```python
    from manim import *

    class GrowFromCenterExample(Scene):
        def construct(self):
            squares = [Square() for _ in range(2)]
            VGroup(*squares).set_x(0).arrange(buff=2)
            self.play(GrowFromCenter(squares[0]))
            self.play(GrowFromCenter(squares[1], point_color=RED))
    ```

    ```python
    class GrowFromCenterExample(Scene):
        def construct(self):
            squares = [Square() for _ in range(2)]
            VGroup(*squares).set_x(0).arrange(buff=2)
            self.play(GrowFromCenter(squares[0]))
            self.play(GrowFromCenter(squares[1], point_color=RED))
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    _original__init__(*mobject*, *point_color=None*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **point_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*)
            - **kwargs** (*Any*)
