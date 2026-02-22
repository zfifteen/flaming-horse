<!-- source: https://docs.manim.community/en/stable/reference/manim.animation.transform_matching_parts.TransformMatchingTex.html -->

# TransformMatchingTex

Qualified name: `manim.animation.transform\_matching\_parts.TransformMatchingTex`

class TransformMatchingTex(*mobject=None*, **args*, *use_override=True*, ***kwargs*)[[source]](../_modules/manim/animation/transform_matching_parts.html#TransformMatchingTex)
:   Bases: [`TransformMatchingAbstractBase`](manim.animation.transform_matching_parts.TransformMatchingAbstractBase.html#manim.animation.transform_matching_parts.TransformMatchingAbstractBase "manim.animation.transform_matching_parts.TransformMatchingAbstractBase")

    A transformation trying to transform rendered LaTeX strings.

    Two submobjects match if their `tex_string` matches.

    See also

    [`TransformMatchingAbstractBase`](manim.animation.transform_matching_parts.TransformMatchingAbstractBase.html#manim.animation.transform_matching_parts.TransformMatchingAbstractBase "manim.animation.transform_matching_parts.TransformMatchingAbstractBase")

    Examples

    Example: MatchingEquationParts

    [
    ](./MatchingEquationParts-1.mp4)

    ```python
    from manim import *

    class MatchingEquationParts(Scene):
        def construct(self):
            variables = VGroup(MathTex("a"), MathTex("b"), MathTex("c")).arrange_submobjects().shift(UP)

            eq1 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2")
            eq2 = MathTex("{{a}}^2", "+", "{{b}}^2", "=", "{{c}}^2")
            eq3 = MathTex("{{a}}^2", "=", "{{c}}^2", "-", "{{b}}^2")

            self.add(eq1)
            self.wait(0.5)
            self.play(TransformMatchingTex(Group(eq1, variables), eq2))
            self.wait(0.5)
            self.play(TransformMatchingTex(eq2, eq3))
            self.wait(0.5)
    ```

    ```python
    class MatchingEquationParts(Scene):
        def construct(self):
            variables = VGroup(MathTex("a"), MathTex("b"), MathTex("c")).arrange_submobjects().shift(UP)

            eq1 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2")
            eq2 = MathTex("{{a}}^2", "+", "{{b}}^2", "=", "{{c}}^2")
            eq3 = MathTex("{{a}}^2", "=", "{{c}}^2", "-", "{{b}}^2")

            self.add(eq1)
            self.wait(0.5)
            self.play(TransformMatchingTex(Group(eq1, variables), eq2))
            self.wait(0.5)
            self.play(TransformMatchingTex(eq2, eq3))
            self.wait(0.5)
    ```

    Methods

    |  |  |
    | --- | --- |
    | `get_mobject_key` |  |
    | `get_mobject_parts` |  |

    Attributes

    |  |  |
    | --- | --- |
    | `run_time` |  |

    Parameters:
    :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **target_mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
        - **transform_mismatches** (*bool*)
        - **fade_transform_mismatches** (*bool*)
        - **key_map** (*dict* *|* *None*)

    _original__init__(*mobject*, *target_mobject*, *transform_mismatches=False*, *fade_transform_mismatches=False*, *key_map=None*, ***kwargs*)
    :   Initialize self. See help(type(self)) for accurate signature.

        Parameters:
        :   - **mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **target_mobject** ([*Mobject*](manim.mobject.mobject.Mobject.html#manim.mobject.mobject.Mobject "manim.mobject.mobject.Mobject"))
            - **transform_mismatches** (*bool*)
            - **fade_transform_mismatches** (*bool*)
            - **key_map** (*dict* *|* *None*)
