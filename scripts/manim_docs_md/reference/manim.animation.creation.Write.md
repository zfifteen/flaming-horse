<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.creation.Write.html -->

# Write

Qualified name: `manim.animation.creation.Write`

class Write(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/creation.html#Write)
:   Bases: [`DrawBorderThenFill`](manim.animation.creation.DrawBorderThenFill.html#manim.animation.creation.DrawBorderThenFill "manim.animation.creation.DrawBorderThenFill")

    Simulate hand-writing a [`Text`](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text") or hand-drawing a [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject").

    Examples

    Example: ShowWrite

    [
    ](./ShowWrite-1.mp4)

    ```python
    from manim import *

    class ShowWrite(Scene):
        def construct(self):
            self.play(Write(Text("Hello", font_size=144)))
    ```

    ```python
    class ShowWrite(Scene):
        def construct(self):
            self.play(Write(Text("Hello", font_size=144)))
    ```

    Example: ShowWriteReversed

    [
    ](./ShowWriteReversed-1.mp4)

    ```python
    from manim import *

    class ShowWriteReversed(Scene):
        def construct(self):
            self.play(Write(Text("Hello", font_size=144), reverse=True, remover=False))
    ```

    ```python
    class ShowWriteReversed(Scene):
        def construct(self):
            self.play(Write(Text("Hello", font_size=144), reverse=True, remover=False))
    ```

    Tests

    Check that creating empty [`Write`](#manim.animation.creation.Write "manim.animation.creation.Write") animations works:

    ```python
    >>> from manim import Write, Text
    >>> Write(Text(''))
    Write(Text(''))
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`begin`](#manim.animation.creation.Write.begin "manim.animation.creation.Write.begin") | Begin the animation. |
    | [`finish`](#manim.animation.creation.Write.finish "manim.animation.creation.Write.finish") | Finish the animation. |
    | `reverse_submobjects` |  |

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    Parameters:
    :   - **vmobject** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") *|* *OpenGLVMobject*)
        - **rate_func** (*Callable**[**[**float**]**,* *float**]*)
        - **reverse** (*bool*)

    _original__init__(*vmobject*, *rate_func=<function linear>*, *reverse=False*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **vmobject** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") *|* *OpenGLVMobject*)
            - **rate_func** (*Callable**[**[**float**]**,* *float**]*)
            - **reverse** (*bool*)

        Return type:
        :   None

    begin()[[source]](../_modules/manim/animation/creation.html#Write.begin)
    :   Begin the animation.

        This method is called right as an animation is being played. As much
        initialization as possible, especially any mobject copying, should live in this
        method.

        Return type:
        :   None

    finish()[[source]](../_modules/manim/animation/creation.html#Write.finish)
    :   Finish the animation.

        This method gets called when the animation is over.

        Return type:
        :   None
