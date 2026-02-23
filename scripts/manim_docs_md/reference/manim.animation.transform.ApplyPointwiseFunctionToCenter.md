<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.transform.ApplyPointwiseFunctionToCenter.html -->

# ApplyPointwiseFunctionToCenter

Qualified name: `manim.animation.transform.ApplyPointwiseFunctionToCenter`

class ApplyPointwiseFunctionToCenter(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/transform.html#ApplyPointwiseFunctionToCenter)
:   Bases: [`ApplyPointwiseFunction`](manim.animation.transform.ApplyPointwiseFunction.html#manim.animation.transform.ApplyPointwiseFunction "manim.animation.transform.ApplyPointwiseFunction")

    Methods

    |  |  |
    | --- | --- |
    | [`begin`](#manim.animation.transform.ApplyPointwiseFunctionToCenter.begin "manim.animation.transform.ApplyPointwiseFunctionToCenter.begin") | Begin the animation. |

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    Parameters:
    :   - **function** (*types.MethodType*)
        - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))

    _original__init__(*function*, *mobject*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **function** (*MethodType*)
            - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))

        Return type:
        :   None

    begin()[[source]](../_modules/manim/animation/transform.html#ApplyPointwiseFunctionToCenter.begin)
    :   Begin the animation.

        This method is called right as an animation is being played. As much
        initialization as possible, especially any mobject copying, should live in this
        method.

        Return type:
        :   None
