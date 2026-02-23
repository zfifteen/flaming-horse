<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.transform.ShrinkToCenter.html -->

# ShrinkToCenter

Qualified name: `manim.animation.transform.ShrinkToCenter`

class ShrinkToCenter(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/transform.html#ShrinkToCenter)
:   Bases: [`ScaleInPlace`](manim.animation.transform.ScaleInPlace.html#manim.animation.transform.ScaleInPlace "manim.animation.transform.ScaleInPlace")

    Animation that makes a mobject shrink to center.

    Examples

    Example: ShrinkToCenterExample

    [
    ](./ShrinkToCenterExample-1.mp4)

    ```python
    from manim import *

    class ShrinkToCenterExample(Scene):
        def construct(self):
            self.play(ShrinkToCenter(Text("Hello World!")))
    ```

    ```python
    class ShrinkToCenterExample(Scene):
        def construct(self):
            self.play(ShrinkToCenter(Text("Hello World!")))
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    Parameters:
    :   **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))

    _original__init__(*mobject*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))

        Return type:
        :   None
