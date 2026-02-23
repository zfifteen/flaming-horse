<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.table.IntegerTable.html -->

# IntegerTable

Qualified name: `manim.mobject.table.IntegerTable`

class IntegerTable(*table*, *element_to_mobject=<class 'manim.mobject.text.numbers.Integer'>*, ***kwargs*)[[source]](../_modules/manim/mobject/table.html#IntegerTable)
:   Bases: [`Table`](manim.mobject.table.Table.html#manim.mobject.table.Table "manim.mobject.table.Table")

    A specialized [`Table`](manim.mobject.table.Table.html#manim.mobject.table.Table "manim.mobject.table.Table") mobject for use with [`Integer`](manim.mobject.text.numbers.Integer.html#manim.mobject.text.numbers.Integer "manim.mobject.text.numbers.Integer").

    Examples

    Example: IntegerTableExample

    ```python
    from manim import *

    class IntegerTableExample(Scene):
        def construct(self):
            t0 = IntegerTable(
                [[0,30,45,60,90],
                [90,60,45,30,0]],
                col_labels=[
                    MathTex(r"\frac{ \sqrt{0} }{2}"),
                    MathTex(r"\frac{ \sqrt{1} }{2}"),
                    MathTex(r"\frac{ \sqrt{2} }{2}"),
                    MathTex(r"\frac{ \sqrt{3} }{2}"),
                    MathTex(r"\frac{ \sqrt{4} }{2}")],
                row_labels=[MathTex(r"\sin"), MathTex(r"\cos")],
                h_buff=1,
                element_to_mobject_config={"unit": r"^{\circ}"})
            self.add(t0)
    ```

    ```python
    class IntegerTableExample(Scene):
        def construct(self):
            t0 = IntegerTable(
                [[0,30,45,60,90],
                [90,60,45,30,0]],
                col_labels=[
                    MathTex(r"\frac{ \sqrt{0} }{2}"),
                    MathTex(r"\frac{ \sqrt{1} }{2}"),
                    MathTex(r"\frac{ \sqrt{2} }{2}"),
                    MathTex(r"\frac{ \sqrt{3} }{2}"),
                    MathTex(r"\frac{ \sqrt{4} }{2}")],
                row_labels=[MathTex(r"\sin"), MathTex(r"\cos")],
                h_buff=1,
                element_to_mobject_config={"unit": r"^{\circ}"})
            self.add(t0)
    ```

    Special case of [`Table`](manim.mobject.table.Table.html#manim.mobject.table.Table "manim.mobject.table.Table") with element_to_mobject set to [`Integer`](manim.mobject.text.numbers.Integer.html#manim.mobject.text.numbers.Integer "manim.mobject.text.numbers.Integer").
    Will round if there are decimal entries in the table.

    Parameters:
    :   - **table** (*Iterable**[**Iterable**[**float* *|* *str**]**]*) – A 2d array or list of lists. Content of the table has to be valid input
          for [`Integer`](manim.mobject.text.numbers.Integer.html#manim.mobject.text.numbers.Integer "manim.mobject.text.numbers.Integer").
        - **element_to_mobject** (*Callable**[**[**float* *|* *str**]**,* [*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")*]*) – The [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") class applied to the table entries. Set as [`Integer`](manim.mobject.text.numbers.Integer.html#manim.mobject.text.numbers.Integer "manim.mobject.text.numbers.Integer").
        - **kwargs** – Additional arguments to be passed to [`Table`](manim.mobject.table.Table.html#manim.mobject.table.Table "manim.mobject.table.Table").

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

    _original__init__(*table*, *element_to_mobject=<class 'manim.mobject.text.numbers.Integer'>*, ***kwargs*)
    :   Special case of [`Table`](manim.mobject.table.Table.html#manim.mobject.table.Table "manim.mobject.table.Table") with element_to_mobject set to [`Integer`](manim.mobject.text.numbers.Integer.html#manim.mobject.text.numbers.Integer "manim.mobject.text.numbers.Integer").
        Will round if there are decimal entries in the table.

        Parameters:
        :   - **table** (*Iterable**[**Iterable**[**float* *|* *str**]**]*) – A 2d array or list of lists. Content of the table has to be valid input
              for [`Integer`](manim.mobject.text.numbers.Integer.html#manim.mobject.text.numbers.Integer "manim.mobject.text.numbers.Integer").
            - **element_to_mobject** (*Callable**[**[**float* *|* *str**]**,* [*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")*]*) – The [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") class applied to the table entries. Set as [`Integer`](manim.mobject.text.numbers.Integer.html#manim.mobject.text.numbers.Integer "manim.mobject.text.numbers.Integer").
            - **kwargs** – Additional arguments to be passed to [`Table`](manim.mobject.table.Table.html#manim.mobject.table.Table "manim.mobject.table.Table").
