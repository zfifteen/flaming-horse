<!-- source: https://docs.manim.community/en/stable/reference/manim.utils.color.core.HSV.html -->

# HSV

Qualified name: `manim.utils.color.core.HSV`

class HSV(*hsv*, *alpha=1.0*)[[source]](../_modules/manim/utils/color/core.html#HSV)
:   Bases: [`ManimColor`](manim.utils.color.core.ManimColor.html#manim.utils.color.core.ManimColor "manim.utils.color.core.ManimColor")

    HSV Color Space

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `h` |  |
    | `hue` |  |
    | `s` |  |
    | `saturation` |  |
    | `v` |  |
    | `value` |  |

    Parameters:
    :   - **hsv** ([*FloatHSVLike*](manim.typing.html#manim.typing.FloatHSVLike "manim.typing.FloatHSVLike") *|* [*FloatHSVALike*](manim.typing.html#manim.typing.FloatHSVALike "manim.typing.FloatHSVALike"))
        - **alpha** (*float*)

    classmethod _from_internal(*value*)[[source]](../_modules/manim/utils/color/core.html#HSV._from_internal)
    :   This method is intended to be overwritten by custom color space classes
        which are subtypes of [`ManimColor`](manim.utils.color.core.ManimColor.html#manim.utils.color.core.ManimColor "manim.utils.color.core.ManimColor").

        The method constructs a new object of the given class by transforming the value
        in the internal format `[r,g,b,a]` into a format which the constructor of the
        custom class can understand. Look at [`HSV`](#manim.utils.color.core.HSV "manim.utils.color.core.HSV") for an example.

        Parameters:
        :   **value** ([*ManimColorInternal*](manim.typing.html#manim.typing.ManimColorInternal "manim.typing.ManimColorInternal"))

        Return type:
        :   *Self*

    property _internal_space: ndarray[tuple[Any, ...], dtype[_ScalarT]]
    :   This is a readonly property which is a custom representation for color space
        operations. It is used for operators and can be used when implementing a custom
        color space.

    property _internal_value: [ManimColorInternal](manim.typing.html#manim.typing.ManimColorInternal "manim.typing.ManimColorInternal")
    :   Return the internal value of the current [`ManimColor`](manim.utils.color.core.ManimColor.html#manim.utils.color.core.ManimColor "manim.utils.color.core.ManimColor") as an
        `[r,g,b,a]` float array.

        Returns:
        :   Internal color representation.

        Return type:
        :   [ManimColorInternal](manim.typing.html#manim.typing.ManimColorInternal "manim.typing.ManimColorInternal")
