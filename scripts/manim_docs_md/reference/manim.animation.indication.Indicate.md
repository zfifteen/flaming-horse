<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.indication.Indicate.html -->

# Indicate

Qualified name: `manim.animation.indication.Indicate`

class Indicate(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/indication.html#Indicate)
:   Bases: [`Transform`](manim.animation.transform.Transform.html#manim.animation.transform.Transform "manim.animation.transform.Transform")

    Indicate a Mobject by temporarily resizing and recoloring it.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobject to indicate.
        - **scale_factor** (*float*) – The factor by which the mobject will be temporally scaled
        - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor")) – The color the mobject temporally takes.
        - **rate_func** ([*RateFunction*](manim.utils.rate_functions.RateFunction.html#manim.utils.rate_functions.RateFunction "manim.utils.rate_functions.RateFunction")) – The function defining the animation progress at every point in time.
        - **kwargs** (*Any*) – Additional arguments to be passed to the [`Succession`](manim.animation.composition.Succession.html#manim.animation.composition.Succession "manim.animation.composition.Succession") constructor

    Examples

    Example: UsingIndicate

    [
    ](./UsingIndicate-1.mp4)

    ```python
    from manim import *

    class UsingIndicate(Scene):
        def construct(self):
            tex = Tex("Indicate").scale(3)
            self.play(Indicate(tex))
            self.wait()
    ```

    ```python
    class UsingIndicate(Scene):
        def construct(self):
            tex = Tex("Indicate").scale(3)
            self.play(Indicate(tex))
            self.wait()
    ```

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

    _original__init__(*mobject*, *scale_factor=1.2*, *color=ManimColor('#FFFF00')*, *rate_func=<function there_and_back>*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **scale_factor** (*float*)
            - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
            - **rate_func** ([*RateFunction*](manim.utils.rate_functions.RateFunction.html#manim.utils.rate_functions.RateFunction "manim.utils.rate_functions.RateFunction"))
            - **kwargs** (*Any*)
