<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.arc.TipableVMobject.html -->

# TipableVMobject

Qualified name: `manim.mobject.geometry.arc.TipableVMobject`

class TipableVMobject(*tip_length=0.35*, *normal_vector=array([0., 0., 1.])*, *tip_style={}*, ***kwargs*)[[source]](../_modules/manim/mobject/geometry/arc.html#TipableVMobject)
:   Bases: [`VMobject`](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")

    Meant for shared functionality between Arc and Line.
    Functionality can be classified broadly into these groups:

    > - Adding, Creating, Modifying tips
    >   :   - add_tip calls create_tip, before pushing the new tip
    >         :   into the TipableVMobject’s list of submobjects
    >       - stylistic and positional configuration
    > - Checking for tips
    >   :   - Boolean checks for whether the TipableVMobject has a tip
    >         :   and a starting tip
    > - Getters
    >   :   - Straightforward accessors, returning information pertaining
    >         :   to the TipableVMobject instance’s tip(s), its length etc

    Methods

    |  |  |
    | --- | --- |
    | [`add_tip`](#manim.mobject.geometry.arc.TipableVMobject.add_tip "manim.mobject.geometry.arc.TipableVMobject.add_tip") | Adds a tip to the TipableVMobject instance, recognising that the endpoints might need to be switched if it's a 'starting tip' or not. |
    | `asign_tip_attr` |  |
    | [`create_tip`](#manim.mobject.geometry.arc.TipableVMobject.create_tip "manim.mobject.geometry.arc.TipableVMobject.create_tip") | Stylises the tip, positions it spatially, and returns the newly instantiated tip to the caller. |
    | `get_default_tip_length` |  |
    | [`get_end`](#manim.mobject.geometry.arc.TipableVMobject.get_end "manim.mobject.geometry.arc.TipableVMobject.get_end") | Returns the point, where the stroke that surrounds the [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") ends. |
    | `get_first_handle` |  |
    | `get_last_handle` |  |
    | `get_length` |  |
    | [`get_start`](#manim.mobject.geometry.arc.TipableVMobject.get_start "manim.mobject.geometry.arc.TipableVMobject.get_start") | Returns the point, where the stroke that surrounds the [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") starts. |
    | [`get_tip`](#manim.mobject.geometry.arc.TipableVMobject.get_tip "manim.mobject.geometry.arc.TipableVMobject.get_tip") | Returns the TipableVMobject instance's (first) tip, otherwise throws an exception. |
    | [`get_tips`](#manim.mobject.geometry.arc.TipableVMobject.get_tips "manim.mobject.geometry.arc.TipableVMobject.get_tips") | Returns a VGroup (collection of VMobjects) containing the TipableVMObject instance's tips. |
    | [`get_unpositioned_tip`](#manim.mobject.geometry.arc.TipableVMobject.get_unpositioned_tip "manim.mobject.geometry.arc.TipableVMobject.get_unpositioned_tip") | Returns a tip that has been stylistically configured, but has not yet been given a position in space. |
    | `has_start_tip` |  |
    | `has_tip` |  |
    | `pop_tips` |  |
    | `position_tip` |  |
    | `reset_endpoints_based_on_tip` |  |

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

    Parameters:
    :   - **tip_length** (*float*)
        - **normal_vector** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
        - **tip_style** (*dict*)
        - **kwargs** (*Any*)

    _original__init__(*tip_length=0.35*, *normal_vector=array([0., 0., 1.])*, *tip_style={}*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **tip_length** (*float*)
            - **normal_vector** ([*Vector3DLike*](manim.typing.html#manim.typing.Vector3DLike "manim.typing.Vector3DLike"))
            - **tip_style** (*dict*)
            - **kwargs** (*Any*)

        Return type:
        :   None

    add_tip(*tip=None*, *tip_shape=None*, *tip_length=None*, *tip_width=None*, *at_start=False*)[[source]](../_modules/manim/mobject/geometry/arc.html#TipableVMobject.add_tip)
    :   Adds a tip to the TipableVMobject instance, recognising
        that the endpoints might need to be switched if it’s
        a ‘starting tip’ or not.

        Parameters:
        :   - **tip** ([*tips.ArrowTip*](manim.mobject.geometry.tips.ArrowTip.html#manim.mobject.geometry.tips.ArrowTip "manim.mobject.geometry.tips.ArrowTip") *|* *None*)
            - **tip_shape** (*type**[*[*tips.ArrowTip*](manim.mobject.geometry.tips.ArrowTip.html#manim.mobject.geometry.tips.ArrowTip "manim.mobject.geometry.tips.ArrowTip")*]* *|* *None*)
            - **tip_length** (*float* *|* *None*)
            - **tip_width** (*float* *|* *None*)
            - **at_start** (*bool*)

        Return type:
        :   Self

    create_tip(*tip_shape=None*, *tip_length=None*, *tip_width=None*, *at_start=False*)[[source]](../_modules/manim/mobject/geometry/arc.html#TipableVMobject.create_tip)
    :   Stylises the tip, positions it spatially, and returns
        the newly instantiated tip to the caller.

        Parameters:
        :   - **tip_shape** (*type**[*[*tips.ArrowTip*](manim.mobject.geometry.tips.ArrowTip.html#manim.mobject.geometry.tips.ArrowTip "manim.mobject.geometry.tips.ArrowTip")*]* *|* *None*)
            - **tip_length** (*float* *|* *None*)
            - **tip_width** (*float* *|* *None*)
            - **at_start** (*bool*)

        Return type:
        :   [tips.ArrowTip](manim.mobject.geometry.tips.ArrowTip.html#manim.mobject.geometry.tips.ArrowTip "manim.mobject.geometry.tips.ArrowTip")

    get_end()[[source]](../_modules/manim/mobject/geometry/arc.html#TipableVMobject.get_end)
    :   Returns the point, where the stroke that surrounds the [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") ends.

        Return type:
        :   [*Point3D*](manim.typing.html#manim.typing.Point3D "manim.typing.Point3D")

    get_start()[[source]](../_modules/manim/mobject/geometry/arc.html#TipableVMobject.get_start)
    :   Returns the point, where the stroke that surrounds the [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") starts.

        Return type:
        :   [*Point3D*](manim.typing.html#manim.typing.Point3D "manim.typing.Point3D")

    get_tip()[[source]](../_modules/manim/mobject/geometry/arc.html#TipableVMobject.get_tip)
    :   Returns the TipableVMobject instance’s (first) tip,
        otherwise throws an exception.

        Return type:
        :   [*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")

    get_tips()[[source]](../_modules/manim/mobject/geometry/arc.html#TipableVMobject.get_tips)
    :   Returns a VGroup (collection of VMobjects) containing
        the TipableVMObject instance’s tips.

        Return type:
        :   [*VGroup*](manim.mobject.types.vectorized_mobject.VGroup.html#manim.mobject.types.vectorized_mobject.VGroup "manim.mobject.types.vectorized_mobject.VGroup")

    get_unpositioned_tip(*tip_shape=None*, *tip_length=None*, *tip_width=None*)[[source]](../_modules/manim/mobject/geometry/arc.html#TipableVMobject.get_unpositioned_tip)
    :   Returns a tip that has been stylistically configured,
        but has not yet been given a position in space.

        Parameters:
        :   - **tip_shape** (*type**[*[*tips.ArrowTip*](manim.mobject.geometry.tips.ArrowTip.html#manim.mobject.geometry.tips.ArrowTip "manim.mobject.geometry.tips.ArrowTip")*]* *|* *None*)
            - **tip_length** (*float* *|* *None*)
            - **tip_width** (*float* *|* *None*)

        Return type:
        :   [tips.ArrowTip](manim.mobject.geometry.tips.ArrowTip.html#manim.mobject.geometry.tips.ArrowTip "manim.mobject.geometry.tips.ArrowTip") | [tips.ArrowTriangleFilledTip](manim.mobject.geometry.tips.ArrowTriangleFilledTip.html#manim.mobject.geometry.tips.ArrowTriangleFilledTip "manim.mobject.geometry.tips.ArrowTriangleFilledTip")
