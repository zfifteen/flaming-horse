<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.matrix.MobjectMatrix.html -->

# MobjectMatrix

Qualified name: `manim.mobject.matrix.MobjectMatrix`

class MobjectMatrix(*matrix*, *element_to_mobject=<function MobjectMatrix.<lambda>>*, ***kwargs*)[[source]](../_modules/manim/mobject/matrix.html#MobjectMatrix)
:   Bases: [`Matrix`](manim.mobject.matrix.Matrix.html#manim.mobject.matrix.Matrix "manim.mobject.matrix.Matrix")

    A mobject that displays a matrix of mobject entries on the screen.

    Examples

    Example: MobjectMatrixExample

    ```python
    from manim import *

    class MobjectMatrixExample(Scene):
        def construct(self):
            a = Circle().scale(0.3)
            b = Square().scale(0.3)
            c = MathTex("\\pi").scale(2)
            d = Star().scale(0.3)
            m0 = MobjectMatrix([[a, b], [c, d]])
            self.add(m0)
    ```

    ```python
    class MobjectMatrixExample(Scene):
        def construct(self):
            a = Circle().scale(0.3)
            b = Square().scale(0.3)
            c = MathTex("\\pi").scale(2)
            d = Star().scale(0.3)
            m0 = MobjectMatrix([[a, b], [c, d]])
            self.add(m0)
    ```

    Methods

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
    :   - **matrix** (*Iterable*)
        - **element_to_mobject** (*type**[*[*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")*]* *|* *Callable**[**...**,* [*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")*]*)
        - **kwargs** (*Any*)

    _original__init__(*matrix*, *element_to_mobject=<function MobjectMatrix.<lambda>>*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **matrix** (*Iterable*)
            - **element_to_mobject** (*type**[*[*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")*]* *|* *Callable**[**[**...**]**,* [*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")*]*)
            - **kwargs** (*Any*)
