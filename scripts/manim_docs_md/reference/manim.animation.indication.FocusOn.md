<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.indication.FocusOn.html -->

# FocusOn

Qualified name: `manim.animation.indication.FocusOn`

class FocusOn(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/indication.html#FocusOn)
:   Bases: [`Transform`](manim.animation.transform.Transform.html#manim.animation.transform.Transform "manim.animation.transform.Transform")

    Shrink a spotlight to a position.

    Parameters:
    :   - **focus_point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike") *|* [*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The point at which to shrink the spotlight. If it is a `Mobject` its center will be used.
        - **opacity** (*float*) – The opacity of the spotlight.
        - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor")) – The color of the spotlight.
        - **run_time** (*float*) – The duration of the animation.
        - **kwargs** (*Any*)

    Examples

    Example: UsingFocusOn

    [
    ](./UsingFocusOn-1.mp4)

    ```python
    from manim import *

    class UsingFocusOn(Scene):
        def construct(self):
            dot = Dot(color=PURE_YELLOW).shift(DOWN)
            self.add(Tex("Focusing on the dot below:"), dot)
            self.play(FocusOn(dot))
            self.wait()
    ```

    ```python
    class UsingFocusOn(Scene):
        def construct(self):
            dot = Dot(color=PURE_YELLOW).shift(DOWN)
            self.add(Tex("Focusing on the dot below:"), dot)
            self.play(FocusOn(dot))
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

    _original__init__(*focus_point*, *opacity=0.2*, *color=ManimColor('#888888')*, *run_time=2*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **focus_point** (*TypeAliasForwardRef**(**'~manim.typing.Point3DLike'**)* *|* [*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **opacity** (*float*)
            - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
            - **run_time** (*float*)
            - **kwargs** (*Any*)
