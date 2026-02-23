<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.transform.TransformFromCopy.html -->

# TransformFromCopy

Qualified name: `manim.animation.transform.TransformFromCopy`

class TransformFromCopy(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/transform.html#TransformFromCopy)
:   Bases: [`Transform`](manim.animation.transform.Transform.html#manim.animation.transform.Transform "manim.animation.transform.Transform")

    Preserves a copy of the original VMobject and transforms only it’s copy to the target VMobject

    Methods

    |  |  |
    | --- | --- |
    | [`interpolate`](#manim.animation.transform.TransformFromCopy.interpolate "manim.animation.transform.TransformFromCopy.interpolate") | Set the animation progress. |

    Attributes

    |  |  |
    | --- | --- |
    | `path_arc` |  |
    | `path_func` |  |
    | `run_time` |  |

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **target_mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))

    _original__init__(*mobject*, *target_mobject*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **target_mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))

        Return type:
        :   None

    interpolate(*alpha*)[[source]](../_modules/manim/animation/transform.html#TransformFromCopy.interpolate)
    :   Set the animation progress.

        This method gets called for every frame during an animation.

        Parameters:
        :   **alpha** (*float*) – The relative time to set the animation to, 0 meaning the start, 1 meaning
            the end.

        Return type:
        :   None
