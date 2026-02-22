<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.indication.Circumscribe.html -->

# Circumscribe

Qualified name: `manim.animation.indication.Circumscribe`

class Circumscribe(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/indication.html#Circumscribe)
:   Bases: [`Succession`](manim.animation.composition.Succession.html#manim.animation.composition.Succession "manim.animation.composition.Succession")

    Draw a temporary line surrounding the mobject.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobject to be circumscribed.
        - **shape** (*type**[*[*Rectangle*](manim.mobject.geometry.polygram.Rectangle.html#manim.mobject.geometry.polygram.Rectangle "manim.mobject.geometry.polygram.Rectangle")*]* *|* *type**[*[*Circle*](manim.mobject.geometry.arc.Circle.html#manim.mobject.geometry.arc.Circle "manim.mobject.geometry.arc.Circle")*]*) – The shape with which to surround the given mobject. Should be either
          [`Rectangle`](manim.mobject.geometry.polygram.Rectangle.html#manim.mobject.geometry.polygram.Rectangle "manim.mobject.geometry.polygram.Rectangle") or [`Circle`](manim.mobject.geometry.arc.Circle.html#manim.mobject.geometry.arc.Circle "manim.mobject.geometry.arc.Circle")
        - **fade_in** (*bool*) – Whether to make the surrounding shape to fade in. It will be drawn otherwise.
        - **fade_out** (*bool*) – Whether to make the surrounding shape to fade out. It will be undrawn otherwise.
        - **time_width** (*float*) – The time_width of the drawing and undrawing. Gets ignored if either fade_in or fade_out is True.
        - **buff** (*float*) – The distance between the surrounding shape and the given mobject.
        - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor")) – The color of the surrounding shape.
        - **run_time** (*float*) – The duration of the entire animation.
        - **kwargs** (*Any*) – Additional arguments to be passed to the [`Succession`](manim.animation.composition.Succession.html#manim.animation.composition.Succession "manim.animation.composition.Succession") constructor
        - **stroke_width** (*float*)

    Examples

    Example: UsingCircumscribe

    [
    ](./UsingCircumscribe-1.mp4)

    ```python
    from manim import *

    class UsingCircumscribe(Scene):
        def construct(self):
            lbl = Tex(r"Circum-\\scribe").scale(2)
            self.add(lbl)
            self.play(Circumscribe(lbl))
            self.play(Circumscribe(lbl, Circle))
            self.play(Circumscribe(lbl, fade_out=True))
            self.play(Circumscribe(lbl, time_width=2))
            self.play(Circumscribe(lbl, Circle, True))
    ```

    ```python
    class UsingCircumscribe(Scene):
        def construct(self):
            lbl = Tex(r"Circum-\\scribe").scale(2)
            self.add(lbl)
            self.play(Circumscribe(lbl))
            self.play(Circumscribe(lbl, Circle))
            self.play(Circumscribe(lbl, fade_out=True))
            self.play(Circumscribe(lbl, time_width=2))
            self.play(Circumscribe(lbl, Circle, True))
    ```

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    _original__init__(*mobject*, *shape=<class 'manim.mobject.geometry.polygram.Rectangle'>*, *fade_in=False*, *fade_out=False*, *time_width=0.3*, *buff=0.1*, *color=ManimColor('#FFFF00')*, *run_time=1*, *stroke_width=4*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **shape** (*type**[*[*Rectangle*](manim.mobject.geometry.polygram.Rectangle.html#manim.mobject.geometry.polygram.Rectangle "manim.mobject.geometry.polygram.Rectangle")*]* *|* *type**[*[*Circle*](manim.mobject.geometry.arc.Circle.html#manim.mobject.geometry.arc.Circle "manim.mobject.geometry.arc.Circle")*]*)
            - **fade_in** (*bool*)
            - **fade_out** (*bool*)
            - **time_width** (*float*)
            - **buff** (*float*)
            - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
            - **run_time** (*float*)
            - **stroke_width** (*float*)
            - **kwargs** (*Any*)
