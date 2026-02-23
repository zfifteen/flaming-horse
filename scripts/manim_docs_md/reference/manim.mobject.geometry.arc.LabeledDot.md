<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.arc.LabeledDot.html -->

# LabeledDot

Qualified name: `manim.mobject.geometry.arc.LabeledDot`

class LabeledDot(*label*, *radius=None*, *buff=0.1*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/arc.html#LabeledDot)
:   Bases: [`Dot`](manim.mobject.geometry.arc.Dot.html#manim.mobject.geometry.arc.Dot "manim.mobject.geometry.arc.Dot")

    A [`Dot`](manim.mobject.geometry.arc.Dot.html#manim.mobject.geometry.arc.Dot "manim.mobject.geometry.arc.Dot") containing a label in its center.

    Parameters:
    :   - **label** (*str* *|* [*SingleStringMathTex*](manim.mobject.text.tex_mobject.SingleStringMathTex.html#manim.mobject.text.tex_mobject.SingleStringMathTex "manim.mobject.text.tex_mobject.SingleStringMathTex") *|* [*Text*](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text") *|* [*Tex*](manim.mobject.text.tex_mobject.Tex.html#manim.mobject.text.tex_mobject.Tex "manim.mobject.text.tex_mobject.Tex")) – The label of the [`Dot`](manim.mobject.geometry.arc.Dot.html#manim.mobject.geometry.arc.Dot "manim.mobject.geometry.arc.Dot"). This is rendered as [`MathTex`](manim.mobject.text.tex_mobject.MathTex.html#manim.mobject.text.tex_mobject.MathTex "manim.mobject.text.tex_mobject.MathTex")
          by default (i.e., when passing a `str`), but other classes
          representing rendered strings like [`Text`](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text") or [`Tex`](manim.mobject.text.tex_mobject.Tex.html#manim.mobject.text.tex_mobject.Tex "manim.mobject.text.tex_mobject.Tex")
          can be passed as well.
        - **radius** (*float* *|* *None*) – The radius of the [`Dot`](manim.mobject.geometry.arc.Dot.html#manim.mobject.geometry.arc.Dot "manim.mobject.geometry.arc.Dot"). If provided, the `buff` is ignored.
          If `None` (the default), the radius is calculated based on the size
          of the `label` and the `buff`.
        - **buff** (*float*)
        - **kwargs** (*Any*)

    Examples

    Example: SeveralLabeledDots

    ```python
    from manim import *

    class SeveralLabeledDots(Scene):
        def construct(self):
            sq = Square(fill_color=RED, fill_opacity=1)
            self.add(sq)
            dot1 = LabeledDot(Tex("42", color=RED))
            dot2 = LabeledDot(MathTex("a", color=GREEN))
            dot3 = LabeledDot(Text("ii", color=BLUE))
            dot4 = LabeledDot("3")
            dot1.next_to(sq, UL)
            dot2.next_to(sq, UR)
            dot3.next_to(sq, DL)
            dot4.next_to(sq, DR)
            self.add(dot1, dot2, dot3, dot4)
    ```

    ```python
    class SeveralLabeledDots(Scene):
        def construct(self):
            sq = Square(fill_color=RED, fill_opacity=1)
            self.add(sq)
            dot1 = LabeledDot(Tex("42", color=RED))
            dot2 = LabeledDot(MathTex("a", color=GREEN))
            dot3 = LabeledDot(Text("ii", color=BLUE))
            dot4 = LabeledDot("3")
            dot1.next_to(sq, UL)
            dot2.next_to(sq, UR)
            dot3.next_to(sq, DL)
            dot4.next_to(sq, DR)
            self.add(dot1, dot2, dot3, dot4)
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

    _original__init__(*label*, *radius=None*, *buff=0.1*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **label** (*str* *|* [*SingleStringMathTex*](manim.mobject.text.tex_mobject.SingleStringMathTex.html#manim.mobject.text.tex_mobject.SingleStringMathTex "manim.mobject.text.tex_mobject.SingleStringMathTex") *|* [*Text*](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text") *|* [*Tex*](manim.mobject.text.tex_mobject.Tex.html#manim.mobject.text.tex_mobject.Tex "manim.mobject.text.tex_mobject.Tex"))
            - **radius** (*float* *|* *None*)
            - **buff** (*float*)
            - **kwargs** (*Any*)

        Return type:
        :   None
