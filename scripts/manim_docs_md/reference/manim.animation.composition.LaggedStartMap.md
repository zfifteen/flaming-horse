<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.composition.LaggedStartMap.html -->

# LaggedStartMap

Qualified name: `manim.animation.composition.LaggedStartMap`

class LaggedStartMap(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/composition.html#LaggedStartMap)
:   Bases: [`LaggedStart`](manim.animation.composition.LaggedStart.html#manim.animation.composition.LaggedStart "manim.animation.composition.LaggedStart")

    Plays a series of [`Animation`](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation") while mapping a function to submobjects.

    Parameters:
    :   - **AnimationClass** – [`Animation`](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation") to apply to mobject.
        - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") whose submobjects the animation, and optionally the function,
          are to be applied.
        - **arg_creator** (*Callable**[**[*[*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")*]**,* *Iterable**[**Any**]**]* *|* *None*) – Function which will be applied to [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject").
        - **run_time** (*float*) – The duration of the animation in seconds.
        - **animation_class** (*type**[*[*Animation*](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation")*]*)
        - **kwargs** (*Any*)

    Examples

    Example: LaggedStartMapExample

    [
    ](./LaggedStartMapExample-1.mp4)

    ```python
    from manim import *

    class LaggedStartMapExample(Scene):
        def construct(self):
            title = Tex("LaggedStartMap").to_edge(UP, buff=LARGE_BUFF)
            dots = VGroup(
                *[Dot(radius=0.16) for _ in range(35)]
                ).arrange_in_grid(rows=5, cols=7, buff=MED_LARGE_BUFF)
            self.add(dots, title)

            # Animate yellow ripple effect
            for mob in dots, title:
                self.play(LaggedStartMap(
                    ApplyMethod, mob,
                    lambda m : (m.set_color, YELLOW),
                    lag_ratio = 0.1,
                    rate_func = there_and_back,
                    run_time = 2
                ))
    ```

    ```python
    class LaggedStartMapExample(Scene):
        def construct(self):
            title = Tex("LaggedStartMap").to_edge(UP, buff=LARGE_BUFF)
            dots = VGroup(
                *[Dot(radius=0.16) for _ in range(35)]
                ).arrange_in_grid(rows=5, cols=7, buff=MED_LARGE_BUFF)
            self.add(dots, title)

            # Animate yellow ripple effect
            for mob in dots, title:
                self.play(LaggedStartMap(
                    ApplyMethod, mob,
                    lambda m : (m.set_color, YELLOW),
                    lag_ratio = 0.1,
                    rate_func = there_and_back,
                    run_time = 2
                ))
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    _original__init__(*animation_class*, *mobject*, *arg_creator=None*, *run_time=2*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **animation_class** (*type**[*[*Animation*](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation")*]*)
            - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **arg_creator** (*Callable**[**[*[*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")*]**,* *Iterable**[**Any**]**]* *|* *None*)
            - **run_time** (*float*)
            - **kwargs** (*Any*)
