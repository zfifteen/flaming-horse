<!-- source: https://docs.manim.community/en/stable/reference/manim.utils.images.html -->

# images

Image manipulation utilities.

Functions

change_to_rgba_array(*image*, *dtype='uint8'*)[[source]](../_modules/manim/utils/images.html#change_to_rgba_array)
:   Converts an RGB array into RGBA with the alpha value opacity maxed.

    Parameters:
    :   - **image** ([*RGBPixelArray*](manim.typing.html#manim.typing.RGBPixelArray "manim.typing.RGBPixelArray"))
        - **dtype** (*str*)

    Return type:
    :   [*RGBAPixelArray*](manim.typing.html#manim.typing.RGBAPixelArray "manim.typing.RGBAPixelArray")

drag_pixels(*frames*)[[source]](../_modules/manim/utils/images.html#drag_pixels)
:   Parameters:
    :   **frames** (*Sequence**[*[*PixelArray*](manim.typing.html#manim.typing.PixelArray "manim.typing.PixelArray")*]*)

    Return type:
    :   list[np.ndarray]

get_full_raster_image_path(*image_file_name*)[[source]](../_modules/manim/utils/images.html#get_full_raster_image_path)
:   Parameters:
    :   **image_file_name** (*str* *|* *PurePath*)

    Return type:
    :   *Path*

get_full_vector_image_path(*image_file_name*)[[source]](../_modules/manim/utils/images.html#get_full_vector_image_path)
:   Parameters:
    :   **image_file_name** (*str* *|* *PurePath*)

    Return type:
    :   *Path*

invert_image(*image*)[[source]](../_modules/manim/utils/images.html#invert_image)
:   Parameters:
    :   **image** ([*PixelArray*](manim.typing.html#manim.typing.PixelArray "manim.typing.PixelArray"))

    Return type:
    :   <module ‘PIL.Image’ from ‘/home/docs/checkouts/readthedocs.org/user_builds/manimce/envs/stable/lib/python3.13/site-packages/PIL/Image.py’>
