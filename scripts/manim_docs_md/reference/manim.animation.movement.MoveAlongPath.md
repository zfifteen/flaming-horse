<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.movement.MoveAlongPath.html -->

# MoveAlongPath

Qualified name: `manim.animation.movement.MoveAlongPath`

class MoveAlongPath(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/movement.html#MoveAlongPath)
:   Bases: [`Animation`](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation")

    Make one mobject move along the path of another mobject.

    Example: MoveAlongPathExample

    [
    ](./MoveAlongPathExample-1.mp4)

    ```python
    from manim import *

    class MoveAlongPathExample(Scene):
        def construct(self):
            d1 = Dot().set_color(ORANGE)
            l1 = Line(LEFT, RIGHT)
            l2 = VMobject()
            self.add(d1, l1, l2)
            l2.add_updater(lambda x: x.become(Line(LEFT, d1.get_center()).set_color(ORANGE)))
            self.play(MoveAlongPath(d1, l1), rate_func=linear)
    ```

    ```python
    class MoveAlongPathExample(Scene):
        def construct(self):
            d1 = Dot().set_color(ORANGE)
            l1 = Line(LEFT, RIGHT)
            l2 = VMobject()
            self.add(d1, l1, l2)
            l2.add_updater(lambda x: x.become(Line(LEFT, d1.get_center()).set_color(ORANGE)))
            self.play(MoveAlongPath(d1, l1), rate_func=linear)
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`interpolate_mobject`](#manim.animation.movement.MoveAlongPath.interpolate_mobject "manim.animation.movement.MoveAlongPath.interpolate_mobject") | Interpolates the mobject of the `Animation` based on alpha value. |

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **path** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject"))
        - **suspend_mobject_updating** (*bool*)
        - **kwargs** (*Any*)

    _original__init__(*mobject*, *path*, *suspend_mobject_updating=False*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **path** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject"))
            - **suspend_mobject_updating** (*bool*)
            - **kwargs** (*Any*)

    interpolate_mobject(*alpha*)[[source]](../_modules/manim/animation/movement.html#MoveAlongPath.interpolate_mobject)
    :   Interpolates the mobject of the `Animation` based on alpha value.

        Parameters:
        :   **alpha** (*float*) – A float between 0 and 1 expressing the ratio to which the animation
            is completed. For example, alpha-values of 0, 0.5, and 1 correspond
            to the animation being completed 0%, 50%, and 100%, respectively.

        Return type:
        :   None
