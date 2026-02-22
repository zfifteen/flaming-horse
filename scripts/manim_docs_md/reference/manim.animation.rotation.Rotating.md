<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.rotation.Rotating.html -->

# Rotating

Qualified name: `manim.animation.rotation.Rotating`

class Rotating(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/rotation.html#Rotating)
:   Bases: [`Animation`](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation")

    Animation that rotates a Mobject.

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")) – The mobject to be rotated.
        - **angle** (*float*) – The rotation angle in radians. Predefined constants such as `DEGREES`
          can also be used to specify the angle in degrees.
        - **axis** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The rotation axis as a numpy vector.
        - **about_point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike") *|* *None*) – The rotation center.
        - **about_edge** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike") *|* *None*) – If `about_point` is `None`, this argument specifies
          the direction of the bounding box point to be taken as
          the rotation center.
        - **run_time** (*float*) – The duration of the animation in seconds.
        - **rate_func** (*Callable**[**[**float**]**,* *float**]*) – The function defining the animation progress based on the relative
          runtime (see [`rate_functions`](manim.utils.rate_functions.html#module-manim.utils.rate_functions "manim.utils.rate_functions")) .
        - ****kwargs** (*Any*) – Additional keyword arguments passed to [`Animation`](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation").

    Examples

    Example: RotatingDemo

    [
    ](./RotatingDemo-1.mp4)

    ```python
    from manim import *

    class RotatingDemo(Scene):
        def construct(self):
            circle = Circle(radius=1, color=BLUE)
            line = Line(start=ORIGIN, end=RIGHT)
            arrow = Arrow(start=ORIGIN, end=RIGHT, buff=0, color=GOLD)
            vg = VGroup(circle,line,arrow)
            self.add(vg)
            anim_kw = {"about_point": arrow.get_start(), "run_time": 1}
            self.play(Rotating(arrow, 180*DEGREES, **anim_kw))
            self.play(Rotating(arrow, PI, **anim_kw))
            self.play(Rotating(vg, PI, about_point=RIGHT))
            self.play(Rotating(vg, PI, axis=UP, about_point=ORIGIN))
            self.play(Rotating(vg, PI, axis=RIGHT, about_edge=UP))
            self.play(vg.animate.move_to(ORIGIN))
    ```

    ```python
    class RotatingDemo(Scene):
        def construct(self):
            circle = Circle(radius=1, color=BLUE)
            line = Line(start=ORIGIN, end=RIGHT)
            arrow = Arrow(start=ORIGIN, end=RIGHT, buff=0, color=GOLD)
            vg = VGroup(circle,line,arrow)
            self.add(vg)
            anim_kw = {"about_point": arrow.get_start(), "run_time": 1}
            self.play(Rotating(arrow, 180*DEGREES, **anim_kw))
            self.play(Rotating(arrow, PI, **anim_kw))
            self.play(Rotating(vg, PI, about_point=RIGHT))
            self.play(Rotating(vg, PI, axis=UP, about_point=ORIGIN))
            self.play(Rotating(vg, PI, axis=RIGHT, about_edge=UP))
            self.play(vg.animate.move_to(ORIGIN))
    ```

    Example: RotatingDifferentAxis

    [
    ](./RotatingDifferentAxis-1.mp4)

    ```python
    from manim import *

    class RotatingDifferentAxis(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            cube = Cube()
            arrow2d = Arrow(start=[0, -1.2, 1], end=[0, 1.2, 1], color=YELLOW_E)
            cube_group = VGroup(cube,arrow2d)
            self.set_camera_orientation(gamma=0, phi=40*DEGREES, theta=40*DEGREES)
            self.add(axes, cube_group)
            play_kw = {"run_time": 1.5}
            self.play(Rotating(cube_group, PI), **play_kw)
            self.play(Rotating(cube_group, PI, axis=UP), **play_kw)
            self.play(Rotating(cube_group, 180*DEGREES, axis=RIGHT), **play_kw)
            self.wait(0.5)
    ```

    ```python
    class RotatingDifferentAxis(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            cube = Cube()
            arrow2d = Arrow(start=[0, -1.2, 1], end=[0, 1.2, 1], color=YELLOW_E)
            cube_group = VGroup(cube,arrow2d)
            self.set_camera_orientation(gamma=0, phi=40*DEGREES, theta=40*DEGREES)
            self.add(axes, cube_group)
            play_kw = {"run_time": 1.5}
            self.play(Rotating(cube_group, PI), **play_kw)
            self.play(Rotating(cube_group, PI, axis=UP), **play_kw)
            self.play(Rotating(cube_group, 180*DEGREES, axis=RIGHT), **play_kw)
            self.wait(0.5)
    ```

    See also

    [`Rotate`](manim.animation.rotation.Rotate.html#manim.animation.rotation.Rotate "manim.animation.rotation.Rotate"), [`rotate()`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject.rotate "manim.mobject.mobject.Mobject.rotate")

    Methods

    |  |  |
    | --- | --- |
    | [`interpolate_mobject`](#manim.animation.rotation.Rotating.interpolate_mobject "manim.animation.rotation.Rotating.interpolate_mobject") | Interpolates the mobject of the `Animation` based on alpha value. |

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    _original__init__(*mobject*, *angle=6.283185307179586*, *axis=array([0.*, *0.*, *1.])*, *about_point=None*, *about_edge=None*, *run_time=5*, *rate_func=<function linear>*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **angle** (*float*)
            - **axis** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
            - **about_point** ([*Point3DLike*](manim.typing.html#manim.typing.Point3DLike "manim.typing.Point3DLike") *|* *None*)
            - **about_edge** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike") *|* *None*)
            - **run_time** (*float*)
            - **rate_func** (*Callable**[**[**float**]**,* *float**]*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    interpolate_mobject(*alpha*)[[source]](../_modules/manim/animation/rotation.html#Rotating.interpolate_mobject)
    :   Interpolates the mobject of the `Animation` based on alpha value.

        Parameters:
        :   **alpha** (*float*) – A float between 0 and 1 expressing the ratio to which the animation
            is completed. For example, alpha-values of 0, 0.5, and 1 correspond
            to the animation being completed 0%, 50%, and 100%, respectively.

        Return type:
        :   None
