<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.logo.ManimBanner.html -->

# ManimBanner

Qualified name: `manim.mobject.logo.ManimBanner`

class ManimBanner(*dark_theme=True*)[[source]](../_modules/manim/mobject/logo.html#ManimBanner)
:   Bases: [`VGroup`](manim.mobject.types.vectorized_mobject.VGroup.html#manim.mobject.types.vectorized_mobject.VGroup "manim.mobject.types.vectorized_mobject.VGroup")

    Convenience class representing Manim’s banner.

    Can be animated using custom methods.

    Parameters:
    :   **dark_theme** (*bool*) – If `True` (the default), the dark theme version of the logo
        (with light text font) will be rendered. Otherwise, if `False`,
        the light theme version (with dark text font) is used.

    Examples

    Example: DarkThemeBanner

    [
    ](./DarkThemeBanner-1.mp4)

    ```python
    from manim import *

    class DarkThemeBanner(Scene):
        def construct(self):
            banner = ManimBanner()
            self.play(banner.create())
            self.play(banner.expand())
            self.wait()
            self.play(Unwrite(banner))
    ```

    ```python
    class DarkThemeBanner(Scene):
        def construct(self):
            banner = ManimBanner()
            self.play(banner.create())
            self.play(banner.expand())
            self.wait()
            self.play(Unwrite(banner))
    ```

    Example: LightThemeBanner

    [
    ](./LightThemeBanner-1.mp4)

    ```python
    from manim import *

    class LightThemeBanner(Scene):
        def construct(self):
            self.camera.background_color = "#ece6e2"
            banner = ManimBanner(dark_theme=False)
            self.play(banner.create())
            self.play(banner.expand())
            self.wait()
            self.play(Unwrite(banner))
    ```

    ```python
    class LightThemeBanner(Scene):
        def construct(self):
            self.camera.background_color = "#ece6e2"
            banner = ManimBanner(dark_theme=False)
            self.play(banner.create())
            self.play(banner.expand())
            self.wait()
            self.play(Unwrite(banner))
    ```

    Methods

    |  |  |
    | --- | --- |
    | [`create`](#manim.mobject.logo.ManimBanner.create "manim.mobject.logo.ManimBanner.create") | The creation animation for Manim's logo. |
    | [`expand`](#manim.mobject.logo.ManimBanner.expand "manim.mobject.logo.ManimBanner.expand") | An animation that expands Manim's logo into its banner. |
    | [`scale`](#manim.mobject.logo.ManimBanner.scale "manim.mobject.logo.ManimBanner.scale") | Scale the banner by the specified scale factor. |

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

    _original__init__(*dark_theme=True*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   **dark_theme** (*bool*)

    create(*run_time=2*)[[source]](../_modules/manim/mobject/logo.html#ManimBanner.create)
    :   The creation animation for Manim’s logo.

        Parameters:
        :   **run_time** (*float*) – The run time of the animation.

        Returns:
        :   An animation to be used in a [`Scene.play()`](manim.scene.scene.Scene.html#manim.scene.scene.Scene.play "manim.scene.scene.Scene.play") call.

        Return type:
        :   [`AnimationGroup`](manim.animation.composition.AnimationGroup.html#manim.animation.composition.AnimationGroup "manim.animation.composition.AnimationGroup")

    expand(*run_time=1.5*, *direction='center'*)[[source]](../_modules/manim/mobject/logo.html#ManimBanner.expand)
    :   An animation that expands Manim’s logo into its banner.

        The returned animation transforms the banner from its initial
        state (representing Manim’s logo with just the icons) to its
        expanded state (showing the full name together with the icons).

        See the class documentation for how to use this.

        Note

        Before calling this method, the text “anim” is not a
        submobject of the banner object. After the expansion,
        it is added as a submobject so subsequent animations
        to the banner object apply to the text “anim” as well.

        Parameters:
        :   - **run_time** (*float*) – The run time of the animation.
            - **direction** (*str*) – The direction in which the logo is expanded.

        Returns:
        :   An animation to be used in a [`Scene.play()`](manim.scene.scene.Scene.html#manim.scene.scene.Scene.play "manim.scene.scene.Scene.play") call.

        Return type:
        :   [`Succession`](manim.animation.composition.Succession.html#manim.animation.composition.Succession "manim.animation.composition.Succession")

        Examples

        Example: ExpandDirections

        [
        ](./ExpandDirections-1.mp4)

        ```python
        from manim import *

        class ExpandDirections(Scene):
            def construct(self):
                banners = [ManimBanner().scale(0.5).shift(UP*x) for x in [-2, 0, 2]]
                self.play(
                    banners[0].expand(direction="right"),
                    banners[1].expand(direction="center"),
                    banners[2].expand(direction="left"),
                )
        ```

        ```python
        class ExpandDirections(Scene):
            def construct(self):
                banners = [ManimBanner().scale(0.5).shift(UP*x) for x in [-2, 0, 2]]
                self.play(
                    banners[0].expand(direction="right"),
                    banners[1].expand(direction="center"),
                    banners[2].expand(direction="left"),
                )
        ```

    scale(*scale_factor*, ***kwargs*)[[source]](../_modules/manim/mobject/logo.html#ManimBanner.scale)
    :   Scale the banner by the specified scale factor.

        Parameters:
        :   - **scale_factor** (*float*) – The factor used for scaling the banner.
            - **kwargs** (*Any*)

        Returns:
        :   The scaled banner.

        Return type:
        :   [`ManimBanner`](#manim.mobject.logo.ManimBanner "manim.mobject.logo.ManimBanner")
