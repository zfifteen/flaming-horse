<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.three_d.three_dimensions.Arrow3D.html -->

# Arrow3D

Qualified name: `manim.mobject.three\_d.three\_dimensions.Arrow3D`

class Arrow3D(*start=array([-1., 0., 0.])*, *end=array([1., 0., 0.])*, *thickness=0.02*, *height=0.3*, *base_radius=0.08*, *color=ManimColor('#FFFFFF')*, *resolution=24*, ***kwargs*)[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Arrow3D)
:   Bases: [`Line3D`](manim.mobject.three_d.three_dimensions.Line3D.html#manim.mobject.three_d.three_dimensions.Line3D "manim.mobject.three_d.three_dimensions.Line3D")

    An arrow made out of a cylindrical line and a conical tip.

    Parameters:
    :   - **start** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike")) – The start position of the arrow.
        - **end** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike")) – The end position of the arrow.
        - **thickness** (*float*) – The thickness of the arrow.
        - **height** (*float*) – The height of the conical tip.
        - **base_radius** (*float*) – The base radius of the conical tip.
        - **color** ([*ManimColor*](manim.utils.color.core.ManimColor.html#manim.utils.color.core.ManimColor "manim.utils.color.core.ManimColor")) – The color of the arrow.
        - **resolution** (*int* *|* *tuple**[**int**,* *int**]*) – The resolution of the arrow line.
        - **kwargs** (*Any*)

    Examples

    Example: ExampleArrow3D

    ```python
    from manim import *

    class ExampleArrow3D(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            arrow = Arrow3D(
                start=np.array([0, 0, 0]),
                end=np.array([2, 2, 2]),
                resolution=8
            )
            self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
            self.add(axes, arrow)
    ```

    ```python
    class ExampleArrow3D(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            arrow = Arrow3D(
                start=np.array([0, 0, 0]),
                end=np.array([2, 2, 2]),
                resolution=8
            )
            self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
            self.add(axes, arrow)
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`get_end`](#manim.mobject.three_d.three_dimensions.Arrow3D.get_end "manim.mobject.three_d.three_dimensions.Arrow3D.get_end") | Returns the ending point of the [`Line3D`](manim.mobject.three_d.three_dimensions.Line3D.html#manim.mobject.three_d.three_dimensions.Line3D "manim.mobject.three_d.three_dimensions.Line3D"). |

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

    _original__init__(*start=array([-1., 0., 0.])*, *end=array([1., 0., 0.])*, *thickness=0.02*, *height=0.3*, *base_radius=0.08*, *color=ManimColor('#FFFFFF')*, *resolution=24*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **start** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike"))
            - **end** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike"))
            - **thickness** (*float*)
            - **height** (*float*)
            - **base_radius** (*float*)
            - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
            - **resolution** (*int* *|* *tuple**[**int**,* *int**]*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    get_end()[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Arrow3D.get_end)
    :   Returns the ending point of the [`Line3D`](manim.mobject.three_d.three_dimensions.Line3D.html#manim.mobject.three_d.three_dimensions.Line3D "manim.mobject.three_d.three_dimensions.Line3D").

        Returns:
        :   **end** – Ending point of the [`Line3D`](manim.mobject.three_d.three_dimensions.Line3D.html#manim.mobject.three_d.three_dimensions.Line3D "manim.mobject.three_d.three_dimensions.Line3D").

        Return type:
        :   `numpy.array`
