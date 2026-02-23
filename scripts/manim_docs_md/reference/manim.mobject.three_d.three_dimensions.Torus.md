<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.three_d.three_dimensions.Torus.html -->

# Torus

Qualified name: `manim.mobject.three\_d.three\_dimensions.Torus`

class Torus(*major_radius=3*, *minor_radius=1*, *u_range=(0, 6.283185307179586)*, *v_range=(0, 6.283185307179586)*, *resolution=None*, ***kwargs*)[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Torus)
:   Bases: [`Surface`](manim.mobject.three_d.three_dimensions.Surface.html#manim.mobject.three_d.three_dimensions.Surface "manim.mobject.three_d.three_dimensions.Surface")

    A torus.

    Parameters:
    :   - **major_radius** (*float*) – Distance from the center of the tube to the center of the torus.
        - **minor_radius** (*float*) – Radius of the tube.
        - **u_range** (*tuple**[**float**,* *float**]*) – The range of the `u` variable: `(u_min, u_max)`.
        - **v_range** (*tuple**[**float**,* *float**]*) – The range of the `v` variable: `(v_min, v_max)`.
        - **resolution** (*int* *|* *tuple**[**int**,* *int**]* *|* *None*) – The number of samples taken of the [`Torus`](#manim.mobject.three_d.three_dimensions.Torus "manim.mobject.three_d.three_dimensions.Torus"). A tuple can be
          used to define different resolutions for `u` and `v` respectively.
        - **kwargs** (*Any*)

    Examples

    Example: ExampleTorus

    ```python
    from manim import *

    class ExampleTorus(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            torus = Torus()
            self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
            self.add(axes, torus)
    ```

    ```python
    class ExampleTorus(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            torus = Torus()
            self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
            self.add(axes, torus)
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`func`](#manim.mobject.three_d.three_dimensions.Torus.func "manim.mobject.three_d.three_dimensions.Torus.func") | The z values defining the [`Torus`](#manim.mobject.three_d.three_dimensions.Torus "manim.mobject.three_d.three_dimensions.Torus") being plotted. |

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

    _original__init__(*major_radius=3*, *minor_radius=1*, *u_range=(0, 6.283185307179586)*, *v_range=(0, 6.283185307179586)*, *resolution=None*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **major_radius** (*float*)
            - **minor_radius** (*float*)
            - **u_range** (*tuple**[**float**,* *float**]*)
            - **v_range** (*tuple**[**float**,* *float**]*)
            - **resolution** (*int* *|* *tuple**[**int**,* *int**]* *|* *None*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    func(*u*, *v*)[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Torus.func)
    :   The z values defining the [`Torus`](#manim.mobject.three_d.three_dimensions.Torus "manim.mobject.three_d.three_dimensions.Torus") being plotted.

        Returns:
        :   The z values defining the [`Torus`](#manim.mobject.three_d.three_dimensions.Torus "manim.mobject.three_d.three_dimensions.Torus").

        Return type:
        :   `numpy.ndarray`

        Parameters:
        :   - **u** (*float*)
            - **v** (*float*)
