<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.frame.ScreenRectangle.html -->

# ScreenRectangle

Qualified name: `manim.mobject.frame.ScreenRectangle`

class ScreenRectangle(*aspect_ratio=1.7777777777777777*, *height=4*, ***kwargs*)[[source]](../_modules/manim/mobject/frame.html#ScreenRectangle)
:   Bases: [`Rectangle`](manim.mobject.geometry.polygram.Rectangle.html#manim.mobject.geometry.polygram.Rectangle "manim.mobject.geometry.polygram.Rectangle")

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `always` | Call a method on a mobject every frame. |
    | `animate` | Used to animate the application of any method of `self`. |
    | `animation_overrides` |  |
    | [`aspect_ratio`](#manim.mobject.frame.ScreenRectangle.aspect_ratio "manim.mobject.frame.ScreenRectangle.aspect_ratio") | The aspect ratio. |
    | `color` |  |
    | `depth` | The depth of the mobject. |
    | `fill_color` | If there are multiple colors (for gradient) this returns the first one |
    | `height` | The height of the mobject. |
    | `n_points_per_curve` |  |
    | `sheen_factor` |  |
    | `stroke_color` |  |
    | `width` | The width of the mobject. |

    Parameters:
    :   - **aspect_ratio** (*float*)
        - **height** (*float*)
        - **kwargs** (*Any*)

    _original__init__(*aspect_ratio=1.7777777777777777*, *height=4*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **aspect_ratio** (*float*)
            - **height** (*float*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    property aspect_ratio: float
    :   The aspect ratio.

        When set, the width is stretched to accommodate
        the new aspect ratio.
