<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.shape_matchers.Underline.html -->

# Underline

Qualified name: `manim.mobject.geometry.shape\_matchers.Underline`

class Underline(*mobject*, *buff=0.1*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/shape_matchers.html#Underline)
:   Bases: [`Line`](manim.mobject.geometry.line.Line.html#manim.mobject.geometry.line.Line "manim.mobject.geometry.line.Line")

    Creates an underline.

    Examples

    Example: UnderLine

    ```python
    from manim import *

    class UnderLine(Scene):
        def construct(self):
            man = Tex("Manim")  # Full Word
            ul = Underline(man)  # Underlining the word
            self.add(man, ul)
    ```

    ```python
    class UnderLine(Scene):
        def construct(self):
            man = Tex("Manim")  # Full Word
            ul = Underline(man)  # Underlining the word
            self.add(man, ul)
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
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **buff** (*float*)
        - **kwargs** (*Any*)

    _original__init__(*mobject*, *buff=0.1*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **buff** (*float*)
            - **kwargs** (*Any*)

        Return type:
        :   None
