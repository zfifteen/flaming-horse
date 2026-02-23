<!-- source: https://docs.manim.community/en/stable/reference/manim.mobject.geometry.arc.html -->

# arc

Mobjects that are curved.

Examples

Example: UsefulAnnotations

```python
from manim import *

class UsefulAnnotations(Scene):
    def construct(self):
        m0 = Dot()
        m1 = AnnotationDot()
        m2 = LabeledDot("ii")
        m3 = LabeledDot(MathTex(r"\alpha").set_color(ORANGE))
        m4 = CurvedArrow(2*LEFT, 2*RIGHT, radius= -5)
        m5 = CurvedArrow(2*LEFT, 2*RIGHT, radius= 8)
        m6 = CurvedDoubleArrow(ORIGIN, 2*RIGHT)

        self.add(m0, m1, m2, m3, m4, m5, m6)
        for i, mobj in enumerate(self.mobjects):
            mobj.shift(DOWN * (i-3))
```

```python
class UsefulAnnotations(Scene):
    def construct(self):
        m0 = Dot()
        m1 = AnnotationDot()
        m2 = LabeledDot("ii")
        m3 = LabeledDot(MathTex(r"\alpha").set_color(ORANGE))
        m4 = CurvedArrow(2*LEFT, 2*RIGHT, radius= -5)
        m5 = CurvedArrow(2*LEFT, 2*RIGHT, radius= 8)
        m6 = CurvedDoubleArrow(ORIGIN, 2*RIGHT)

        self.add(m0, m1, m2, m3, m4, m5, m6)
        for i, mobj in enumerate(self.mobjects):
            mobj.shift(DOWN * (i-3))
```

Classes

|  |  |
| --- | --- |
| [`AnnotationDot`](manim.mobject.geometry.arc.AnnotationDot.html#manim.mobject.geometry.arc.AnnotationDot "manim.mobject.geometry.arc.AnnotationDot") | A dot with bigger radius and bold stroke to annotate scenes. |
| [`AnnularSector`](manim.mobject.geometry.arc.AnnularSector.html#manim.mobject.geometry.arc.AnnularSector "manim.mobject.geometry.arc.AnnularSector") | A sector of an annulus. |
| [`Annulus`](manim.mobject.geometry.arc.Annulus.html#manim.mobject.geometry.arc.Annulus "manim.mobject.geometry.arc.Annulus") | Region between two concentric [`Circles`](manim.mobject.geometry.arc.Circle.html#manim.mobject.geometry.arc.Circle "manim.mobject.geometry.arc.Circle"). |
| [`Arc`](manim.mobject.geometry.arc.Arc.html#manim.mobject.geometry.arc.Arc "manim.mobject.geometry.arc.Arc") | A circular arc. |
| [`ArcBetweenPoints`](manim.mobject.geometry.arc.ArcBetweenPoints.html#manim.mobject.geometry.arc.ArcBetweenPoints "manim.mobject.geometry.arc.ArcBetweenPoints") | Inherits from Arc and additionally takes 2 points between which the arc is spanned. |
| [`ArcPolygon`](manim.mobject.geometry.arc.ArcPolygon.html#manim.mobject.geometry.arc.ArcPolygon "manim.mobject.geometry.arc.ArcPolygon") | A generalized polygon allowing for points to be connected with arcs. |
| [`ArcPolygonFromArcs`](manim.mobject.geometry.arc.ArcPolygonFromArcs.html#manim.mobject.geometry.arc.ArcPolygonFromArcs "manim.mobject.geometry.arc.ArcPolygonFromArcs") | A generalized polygon allowing for points to be connected with arcs. |
| [`Circle`](manim.mobject.geometry.arc.Circle.html#manim.mobject.geometry.arc.Circle "manim.mobject.geometry.arc.Circle") | A circle. |
| [`CubicBezier`](manim.mobject.geometry.arc.CubicBezier.html#manim.mobject.geometry.arc.CubicBezier "manim.mobject.geometry.arc.CubicBezier") | A cubic Bézier curve. |
| [`CurvedArrow`](manim.mobject.geometry.arc.CurvedArrow.html#manim.mobject.geometry.arc.CurvedArrow "manim.mobject.geometry.arc.CurvedArrow") |  |
| [`CurvedDoubleArrow`](manim.mobject.geometry.arc.CurvedDoubleArrow.html#manim.mobject.geometry.arc.CurvedDoubleArrow "manim.mobject.geometry.arc.CurvedDoubleArrow") |  |
| [`Dot`](manim.mobject.geometry.arc.Dot.html#manim.mobject.geometry.arc.Dot "manim.mobject.geometry.arc.Dot") | A circle with a very small radius. |
| [`Ellipse`](manim.mobject.geometry.arc.Ellipse.html#manim.mobject.geometry.arc.Ellipse "manim.mobject.geometry.arc.Ellipse") | A circular shape; oval, circle. |
| [`LabeledDot`](manim.mobject.geometry.arc.LabeledDot.html#manim.mobject.geometry.arc.LabeledDot "manim.mobject.geometry.arc.LabeledDot") | A [`Dot`](manim.mobject.geometry.arc.Dot.html#manim.mobject.geometry.arc.Dot "manim.mobject.geometry.arc.Dot") containing a label in its center. |
| [`Sector`](manim.mobject.geometry.arc.Sector.html#manim.mobject.geometry.arc.Sector "manim.mobject.geometry.arc.Sector") | A sector of a circle. |
| [`TangentialArc`](manim.mobject.geometry.arc.TangentialArc.html#manim.mobject.geometry.arc.TangentialArc "manim.mobject.geometry.arc.TangentialArc") | Construct an arc that is tangent to two intersecting lines. |
| [`TipableVMobject`](manim.mobject.geometry.arc.TipableVMobject.html#manim.mobject.geometry.arc.TipableVMobject "manim.mobject.geometry.arc.TipableVMobject") | Meant for shared functionality between Arc and Line. |
