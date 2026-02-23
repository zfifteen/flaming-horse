<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.svg.brace.BraceLabel.html -->

# BraceLabel

Qualified name: `manim.mobject.svg.brace.BraceLabel`

class BraceLabel(*obj*, *text*, *brace_direction=array([ 0.*, *-1.*, *0.])*, *label_constructor=<class 'manim.mobject.text.tex_mobject.MathTex'>*, *font_size=48*, *buff=0.2*, *brace_config=None*, ***kwargs*)[[source]](../_modules/manim/mobject/svg/brace.html#BraceLabel)
:   Bases: [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")

    Create a brace with a label attached.

    Parameters:
    :   - **obj** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobject adjacent to which the brace is placed.
        - **text** (*str*) – The label text.
        - **brace_direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The direction of the brace. By default `DOWN`.
        - **label_constructor** (*type**[*[*SingleStringMathTex*](manim.mobject.text.tex_mobject.SingleStringMathTex.html#manim.mobject.text.tex_mobject.SingleStringMathTex "manim.mobject.text.tex_mobject.SingleStringMathTex") *|* [*Text*](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text")*]*) – A class or function used to construct a mobject representing
          the label. By default [`MathTex`](manim.mobject.text.tex_mobject.MathTex.html#manim.mobject.text.tex_mobject.MathTex "manim.mobject.text.tex_mobject.MathTex").
        - **font_size** (*float*) – The font size of the label, passed to the `label_constructor`.
        - **buff** (*float*) – The buffer between the mobject and the brace.
        - **brace_config** (*dict**[**str**,* *Any**]* *|* *None*) – Arguments to be passed to [`Brace`](manim.mobject.svg.brace.Brace.html#manim.mobject.svg.brace.Brace "manim.mobject.svg.brace.Brace").
        - **kwargs** (*Any*) – Additional arguments to be passed to [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject").

    Methods

    |  |  |
    | --- | --- |
    | `change_brace_label` |  |
    | `change_label` |  |
    | `creation_anim` |  |
    | `shift_brace` |  |

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

    _original__init__(*obj*, *text*, *brace_direction=array([ 0.*, *-1.*, *0.])*, *label_constructor=<class 'manim.mobject.text.tex_mobject.MathTex'>*, *font_size=48*, *buff=0.2*, *brace_config=None*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **obj** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **text** (*str*)
            - **brace_direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
            - **label_constructor** (*type**[*[*SingleStringMathTex*](manim.mobject.text.tex_mobject.SingleStringMathTex.html#manim.mobject.text.tex_mobject.SingleStringMathTex "manim.mobject.text.tex_mobject.SingleStringMathTex") *|* [*Text*](manim.mobject.text.text_mobject.Text.html#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text")*]*)
            - **font_size** (*float*)
            - **buff** (*float*)
            - **brace_config** (*dict**[**str**,* *Any**]* *|* *None*)
            - **kwargs** (*Any*)
