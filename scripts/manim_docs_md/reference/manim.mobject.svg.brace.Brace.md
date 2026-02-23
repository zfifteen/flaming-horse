<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.svg.brace.Brace.html -->

# Brace

Qualified name: `manim.mobject.svg.brace.Brace`

class Brace(*mobject*, *direction=array([0., -1., 0.])*, *buff=0.2*, *sharpness=2*, *stroke_width=0*, *fill_opacity=1.0*, *background_stroke_width=0*, *background_stroke_color=ManimColor('#000000')*, ***kwargs*)[[source]](../_modules/manim/mobject/svg/brace.html#Brace)
:   Bases: [`VMobjectFromSVGPath`](manim.mobject.svg.svg_mobject.VMobjectFromSVGPath.html#manim.mobject.svg.svg_mobject.VMobjectFromSVGPath "manim.mobject.svg.svg_mobject.VMobjectFromSVGPath")

    Takes a mobject and draws a brace adjacent to it.

    Passing a direction vector determines the direction from which the
    brace is drawn. By default it is drawn from below.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobject adjacent to which the brace is placed.
        - **direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The direction from which the brace faces the mobject.
        - **buff** (*float*)
        - **sharpness** (*float*)
        - **stroke_width** (*float*)
        - **fill_opacity** (*float*)
        - **background_stroke_width** (*float*)
        - **background_stroke_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
        - **kwargs** (*Any*)

    See also

    [`BraceBetweenPoints`](manim.mobject.svg.brace.BraceBetweenPoints.html#manim.mobject.svg.brace.BraceBetweenPoints "manim.mobject.svg.brace.BraceBetweenPoints")

    Examples

    Example: BraceExample

    ```python
    from manim import *

    class BraceExample(Scene):
        def construct(self):
            s = Square()
            self.add(s)
            for i in np.linspace(0.1,1.0,4):
                br = Brace(s, sharpness=i)
                t = Text(f"sharpness= {i}").next_to(br, RIGHT)
                self.add(t)
                self.add(br)
            VGroup(*self.mobjects).arrange(DOWN, buff=0.2)
    ```

    ```python
    class BraceExample(Scene):
        def construct(self):
            s = Square()
            self.add(s)
            for i in np.linspace(0.1,1.0,4):
                br = Brace(s, sharpness=i)
                t = Text(f"sharpness= {i}").next_to(br, RIGHT)
                self.add(t)
                self.add(br)
            VGroup(*self.mobjects).arrange(DOWN, buff=0.2)
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`get_direction`](#manim.mobject.svg.brace.Brace.get_direction "manim.mobject.svg.brace.Brace.get_direction") | Returns the direction from the center to the brace tip. |
    | [`get_tex`](#manim.mobject.svg.brace.Brace.get_tex "manim.mobject.svg.brace.Brace.get_tex") | Places the tex at the brace tip. |
    | [`get_text`](#manim.mobject.svg.brace.Brace.get_text "manim.mobject.svg.brace.Brace.get_text") | Places the text at the brace tip. |
    | [`get_tip`](#manim.mobject.svg.brace.Brace.get_tip "manim.mobject.svg.brace.Brace.get_tip") | Returns the point at the brace tip. |
    | [`put_at_tip`](#manim.mobject.svg.brace.Brace.put_at_tip "manim.mobject.svg.brace.Brace.put_at_tip") | Puts the given mobject at the brace tip. |

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

    _original__init__(*mobject*, *direction=array([0., -1., 0.])*, *buff=0.2*, *sharpness=2*, *stroke_width=0*, *fill_opacity=1.0*, *background_stroke_width=0*, *background_stroke_color=ManimColor('#000000')*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
            - **buff** (*float*)
            - **sharpness** (*float*)
            - **stroke_width** (*float*)
            - **fill_opacity** (*float*)
            - **background_stroke_width** (*float*)
            - **background_stroke_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
            - **kwargs** (*Any*)

    get_direction()[[source]](../_modules/manim/mobject/svg/brace.html#Brace.get_direction)
    :   Returns the direction from the center to the brace tip.

        Return type:
        :   [*Vector3D*](manim.typing.html#manim.typing.Vector3D "manim.typing.Vector3D")

    get_tex(**tex*, ***kwargs*)[[source]](../_modules/manim/mobject/svg/brace.html#Brace.get_tex)
    :   Places the tex at the brace tip.

        Parameters:
        :   - **tex** (*str*) – The tex to be placed at the brace tip.
            - **kwargs** (*Any*) – Any further keyword arguments are passed to [`put_at_tip()`](#manim.mobject.svg.brace.Brace.put_at_tip "manim.mobject.svg.brace.Brace.put_at_tip") which
              is used to position the tex at the brace tip.

        Return type:
        :   [`MathTex`](manim.mobject.text.tex_mobject.MathTex.html#manim.mobject.text.tex_mobject.MathTex "manim.mobject.text.tex_mobject.MathTex")

    get_text(**text*, ***kwargs*)[[source]](../_modules/manim/mobject/svg/brace.html#Brace.get_text)
    :   Places the text at the brace tip.

        Parameters:
        :   - **text** (*str*) – The text to be placed at the brace tip.
            - **kwargs** (*Any*) – Any additional keyword arguments are passed to [`put_at_tip()`](#manim.mobject.svg.brace.Brace.put_at_tip "manim.mobject.svg.brace.Brace.put_at_tip") which
              is used to position the text at the brace tip.

        Return type:
        :   [`Tex`](manim.mobject.text.tex_mobject.Tex.html#manim.mobject.text.tex_mobject.Tex "manim.mobject.text.tex_mobject.Tex")

    get_tip()[[source]](../_modules/manim/mobject/svg/brace.html#Brace.get_tip)
    :   Returns the point at the brace tip.

        Return type:
        :   [*Point3D*](manim.typing.html#manim.typing.Point3D "manim.typing.Point3D")

    put_at_tip(*mob*, *use_next_to=True*, ***kwargs*)[[source]](../_modules/manim/mobject/svg/brace.html#Brace.put_at_tip)
    :   Puts the given mobject at the brace tip.

        Parameters:
        :   - **mob** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobject to be placed at the tip.
            - **use_next_to** (*bool*) – If true, then `next_to()` is used to place the mobject at the
              tip.
            - **kwargs** (*Any*) – Any additional keyword arguments are passed to `next_to()` which
              is used to put the mobject next to the brace tip.

        Return type:
        :   *Self*
