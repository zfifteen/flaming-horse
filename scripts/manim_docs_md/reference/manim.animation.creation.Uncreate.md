<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.creation.Uncreate.html -->

# Uncreate

Qualified name: `manim.animation.creation.Uncreate`

class Uncreate(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/creation.html#Uncreate)
:   Bases: [`Create`](manim.animation.creation.Create.html#manim.animation.creation.Create "manim.animation.creation.Create")

    Like [`Create`](manim.animation.creation.Create.html#manim.animation.creation.Create "manim.animation.creation.Create") but in reverse.

    Examples

    Example: ShowUncreate

    [
    ](./ShowUncreate-1.mp4)

    ```python
    from manim import *

    class ShowUncreate(Scene):
        def construct(self):
            self.play(Uncreate(Square()))
    ```

    ```python
    class ShowUncreate(Scene):
        def construct(self):
            self.play(Uncreate(Square()))
    ```

    See also

    [`Create`](manim.animation.creation.Create.html#manim.animation.creation.Create "manim.animation.creation.Create")

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    Parameters:
    :   - **mobject** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") *|* *OpenGLVMobject*)
        - **reverse_rate_function** (*bool*)
        - **remover** (*bool*)

    _original__init__(*mobject*, *reverse_rate_function=True*, *remover=True*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") *|* *OpenGLVMobject*)
            - **reverse_rate_function** (*bool*)
            - **remover** (*bool*)

        Return type:
        :   None
