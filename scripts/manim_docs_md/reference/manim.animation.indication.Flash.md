<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.indication.Flash.html -->

# Flash

Qualified name: `manim.animation.indication.Flash`

class Flash(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/indication.html#Flash)
:   Bases: [`AnimationGroup`](manim.animation.composition.AnimationGroup.html#manim.animation.composition.AnimationGroup "manim.animation.composition.AnimationGroup")

    Send out lines in all directions.

    Parameters:
    :   - **point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike") *|* [*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The center of the flash lines. If it is a `Mobject` its center will be used.
        - **line_length** (*float*) – The length of the flash lines.
        - **num_lines** (*int*) – The number of flash lines.
        - **flash_radius** (*float*) – The distance from point at which the flash lines start.
        - **line_stroke_width** (*int*) – The stroke width of the flash lines.
        - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor")) – The color of the flash lines.
        - **time_width** (*float*) – The time width used for the flash lines. See `ShowPassingFlash` for more details.
        - **run_time** (*float*) – The duration of the animation.
        - **kwargs** (*Any*) – Additional arguments to be passed to the [`Succession`](manim.animation.composition.Succession.html#manim.animation.composition.Succession "manim.animation.composition.Succession") constructor

    Examples

    Example: UsingFlash

    [
    ](./UsingFlash-1.mp4)

    ```python
    from manim import *

    class UsingFlash(Scene):
        def construct(self):
            dot = Dot(color=PURE_YELLOW).shift(DOWN)
            self.add(Tex("Flash the dot below:"), dot)
            self.play(Flash(dot))
            self.wait()
    ```

    ```python
    class UsingFlash(Scene):
        def construct(self):
            dot = Dot(color=PURE_YELLOW).shift(DOWN)
            self.add(Tex("Flash the dot below:"), dot)
            self.play(Flash(dot))
            self.wait()
    ```

    Example: FlashOnCircle

    [
    ](./FlashOnCircle-1.mp4)

    ```python
    from manim import *

    class FlashOnCircle(Scene):
        def construct(self):
            radius = 2
            circle = Circle(radius)
            self.add(circle)
            self.play(Flash(
                circle, line_length=1,
                num_lines=30, color=RED,
                flash_radius=radius+SMALL_BUFF,
                time_width=0.3, run_time=2,
                rate_func = rush_from
            ))
    ```

    ```python
    class FlashOnCircle(Scene):
        def construct(self):
            radius = 2
            circle = Circle(radius)
            self.add(circle)
            self.play(Flash(
                circle, line_length=1,
                num_lines=30, color=RED,
                flash_radius=radius+SMALL_BUFF,
                time_width=0.3, run_time=2,
                rate_func = rush_from
            ))
    ```

    Methods

    |  |  |
    | --- | --- |
    | `create_line_anims` |  |
    | `create_lines` |  |

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    _original__init__(*point*, *line_length=0.2*, *num_lines=12*, *flash_radius=0.1*, *line_stroke_width=3*, *color=ManimColor('#FFFF00')*, *time_width=1*, *run_time=1.0*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **point** (*TypeAliasForwardRef**(**'~manim.typing.Point3DLike'**)* *|* [*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **line_length** (*float*)
            - **num_lines** (*int*)
            - **flash_radius** (*float*)
            - **line_stroke_width** (*int*)
            - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))
            - **time_width** (*float*)
            - **run_time** (*float*)
            - **kwargs** (*Any*)
