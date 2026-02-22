<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.shape_matchers.Cross.html -->

# Cross

Qualified name: `manim.mobject.geometry.shape\_matchers.Cross`

class Cross(*mobject=None*, *stroke_color=ManimColor('#FC6255')*, *stroke_width=6.0*, *scale_factor=1.0*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/shape_matchers.html#Cross)
:   Bases: [`VGroup`](manim.mobject.types.vectorized_mobject.VGroup.html#manim.mobject.types.vectorized_mobject.VGroup "manim.mobject.types.vectorized_mobject.VGroup")

    Creates a cross.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") *|* *None*) – The mobject linked to this instance. It fits the mobject when specified. Defaults to None.
        - **stroke_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor")) – Specifies the color of the cross lines. Defaults to RED.
        - **stroke_width** (*float*) – Specifies the width of the cross lines. Defaults to 6.
        - **scale_factor** (*float*) – Scales the cross to the provided units. Defaults to 1.
        - **kwargs** (*Any*)

    Examples

    Example: ExampleCross

    ```python
    from manim import *

    class ExampleCross(Scene):
        def construct(self):
            cross = Cross()
            self.add(cross)
    ```

    ```python
    class ExampleCross(Scene):
        def construct(self):
            cross = Cross()
            self.add(cross)
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

    _original__init__(*mobject=None*, *stroke_color=ManimColor('#FC6255')*, *stroke_width=6.0*, *scale_factor=1.0*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") *|* *None*)
            - **stroke_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
            - **stroke_width** (*float*)
            - **scale_factor** (*float*)
            - **kwargs** (*Any*)

        Return type:
        :   None
