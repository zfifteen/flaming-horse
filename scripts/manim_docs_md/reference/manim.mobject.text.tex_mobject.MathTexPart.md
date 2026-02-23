<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.text.tex_mobject.MathTexPart.html -->

# MathTexPart

Qualified name: `manim.mobject.text.tex\_mobject.MathTexPart`

class MathTexPart(*fill_color=None*, *fill_opacity=0.0*, *stroke_color=None*, *stroke_opacity=1.0*, *stroke_width=4*, *background_stroke_color=ManimColor('#000000')*, *background_stroke_opacity=1.0*, *background_stroke_width=0*, *sheen_factor=0.0*, *joint_type=None*, *sheen_direction=array([-1., 1., 0.])*, *close_new_points=False*, *pre_function_handle_to_anchor_scale_factor=0.01*, *make_smooth_after_applying_functions=False*, *background_image=None*, *shade_in_3d=False*, *tolerance_for_point_equality=1e-06*, *n_points_per_cubic_curve=4*, *cap_style=CapStyleType.AUTO*, ***kwargs*)[[source]](../_modules/manim/mobject/text/tex_mobject.html#MathTexPart)
:   Bases: [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")

    Methods

    Attributes

    |  |  |
    | --- | --- |
    | `always` | Call a method on a mobject every frame. |
    | `animate` | Used to animate the application of any method of `self`. |
    | `animation_overrides` |  |
    | `color` |  |
    | `depth` | The depth of the mobject. |
    | `fill_color` | If there are multiple colors (for gradient) this returns the first one |
    | `height` | The height of the mobject. |
    | `n_points_per_curve` |  |
    | `sheen_factor` |  |
    | `stroke_color` |  |
    | `width` | The width of the mobject. |
    | `tex_string` |  |

    Parameters:
    :   - **fill_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*)
        - **fill_opacity** (*float*)
        - **stroke_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*)
        - **stroke_opacity** (*float*)
        - **stroke_width** (*float*)
        - **background_stroke_color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*)
        - **background_stroke_opacity** (*float*)
        - **background_stroke_width** (*float*)
        - **sheen_factor** (*float*)
        - **joint_type** ([*LineJointType*](manim.constants.LineJointType.html#manim.constants.LineJointType "manim.constants.LineJointType") *|* *None*)
        - **sheen_direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
        - **close_new_points** (*bool*)
        - **pre_function_handle_to_anchor_scale_factor** (*float*)
        - **make_smooth_after_applying_functions** (*bool*)
        - **background_image** (*Image* *|* *str* *|* *None*)
        - **shade_in_3d** (*bool*)
        - **tolerance_for_point_equality** (*float*)
        - **n_points_per_cubic_curve** (*int*)
        - **cap_style** ([*CapStyleType*](manim.constants.CapStyleType.html#manim.constants.CapStyleType "manim.constants.CapStyleType"))
        - **kwargs** (*Any*)

    _original__init__(*fill_color=None*, *fill_opacity=0.0*, *stroke_color=None*, *stroke_opacity=1.0*, *stroke_width=4*, *background_stroke_color=ManimColor('#000000')*, *background_stroke_opacity=1.0*, *background_stroke_width=0*, *sheen_factor=0.0*, *joint_type=None*, *sheen_direction=array([-1., 1., 0.])*, *close_new_points=False*, *pre_function_handle_to_anchor_scale_factor=0.01*, *make_smooth_after_applying_functions=False*, *background_image=None*, *shade_in_3d=False*, *tolerance_for_point_equality=1e-06*, *n_points_per_cubic_curve=4*, *cap_style=CapStyleType.AUTO*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **fill_color** (*TypeAliasForwardRef**(**'~manim.utils.color.core.ParsableManimColor'**)* *|* *None*)
            - **fill_opacity** (*float*)
            - **stroke_color** (*TypeAliasForwardRef**(**'~manim.utils.color.core.ParsableManimColor'**)* *|* *None*)
            - **stroke_opacity** (*float*)
            - **stroke_width** (*float*)
            - **background_stroke_color** (*TypeAliasForwardRef**(**'~manim.utils.color.core.ParsableManimColor'**)* *|* *None*)
            - **background_stroke_opacity** (*float*)
            - **background_stroke_width** (*float*)
            - **sheen_factor** (*float*)
            - **joint_type** ([*LineJointType*](manim.constants.LineJointType.html#manim.constants.LineJointType "manim.constants.LineJointType") *|* *None*)
            - **sheen_direction** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
            - **close_new_points** (*bool*)
            - **pre_function_handle_to_anchor_scale_factor** (*float*)
            - **make_smooth_after_applying_functions** (*bool*)
            - **background_image** (*Image* *|* *str* *|* *None*)
            - **shade_in_3d** (*bool*)
            - **tolerance_for_point_equality** (*float*)
            - **n_points_per_cubic_curve** (*int*)
            - **cap_style** ([*CapStyleType*](manim.constants.CapStyleType.html#manim.constants.CapStyleType "manim.constants.CapStyleType"))
            - **kwargs** (*Any*)
