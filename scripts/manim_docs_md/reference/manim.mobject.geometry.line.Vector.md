<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Vector.html -->

# Vector

Qualified name: `manim.mobject.geometry.line.Vector`

class Vector(*direction=array([1., 0., 0.])*, *buff=0*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/line.html#Vector)
:   Bases: [`Arrow`](manim.mobject.geometry.line.Arrow.html#manim.mobject.geometry.line.Arrow "manim.mobject.geometry.line.Arrow")

    A vector specialized for use in graphs.

    Caution

    Do not confuse with the [`Vector2D`](manim.typing.html#manim.typing.Vector2D "manim.typing.Vector2D"),
    [`Vector3D`](manim.typing.html#manim.typing.Vector3D "manim.typing.Vector3D") or [`VectorND`](manim.typing.html#manim.typing.VectorND "manim.typing.VectorND") type aliases,
    which are not Mobjects!

    Parameters:
    :   - **direction** ([*Vector2DLike*](manim.typing.html#manim.typing.Vector2DLike "manim.typing.Vector2DLike") *|* [*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The direction of the arrow.
        - **buff** (*float*) – The distance of the vector from its endpoints.
        - **kwargs** (*Any*) – Additional arguments to be passed to [`Arrow`](manim.mobject.geometry.line.Arrow.html#manim.mobject.geometry.line.Arrow "manim.mobject.geometry.line.Arrow")

    Examples

    Example: VectorExample

    ```python
    from manim import *

    class VectorExample(Scene):
        def construct(self):
            plane = NumberPlane()
            vector_1 = Vector([1,2])
            vector_2 = Vector([-5,-2])
            self.add(plane, vector_1, vector_2)
    ```

    ```python
    class VectorExample(Scene):
        def construct(self):
            plane = NumberPlane()
            vector_1 = Vector([1,2])
            vector_2 = Vector([-5,-2])
            self.add(plane, vector_1, vector_2)
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`coordinate_label`](#manim.mobject.geometry.line.Vector.coordinate_label "manim.mobject.geometry.line.Vector.coordinate_label") | Creates a label based on the coordinates of the vector. |

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

    _original__init__(*direction=array([1., 0., 0.])*, *buff=0*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **direction** (*TypeAliasForwardRef**(**'~manim.typing.Vector2DLike'**)* *|* *TypeAliasForwardRef**(**'~manim.typing.Vector3DLike'**)*)
            - **buff** (*float*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    coordinate_label(*integer_labels=True*, *n_dim=2*, *color=None*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/line.html#Vector.coordinate_label)
    :   Creates a label based on the coordinates of the vector.

        Parameters:
        :   - **integer_labels** (*bool*) – Whether or not to round the coordinates to integers.
            - **n_dim** (*int*) – The number of dimensions of the vector.
            - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*) – Sets the color of label, optional.
            - **kwargs** (*Any*) – Additional arguments to be passed to [`Matrix`](manim.mobject.matrix.Matrix.html#manim.mobject.matrix.Matrix "manim.mobject.matrix.Matrix").

        Returns:
        :   The label.

        Return type:
        :   [`Matrix`](manim.mobject.matrix.Matrix.html#manim.mobject.matrix.Matrix "manim.mobject.matrix.Matrix")

        Examples

        Example: VectorCoordinateLabel

        ```python
        from manim import *

        class VectorCoordinateLabel(Scene):
            def construct(self):
                plane = NumberPlane()

                vec_1 = Vector([1, 2])
                vec_2 = Vector([-3, -2])
                label_1 = vec_1.coordinate_label()
                label_2 = vec_2.coordinate_label(color=YELLOW)

                self.add(plane, vec_1, vec_2, label_1, label_2)
        ```

        ```python
        class VectorCoordinateLabel(Scene):
            def construct(self):
                plane = NumberPlane()

                vec_1 = Vector([1, 2])
                vec_2 = Vector([-3, -2])
                label_1 = vec_1.coordinate_label()
                label_2 = vec_2.coordinate_label(color=YELLOW)

                self.add(plane, vec_1, vec_2, label_1, label_2)
        ```
