<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.svg.brace.BraceText.html -->

# BraceText

Qualified name: `manim.mobject.svg.brace.BraceText`

class BraceText(*obj*, *text*, *label_constructor=<class 'manim.mobject.text.text_mobject.Text'>*, ***kwargs*)[[source]](../_modules/manim/mobject/svg/brace.html#BraceText)
:   Bases: [`BraceLabel`](manim.mobject.svg.brace.BraceLabel.html#manim.mobject.svg.brace.BraceLabel "manim.mobject.svg.brace.BraceLabel")

    Create a brace with a text label attached.

    Parameters:
    :   - **obj** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobject adjacent to which the brace is placed.
        - **text** (*str*) – The label text.
        - **brace_direction** – The direction of the brace. By default `DOWN`.
        - **label_constructor** (*type**[*[*SingleStringMathTex*](manim.mobject.text.tex_mobject.SingleStringMathTex.html#manim.mobject.text.tex_mobject.SingleStringMathTex "manim.mobject.text.tex_mobject.SingleStringMathTex") *|* [*Text*](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text")*]*) – A class or function used to construct a mobject representing
          the label. By default [`Text`](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text").
        - **font_size** – The font size of the label, passed to the `label_constructor`.
        - **buff** – The buffer between the mobject and the brace.
        - **brace_config** – Arguments to be passed to [`Brace`](manim.mobject.svg.brace.Brace.html#manim.mobject.svg.brace.Brace "manim.mobject.svg.brace.Brace").
        - **kwargs** (*Any*) – Additional arguments to be passed to [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject").

    Examples

    Example: BraceTextExample

    ```python
    from manim import *

    class BraceTextExample(Scene):
        def construct(self):
            s1 = Square().move_to(2*LEFT)
            self.add(s1)
            br1 = BraceText(s1, "Label")
            self.add(br1)

            s2 = Square().move_to(2*RIGHT)
            self.add(s2)
            br2 = BraceText(s2, "Label")

            br2.change_label("new")
            self.add(br2)
            self.wait(0.1)
    ```

    ```python
    class BraceTextExample(Scene):
        def construct(self):
            s1 = Square().move_to(2*LEFT)
            self.add(s1)
            br1 = BraceText(s1, "Label")
            self.add(br1)

            s2 = Square().move_to(2*RIGHT)
            self.add(s2)
            br2 = BraceText(s2, "Label")

            br2.change_label("new")
            self.add(br2)
            self.wait(0.1)
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `always` | Call a method on a mobject every frame. |
    | `animate` | Used to animate the application of any method of `self`. |
    | `animation_overrides` |  |
    | `color` |  |
    | `depth` | The depth of the mobject. |
    | `fill_color` | If there are multiple colors (for gradient) this returns the first one |
    | `height` | The height of the mobject. |
    | `n_points_per_curve` |  |
    | `sheen_factor` |  |
    | `stroke_color` |  |
    | `width` | The width of the mobject. |

    _original__init__(*obj*, *text*, *label_constructor=<class 'manim.mobject.text.text_mobject.Text'>*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **obj** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **text** (*str*)
            - **label_constructor** (*type**[*[*SingleStringMathTex*](manim.mobject.text.tex_mobject.SingleStringMathTex.html#manim.mobject.text.tex_mobject.SingleStringMathTex "manim.mobject.text.tex_mobject.SingleStringMathTex") *|* [*Text*](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text")*]*)
            - **kwargs** (*Any*)
