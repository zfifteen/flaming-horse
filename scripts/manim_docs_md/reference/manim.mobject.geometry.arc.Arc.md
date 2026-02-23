<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.arc.Arc.html -->

# Arc

Qualified name: `manim.mobject.geometry.arc.Arc`

class Arc(*radius=1.0*, *start_angle=0*, *angle=1.5707963267948966*, *num_components=9*, *arc_center=array([0., 0., 0.])*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/arc.html#Arc)
:   Bases: [`TipableVMobject`](manim.mobject.geometry.arc.TipableVMobject.html#manim.mobject.geometry.arc.TipableVMobject "manim.mobject.geometry.arc.TipableVMobject")

    A circular arc.

    Examples

    A simple arc of angle Pi.

    Example: ArcExample

    ```python
    from manim import *

    class ArcExample(Scene):
        def construct(self):
            self.add(Arc(angle=PI))
    ```

    ```python
    class ArcExample(Scene):
        def construct(self):
            self.add(Arc(angle=PI))
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`generate_points`](#manim.mobject.geometry.arc.Arc.generate_points "manim.mobject.geometry.arc.Arc.generate_points") | Initializes `points` and therefore the shape. |
    | [`get_arc_center`](#manim.mobject.geometry.arc.Arc.get_arc_center "manim.mobject.geometry.arc.Arc.get_arc_center") | Looks at the normals to the first two anchors, and finds their intersection points |
    | `init_points` |  |
    | `move_arc_center_to` |  |
    | `stop_angle` |  |

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

    Parameters:
    :   - **radius** (*float* *|* *None*)
        - **start_angle** (*float*)
        - **angle** (*float*)
        - **num_components** (*int*)
        - **arc_center** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike"))
        - **kwargs** (*Any*)

    _original__init__(*radius=1.0*, *start_angle=0*, *angle=1.5707963267948966*, *num_components=9*, *arc_center=array([0., 0., 0.])*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **radius** (*float* *|* *None*)
            - **start_angle** (*float*)
            - **angle** (*float*)
            - **num_components** (*int*)
            - **arc_center** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike"))
            - **kwargs** (*Any*)

    generate_points()[[source]](../_modules/manim/mobject/geometry/arc.html#Arc.generate_points)
    :   Initializes `points` and therefore the shape.

        Gets called upon creation. This is an empty method that can be implemented by
        subclasses.

        Return type:
        :   None

    get_arc_center(*warning=True*)[[source]](../_modules/manim/mobject/geometry/arc.html#Arc.get_arc_center)
    :   Looks at the normals to the first two
        anchors, and finds their intersection points

        Parameters:
        :   **warning** (*bool*)

        Return type:
        :   [*Point3D*](manim.typing.html#manim.typing.Point3D "manim.typing.Point3D")
