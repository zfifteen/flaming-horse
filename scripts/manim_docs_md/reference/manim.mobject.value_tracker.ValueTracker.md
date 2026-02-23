<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.value_tracker.ValueTracker.html -->

# ValueTracker

Qualified name: `manim.mobject.value\_tracker.ValueTracker`

class ValueTracker(*value=0*, ***kwargs*)[[source]](../_modules/manim/mobject/value_tracker.html#ValueTracker)
:   Bases: [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")

    A mobject that can be used for tracking (real-valued) parameters.
    Useful for animating parameter changes.

    Not meant to be displayed. Instead the position encodes some
    number, often one which another animation or continual_animation
    uses for its update function, and by treating it as a mobject it can
    still be animated and manipulated just like anything else.

    This value changes continuously when animated using the `animate` syntax.

    Examples

    Example: ValueTrackerExample

    [
    ](./ValueTrackerExample-1.mp4)

    ```python
    from manim import *

    class ValueTrackerExample(Scene):
        def construct(self):
            number_line = NumberLine()
            pointer = Vector(DOWN)
            label = MathTex("x").add_updater(lambda m: m.next_to(pointer, UP))

            tracker = ValueTracker(0)
            pointer.add_updater(
                lambda m: m.next_to(
                            number_line.n2p(tracker.get_value()),
                            UP
                        )
            )
            self.add(number_line, pointer,label)
            tracker += 1.5
            self.wait(1)
            tracker -= 4
            self.wait(0.5)
            self.play(tracker.animate.set_value(5))
            self.wait(0.5)
            self.play(tracker.animate.set_value(3))
            self.play(tracker.animate.increment_value(-2))
            self.wait(0.5)
    ```

    ```python
    class ValueTrackerExample(Scene):
        def construct(self):
            number_line = NumberLine()
            pointer = Vector(DOWN)
            label = MathTex("x").add_updater(lambda m: m.next_to(pointer, UP))

            tracker = ValueTracker(0)
            pointer.add_updater(
                lambda m: m.next_to(
                            number_line.n2p(tracker.get_value()),
                            UP
                        )
            )
            self.add(number_line, pointer,label)
            tracker += 1.5
            self.wait(1)
            tracker -= 4
            self.wait(0.5)
            self.play(tracker.animate.set_value(5))
            self.wait(0.5)
            self.play(tracker.animate.set_value(3))
            self.play(tracker.animate.increment_value(-2))
            self.wait(0.5)
    ```

    Note

    You can also link ValueTrackers to updaters. In this case, you have to make sure that the
    ValueTracker is added to the scene by `add`

    Example: ValueTrackerExample

    [
    ](./ValueTrackerExample-2.mp4)

    ```python
    from manim import *

    class ValueTrackerExample(Scene):
        def construct(self):
            tracker = ValueTracker(0)
            label = Dot(radius=3).add_updater(lambda x : x.set_x(tracker.get_value()))
            self.add(label)
            self.add(tracker)
            tracker.add_updater(lambda mobject, dt: mobject.increment_value(dt))
            self.wait(2)
    ```

    ```python
    class ValueTrackerExample(Scene):
        def construct(self):
            tracker = ValueTracker(0)
            label = Dot(radius=3).add_updater(lambda x : x.set_x(tracker.get_value()))
            self.add(label)
            self.add(tracker)
            tracker.add_updater(lambda mobject, dt: mobject.increment_value(dt))
            self.wait(2)
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`get_value`](#manim.mobject.value_tracker.ValueTracker.get_value "manim.mobject.value_tracker.ValueTracker.get_value") | Get the current value of this ValueTracker. |
    | [`increment_value`](#manim.mobject.value_tracker.ValueTracker.increment_value "manim.mobject.value_tracker.ValueTracker.increment_value") | Increments (adds) a scalar value to the ValueTracker. |
    | [`interpolate`](#manim.mobject.value_tracker.ValueTracker.interpolate "manim.mobject.value_tracker.ValueTracker.interpolate") | Turns `self` into an interpolation between `mobject1` and `mobject2`. |
    | [`set_value`](#manim.mobject.value_tracker.ValueTracker.set_value "manim.mobject.value_tracker.ValueTracker.set_value") | Sets a new scalar value to the ValueTracker. |

    Attributes

    |  |  |
    | --- | --- |
    | `always` | Call a method on a mobject every frame. |
    | `animate` | Used to animate the application of any method of `self`. |
    | `animation_overrides` |  |
    | `depth` | The depth of the mobject. |
    | `height` | The height of the mobject. |
    | `width` | The width of the mobject. |

    Parameters:
    :   - **value** (*float*)
        - **kwargs** (*Any*)

    _original__init__(*value=0*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **value** (*float*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    get_value()[[source]](../_modules/manim/mobject/value_tracker.html#ValueTracker.get_value)
    :   Get the current value of this ValueTracker.

        Return type:
        :   float

    increment_value(*d_value*)[[source]](../_modules/manim/mobject/value_tracker.html#ValueTracker.increment_value)
    :   Increments (adds) a scalar value to the ValueTracker.

        Parameters:
        :   **d_value** (*float*)

        Return type:
        :   Self

    interpolate(*mobject1*, *mobject2*, *alpha*, *path_func=<function interpolate>*)[[source]](../_modules/manim/mobject/value_tracker.html#ValueTracker.interpolate)
    :   Turns `self` into an interpolation between `mobject1` and `mobject2`.

        Parameters:
        :   - **mobject1** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **mobject2** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **alpha** (*float*)
            - **path_func** ([*PathFuncType*](manim.typing.html#manim.typing.PathFuncType "manim.typing.PathFuncType"))

        Return type:
        :   Self

    set_value(*value*)[[source]](../_modules/manim/mobject/value_tracker.html#ValueTracker.set_value)
    :   Sets a new scalar value to the ValueTracker.

        Parameters:
        :   **value** (*float*)

        Return type:
        :   Self
