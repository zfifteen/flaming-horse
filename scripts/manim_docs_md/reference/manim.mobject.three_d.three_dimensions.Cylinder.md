<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.three_d.three_dimensions.Cylinder.html -->

# Cylinder

Qualified name: `manim.mobject.three\_d.three\_dimensions.Cylinder`

class Cylinder(*radius=1*, *height=2*, *direction=array([0., 0., 1.])*, *v_range=(0, 6.283185307179586)*, *show_ends=True*, *resolution=(24, 24)*, ***kwargs*)[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Cylinder)
:   Bases: [`Surface`](manim.mobject.three_d.three_dimensions.Surface.html#manim.mobject.three_d.three_dimensions.Surface "manim.mobject.three_d.three_dimensions.Surface")

    A cylinder, defined by its height, radius and direction,

    Parameters:
    :   - **radius** (*float*) – The radius of the cylinder.
        - **height** (*float*) – The height of the cylinder.
        - **direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The direction of the central axis of the cylinder.
        - **v_range** (*tuple**[**float**,* *float**]*) – The height along the height axis (given by direction) to start and end on.
        - **show_ends** (*bool*) – Whether to show the end caps or not.
        - **resolution** (*int* *|* *tuple**[**int**,* *int**]*) – The number of samples taken of the [`Cylinder`](#manim.mobject.three_d.three_dimensions.Cylinder "manim.mobject.three_d.three_dimensions.Cylinder"). A tuple can be used
          to define different resolutions for `u` and `v` respectively.
        - **kwargs** (*Any*)

    Examples

    Example: ExampleCylinder

    ```python
    from manim import *

    class ExampleCylinder(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            cylinder = Cylinder(radius=2, height=3)
            self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
            self.add(axes, cylinder)
    ```

    ```python
    class ExampleCylinder(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            cylinder = Cylinder(radius=2, height=3)
            self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
            self.add(axes, cylinder)
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`add_bases`](#manim.mobject.three_d.three_dimensions.Cylinder.add_bases "manim.mobject.three_d.three_dimensions.Cylinder.add_bases") | Adds the end caps of the cylinder. |
    | [`func`](#manim.mobject.three_d.three_dimensions.Cylinder.func "manim.mobject.three_d.three_dimensions.Cylinder.func") | Converts from cylindrical coordinates to cartesian. |
    | [`get_direction`](#manim.mobject.three_d.three_dimensions.Cylinder.get_direction "manim.mobject.three_d.three_dimensions.Cylinder.get_direction") | Returns the direction of the central axis of the [`Cylinder`](#manim.mobject.three_d.three_dimensions.Cylinder "manim.mobject.three_d.three_dimensions.Cylinder"). |
    | [`set_direction`](#manim.mobject.three_d.three_dimensions.Cylinder.set_direction "manim.mobject.three_d.three_dimensions.Cylinder.set_direction") | Sets the direction of the central axis of the [`Cylinder`](#manim.mobject.three_d.three_dimensions.Cylinder "manim.mobject.three_d.three_dimensions.Cylinder"). |

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

    _original__init__(*radius=1*, *height=2*, *direction=array([0., 0., 1.])*, *v_range=(0, 6.283185307179586)*, *show_ends=True*, *resolution=(24, 24)*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **radius** (*float*)
            - **height** (*float*)
            - **direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
            - **v_range** (*tuple**[**float**,* *float**]*)
            - **show_ends** (*bool*)
            - **resolution** (*int* *|* *tuple**[**int**,* *int**]*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    add_bases()[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Cylinder.add_bases)
    :   Adds the end caps of the cylinder.

        Return type:
        :   None

    func(*u*, *v*)[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Cylinder.func)
    :   Converts from cylindrical coordinates to cartesian.

        Parameters:
        :   - **u** (*float*) – The height.
            - **v** (*float*) – The azimuthal angle.

        Returns:
        :   Points defining the [`Cylinder`](#manim.mobject.three_d.three_dimensions.Cylinder "manim.mobject.three_d.three_dimensions.Cylinder").

        Return type:
        :   `numpy.ndarray`

    get_direction()[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Cylinder.get_direction)
    :   Returns the direction of the central axis of the [`Cylinder`](#manim.mobject.three_d.three_dimensions.Cylinder "manim.mobject.three_d.three_dimensions.Cylinder").

        Returns:
        :   **direction** – The direction of the central axis of the [`Cylinder`](#manim.mobject.three_d.three_dimensions.Cylinder "manim.mobject.three_d.three_dimensions.Cylinder").

        Return type:
        :   `numpy.array`

    set_direction(*direction*)[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Cylinder.set_direction)
    :   Sets the direction of the central axis of the [`Cylinder`](#manim.mobject.three_d.three_dimensions.Cylinder "manim.mobject.three_d.three_dimensions.Cylinder").

        Parameters:
        :   **direction** (`numpy.array`) – The direction of the central axis of the [`Cylinder`](#manim.mobject.three_d.three_dimensions.Cylinder "manim.mobject.three_d.three_dimensions.Cylinder").

        Return type:
        :   None
