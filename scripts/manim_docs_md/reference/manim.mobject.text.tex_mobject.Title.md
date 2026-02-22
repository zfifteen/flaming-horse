<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.text.tex_mobject.Title.html -->

# Title

Qualified name: `manim.mobject.text.tex\_mobject.Title`

class Title(**text_parts*, *include_underline=True*, *match_underline_width_to_text=False*, *underline_buff=0.25*, ***kwargs*)[[source]](../_modules/manim/mobject/text/tex_mobject.html#Title)
:   Bases: [`Tex`](manim.mobject.text.tex_mobject.Tex.html#manim.mobject.text.tex_mobject.Tex "manim.mobject.text.tex_mobject.Tex")

    A mobject representing an underlined title.

    Examples

    Example: TitleExample

    ```python
    from manim import *

    import manim

    class TitleExample(Scene):
        def construct(self):
            banner = ManimBanner()
            title = Title(f"Manim version {manim.__version__}")
            self.add(banner, title)
    ```

    ```python
    import manim

    class TitleExample(Scene):
        def construct(self):
            banner = ManimBanner()
            title = Title(f"Manim version {manim.__version__}")
            self.add(banner, title)
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
    | `font_size` | The font size of the tex mobject. |
    | `hash_seed` | A unique hash representing the result of the generated mobject points. |
    | `height` | The height of the mobject. |
    | `n_points_per_curve` |  |
    | `sheen_factor` |  |
    | `stroke_color` |  |
    | `width` | The width of the mobject. |

    Parameters:
    :   - **text_parts** (*str*)
        - **include_underline** (*bool*)
        - **match_underline_width_to_text** (*bool*)
        - **underline_buff** (*float*)
        - **kwargs** (*Any*)

    _original__init__(**text_parts*, *include_underline=True*, *match_underline_width_to_text=False*, *underline_buff=0.25*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **text_parts** (*str*)
            - **include_underline** (*bool*)
            - **match_underline_width_to_text** (*bool*)
            - **underline_buff** (*float*)
            - **kwargs** (*Any*)
