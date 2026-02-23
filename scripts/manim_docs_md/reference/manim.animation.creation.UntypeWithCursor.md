<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.creation.UntypeWithCursor.html -->

# UntypeWithCursor

Qualified name: `manim.animation.creation.UntypeWithCursor`

class UntypeWithCursor(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/creation.html#UntypeWithCursor)
:   Bases: [`TypeWithCursor`](manim.animation.creation.TypeWithCursor.html#manim.animation.creation.TypeWithCursor "manim.animation.creation.TypeWithCursor")

    Similar to [`RemoveTextLetterByLetter`](manim.animation.creation.RemoveTextLetterByLetter.html#manim.animation.creation.RemoveTextLetterByLetter "manim.animation.creation.RemoveTextLetterByLetter") , but with an additional cursor mobject at the end.

    Parameters:
    :   - **time_per_char** (*float*) – Frequency of appearance of the letters.
        - **cursor** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") *|* *None*) – [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") shown after the last added letter.
        - **buff** – Controls how far away the cursor is to the right of the last added letter.
        - **keep_cursor_y** – If `True`, the cursor’s y-coordinate is set to the center of the `Text` and remains the same throughout the animation. Otherwise, it is set to the center of the last added letter.
        - **leave_cursor_on** – Whether to show the cursor after the animation.
        - **tip::** (*..*) – This is currently only possible for class:~.Text and not for class:~.MathTex.
        - **text** ([*Text*](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text"))

    Examples

    Example: DeletingTextExample

    [
    ](./DeletingTextExample-1.mp4)

    ```python
    from manim import *

    class DeletingTextExample(Scene):
        def construct(self):
            text = Text("Deleting", color=PURPLE).scale(1.5).to_edge(LEFT)
            cursor = Rectangle(
                color = GREY_A,
                fill_color = GREY_A,
                fill_opacity = 1.0,
                height = 1.1,
                width = 0.5,
            ).move_to(text[0]) # Position the cursor

            self.play(UntypeWithCursor(text, cursor))
            self.play(Blink(cursor, blinks=2))
    ```

    ```python
    class DeletingTextExample(Scene):
        def construct(self):
            text = Text("Deleting", color=PURPLE).scale(1.5).to_edge(LEFT)
            cursor = Rectangle(
                color = GREY_A,
                fill_color = GREY_A,
                fill_opacity = 1.0,
                height = 1.1,
                width = 0.5,
            ).move_to(text[0]) # Position the cursor

            self.play(UntypeWithCursor(text, cursor))
            self.play(Blink(cursor, blinks=2))
    ```

    References: [`Blink`](manim.animation.indication.Blink.html#manim.animation.indication.Blink "manim.animation.indication.Blink")

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    _original__init__(*text*, *cursor=None*, *time_per_char=0.1*, *reverse_rate_function=True*, *introducer=False*, *remover=True*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **text** ([*Text*](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text"))
            - **cursor** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") *|* *None*)
            - **time_per_char** (*float*)

        Return type:
        :   None
