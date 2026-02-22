<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.creation.Unwrite.html -->

# Unwrite

Qualified name: `manim.animation.creation.Unwrite`

class Unwrite(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/creation.html#Unwrite)
:   Bases: [`Write`](manim.animation.creation.Write.html#manim.animation.creation.Write "manim.animation.creation.Write")

    Simulate erasing by hand a [`Text`](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text") or a [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject").

    Parameters:
    :   - **reverse** (*bool*) – Set True to have the animation start erasing from the last submobject first.
        - **vmobject** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject"))
        - **rate_func** (*Callable**[**[**float**]**,* *float**]*)

    Examples

    Example: UnwriteReverseTrue

    [
    ](./UnwriteReverseTrue-1.mp4)

    ```python
    from manim import *

    class UnwriteReverseTrue(Scene):
        def construct(self):
            text = Tex("Alice and Bob").scale(3)
            self.add(text)
            self.play(Unwrite(text))
    ```

    ```python
    class UnwriteReverseTrue(Scene):
        def construct(self):
            text = Tex("Alice and Bob").scale(3)
            self.add(text)
            self.play(Unwrite(text))
    ```

    Example: UnwriteReverseFalse

    [
    ](./UnwriteReverseFalse-1.mp4)

    ```python
    from manim import *

    class UnwriteReverseFalse(Scene):
        def construct(self):
            text = Tex("Alice and Bob").scale(3)
            self.add(text)
            self.play(Unwrite(text, reverse=False))
    ```

    ```python
    class UnwriteReverseFalse(Scene):
        def construct(self):
            text = Tex("Alice and Bob").scale(3)
            self.add(text)
            self.play(Unwrite(text, reverse=False))
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    _original__init__(*vmobject*, *rate_func=<function linear>*, *reverse=True*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **vmobject** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject"))
            - **rate_func** (*Callable**[**[**float**]**,* *float**]*)
            - **reverse** (*bool*)

        Return type:
        :   None
