<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.numbers.ChangeDecimalToValue.html -->

# ChangeDecimalToValue

Qualified name: `manim.animation.numbers.ChangeDecimalToValue`

class ChangeDecimalToValue(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/numbers.html#ChangeDecimalToValue)
:   Bases: [`ChangingDecimal`](manim.animation.numbers.ChangingDecimal.html#manim.animation.numbers.ChangingDecimal "manim.animation.numbers.ChangingDecimal")

    Animate a [`DecimalNumber`](manim.mobject.text.numbers.DecimalNumber.html#manim.mobject.text.numbers.DecimalNumber "manim.mobject.text.numbers.DecimalNumber") to a target value using linear interpolation.

    Parameters:
    :   - **decimal_mob** ([*DecimalNumber*](manim.mobject.text.numbers.DecimalNumber.html#manim.mobject.text.numbers.DecimalNumber "manim.mobject.text.numbers.DecimalNumber")) – The [`DecimalNumber`](manim.mobject.text.numbers.DecimalNumber.html#manim.mobject.text.numbers.DecimalNumber "manim.mobject.text.numbers.DecimalNumber") instance to animate.
        - **target_number** (*int*) – The target value to transition to.
        - **kwargs** (*Any*)

    Examples

    Example: ChangeDecimalToValueExample

    [
    ](./ChangeDecimalToValueExample-1.mp4)

    ```python
    from manim import *

    class ChangeDecimalToValueExample(Scene):
        def construct(self):
            number = DecimalNumber(0)
            self.add(number)
            self.play(ChangeDecimalToValue(number, 10, run_time=3))
            self.wait()
    ```

    ```python
    class ChangeDecimalToValueExample(Scene):
        def construct(self):
            number = DecimalNumber(0)
            self.add(number)
            self.play(ChangeDecimalToValue(number, 10, run_time=3))
            self.wait()
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    _original__init__(*decimal_mob*, *target_number*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **decimal_mob** ([*DecimalNumber*](manim.mobject.text.numbers.DecimalNumber.html#manim.mobject.text.numbers.DecimalNumber "manim.mobject.text.numbers.DecimalNumber"))
            - **target_number** (*int*)
            - **kwargs** (*Any*)

        Return type:
        :   None
