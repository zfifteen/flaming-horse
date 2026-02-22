<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.shape_matchers.BackgroundRectangle.html -->

# BackgroundRectangle

Qualified name: `manim.mobject.geometry.shape\_matchers.BackgroundRectangle`

class BackgroundRectangle(**mobjects*, *color=None*, *stroke_width=0*, *stroke_opacity=0*, *fill_opacity=0.75*, *buff=0*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/shape_matchers.html#BackgroundRectangle)
:   Bases: [`SurroundingRectangle`](manim.mobject.geometry.shape_matchers.SurroundingRectangle.html#manim.mobject.geometry.shape_matchers.SurroundingRectangle "manim.mobject.geometry.shape_matchers.SurroundingRectangle")

    A background rectangle. Its default color is the background color
    of the scene.

    Examples

    Example: ExampleBackgroundRectangle

    ```python
    from manim import *

    class ExampleBackgroundRectangle(Scene):
        def construct(self):
            circle = Circle().shift(LEFT)
            circle.set_stroke(color=GREEN, width=20)
            triangle = Triangle().shift(2 * RIGHT)
            triangle.set_fill(PINK, opacity=0.5)
            backgroundRectangle1 = BackgroundRectangle(circle, color=WHITE, fill_opacity=0.15)
            backgroundRectangle2 = BackgroundRectangle(triangle, color=WHITE, fill_opacity=0.15)
            self.add(backgroundRectangle1)
            self.add(backgroundRectangle2)
            self.add(circle)
            self.add(triangle)
            self.play(Rotate(backgroundRectangle1, PI / 4))
            self.play(Rotate(backgroundRectangle2, PI / 2))
    ```

    ```python
    class ExampleBackgroundRectangle(Scene):
        def construct(self):
            circle = Circle().shift(LEFT)
            circle.set_stroke(color=GREEN, width=20)
            triangle = Triangle().shift(2 * RIGHT)
            triangle.set_fill(PINK, opacity=0.5)
            backgroundRectangle1 = BackgroundRectangle(circle, color=WHITE, fill_opacity=0.15)
            backgroundRectangle2 = BackgroundRectangle(triangle, color=WHITE, fill_opacity=0.15)
            self.add(backgroundRectangle1)
            self.add(backgroundRectangle2)
            self.add(circle)
            self.add(triangle)
            self.play(Rotate(backgroundRectangle1, PI / 4))
            self.play(Rotate(backgroundRectangle2, PI / 2))
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`pointwise_become_partial`](#manim.mobject.geometry.shape_matchers.BackgroundRectangle.pointwise_become_partial "manim.mobject.geometry.shape_matchers.BackgroundRectangle.pointwise_become_partial") | Given a 2nd [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") `vmobject`, a lower bound `a` and an upper bound `b`, modify this [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")'s points to match the portion of the Bézier spline described by `vmobject.points` with the parameter `t` between `a` and `b`. |
    | `set_style` |  |

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
    :   - **mobjects** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*)
        - **stroke_width** (*float*)
        - **stroke_opacity** (*float*)
        - **fill_opacity** (*float*)
        - **buff** (*float* *|* *tuple**[**float**,* *float**]*)
        - **kwargs** (*Any*)

    _original__init__(**mobjects*, *color=None*, *stroke_width=0*, *stroke_opacity=0*, *fill_opacity=0.75*, *buff=0*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobjects** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **color** (*TypeAliasForwardRef**(**'~manim.utils.color.core.ParsableManimColor'**)* *|* *None*)
            - **stroke_width** (*float*)
            - **stroke_opacity** (*float*)
            - **fill_opacity** (*float*)
            - **buff** (*float* *|* *tuple**[**float**,* *float**]*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    pointwise_become_partial(*mobject*, *a*, *b*)[[source]](../_modules/manim/mobject/geometry/shape_matchers.html#BackgroundRectangle.pointwise_become_partial)
    :   Given a 2nd [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") `vmobject`, a lower bound `a` and
        an upper bound `b`, modify this [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")’s points to
        match the portion of the Bézier spline described by `vmobject.points`
        with the parameter `t` between `a` and `b`.

        Parameters:
        :   - **vmobject** – The [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") that will serve as a model.
            - **a** (*Any*) – The lower bound for `t`.
            - **b** (*float*) – The upper bound for `t`
            - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))

        Returns:
        :   The [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") itself, after the transformation.

        Return type:
        :   [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")

        Raises:
        :   **TypeError** – If `vmobject` is not an instance of `VMobject`.
