<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.text.text_mobject.Text.html -->

# Text

Qualified name: `manim.mobject.text.text\_mobject.Text`

class Text(*text*, *fill_opacity=1.0*, *stroke_width=0*, ***, *color=ManimColor('#FFFFFF')*, *font_size=48*, *line_spacing=-1*, *font=''*, *slant='NORMAL'*, *weight='NORMAL'*, *t2c=None*, *t2f=None*, *t2g=None*, *t2s=None*, *t2w=None*, *gradient=None*, *tab_width=4*, *warn_missing_font=True*, *height=None*, *width=None*, *should_center=True*, *disable_ligatures=False*, *use_svg_cache=False*, ***kwargs*)[[source]](../_modules/manim/mobject/text/text_mobject.html#Text)
:   Bases: [`SVGMobject`](manim.mobject.svg.svg_mobject.SVGMobject.html#manim.mobject.svg.svg_mobject.SVGMobject "manim.mobject.svg.svg_mobject.SVGMobject")

    Display (non-LaTeX) text rendered using [Pango](https://pango.org/).

    Text objects behave like a [`VGroup`](manim.mobject.types.vectorized_mobject.VGroup.html#manim.mobject.types.vectorized_mobject.VGroup "manim.mobject.types.vectorized_mobject.VGroup")-like iterable of all characters
    in the given text. In particular, slicing is possible.

    Parameters:
    :   - **text** (*str*) – The text that needs to be created as a mobject.
        - **font** (*str*) – The font family to be used to render the text. This is either a system font or
          one loaded with register_font(). Note that font family names may be different
          across operating systems.
        - **warn_missing_font** (*bool*) – If True (default), Manim will issue a warning if the font does not exist in the
          (case-sensitive) list of fonts returned from manimpango.list_fonts().
        - **fill_opacity** (*float*)
        - **stroke_width** (*float*)
        - **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor") *|* *None*)
        - **font_size** (*float*)
        - **line_spacing** (*float*)
        - **slant** (*str*)
        - **weight** (*str*)
        - **t2c** (*dict**[**str**,* *str**]* *|* *None*)
        - **t2f** (*dict**[**str**,* *str**]* *|* *None*)
        - **t2g** (*dict**[**str**,* *Iterable**[*[*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor")*]**]* *|* *None*)
        - **t2s** (*dict**[**str**,* *str**]* *|* *None*)
        - **t2w** (*dict**[**str**,* *str**]* *|* *None*)
        - **gradient** (*Iterable**[*[*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor")*]* *|* *None*)
        - **tab_width** (*int*)
        - **height** (*float* *|* *None*)
        - **width** (*float* *|* *None*)
        - **should_center** (*bool*)
        - **disable_ligatures** (*bool*)
        - **use_svg_cache** (*bool*)
        - **kwargs** (*Any*)

    Returns:
    :   The mobject-like [`VGroup`](manim.mobject.types.vectorized_mobject.VGroup.html#manim.mobject.types.vectorized_mobject.VGroup "manim.mobject.types.vectorized_mobject.VGroup").

    Return type:
    :   [`Text`](#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text")

    Examples

    Example: Example1Text

    ```python
    from manim import *

    class Example1Text(Scene):
        def construct(self):
            text = Text('Hello world').scale(3)
            self.add(text)
    ```

    ```python
    class Example1Text(Scene):
        def construct(self):
            text = Text('Hello world').scale(3)
            self.add(text)
    ```

    Example: TextColorExample

    ```python
    from manim import *

    class TextColorExample(Scene):
        def construct(self):
            text1 = Text('Hello world', color=BLUE).scale(3)
            text2 = Text('Hello world', gradient=(BLUE, GREEN)).scale(3).next_to(text1, DOWN)
            self.add(text1, text2)
    ```

    ```python
    class TextColorExample(Scene):
        def construct(self):
            text1 = Text('Hello world', color=BLUE).scale(3)
            text2 = Text('Hello world', gradient=(BLUE, GREEN)).scale(3).next_to(text1, DOWN)
            self.add(text1, text2)
    ```

    Example: TextItalicAndBoldExample

    ```python
    from manim import *

    class TextItalicAndBoldExample(Scene):
        def construct(self):
            text1 = Text("Hello world", slant=ITALIC)
            text2 = Text("Hello world", t2s={'world':ITALIC})
            text3 = Text("Hello world", weight=BOLD)
            text4 = Text("Hello world", t2w={'world':BOLD})
            text5 = Text("Hello world", t2c={'o':YELLOW}, disable_ligatures=True)
            text6 = Text(
                "Visit us at docs.manim.community",
                t2c={"docs.manim.community": YELLOW},
                disable_ligatures=True,
           )
            text6.scale(1.3).shift(DOWN)
            self.add(text1, text2, text3, text4, text5 , text6)
            Group(*self.mobjects).arrange(DOWN, buff=.8).set(height=config.frame_height-LARGE_BUFF)
    ```

    ```python
    class TextItalicAndBoldExample(Scene):
        def construct(self):
            text1 = Text("Hello world", slant=ITALIC)
            text2 = Text("Hello world", t2s={'world':ITALIC})
            text3 = Text("Hello world", weight=BOLD)
            text4 = Text("Hello world", t2w={'world':BOLD})
            text5 = Text("Hello world", t2c={'o':YELLOW}, disable_ligatures=True)
            text6 = Text(
                "Visit us at docs.manim.community",
                t2c={"docs.manim.community": YELLOW},
                disable_ligatures=True,
           )
            text6.scale(1.3).shift(DOWN)
            self.add(text1, text2, text3, text4, text5 , text6)
            Group(*self.mobjects).arrange(DOWN, buff=.8).set(height=config.frame_height-LARGE_BUFF)
    ```

    Example: TextMoreCustomization

    ```python
    from manim import *

    class TextMoreCustomization(Scene):
        def construct(self):
            text1 = Text(
                'Google',
                t2c={'[:1]': '#3174f0', '[1:2]': '#e53125',
                     '[2:3]': '#fbb003', '[3:4]': '#3174f0',
                     '[4:5]': '#269a43', '[5:]': '#e53125'}, font_size=58).scale(3)
            self.add(text1)
    ```

    ```python
    class TextMoreCustomization(Scene):
        def construct(self):
            text1 = Text(
                'Google',
                t2c={'[:1]': '#3174f0', '[1:2]': '#e53125',
                     '[2:3]': '#fbb003', '[3:4]': '#3174f0',
                     '[4:5]': '#269a43', '[5:]': '#e53125'}, font_size=58).scale(3)
            self.add(text1)
    ```

    As [`Text`](#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text") uses Pango to render text, rendering non-English
    characters is easily possible:

    Example: MultipleFonts

    ```python
    from manim import *

    class MultipleFonts(Scene):
        def construct(self):
            morning = Text("வணக்கம்", font="sans-serif")
            japanese = Text(
                "日本へようこそ", t2c={"日本": BLUE}
            )  # works same as ``Text``.
            mess = Text("Multi-Language", weight=BOLD)
            russ = Text("Здравствуйте मस नम म ", font="sans-serif")
            hin = Text("नमस्ते", font="sans-serif")
            arb = Text(
                "صباح الخير \n تشرفت بمقابلتك", font="sans-serif"
            )  # don't mix RTL and LTR languages nothing shows up then ;-)
            chinese = Text("臂猿「黛比」帶著孩子", font="sans-serif")
            self.add(morning, japanese, mess, russ, hin, arb, chinese)
            for i,mobj in enumerate(self.mobjects):
                mobj.shift(DOWN*(i-3))
    ```

    ```python
    class MultipleFonts(Scene):
        def construct(self):
            morning = Text("வணக்கம்", font="sans-serif")
            japanese = Text(
                "日本へようこそ", t2c={"日本": BLUE}
            )  # works same as ``Text``.
            mess = Text("Multi-Language", weight=BOLD)
            russ = Text("Здравствуйте मस नम म ", font="sans-serif")
            hin = Text("नमस्ते", font="sans-serif")
            arb = Text(
                "صباح الخير \n تشرفت بمقابلتك", font="sans-serif"
            )  # don't mix RTL and LTR languages nothing shows up then ;-)
            chinese = Text("臂猿「黛比」帶著孩子", font="sans-serif")
            self.add(morning, japanese, mess, russ, hin, arb, chinese)
            for i,mobj in enumerate(self.mobjects):
                mobj.shift(DOWN*(i-3))
    ```

    Example: PangoRender

    [
    ](./PangoRender-1.mp4)

    ```python
    from manim import *

    class PangoRender(Scene):
        def construct(self):
            morning = Text("வணக்கம்", font="sans-serif")
            self.play(Write(morning))
            self.wait(2)
    ```

    ```python
    class PangoRender(Scene):
        def construct(self):
            morning = Text("வணக்கம்", font="sans-serif")
            self.play(Write(morning))
            self.wait(2)
    ```

    Tests

    Check that the creation of [`Text`](#manim.mobject.text.text_mobject.Text "manim.mobject.text.text_mobject.Text") works:

    ```python
    >>> Text('The horse does not eat cucumber salad.')
    Text('The horse does not eat cucumber salad.')
    ```

    Methods

    |  |  |
    | --- | --- |
    | `font_list` |  |
    | [`init_colors`](#manim.mobject.text.text_mobject.Text.init_colors "manim.mobject.text.text_mobject.Text.init_colors") | Initializes the colors. |

    Attributes

    |  |  |
    | --- | --- |
    | `always` | Call a method on a mobject every frame. |
    | `animate` | Used to animate the application of any method of `self`. |
    | `animation_overrides` |  |
    | `color` |  |
    | `depth` | The depth of the mobject. |
    | `fill_color` | If there are multiple colors (for gradient) this returns the first one |
    | `font_size` |  |
    | `hash_seed` | A unique hash representing the result of the generated mobject points. |
    | `height` | The height of the mobject. |
    | `n_points_per_curve` |  |
    | `sheen_factor` |  |
    | `stroke_color` |  |
    | `width` | The width of the mobject. |

    _find_indexes(*word*, *text*)[[source]](../_modules/manim/mobject/text/text_mobject.html#Text._find_indexes)
    :   Finds the indexes of `text` in `word`.

        Parameters:
        :   - **word** (*str*)
            - **text** (*str*)

        Return type:
        :   list[tuple[int, int]]

    _original__init__(*text*, *fill_opacity=1.0*, *stroke_width=0*, *color=None*, *font_size=48*, *line_spacing=-1*, *font=''*, *slant='NORMAL'*, *weight='NORMAL'*, *t2c=None*, *t2f=None*, *t2g=None*, *t2s=None*, *t2w=None*, *gradient=None*, *tab_width=4*, *warn_missing_font=True*, *height=None*, *width=None*, *should_center=True*, *disable_ligatures=False*, *use_svg_cache=False*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **text** (*str*)
            - **fill_opacity** (*float*)
            - **stroke_width** (*float*)
            - **color** (*TypeAliasForwardRef**(**'~manim.utils.color.core.ParsableManimColor'**)* *|* *None*)
            - **font_size** (*float*)
            - **line_spacing** (*float*)
            - **font** (*str*)
            - **slant** (*str*)
            - **weight** (*str*)
            - **t2c** (*dict**[**str**,* *str**]* *|* *None*)
            - **t2f** (*dict**[**str**,* *str**]* *|* *None*)
            - **t2g** (*dict**[**str**,* *Iterable**[**TypeAliasForwardRef**(**'~manim.utils.color.core.ParsableManimColor'**)**]**]* *|* *None*)
            - **t2s** (*dict**[**str**,* *str**]* *|* *None*)
            - **t2w** (*dict**[**str**,* *str**]* *|* *None*)
            - **gradient** (*Iterable**[**TypeAliasForwardRef**(**'~manim.utils.color.core.ParsableManimColor'**)**]* *|* *None*)
            - **tab_width** (*int*)
            - **warn_missing_font** (*bool*)
            - **height** (*float* *|* *None*)
            - **width** (*float* *|* *None*)
            - **should_center** (*bool*)
            - **disable_ligatures** (*bool*)
            - **use_svg_cache** (*bool*)
            - **kwargs** (*Any*)

    _text2hash(*color*)[[source]](../_modules/manim/mobject/text/text_mobject.html#Text._text2hash)
    :   Generates `sha256` hash for file name.

        Parameters:
        :   **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))

        Return type:
        :   str

    _text2settings(*color*)[[source]](../_modules/manim/mobject/text/text_mobject.html#Text._text2settings)
    :   Converts the texts and styles to a setting for parsing.

        Parameters:
        :   **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))

        Return type:
        :   list[*TextSetting*]

    _text2svg(*color*)[[source]](../_modules/manim/mobject/text/text_mobject.html#Text._text2svg)
    :   Convert the text to SVG using Pango.

        Parameters:
        :   **color** ([*ParsableManimColor*](manim.utils.color.core.html#manim.utils.color.core.ParsableManimColor "manim.utils.color.core.ParsableManimColor"))

        Return type:
        :   str

    init_colors(*propagate_colors=True*)[[source]](../_modules/manim/mobject/text/text_mobject.html#Text.init_colors)
    :   Initializes the colors.

        Gets called upon creation. This is an empty method that can be implemented by
        subclasses.

        Parameters:
        :   **propagate_colors** (*bool*)

        Return type:
        :   Self
