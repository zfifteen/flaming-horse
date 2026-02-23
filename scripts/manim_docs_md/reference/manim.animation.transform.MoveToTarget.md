<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.transform.MoveToTarget.html -->

# MoveToTarget

Qualified name: `manim.animation.transform.MoveToTarget`

class MoveToTarget(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/transform.html#MoveToTarget)
:   Bases: [`Transform`](manim.animation.transform.Transform.html#manim.animation.transform.Transform "manim.animation.transform.Transform")

    Transforms a mobject to the mobject stored in its `target` attribute.

    After calling the `generate_target()` method, the `target`
    attribute of the mobject is populated with a copy of it. After modifying the attribute,
    playing the [`MoveToTarget`](#manim.animation.transform.MoveToTarget "manim.animation.transform.MoveToTarget") animation transforms the original mobject
    into the modified one stored in the `target` attribute.

    Examples

    Example: MoveToTargetExample

    [
    ](./MoveToTargetExample-1.mp4)

    ```python
    from manim import *

    class MoveToTargetExample(Scene):
        def construct(self):
            c = Circle()

            c.generate_target()
            c.target.set_fill(color=GREEN, opacity=0.5)
            c.target.shift(2*RIGHT + UP).scale(0.5)

            self.add(c)
            self.play(MoveToTarget(c))
    ```

    ```python
    class MoveToTargetExample(Scene):
        def construct(self):
            c = Circle()

            c.generate_target()
            c.target.set_fill(color=GREEN, opacity=0.5)
            c.target.shift(2*RIGHT + UP).scale(0.5)

            self.add(c)
            self.play(MoveToTarget(c))
    ```

    Methods

    |  |  |
    | --- | --- |
    | `check_validity_of_input` |  |

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    Parameters:
    :   **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))

    _original__init__(*mobject*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))

        Return type:
        :   None
