<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.growing.SpinInFromNothing.html -->

# SpinInFromNothing

Qualified name: `manim.animation.growing.SpinInFromNothing`

class SpinInFromNothing(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/growing.html#SpinInFromNothing)
:   Bases: [`GrowFromCenter`](manim.animation.growing.GrowFromCenter.html#manim.animation.growing.GrowFromCenter "manim.animation.growing.GrowFromCenter")

    Introduce an [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") spinning and growing it from its center.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobjects to be introduced.
        - **angle** (*float*) – The amount of spinning before mobject reaches its full size. E.g. 2*PI means
          that the object will do one full spin before being fully introduced.
        - **point_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*) – Initial color of the mobject before growing to its full size. Leave empty to match mobject’s color.
        - **kwargs** (*Any*)

    Examples

    Example: SpinInFromNothingExample

    [
    ](./SpinInFromNothingExample-1.mp4)

    ```python
    from manim import *

    class SpinInFromNothingExample(Scene):
        def construct(self):
            squares = [Square() for _ in range(3)]
            VGroup(*squares).set_x(0).arrange(buff=2)
            self.play(SpinInFromNothing(squares[0]))
            self.play(SpinInFromNothing(squares[1], angle=2 * PI))
            self.play(SpinInFromNothing(squares[2], point_color=RED))
    ```

    ```python
    class SpinInFromNothingExample(Scene):
        def construct(self):
            squares = [Square() for _ in range(3)]
            VGroup(*squares).set_x(0).arrange(buff=2)
            self.play(SpinInFromNothing(squares[0]))
            self.play(SpinInFromNothing(squares[1], angle=2 * PI))
            self.play(SpinInFromNothing(squares[2], point_color=RED))
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    _original__init__(*mobject*, *angle=1.5707963267948966*, *point_color=None*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **angle** (*float*)
            - **point_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*)
            - **kwargs** (*Any*)
