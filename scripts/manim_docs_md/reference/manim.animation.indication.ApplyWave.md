<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.indication.ApplyWave.html -->

# ApplyWave

Qualified name: `manim.animation.indication.ApplyWave`

class ApplyWave(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/indication.html#ApplyWave)
:   Bases: [`Homotopy`](manim.animation.movement.Homotopy.html#manim.animation.movement.Homotopy "manim.animation.movement.Homotopy")

    Send a wave through the Mobject distorting it temporarily.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobject to be distorted.
        - **direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The direction in which the wave nudges points of the shape
        - **amplitude** (*float*) – The distance points of the shape get shifted
        - **wave_func** ([*RateFunction*](manim.utils.rate_functions.RateFunction.html#manim.utils.rate_functions.RateFunction "manim.utils.rate_functions.RateFunction")) – The function defining the shape of one wave flank.
        - **time_width** (*float*) – The length of the wave relative to the width of the mobject.
        - **ripples** (*int*) – The number of ripples of the wave
        - **run_time** (*float*) – The duration of the animation.
        - **kwargs** (*Any*)

    Examples

    Example: ApplyingWaves

    [
    ](./ApplyingWaves-1.mp4)

    ```python
    from manim import *

    class ApplyingWaves(Scene):
        def construct(self):
            tex = Tex("WaveWaveWaveWaveWave").scale(2)
            self.play(ApplyWave(tex))
            self.play(ApplyWave(
                tex,
                direction=RIGHT,
                time_width=0.5,
                amplitude=0.3
            ))
            self.play(ApplyWave(
                tex,
                rate_func=linear,
                ripples=4
            ))
    ```

    ```python
    class ApplyingWaves(Scene):
        def construct(self):
            tex = Tex("WaveWaveWaveWaveWave").scale(2)
            self.play(ApplyWave(tex))
            self.play(ApplyWave(
                tex,
                direction=RIGHT,
                time_width=0.5,
                amplitude=0.3
            ))
            self.play(ApplyWave(
                tex,
                rate_func=linear,
                ripples=4
            ))
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    _original__init__(*mobject*, *direction=array([0.*, *1.*, *0.])*, *amplitude=0.2*, *wave_func=<function smooth>*, *time_width=1*, *ripples=1*, *run_time=2*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
            - **amplitude** (*float*)
            - **wave_func** ([*RateFunction*](manim.utils.rate_functions.RateFunction.html#manim.utils.rate_functions.RateFunction "manim.utils.rate_functions.RateFunction"))
            - **time_width** (*float*)
            - **ripples** (*int*)
            - **run_time** (*float*)
            - **kwargs** (*Any*)
