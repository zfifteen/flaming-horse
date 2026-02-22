<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.types.point_cloud_mobject.PointCloudDot.html -->

# PointCloudDot

Qualified name: `manim.mobject.types.point\_cloud\_mobject.PointCloudDot`

class PointCloudDot(*center=array([0., 0., 0.])*, *radius=2.0*, *stroke_width=2*, *density=10*, *color=ManimColor('#FFFF00')*, ***kwargs*)[[source]](../_modules/manim/mobject/types/point_cloud_mobject.html#PointCloudDot)
:   Bases: [`Mobject1D`](manim.mobject.types.point_cloud_mobject.Mobject1D.html#manim.mobject.types.point_cloud_mobject.Mobject1D "manim.mobject.types.point_cloud_mobject.Mobject1D")

    A disc made of a cloud of dots.

    Examples

    Example: PointCloudDotExample

    ```python
    from manim import *

    class PointCloudDotExample(Scene):
        def construct(self):
            cloud_1 = PointCloudDot(color=RED)
            cloud_2 = PointCloudDot(stroke_width=4, radius=1)
            cloud_3 = PointCloudDot(density=15)

            group = Group(cloud_1, cloud_2, cloud_3).arrange()
            self.add(group)
    ```

    ```python
    class PointCloudDotExample(Scene):
        def construct(self):
            cloud_1 = PointCloudDot(color=RED)
            cloud_2 = PointCloudDot(stroke_width=4, radius=1)
            cloud_3 = PointCloudDot(density=15)

            group = Group(cloud_1, cloud_2, cloud_3).arrange()
            self.add(group)
    ```

    Example: PointCloudDotExample2

    [
    ](./PointCloudDotExample2-1.mp4)

    ```python
    from manim import *

    class PointCloudDotExample2(Scene):
        def construct(self):
            plane = ComplexPlane()
            cloud = PointCloudDot(color=RED)
            self.add(
                plane, cloud
            )
            self.wait()
            self.play(
                cloud.animate.apply_complex_function(lambda z: np.exp(z))
            )
    ```

    ```python
    class PointCloudDotExample2(Scene):
        def construct(self):
            plane = ComplexPlane()
            cloud = PointCloudDot(color=RED)
            self.add(
                plane, cloud
            )
            self.wait()
            self.play(
                cloud.animate.apply_complex_function(lambda z: np.exp(z))
            )
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`generate_points`](#manim.mobject.types.point_cloud_mobject.PointCloudDot.generate_points "manim.mobject.types.point_cloud_mobject.PointCloudDot.generate_points") | Initializes `points` and therefore the shape. |
    | `init_points` |  |

    Attributes

    |  |  |
    | --- | --- |
    | `always` | Call a method on a mobject every frame. |
    | `animate` | Used to animate the application of any method of `self`. |
    | `animation_overrides` |  |
    | `depth` | The depth of the mobject. |
    | `height` | The height of the mobject. |
    | `width` | The width of the mobject. |

    Parameters:
    :   - **center** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike"))
        - **radius** (*float*)
        - **stroke_width** (*int*)
        - **density** (*int*)
        - **color** ([*ManimColor*](manim.utils.color.core.ManimColor.html#manim.utils.color.core.ManimColor "manim.utils.color.core.ManimColor"))
        - **kwargs** (*Any*)

    _original__init__(*center=array([0., 0., 0.])*, *radius=2.0*, *stroke_width=2*, *density=10*, *color=ManimColor('#FFFF00')*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **center** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike"))
            - **radius** (*float*)
            - **stroke_width** (*int*)
            - **density** (*int*)
            - **color** ([*ManimColor*](manim.utils.color.core.ManimColor.html#manim.utils.color.core.ManimColor "manim.utils.color.core.ManimColor"))
            - **kwargs** (*Any*)

        Return type:
        :   None

    generate_points()[[source]](../_modules/manim/mobject/types/point_cloud_mobject.html#PointCloudDot.generate_points)
    :   Initializes `points` and therefore the shape.

        Gets called upon creation. This is an empty method that can be implemented by
        subclasses.

        Return type:
        :   None
