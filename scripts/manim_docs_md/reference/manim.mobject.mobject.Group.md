<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.mobject.Group.html -->

# Group

Qualified name: `manim.mobject.mobject.Group`

class Group(**mobjects*, ***kwargs*)[[source]](../_modules/manim/mobject/mobject.html#Group)
:   Bases: [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")

    Groups together multiple [`Mobjects`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject").

    Notes

    When adding the same mobject more than once, repetitions are ignored.
    Use [`Mobject.copy()`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject.copy "manim.mobject.mobject.Mobject.copy") to create a separate copy which can then
    be added to the group.

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `always` | Call a method on a mobject every frame. |
    | `animate` | Used to animate the application of any method of `self`. |
    | `animation_overrides` |  |
    | `depth` | The depth of the mobject. |
    | `height` | The height of the mobject. |
    | `width` | The width of the mobject. |

    _original__init__(**mobjects*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Return type:
        :   None
