<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.creation.DrawBorderThenFill.html -->

# DrawBorderThenFill

Qualified name: `manim.animation.creation.DrawBorderThenFill`

class DrawBorderThenFill(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/creation.html#DrawBorderThenFill)
:   Bases: [`Animation`](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation")

    Draw the border first and then show the fill.

    Examples

    Example: ShowDrawBorderThenFill

    [
    ](./ShowDrawBorderThenFill-1.mp4)

    ```python
    from manim import *

    class ShowDrawBorderThenFill(Scene):
        def construct(self):
            self.play(DrawBorderThenFill(Square(fill_opacity=1, fill_color=ORANGE)))
    ```

    ```python
    class ShowDrawBorderThenFill(Scene):
        def construct(self):
            self.play(DrawBorderThenFill(Square(fill_opacity=1, fill_color=ORANGE)))
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`begin`](#manim.animation.creation.DrawBorderThenFill.begin "manim.animation.creation.DrawBorderThenFill.begin") | Begin the animation. |
    | [`get_all_mobjects`](#manim.animation.creation.DrawBorderThenFill.get_all_mobjects "manim.animation.creation.DrawBorderThenFill.get_all_mobjects") | Get all mobjects involved in the animation. |
    | `get_outline` |  |
    | `get_stroke_color` |  |
    | `interpolate_submobject` |  |

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    Parameters:
    :   - **vmobject** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") *|* *OpenGLVMobject*)
        - **run_time** (*float*)
        - **rate_func** (*Callable**[**[**float**]**,* *float**]*)
        - **stroke_width** (*float*)
        - **stroke_color** (*str*)
        - **introducer** (*bool*)

    _original__init__(*vmobject*, *run_time=2*, *rate_func=<function double_smooth>*, *stroke_width=2*, *stroke_color=None*, *introducer=True*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **vmobject** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") *|* *OpenGLVMobject*)
            - **run_time** (*float*)
            - **rate_func** (*Callable**[**[**float**]**,* *float**]*)
            - **stroke_width** (*float*)
            - **stroke_color** (*str*)
            - **introducer** (*bool*)

        Return type:
        :   None

    begin()[[source]](../_modules/manim/animation/creation.html#DrawBorderThenFill.begin)
    :   Begin the animation.

        This method is called right as an animation is being played. As much
        initialization as possible, especially any mobject copying, should live in this
        method.

        Return type:
        :   None

    get_all_mobjects()[[source]](../_modules/manim/animation/creation.html#DrawBorderThenFill.get_all_mobjects)
    :   Get all mobjects involved in the animation.

        Ordering must match the ordering of arguments to interpolate_submobject

        Returns:
        :   The sequence of mobjects.

        Return type:
        :   Sequence[[Mobject](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")]
