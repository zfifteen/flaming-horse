<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.types.image_mobject.ImageMobjectFromCamera.html -->

# ImageMobjectFromCamera

Qualified name: `manim.mobject.types.image\_mobject.ImageMobjectFromCamera`

class ImageMobjectFromCamera(*camera*, *default_display_frame_config=None*, ***kwargs*)[[source]](../_modules/manim/mobject/types/image_mobject.html#ImageMobjectFromCamera)
:   Bases: [`AbstractImageMobject`](manim.mobject.types.image_mobject.AbstractImageMobject.html#manim.mobject.types.image_mobject.AbstractImageMobject "manim.mobject.types.image_mobject.AbstractImageMobject")

    Methods

    |  |  |
    | --- | --- |
    | `add_display_frame` |  |
    | `get_pixel_array` |  |
    | `interpolate_color` |  |

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
    :   - **camera** ([*MovingCamera*](manim.camera.moving_camera.MovingCamera.html#manim.camera.moving_camera.MovingCamera "manim.camera.moving_camera.MovingCamera"))
        - **default_display_frame_config** (*dict**[**str**,* *Any**]* *|* *None*)
        - **kwargs** (*Any*)

    _original__init__(*camera*, *default_display_frame_config=None*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **camera** ([*MovingCamera*](manim.camera.moving_camera.MovingCamera.html#manim.camera.moving_camera.MovingCamera "manim.camera.moving_camera.MovingCamera"))
            - **default_display_frame_config** (*dict**[**str**,* *Any**]* *|* *None*)
            - **kwargs** (*Any*)

        Return type:
        :   None
