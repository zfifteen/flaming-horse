<!-- source: https://docs.manim.community/en/stable/reference/manim.scene.scene_file_writer.html -->

# scene_file_writer

The interface between scenes and ffmpeg.

Classes

|  |  |
| --- | --- |
| [`SceneFileWriter`](manim.scene.scene_file_writer.SceneFileWriter.html#manim.scene.scene_file_writer.SceneFileWriter "manim.scene.scene_file_writer.SceneFileWriter") | SceneFileWriter is the object that actually writes the animations played, into video files, using FFMPEG. |

Functions

convert_audio(*input_path*, *output_path*, *codec_name*)[[source]](../_modules/manim/scene/scene_file_writer.html#convert_audio)
:   Parameters:
    :   - **input_path** (*Path*)
        - **output_path** (*Path* *|* *_TemporaryFileWrapper**[**bytes**]*)
        - **codec_name** (*str*)

    Return type:
    :   None

to_av_frame_rate(*fps*)[[source]](../_modules/manim/scene/scene_file_writer.html#to_av_frame_rate)
:   Parameters:
    :   **fps** (*float*)

    Return type:
    :   *Fraction*
