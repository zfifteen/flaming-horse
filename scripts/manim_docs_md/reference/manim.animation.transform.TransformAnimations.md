<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.transform.TransformAnimations.html -->

# TransformAnimations

Qualified name: `manim.animation.transform.TransformAnimations`

class TransformAnimations(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/transform.html#TransformAnimations)
:   Bases: [`Transform`](manim.animation.transform.Transform.html#manim.animation.transform.Transform "manim.animation.transform.Transform")

    Methods

    |  |  |
    | --- | --- |
    | [`interpolate`](#manim.animation.transform.TransformAnimations.interpolate "manim.animation.transform.TransformAnimations.interpolate") | Set the animation progress. |

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    Parameters:
    :   - **start_anim** ([*Animation*](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation"))
        - **end_anim** ([*Animation*](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation"))
        - **rate_func** (*Callable*)

    _original__init__(*start_anim*, *end_anim*, *rate_func=<function squish_rate_func.<locals>.result>*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **start_anim** ([*Animation*](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation"))
            - **end_anim** ([*Animation*](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation"))
            - **rate_func** (*Callable*)

        Return type:
        :   None

    interpolate(*alpha*)[[source]](../_modules/manim/animation/transform.html#TransformAnimations.interpolate)
    :   Set the animation progress.

        This method gets called for every frame during an animation.

        Parameters:
        :   **alpha** (*float*) – The relative time to set the animation to, 0 meaning the start, 1 meaning
            the end.

        Return type:
        :   None
