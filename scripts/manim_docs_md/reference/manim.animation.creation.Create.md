<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.creation.Create.html -->

# Create

Qualified name: `manim.animation.creation.Create`

class Create(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/creation.html#Create)
:   Bases: [`ShowPartial`](manim.animation.creation.ShowPartial.html#manim.animation.creation.ShowPartial "manim.animation.creation.ShowPartial")

    Incrementally show a VMobject.

    Parameters:
    :   - **mobject** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") *|* *OpenGLVMobject* *|* *OpenGLSurface*) – The VMobject to animate.
        - **lag_ratio** (*float*)
        - **introducer** (*bool*)

    Raises:
    :   **TypeError** – If `mobject` is not an instance of [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject").

    Examples

    Example: CreateScene

    [
    ](./CreateScene-1.mp4)

    ```python
    from manim import *

    class CreateScene(Scene):
        def construct(self):
            self.play(Create(Square()))
    ```

    ```python
    class CreateScene(Scene):
        def construct(self):
            self.play(Create(Square()))
    ```

    See also

    [`ShowPassingFlash`](manim.animation.indication.ShowPassingFlash.html#manim.animation.indication.ShowPassingFlash "manim.animation.indication.ShowPassingFlash")

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    _original__init__(*mobject*, *lag_ratio=1.0*, *introducer=True*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject") *|* *OpenGLVMobject* *|* *OpenGLSurface*)
            - **lag_ratio** (*float*)
            - **introducer** (*bool*)

        Return type:
        :   None
