<!-- source: https://docs.manim.community/en/stable/reference/manim.utils.debug.html -->

# debug

Debugging utilities.

Functions

index_labels(*mobject*, *label_height=0.15*, *background_stroke_width=5*, *background_stroke_color=ManimColor('#000000')*, ***kwargs*)[[source]](../_modules/manim/utils/debug.html#index_labels)
:   Returns a [`VGroup`](manim.mobject.types.vectorized_mobject.VGroup.html#manim.mobject.types.vectorized_mobject.VGroup "manim.mobject.types.vectorized_mobject.VGroup") of [`Integer`](manim.mobject.text.numbers.Integer.html#manim.mobject.text.numbers.Integer "manim.mobject.text.numbers.Integer") mobjects
    that shows the index of each submobject.

    Useful for working with parts of complicated mobjects.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobject that will have its submobjects labelled.
        - **label_height** (*float*) – The height of the labels, by default 0.15.
        - **background_stroke_width** (*float*) – The stroke width of the outline of the labels, by default 5.
        - **background_stroke_color** ([*ManimColor*](manim.utils.color.core.ManimColor.html#manim.utils.color.core.ManimColor "manim.utils.color.core.ManimColor")) – The stroke color of the outline of labels.
        - **kwargs** (*Any*) – Additional parameters to be passed into the :class`~.Integer`
          mobjects used to construct the labels.

    Return type:
    :   [*VGroup*](manim.mobject.types.vectorized_mobject.VGroup.html#manim.mobject.types.vectorized_mobject.VGroup "manim.mobject.types.vectorized_mobject.VGroup")

    Examples

    Example: IndexLabelsExample

    ```python
    from manim import *

    class IndexLabelsExample(Scene):
        def construct(self):
            text = MathTex(
                "\\frac{d}{dx}f(x)g(x)=",
                "f(x)\\frac{d}{dx}g(x)",
                "+",
                "g(x)\\frac{d}{dx}f(x)",
            )

            #index the fist term in the MathTex mob
            indices = index_labels(text[0])

            text[0][1].set_color(PURPLE_B)
            text[0][8:12].set_color(DARK_BLUE)

            self.add(text, indices)
    ```

    ```python
    class IndexLabelsExample(Scene):
        def construct(self):
            text = MathTex(
                "\\frac{d}{dx}f(x)g(x)=",
                "f(x)\\frac{d}{dx}g(x)",
                "+",
                "g(x)\\frac{d}{dx}f(x)",
            )

            #index the fist term in the MathTex mob
            indices = index_labels(text[0])

            text[0][1].set_color(PURPLE_B)
            text[0][8:12].set_color(DARK_BLUE)

            self.add(text, indices)
    ```

print_family(*mobject*, *n_tabs=0*)[[source]](../_modules/manim/utils/debug.html#print_family)
:   For debugging purposes

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **n_tabs** (*int*)

    Return type:
    :   None
