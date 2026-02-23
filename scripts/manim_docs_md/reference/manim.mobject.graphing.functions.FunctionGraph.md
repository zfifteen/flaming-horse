<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.graphing.functions.FunctionGraph.html -->

# FunctionGraph

Qualified name: `manim.mobject.graphing.functions.FunctionGraph`

class FunctionGraph(*function*, *x_range=None*, *color=ManimColor('#FFFF00')*, ***kwargs*)[[source]](../_modules/manim/mobject/graphing/functions.html#FunctionGraph)
:   Bases: [`ParametricFunction`](manim.mobject.graphing.functions.ParametricFunction.html#manim.mobject.graphing.functions.ParametricFunction "manim.mobject.graphing.functions.ParametricFunction")

    A [`ParametricFunction`](manim.mobject.graphing.functions.ParametricFunction.html#manim.mobject.graphing.functions.ParametricFunction "manim.mobject.graphing.functions.ParametricFunction") that spans the length of the scene by default.

    Examples

    Example: ExampleFunctionGraph

    ```python
    from manim import *

    class ExampleFunctionGraph(Scene):
        def construct(self):
            cos_func = FunctionGraph(
                lambda t: np.cos(t) + 0.5 * np.cos(7 * t) + (1 / 7) * np.cos(14 * t),
                color=RED,
            )

            sin_func_1 = FunctionGraph(
                lambda t: np.sin(t) + 0.5 * np.sin(7 * t) + (1 / 7) * np.sin(14 * t),
                color=BLUE,
            )

            sin_func_2 = FunctionGraph(
                lambda t: np.sin(t) + 0.5 * np.sin(7 * t) + (1 / 7) * np.sin(14 * t),
                x_range=[-4, 4],
                color=GREEN,
            ).move_to([0, 1, 0])

            self.add(cos_func, sin_func_1, sin_func_2)
    ```

    ```python
    class ExampleFunctionGraph(Scene):
        def construct(self):
            cos_func = FunctionGraph(
                lambda t: np.cos(t) + 0.5 * np.cos(7 * t) + (1 / 7) * np.cos(14 * t),
                color=RED,
            )

            sin_func_1 = FunctionGraph(
                lambda t: np.sin(t) + 0.5 * np.sin(7 * t) + (1 / 7) * np.sin(14 * t),
                color=BLUE,
            )

            sin_func_2 = FunctionGraph(
                lambda t: np.sin(t) + 0.5 * np.sin(7 * t) + (1 / 7) * np.sin(14 * t),
                x_range=[-4, 4],
                color=GREEN,
            ).move_to([0, 1, 0])

            self.add(cos_func, sin_func_1, sin_func_2)
    ```

    Methods

    |  |  |
    | --- | --- |
    | `get_function` |  |
    | `get_point_from_function` |  |

    Attributes

    |  |  |
    | --- | --- |
    | `always` | Call a method on a mobject every frame. |
    | `animate` | Used to animate the application of any method of `self`. |
    | `animation_overrides` |  |
    | `color` |  |
    | `depth` | The depth of the mobject. |
    | `fill_color` | If there are multiple colors (for gradient) this returns the first one |
    | `height` | The height of the mobject. |
    | `n_points_per_curve` |  |
    | `sheen_factor` |  |
    | `stroke_color` |  |
    | `width` | The width of the mobject. |

    Parameters:
    :   - **function** (*Callable**[**[**float**]**,* *Any**]*)
        - **x_range** (*tuple**[**float**,* *float**]* *|* *tuple**[**float**,* *float**,* *float**]* *|* *None*)
        - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
        - **kwargs** (*Any*)

    _original__init__(*function*, *x_range=None*, *color=ManimColor('#FFFF00')*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **function** (*Callable**[**[**float**]**,* *Any**]*)
            - **x_range** (*tuple**[**float**,* *float**]* *|* *tuple**[**float**,* *float**,* *float**]* *|* *None*)
            - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
            - **kwargs** (*Any*)

        Return type:
        :   None
