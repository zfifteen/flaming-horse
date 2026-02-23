<!-- source: https://docs.manim.community/en/stable/reference/manim.utils.commands.html -->

# commands

Classes

|  |  |
| --- | --- |
| [`VideoMetadata`](manim.utils.commands.VideoMetadata.html#manim.utils.commands.VideoMetadata "manim.utils.commands.VideoMetadata") |  |

Functions

capture(*command*, *cwd=None*, *command_input=None*)[[source]](../_modules/manim/utils/commands.html#capture)
:   Parameters:
    :   - **command** (*str* *|* *list**[**str**]*)
        - **cwd** (*TypeAliasForwardRef**(**'~manim.typing.StrOrBytesPath'**)* *|* *None*)
        - **command_input** (*str* *|* *None*)

    Return type:
    :   tuple[str, str, int]

get_dir_layout(*dirpath*)[[source]](../_modules/manim/utils/commands.html#get_dir_layout)
:   Get list of paths relative to dirpath of all files in dir and subdirs recursively.

    Parameters:
    :   **dirpath** (*Path*)

    Return type:
    :   *Generator*[str, None, None]

get_video_metadata(*path_to_video*)[[source]](../_modules/manim/utils/commands.html#get_video_metadata)
:   Parameters:
    :   **path_to_video** (*str* *|* *PathLike*)

    Return type:
    :   [*VideoMetadata*](manim.utils.commands.VideoMetadata.html#manim.utils.commands.VideoMetadata "manim.utils.commands.VideoMetadata")
