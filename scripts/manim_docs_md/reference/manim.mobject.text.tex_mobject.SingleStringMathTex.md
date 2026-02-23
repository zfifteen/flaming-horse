<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.text.tex_mobject.SingleStringMathTex.html -->

# SingleStringMathTex

Qualified name: `manim.mobject.text.tex\_mobject.SingleStringMathTex`

class SingleStringMathTex(*tex_string*, *stroke_width=0*, *should_center=True*, *height=None*, *organize_left_to_right=False*, *tex_environment='align*'*, *tex_template=None*, *font_size=48*, *color=None*, ***kwargs*)[[source]](../_modules/manim/mobject/text/tex_mobject.html#SingleStringMathTex)
:   Bases: [`SVGMobject`](manim.mobject.svg.svg_mobject.SVGMobject.html#manim.mobject.svg.svg_mobject.SVGMobject "manim.mobject.svg.svg_mobject.SVGMobject")

    Elementary building block for rendering text with LaTeX.

    Tests

    Check that creating a [`SingleStringMathTex`](#manim.mobject.text.tex_mobject.SingleStringMathTex "manim.mobject.text.tex_mobject.SingleStringMathTex") object works:

    ```python
    >>> SingleStringMathTex('Test')
    SingleStringMathTex('Test')
    ```

    Methods

    |  |  |
    | --- | --- |
    | `get_tex_string` |  |
    | [`init_colors`](#manim.mobject.text.tex_mobject.SingleStringMathTex.init_colors "manim.mobject.text.tex_mobject.SingleStringMathTex.init_colors") | Initializes the colors. |

    Attributes

    |  |  |
    | --- | --- |
    | `always` | Call a method on a mobject every frame. |
    | `animate` | Used to animate the application of any method of `self`. |
    | `animation_overrides` |  |
    | `color` |  |
    | `depth` | The depth of the mobject. |
    | `fill_color` | If there are multiple colors (for gradient) this returns the first one |
    | [`font_size`](#manim.mobject.text.tex_mobject.SingleStringMathTex.font_size "manim.mobject.text.tex_mobject.SingleStringMathTex.font_size") | The font size of the tex mobject. |
    | `hash_seed` | A unique hash representing the result of the generated mobject points. |
    | `height` | The height of the mobject. |
    | `n_points_per_curve` |  |
    | `sheen_factor` |  |
    | `stroke_color` |  |
    | `width` | The width of the mobject. |

    Parameters:
    :   - **tex_string** (*str*)
        - **stroke_width** (*float*)
        - **should_center** (*bool*)
        - **height** (*float* *|* *None*)
        - **organize_left_to_right** (*bool*)
        - **tex_environment** (*str* *|* *None*)
        - **tex_template** ([*TexTemplate*](manim.utils.tex.TexTemplate.html#manim.utils.tex.TexTemplate "manim.utils.tex.TexTemplate") *|* *None*)
        - **font_size** (*float*)
        - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*)
        - **kwargs** (*Any*)

    _original__init__(*tex_string*, *stroke_width=0*, *should_center=True*, *height=None*, *organize_left_to_right=False*, *tex_environment='align*'*, *tex_template=None*, *font_size=48*, *color=None*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **tex_string** (*str*)
            - **stroke_width** (*float*)
            - **should_center** (*bool*)
            - **height** (*float* *|* *None*)
            - **organize_left_to_right** (*bool*)
            - **tex_environment** (*str* *|* *None*)
            - **tex_template** ([*TexTemplate*](manim.utils.tex.TexTemplate.html#manim.utils.tex.TexTemplate "manim.utils.tex.TexTemplate") *|* *None*)
            - **font_size** (*float*)
            - **color** (*TypeAliasForwardRef**(**'~manim.utils.color.core.ParsableManimColor'**)* *|* *None*)
            - **kwargs** (*Any*)

    _remove_stray_braces(*tex*)[[source]](../_modules/manim/mobject/text/tex_mobject.html#SingleStringMathTex._remove_stray_braces)
    :   Makes [`MathTex`](manim.mobject.text.tex_mobject.MathTex.html#manim.mobject.text.tex_mobject.MathTex "manim.mobject.text.tex_mobject.MathTex") resilient to unmatched braces.

        This is important when the braces in the TeX code are spread over
        multiple arguments as in, e.g., `MathTex(r"e^{i", r"\tau} = 1")`.

        Parameters:
        :   **tex** (*str*)

        Return type:
        :   str

    property font_size: float
    :   The font size of the tex mobject.

    init_colors(*propagate_colors=True*)[[source]](../_modules/manim/mobject/text/tex_mobject.html#SingleStringMathTex.init_colors)
    :   Initializes the colors.

        Gets called upon creation. This is an empty method that can be implemented by
        subclasses.

        Parameters:
        :   **propagate_colors** (*bool*)

        Return type:
        :   *Self*
