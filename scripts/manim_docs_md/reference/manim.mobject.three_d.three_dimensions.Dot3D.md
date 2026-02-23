<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.three_d.three_dimensions.Dot3D.html -->

# Dot3D

Qualified name: `manim.mobject.three\_d.three\_dimensions.Dot3D`

class Dot3D(*point=array([0., 0., 0.])*, *radius=0.08*, *color=ManimColor('#FFFFFF')*, *resolution=(8, 8)*, ***kwargs*)[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Dot3D)
:   Bases: [`Sphere`](manim.mobject.three_d.three_dimensions.Sphere.html#manim.mobject.three_d.three_dimensions.Sphere "manim.mobject.three_d.three_dimensions.Sphere")

    A spherical dot.

    Parameters:
    :   - **point** ([*Point3D*](manim.typing.html#manim.typing.Point3D "manim.typing.Point3D")) – The location of the dot.
        - **radius** (*float*) – The radius of the dot.
        - **color** ([*ManimColor*](manim.utils.color.core.ManimColor.html#manim.utils.color.core.ManimColor "manim.utils.color.core.ManimColor")) – The color of the [`Dot3D`](#manim.mobject.three_d.three_dimensions.Dot3D "manim.mobject.three_d.three_dimensions.Dot3D").
        - **resolution** (*int* *|* *tuple**[**int**,* *int**]* *|* *None*) – The number of samples taken of the [`Dot3D`](#manim.mobject.three_d.three_dimensions.Dot3D "manim.mobject.three_d.three_dimensions.Dot3D"). A tuple can be
          used to define different resolutions for `u` and `v` respectively.
        - **kwargs** (*Any*)

    Examples

    Example: Dot3DExample

    ```python
    from manim import *

    class Dot3DExample(ThreeDScene):
        def construct(self):
            self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)

            axes = ThreeDAxes()
            dot_1 = Dot3D(point=axes.coords_to_point(0, 0, 1), color=RED)
            dot_2 = Dot3D(point=axes.coords_to_point(2, 0, 0), radius=0.1, color=BLUE)
            dot_3 = Dot3D(point=[0, 0, 0], radius=0.1, color=ORANGE)
            self.add(axes, dot_1, dot_2,dot_3)
    ```

    ```python
    class Dot3DExample(ThreeDScene):
        def construct(self):
            self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)

            axes = ThreeDAxes()
            dot_1 = Dot3D(point=axes.coords_to_point(0, 0, 1), color=RED)
            dot_2 = Dot3D(point=axes.coords_to_point(2, 0, 0), radius=0.1, color=BLUE)
            dot_3 = Dot3D(point=[0, 0, 0], radius=0.1, color=ORANGE)
            self.add(axes, dot_1, dot_2,dot_3)
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

    _original__init__(*point=array([0., 0., 0.])*, *radius=0.08*, *color=ManimColor('#FFFFFF')*, *resolution=(8, 8)*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **point** ([*Point3D*](manim.typing.html#manim.typing.Point3D "manim.typing.Point3D"))
            - **radius** (*float*)
            - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
            - **resolution** (*int* *|* *tuple**[**int**,* *int**]* *|* *None*)
            - **kwargs** (*Any*)

        Return type:
        :   None
