<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.transform.CounterclockwiseTransform.html -->

# CounterclockwiseTransform

Qualified name: `manim.animation.transform.CounterclockwiseTransform`

class CounterclockwiseTransform(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/transform.html#CounterclockwiseTransform)
:   Bases: [`Transform`](manim.animation.transform.Transform.html#manim.animation.transform.Transform "manim.animation.transform.Transform")

    Transforms the points of a mobject along a counterclockwise oriented arc.

    See also

    [`Transform`](manim.animation.transform.Transform.html#manim.animation.transform.Transform "manim.animation.transform.Transform"), [`ClockwiseTransform`](manim.animation.transform.ClockwiseTransform.html#manim.animation.transform.ClockwiseTransform "manim.animation.transform.ClockwiseTransform")

    Examples

    Example: CounterclockwiseTransform_vs_Transform

    [
    ](./CounterclockwiseTransform_vs_Transform-1.mp4)

    ```python
    from manim import *

    class CounterclockwiseTransform_vs_Transform(Scene):
        def construct(self):
            # set up the numbers
            c_transform = VGroup(DecimalNumber(number=3.141, num_decimal_places=3), DecimalNumber(number=1.618, num_decimal_places=3))
            text_1 = Text("CounterclockwiseTransform", color=RED)
            c_transform.add(text_1)

            transform = VGroup(DecimalNumber(number=1.618, num_decimal_places=3), DecimalNumber(number=3.141, num_decimal_places=3))
            text_2 = Text("Transform", color=BLUE)
            transform.add(text_2)

            ints = VGroup(c_transform, transform)
            texts = VGroup(text_1, text_2).scale(0.75)
            c_transform.arrange(direction=UP, buff=1)
            transform.arrange(direction=UP, buff=1)

            ints.arrange(buff=2)
            self.add(ints, texts)

            # The mobs move in clockwise direction for ClockwiseTransform()
            self.play(CounterclockwiseTransform(c_transform[0], c_transform[1]))

            # The mobs move straight up for Transform()
            self.play(Transform(transform[0], transform[1]))
    ```

    ```python
    class CounterclockwiseTransform_vs_Transform(Scene):
        def construct(self):
            # set up the numbers
            c_transform = VGroup(DecimalNumber(number=3.141, num_decimal_places=3), DecimalNumber(number=1.618, num_decimal_places=3))
            text_1 = Text("CounterclockwiseTransform", color=RED)
            c_transform.add(text_1)

            transform = VGroup(DecimalNumber(number=1.618, num_decimal_places=3), DecimalNumber(number=3.141, num_decimal_places=3))
            text_2 = Text("Transform", color=BLUE)
            transform.add(text_2)

            ints = VGroup(c_transform, transform)
            texts = VGroup(text_1, text_2).scale(0.75)
            c_transform.arrange(direction=UP, buff=1)
            transform.arrange(direction=UP, buff=1)

            ints.arrange(buff=2)
            self.add(ints, texts)

            # The mobs move in clockwise direction for ClockwiseTransform()
            self.play(CounterclockwiseTransform(c_transform[0], c_transform[1]))

            # The mobs move straight up for Transform()
            self.play(Transform(transform[0], transform[1]))
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **target_mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **path_arc** (*float*)

    _original__init__(*mobject*, *target_mobject*, *path_arc=3.141592653589793*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **target_mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **path_arc** (*float*)

        Return type:
        :   None
