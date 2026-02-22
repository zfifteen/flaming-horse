<!-- source: https://docs.manim.community/en/stable/reference/manim.utils.hashing.html -->

# hashing

Utilities for scene caching.

Functions

get_hash_from_play_call(*scene_object*, *camera_object*, *animations_list*, *current_mobjects_list*)[[source]](../_modules/manim/utils/hashing.html#get_hash_from_play_call)
:   Take the list of animations and a list of mobjects and output their hashes. This is meant to be used for scene.play function.

    Parameters:
    :   - **scene_object** ([*Scene*](manim.scene.scene.Scene.html#manim.scene.scene.Scene "manim.scene.scene.Scene")) – The scene object.
        - **camera_object** ([*Camera*](manim.camera.camera.Camera.html#manim.camera.camera.Camera "manim.camera.camera.Camera") *|* *OpenGLCamera*) – The camera object used in the scene.
        - **animations_list** (*Iterable**[*[*Animation*](manim.animation.animation.Animation.html#manim.animation.animation.Animation "manim.animation.animation.Animation")*]*) – The list of animations.
        - **current_mobjects_list** (*Iterable**[*[*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject")*]*) – The list of mobjects.

    Returns:
    :   A string concatenation of the respective hashes of camera_object, animations_list and current_mobjects_list, separated by _.

    Return type:
    :   `str`

get_json(*obj*)[[source]](../_modules/manim/utils/hashing.html#get_json)
:   Recursively serialize object to JSON using the `CustomEncoder` class.

    Parameters:
    :   **obj** (*Any*) – The dict to flatten

    Returns:
    :   The flattened object

    Return type:
    :   `str`
