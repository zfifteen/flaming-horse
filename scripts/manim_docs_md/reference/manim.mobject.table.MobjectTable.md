<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.table.MobjectTable.html -->

# MobjectTable

Qualified name: `manim.mobject.table.MobjectTable`

class MobjectTable(*table*, *element_to_mobject=<function MobjectTable.<lambda>>*, ***kwargs*)[[source]](../_modules/manim/mobject/table.html#MobjectTable)
:   Bases: [`Table`](manim.mobject.table.Table.html#manim.mobject.table.Table "manim.mobject.table.Table")

    A specialized [`Table`](manim.mobject.table.Table.html#manim.mobject.table.Table "manim.mobject.table.Table") mobject for use with [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject").

    Examples

    Example: MobjectTableExample

    ```python
    from manim import *

    class MobjectTableExample(Scene):
        def construct(self):
            cross = VGroup(
                Line(UP + LEFT, DOWN + RIGHT),
                Line(UP + RIGHT, DOWN + LEFT),
            )
            a = Circle().set_color(RED).scale(0.5)
            b = cross.set_color(BLUE).scale(0.5)
            t0 = MobjectTable(
                [[a.copy(),b.copy(),a.copy()],
                [b.copy(),a.copy(),a.copy()],
                [a.copy(),b.copy(),b.copy()]]
            )
            line = Line(
                t0.get_corner(DL), t0.get_corner(UR)
            ).set_color(RED)
            self.add(t0, line)
    ```

    ```python
    class MobjectTableExample(Scene):
        def construct(self):
            cross = VGroup(
                Line(UP + LEFT, DOWN + RIGHT),
                Line(UP + RIGHT, DOWN + LEFT),
            )
            a = Circle().set_color(RED).scale(0.5)
            b = cross.set_color(BLUE).scale(0.5)
            t0 = MobjectTable(
                [[a.copy(),b.copy(),a.copy()],
                [b.copy(),a.copy(),a.copy()],
                [a.copy(),b.copy(),b.copy()]]
            )
            line = Line(
                t0.get_corner(DL), t0.get_corner(UR)
            ).set_color(RED)
            self.add(t0, line)
    ```

    Special case of [`Table`](manim.mobject.table.Table.html#manim.mobject.table.Table "manim.mobject.table.Table") with `element_to_mobject` set to an identity function.
    Here, every item in `table` must already be of type [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject").

    Parameters:
    :   - **table** (*Iterable**[**Iterable**[*[*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")*]**]*) – A 2D array or list of lists. Content of the table must be of type [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject").
        - **element_to_mobject** (*Callable**[**[*[*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")*]**,* [*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")*]*) – The [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") class applied to the table entries. Set as `lambda m : m` to return itself.
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

    _original__init__(*table*, *element_to_mobject=<function MobjectTable.<lambda>>*, ***kwargs*)
    :   Special case of [`Table`](manim.mobject.table.Table.html#manim.mobject.table.Table "manim.mobject.table.Table") with `element_to_mobject` set to an identity function.
        Here, every item in `table` must already be of type [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject").

        Parameters:
        :   - **table** (*Iterable**[**Iterable**[*[*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")*]**]*) – A 2D array or list of lists. Content of the table must be of type [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject").
            - **element_to_mobject** (*Callable**[**[*[*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")*]**,* [*VMobject*](manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject "manim.mobject.types.vectorized_mobject.VMobject")*]*) – The [`Mobject`](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject") class applied to the table entries. Set as `lambda m : m` to return itself.
            - **kwargs** – Additional arguments to be passed to [`Table`](manim.mobject.table.Table.html#manim.mobject.table.Table "manim.mobject.table.Table").
