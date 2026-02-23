<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.rotation.Rotate.html -->

# Rotate

Qualified name: `manim.animation.rotation.Rotate`

class Rotate(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/rotation.html#Rotate)
:   Bases: [`Transform`](manim.animation.transform.Transform.html#manim.animation.transform.Transform "manim.animation.transform.Transform")

    Animation that rotates a Mobject.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobject to be rotated.
        - **angle** (*float*) – The rotation angle.
        - **axis** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The rotation axis as a numpy vector.
        - **about_point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike") *|* *None*) – The rotation center.
        - **about_edge** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike") *|* *None*) – If `about_point` is `None`, this argument specifies
          the direction of the bounding box point to be taken as
          the rotation center.
        - **kwargs** (*Any*)

    Examples

    Example: UsingRotate

    [
    ](./UsingRotate-1.mp4)

    ```python
    from manim import *

    class UsingRotate(Scene):
        def construct(self):
            self.play(
                Rotate(
                    Square(side_length=0.5).shift(UP * 2),
                    angle=2*PI,
                    about_point=ORIGIN,
                    rate_func=linear,
                ),
                Rotate(Square(side_length=0.5), angle=2*PI, rate_func=linear),
                )
    ```

    ```python
    class UsingRotate(Scene):
        def construct(self):
            self.play(
                Rotate(
                    Square(side_length=0.5).shift(UP * 2),
                    angle=2*PI,
                    about_point=ORIGIN,
                    rate_func=linear,
                ),
                Rotate(Square(side_length=0.5), angle=2*PI, rate_func=linear),
                )
    ```

    See also

    [`Rotating`](manim.animation.rotation.Rotating.html#manim.animation.rotation.Rotating "manim.animation.rotation.Rotating"), [`rotate()`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject.rotate "manim.mobject.mobject.Mobject.rotate")

    Methods

    |  |  |
    | --- | --- |
    | `create_target` |  |

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    _original__init__(*mobject*, *angle=3.141592653589793*, *axis=array([0., 0., 1.])*, *about_point=None*, *about_edge=None*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **angle** (*float*)
            - **axis** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
            - **about_point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike") *|* *None*)
            - **about_edge** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike") *|* *None*)
            - **kwargs** (*Any*)

        Return type:
        :   None
