<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.animation.html -->

# animation

Animate mobjects.

Classes

|  |  |
| --- | --- |
| [`Add`](manim.animation.animation.Add.html#manim.animation.animation.Add "manim.animation.animation.Add") | Add Mobjects to a scene, without animating them in any other way. |
| [`Animation`](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation") | An animation. |
| [`Wait`](manim.animation.animation.Wait.html#manim.animation.animation.Wait "manim.animation.animation.Wait") | A "no operation" animation. |

Functions

override_animation(*animation_class*)[[source]](../_modules/manim/animation/animation.html#override_animation)
:   Decorator used to mark methods as overrides for specific [`Animation`](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation") types.

    Should only be used to decorate methods of classes derived from [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject").
    `Animation` overrides get inherited to subclasses of the `Mobject` who defined
    them. They don’t override subclasses of the `Animation` they override.

    See also

    [`add_animation_override()`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject.add_animation_override "manim.mobject.mobject.Mobject.add_animation_override")

    Parameters:
    :   **animation_class** (*type**[*[*Animation*](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation")*]*) – The animation to be overridden.

    Returns:
    :   The actual decorator. This marks the method as overriding an animation.

    Return type:
    :   Callable[[Callable], Callable]

    Examples

    Example: OverrideAnimationExample

    [
    ](./OverrideAnimationExample-1.mp4)

    ```python
    from manim import *

    class MySquare(Square):
        @override_animation(FadeIn)
        def _fade_in_override(self, **kwargs):
            return Create(self, **kwargs)

    class OverrideAnimationExample(Scene):
        def construct(self):
            self.play(FadeIn(MySquare()))
    ```

    ```python
    class MySquare(Square):
        @override_animation(FadeIn)
        def _fade_in_override(self, **kwargs):
            return Create(self, **kwargs)

    class OverrideAnimationExample(Scene):
        def construct(self):
            self.play(FadeIn(MySquare()))
    ```

prepare_animation(*anim*)[[source]](../_modules/manim/animation/animation.html#prepare_animation)
:   Returns either an unchanged animation, or the animation built
    from a passed animation factory.

    Examples

    ```python
    >>> from manim import Square, FadeIn
    >>> s = Square()
    >>> prepare_animation(FadeIn(s))
    FadeIn(Square)
    ```

    ```python
    >>> prepare_animation(s.animate.scale(2).rotate(42))
    _MethodAnimation(Square)
    ```

    ```python
    >>> prepare_animation(42)
    Traceback (most recent call last):
    ...
    TypeError: Object 42 cannot be converted to an animation
    ```

    Parameters:
    :   **anim** ([*Animation*](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation") *|* *_AnimationBuilder* *|* *_AnimationBuilder*)

    Return type:
    :   [*Animation*](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation")
