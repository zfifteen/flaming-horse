<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.updaters.update.UpdateFromAlphaFunc.html -->

# UpdateFromAlphaFunc

Qualified name: `manim.animation.updaters.update.UpdateFromAlphaFunc`

class UpdateFromAlphaFunc(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/updaters/update.html#UpdateFromAlphaFunc)
:   Bases: [`UpdateFromFunc`](manim.animation.updaters.update.UpdateFromFunc.html#manim.animation.updaters.update.UpdateFromFunc "manim.animation.updaters.update.UpdateFromFunc")

    Methods

    |  |  |
    | --- | --- |
    | [`interpolate_mobject`](#manim.animation.updaters.update.UpdateFromAlphaFunc.interpolate_mobject "manim.animation.updaters.update.UpdateFromAlphaFunc.interpolate_mobject") | Interpolates the mobject of the `Animation` based on alpha value. |

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **update_function** (*Callable**[**[*[*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")*]**,* *Any**]*)
        - **suspend_mobject_updating** (*bool*)
        - **kwargs** (*Any*)

    _original__init__(*mobject*, *update_function*, *suspend_mobject_updating=False*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **update_function** (*Callable**[**[*[*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")*]**,* *Any**]*)
            - **suspend_mobject_updating** (*bool*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    interpolate_mobject(*alpha*)[[source]](../_modules/manim/animation/updaters/update.html#UpdateFromAlphaFunc.interpolate_mobject)
    :   Interpolates the mobject of the `Animation` based on alpha value.

        Parameters:
        :   **alpha** (*float*) – A float between 0 and 1 expressing the ratio to which the animation
            is completed. For example, alpha-values of 0, 0.5, and 1 correspond
            to the animation being completed 0%, 50%, and 100%, respectively.

        Return type:
        :   None
