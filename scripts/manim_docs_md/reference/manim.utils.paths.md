<!-- source: https://docs.manim.community/en/stable/reference/manim.utils.paths.html -->

# paths

Functions determining transformation paths between sets of points.

Functions

clockwise_path()[[source]](../_modules/manim/utils/paths.html#clockwise_path)
:   This function transforms each point by moving clockwise around a half circle.

    Examples

    Example: ClockwisePathExample

    [
    ](./ClockwisePathExample-1.mp4)

    ```python
    from manim import *

    class ClockwisePathExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.clockwise_path(),
                    run_time=2,
                )
            )
            self.wait()
    ```

    ```python
    class ClockwisePathExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.clockwise_path(),
                    run_time=2,
                )
            )
            self.wait()
    ```

    Return type:
    :   [*PathFuncType*](manim.typing.html#manim.typing.PathFuncType "manim.typing.PathFuncType")

counterclockwise_path()[[source]](../_modules/manim/utils/paths.html#counterclockwise_path)
:   This function transforms each point by moving counterclockwise around a half circle.

    Examples

    Example: CounterclockwisePathExample

    [
    ](./CounterclockwisePathExample-1.mp4)

    ```python
    from manim import *

    class CounterclockwisePathExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.counterclockwise_path(),
                    run_time=2,
                )
            )
            self.wait()
    ```

    ```python
    class CounterclockwisePathExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.counterclockwise_path(),
                    run_time=2,
                )
            )
            self.wait()
    ```

    Return type:
    :   [*PathFuncType*](manim.typing.html#manim.typing.PathFuncType "manim.typing.PathFuncType")

path_along_arc(*arc_angle*, *axis=array([0., 0., 1.])*)[[source]](../_modules/manim/utils/paths.html#path_along_arc)
:   This function transforms each point by moving it along a circular arc.

    Parameters:
    :   - **arc_angle** (*float*) – The angle each point traverses around a circular arc.
        - **axis** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The axis of rotation.

    Return type:
    :   [*PathFuncType*](manim.typing.html#manim.typing.PathFuncType "manim.typing.PathFuncType")

    Examples

    Example: PathAlongArcExample

    [
    ](./PathAlongArcExample-1.mp4)

    ```python
    from manim import *

    class PathAlongArcExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.path_along_arc(TAU * 2 / 3),
                    run_time=3,
                )
            )
            self.wait()
    ```

    ```python
    class PathAlongArcExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.path_along_arc(TAU * 2 / 3),
                    run_time=3,
                )
            )
            self.wait()
    ```

path_along_circles(*arc_angle*, *circles_centers*, *axis=array([0., 0., 1.])*)[[source]](../_modules/manim/utils/paths.html#path_along_circles)
:   This function transforms each point by moving it roughly along a circle, each with its own specified center.

    The path may be seen as each point smoothly changing its orbit from its starting position to its destination.

    Parameters:
    :   - **arc_angle** (*float*) – The angle each point traverses around the quasicircle.
        - **circles_centers** ([*Point3DLike_Array*](manim.typing.html#manim.typing.Point3DLike_Array "manim.typing.Point3DLike_Array")) – The centers of each point’s quasicircle to rotate around.
        - **axis** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The axis of rotation.

    Return type:
    :   [*PathFuncType*](manim.typing.html#manim.typing.PathFuncType "manim.typing.PathFuncType")

    Examples

    Example: PathAlongCirclesExample

    [
    ](./PathAlongCirclesExample-1.mp4)

    ```python
    from manim import *

    class PathAlongCirclesExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            circle_center = Dot(3 * LEFT)
            self.add(circle_center)

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.path_along_circles(
                        2 * PI, circle_center.get_center()
                    ),
                    run_time=3,
                )
            )
            self.wait()
    ```

    ```python
    class PathAlongCirclesExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            circle_center = Dot(3 * LEFT)
            self.add(circle_center)

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.path_along_circles(
                        2 * PI, circle_center.get_center()
                    ),
                    run_time=3,
                )
            )
            self.wait()
    ```

spiral_path(*angle*, *axis=array([0., 0., 1.])*)[[source]](../_modules/manim/utils/paths.html#spiral_path)
:   This function transforms each point by moving along a spiral to its destination.

    Parameters:
    :   - **angle** (*float*) – The angle each point traverses around a spiral.
        - **axis** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike")) – The axis of rotation.

    Return type:
    :   [*PathFuncType*](manim.typing.html#manim.typing.PathFuncType "manim.typing.PathFuncType")

    Examples

    Example: SpiralPathExample

    [
    ](./SpiralPathExample-1.mp4)

    ```python
    from manim import *

    class SpiralPathExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.spiral_path(2 * TAU),
                    run_time=5,
                )
            )
            self.wait()
    ```

    ```python
    class SpiralPathExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.spiral_path(2 * TAU),
                    run_time=5,
                )
            )
            self.wait()
    ```

straight_path()[[source]](../_modules/manim/utils/paths.html#straight_path)
:   Simplest path function. Each point in a set goes in a straight path toward its destination.

    Examples

    Example: StraightPathExample

    [
    ](./StraightPathExample-1.mp4)

    ```python
    from manim import *

    class StraightPathExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.straight_path(),
                    run_time=2,
                )
            )
            self.wait()
    ```

    ```python
    class StraightPathExample(Scene):
        def construct(self):
            colors = [RED, GREEN, BLUE]

            starting_points = VGroup(
                *[
                    Dot(LEFT + pos, color=color)
                    for pos, color in zip([UP, DOWN, LEFT], colors)
                ]
            )

            finish_points = VGroup(
                *[
                    Dot(RIGHT + pos, color=color)
                    for pos, color in zip([ORIGIN, UP, DOWN], colors)
                ]
            )

            self.add(starting_points)
            self.add(finish_points)
            for dot in starting_points:
                self.add(TracedPath(dot.get_center, stroke_color=dot.get_color()))

            self.wait()
            self.play(
                Transform(
                    starting_points,
                    finish_points,
                    path_func=utils.paths.straight_path(),
                    run_time=2,
                )
            )
            self.wait()
    ```

    Return type:
    :   [*PathFuncType*](manim.typing.html#manim.typing.PathFuncType "manim.typing.PathFuncType")
