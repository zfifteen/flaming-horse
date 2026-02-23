<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.three_d.three_dimensions.Cube.html -->

# Cube

Qualified name: `manim.mobject.three\_d.three\_dimensions.Cube`

class Cube(*side_length=2*, *fill_opacity=0.75*, *fill_color=ManimColor('#58C4DD')*, *stroke_width=0*, ***kwargs*)[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Cube)
:   Bases: [`VGroup`](manim.mobject.types.vectorized_mobject.VGroup.html#manim.mobject.types.vectorized_mobject.VGroup "manim.mobject.types.vectorized_mobject.VGroup")

    A three-dimensional cube.

    Parameters:
    :   - **side_length** (*float*) – Length of each side of the [`Cube`](#manim.mobject.three_d.three_dimensions.Cube "manim.mobject.three_d.three_dimensions.Cube").
        - **fill_opacity** (*float*) – The opacity of the [`Cube`](#manim.mobject.three_d.three_dimensions.Cube "manim.mobject.three_d.three_dimensions.Cube"), from 0 being fully transparent to 1 being
          fully opaque. Defaults to 0.75.
        - **fill_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor")) – The color of the [`Cube`](#manim.mobject.three_d.three_dimensions.Cube "manim.mobject.three_d.three_dimensions.Cube").
        - **stroke_width** (*float*) – The width of the stroke surrounding each face of the [`Cube`](#manim.mobject.three_d.three_dimensions.Cube "manim.mobject.three_d.three_dimensions.Cube").
        - **kwargs** (*Any*)

    Examples

    Example: CubeExample

    ```python
    from manim import *

    class CubeExample(ThreeDScene):
        def construct(self):
            self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)

            axes = ThreeDAxes()
            cube = Cube(side_length=3, fill_opacity=0.7, fill_color=BLUE)
            self.add(cube)
    ```

    ```python
    class CubeExample(ThreeDScene):
        def construct(self):
            self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)

            axes = ThreeDAxes()
            cube = Cube(side_length=3, fill_opacity=0.7, fill_color=BLUE)
            self.add(cube)
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`generate_points`](#manim.mobject.three_d.three_dimensions.Cube.generate_points "manim.mobject.three_d.three_dimensions.Cube.generate_points") | Creates the sides of the [`Cube`](#manim.mobject.three_d.three_dimensions.Cube "manim.mobject.three_d.three_dimensions.Cube"). |
    | `init_points` |  |

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

    _original__init__(*side_length=2*, *fill_opacity=0.75*, *fill_color=ManimColor('#58C4DD')*, *stroke_width=0*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **side_length** (*float*)
            - **fill_opacity** (*float*)
            - **fill_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
            - **stroke_width** (*float*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    generate_points()[[source]](../_modules/manim/mobject/three_d/three_dimensions.html#Cube.generate_points)
    :   Creates the sides of the [`Cube`](#manim.mobject.three_d.three_dimensions.Cube "manim.mobject.three_d.three_dimensions.Cube").

        Return type:
        :   None
