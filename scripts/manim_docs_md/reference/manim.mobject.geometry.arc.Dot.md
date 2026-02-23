<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.arc.Dot.html -->

# Dot

Qualified name: `manim.mobject.geometry.arc.Dot`

class Dot(*point=array([0., 0., 0.])*, *radius=0.08*, *stroke_width=0*, *fill_opacity=1.0*, *color=ManimColor('#FFFFFF')*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/arc.html#Dot)
:   Bases: [`Circle`](manim.mobject.geometry.arc.Circle.html#manim.mobject.geometry.arc.Circle "manim.mobject.geometry.arc.Circle")

    A circle with a very small radius.

    Parameters:
    :   - **point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike")) – The location of the dot.
        - **radius** (*float*) – The radius of the dot.
        - **stroke_width** (*float*) – The thickness of the outline of the dot.
        - **fill_opacity** (*float*) – The opacity of the dot’s fill_colour
        - **color** ([*ManimColor*](manim.utils.color.core.ManimColor.html#manim.utils.color.core.ManimColor "manim.utils.color.core.ManimColor")) – The color of the dot.
        - **kwargs** (*Any*) – Additional arguments to be passed to [`Circle`](manim.mobject.geometry.arc.Circle.html#manim.mobject.geometry.arc.Circle "manim.mobject.geometry.arc.Circle")

    Examples

    Example: DotExample

    ```python
    from manim import *

    class DotExample(Scene):
        def construct(self):
            dot1 = Dot(point=LEFT, radius=0.08)
            dot2 = Dot(point=ORIGIN)
            dot3 = Dot(point=RIGHT)
            self.add(dot1,dot2,dot3)
    ```

    ```python
    class DotExample(Scene):
        def construct(self):
            dot1 = Dot(point=LEFT, radius=0.08)
            dot2 = Dot(point=ORIGIN)
            dot3 = Dot(point=RIGHT)
            self.add(dot1,dot2,dot3)
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

    _original__init__(*point=array([0., 0., 0.])*, *radius=0.08*, *stroke_width=0*, *fill_opacity=1.0*, *color=ManimColor('#FFFFFF')*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike"))
            - **radius** (*float*)
            - **stroke_width** (*float*)
            - **fill_opacity** (*float*)
            - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
            - **kwargs** (*Any*)

        Return type:
        :   None
