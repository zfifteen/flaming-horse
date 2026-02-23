<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.indication.Wiggle.html -->

# Wiggle

Qualified name: `manim.animation.indication.Wiggle`

class Wiggle(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/indication.html#Wiggle)
:   Bases: [`Animation`](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation")

    Wiggle a Mobject.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobject to wiggle.
        - **scale_value** (*float*) – The factor by which the mobject will be temporarily scaled.
        - **rotation_angle** (*float*) – The wiggle angle.
        - **n_wiggles** (*int*) – The number of wiggles.
        - **scale_about_point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike") *|* *None*) – The point about which the mobject gets scaled.
        - **rotate_about_point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike") *|* *None*) – The point around which the mobject gets rotated.
        - **run_time** (*float*) – The duration of the animation
        - **kwargs** (*Any*)

    Examples

    Example: ApplyingWaves

    [
    ](./ApplyingWaves-2.mp4)

    ```python
    from manim import *

    class ApplyingWaves(Scene):
        def construct(self):
            tex = Tex("Wiggle").scale(3)
            self.play(Wiggle(tex))
            self.wait()
    ```

    ```python
    class ApplyingWaves(Scene):
        def construct(self):
            tex = Tex("Wiggle").scale(3)
            self.play(Wiggle(tex))
            self.wait()
    ```

    Methods

    |  |  |
    | --- | --- |
    | `get_rotate_about_point` |  |
    | `get_scale_about_point` |  |
    | `interpolate_submobject` |  |

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    _original__init__(*mobject*, *scale_value=1.1*, *rotation_angle=0.06283185307179587*, *n_wiggles=6*, *scale_about_point=None*, *rotate_about_point=None*, *run_time=2*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **scale_value** (*float*)
            - **rotation_angle** (*float*)
            - **n_wiggles** (*int*)
            - **scale_about_point** (*TypeAliasForwardRef**(**'~manim.typing.Point3DLike'**)* *|* *None*)
            - **rotate_about_point** (*TypeAliasForwardRef**(**'~manim.typing.Point3DLike'**)* *|* *None*)
            - **run_time** (*float*)
            - **kwargs** (*Any*)
