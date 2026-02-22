<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.transform.FadeToColor.html -->

# FadeToColor

Qualified name: `manim.animation.transform.FadeToColor`

class FadeToColor(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/transform.html#FadeToColor)
:   Bases: [`ApplyMethod`](manim.animation.transform.ApplyMethod.html#manim.animation.transform.ApplyMethod "manim.animation.transform.ApplyMethod")

    Animation that changes color of a mobject.

    Examples

    Example: FadeToColorExample

    [
    ](./FadeToColorExample-1.mp4)

    ```python
    from manim import *

    class FadeToColorExample(Scene):
        def construct(self):
            self.play(FadeToColor(Text("Hello World!"), color=RED))
    ```

    ```python
    class FadeToColorExample(Scene):
        def construct(self):
            self.play(FadeToColor(Text("Hello World!"), color=RED))
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **color** (*str*)

    _original__init__(*mobject*, *color*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **color** (*str*)

        Return type:
        :   None
