<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.transform.ApplyPointwiseFunction.html -->

# ApplyPointwiseFunction

Qualified name: `manim.animation.transform.ApplyPointwiseFunction`

class ApplyPointwiseFunction(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/transform.html#ApplyPointwiseFunction)
:   Bases: [`ApplyMethod`](manim.animation.transform.ApplyMethod.html#manim.animation.transform.ApplyMethod "manim.animation.transform.ApplyMethod")

    Animation that applies a pointwise function to a mobject.

    Examples

    Example: WarpSquare

    [
    ](./WarpSquare-1.mp4)

    ```python
    from manim import *

    class WarpSquare(Scene):
        def construct(self):
            square = Square()
            self.play(
                ApplyPointwiseFunction(
                    lambda point: complex_to_R3(np.exp(R3_to_complex(point))), square
                )
            )
            self.wait()
    ```

    ```python
    class WarpSquare(Scene):
        def construct(self):
            square = Square()
            self.play(
                ApplyPointwiseFunction(
                    lambda point: complex_to_R3(np.exp(R3_to_complex(point))), square
                )
            )
            self.wait()
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    Parameters:
    :   - **function** (*types.MethodType*)
        - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **run_time** (*float*)

    _original__init__(*function*, *mobject*, *run_time=3.0*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **function** (*MethodType*)
            - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **run_time** (*float*)

        Return type:
        :   None
