<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.numbers.ChangingDecimal.html -->

# ChangingDecimal

Qualified name: `manim.animation.numbers.ChangingDecimal`

class ChangingDecimal(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/numbers.html#ChangingDecimal)
:   Bases: [`Animation`](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation")

    Animate a [`DecimalNumber`](manim.mobject.text.numbers.DecimalNumber.html#manim.mobject.text.numbers.DecimalNumber "manim.mobject.text.numbers.DecimalNumber") to values specified by a user-supplied function.

    Parameters:
    :   - **decimal_mob** ([*DecimalNumber*](manim.mobject.text.numbers.DecimalNumber.html#manim.mobject.text.numbers.DecimalNumber "manim.mobject.text.numbers.DecimalNumber")) – The [`DecimalNumber`](manim.mobject.text.numbers.DecimalNumber.html#manim.mobject.text.numbers.DecimalNumber "manim.mobject.text.numbers.DecimalNumber") instance to animate.
        - **number_update_func** (*Callable**[**[**float**]**,* *float**]*) – A function that returns the number to display at each point in the animation.
        - **suspend_mobject_updating** (*bool*) – If `True`, the mobject is not updated outside this animation.
        - **kwargs** (*Any*)

    Raises:
    :   **TypeError** – If `decimal_mob` is not an instance of [`DecimalNumber`](manim.mobject.text.numbers.DecimalNumber.html#manim.mobject.text.numbers.DecimalNumber "manim.mobject.text.numbers.DecimalNumber").

    Examples

    Example: ChangingDecimalExample

    [
    ](./ChangingDecimalExample-1.mp4)

    ```python
    from manim import *

    class ChangingDecimalExample(Scene):
        def construct(self):
            number = DecimalNumber(0)
            self.add(number)
            self.play(
                ChangingDecimal(
                    number,
                    lambda a: 5 * a,
                    run_time=3
                )
            )
            self.wait()
    ```

    ```python
    class ChangingDecimalExample(Scene):
        def construct(self):
            number = DecimalNumber(0)
            self.add(number)
            self.play(
                ChangingDecimal(
                    number,
                    lambda a: 5 * a,
                    run_time=3
                )
            )
            self.wait()
    ```

    Methods

    |  |  |
    | --- | --- |
    | `check_validity_of_input` |  |
    | [`interpolate_mobject`](#manim.animation.numbers.ChangingDecimal.interpolate_mobject "manim.animation.numbers.ChangingDecimal.interpolate_mobject") | Interpolates the mobject of the `Animation` based on alpha value. |

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    _original__init__(*decimal_mob*, *number_update_func*, *suspend_mobject_updating=False*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **decimal_mob** ([*DecimalNumber*](manim.mobject.text.numbers.DecimalNumber.html#manim.mobject.text.numbers.DecimalNumber "manim.mobject.text.numbers.DecimalNumber"))
            - **number_update_func** (*Callable**[**[**float**]**,* *float**]*)
            - **suspend_mobject_updating** (*bool*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    interpolate_mobject(*alpha*)[[source]](../_modules/manim/animation/numbers.html#ChangingDecimal.interpolate_mobject)
    :   Interpolates the mobject of the `Animation` based on alpha value.

        Parameters:
        :   **alpha** (*float*) – A float between 0 and 1 expressing the ratio to which the animation
            is completed. For example, alpha-values of 0, 0.5, and 1 correspond
            to the animation being completed 0%, 50%, and 100%, respectively.

        Return type:
        :   None
