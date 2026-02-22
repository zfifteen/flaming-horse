<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.growing.GrowArrow.html -->

# GrowArrow

Qualified name: `manim.animation.growing.GrowArrow`

class GrowArrow(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/growing.html#GrowArrow)
:   Bases: [`GrowFromPoint`](manim.animation.growing.GrowFromPoint.html#manim.animation.growing.GrowFromPoint "manim.animation.growing.GrowFromPoint")

    Introduce an [`Arrow`](manim.mobject.geometry.line.Arrow.html#manim.mobject.geometry.line.Arrow "manim.mobject.geometry.line.Arrow") by growing it from its start toward its tip.

    Parameters:
    :   - **arrow** ([*Arrow*](manim.mobject.geometry.line.Arrow.html#manim.mobject.geometry.line.Arrow "manim.mobject.geometry.line.Arrow")) – The arrow to be introduced.
        - **point_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*) – Initial color of the arrow before growing to its full size. Leave empty to match arrow’s color.
        - **kwargs** (*Any*)

    Examples

    Example: GrowArrowExample

    [
    ](./GrowArrowExample-1.mp4)

    ```python
    from manim import *

    class GrowArrowExample(Scene):
        def construct(self):
            arrows = [Arrow(2 * LEFT, 2 * RIGHT), Arrow(2 * DR, 2 * UL)]
            VGroup(*arrows).set_x(0).arrange(buff=2)
            self.play(GrowArrow(arrows[0]))
            self.play(GrowArrow(arrows[1], point_color=RED))
    ```

    ```python
    class GrowArrowExample(Scene):
        def construct(self):
            arrows = [Arrow(2 * LEFT, 2 * RIGHT), Arrow(2 * DR, 2 * UL)]
            VGroup(*arrows).set_x(0).arrange(buff=2)
            self.play(GrowArrow(arrows[0]))
            self.play(GrowArrow(arrows[1], point_color=RED))
    ```

    Methods

    |  |  |
    | --- | --- |
    | `create_starting_mobject` |  |

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    _original__init__(*arrow*, *point_color=None*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **arrow** ([*Arrow*](manim.mobject.geometry.line.Arrow.html#manim.mobject.geometry.line.Arrow "manim.mobject.geometry.line.Arrow"))
            - **point_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*)
            - **kwargs** (*Any*)
