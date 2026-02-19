# Manim CE Kitchen Sink (Static Agent Reference)

Use this document as direct implementation guidance when generating Manim scene code.
This file is designed for system-prompt injection and contains placeholder blocks where canonical examples will be inserted.

---

## Source Policy (Official Manim CE Docs Only)

Use only these official Manim Community Edition docs:

- [Docs Home](https://docs.manim.community/en/stable/index.html)
- [Reference Manual](https://docs.manim.community/en/stable/reference.html)
- [Tutorials & Guides](https://docs.manim.community/en/stable/tutorials_guides.html)
- [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)
- [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
- [Scenes Index](https://docs.manim.community/en/stable/reference_index/scenes.html)
- [Cameras Index](https://docs.manim.community/en/stable/reference_index/cameras.html)
- [Utilities Index](https://docs.manim.community/en/stable/reference_index/utilities_misc.html)
- [Building Blocks Tutorial](https://docs.manim.community/en/stable/tutorials/building_blocks.html)
- [Using Text and LaTeX](https://docs.manim.community/en/stable/guides/using_text.html)

---

## Core Contract (Doc-Backed Assertions)

- Scenes are implemented through `construct()` in `Scene`/scene subclasses.  
  Source: [Scenes Index](https://docs.manim.community/en/stable/reference_index/scenes.html)
- Animation progression is controlled via scene animation APIs (`play`, animation classes, composition).  
  Source: [Scene Reference](https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html), [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)
- Mobjects are the primary object model for visual elements and transformations.  
  Source: [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
- Use only documented stable APIs for compatibility.  
  Source: [Reference Manual](https://docs.manim.community/en/stable/reference.html)

---

## Pattern Family A: Scene Lifecycle and `self.play(...)`

Doc-backed assertions:
- Scene lifecycle is centered around `construct()` and staged animation calls.  
  Source: [Scene Reference](https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html), [Building Blocks Tutorial](https://docs.manim.community/en/stable/tutorials/building_blocks.html)
- Progressive sequencing (create -> animate -> remove/replace) is a standard tutorial pattern.  
  Source: [Building Blocks Tutorial](https://docs.manim.community/en/stable/tutorials/building_blocks.html)

```python
# PLACEHOLDER: A1 Scene Lifecycle Baseline
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_2d.py
# Future class: SceneLifecycleBaseline
#
# Insert canonical example demonstrating:
# - clean construct() flow
# - object setup
# - one reveal sequence
# - one transform sequence
# - cleanup before scene end
```

---

## Pattern Family B: 2D Geometry, Grouping, and Layout Composition

Doc-backed assertions:
- 2D primitives (for example `Circle`, `Rectangle`, `Polygon`, `Line`, `Arrow`) are part of documented mobject families.  
  Source: [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
- Grouping classes such as `VGroup` are provided for composition of multiple mobjects.  
  Source: [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)

```python
# PLACEHOLDER: B1 2D Primitive Gallery
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_2d.py
# Future class: GeometryGallery2D
#
# Insert canonical example demonstrating:
# - multiple primitives composed into one concept
# - VGroup-based organization
# - staged animation sequence with clear visual intent
```

```python
# PLACEHOLDER: B2 Layout and Label Anchoring
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_2d.py
# Future class: LayoutAndLabelAnchoring2D
#
# Insert canonical example demonstrating:
# - explicit placement + relative placement
# - label anchoring to nearby objects
# - spacing strategy that preserves readability
```

---

## Pattern Family C: Text and Math Typesetting (`Text`, `Tex`, `MathTex`)

Doc-backed assertions:
- Text and formula objects are documented separately and have distinct usage patterns.  
  Source: [Using Text and LaTeX](https://docs.manim.community/en/stable/guides/using_text.html), [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
- LaTeX rendering for formulas is covered in official text/formula guidance.  
  Source: [Using Text and LaTeX](https://docs.manim.community/en/stable/guides/using_text.html)

```python
# PLACEHOLDER: C1 Text Hierarchy and Annotations
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_text_math.py
# Future class: TextHierarchyAndCallouts
#
# Insert canonical example demonstrating:
# - title/subtitle structure
# - annotation labels
# - staged text reveal timing
```

```python
# PLACEHOLDER: C2 Math Transformation Pattern
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_text_math.py
# Future class: MathTexDerivationPattern
#
# Insert canonical example demonstrating:
# - equation introduction with MathTex
# - transformation between equation states
# - emphasis on key terms/parts
```

---

## Pattern Family D: Transition Choreography and Animation Composition

Doc-backed assertions:
- Transform variants (`Transform`, `ReplacementTransform`, `FadeTransform`) are documented animation classes.  
  Source: [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)
- Composition helpers (`AnimationGroup`, `LaggedStart`, `Succession`) are documented composition tools.  
  Source: [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)

```python
# PLACEHOLDER: D1 Core Transition Patterns
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_transitions.py
# Future class: TransitionPatternsCore
#
# Insert canonical example demonstrating:
# - Transform vs ReplacementTransform vs FadeTransform usage
# - comments on when each transition type is semantically correct
```

```python
# PLACEHOLDER: D2 Group Timing Patterns
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_transitions.py
# Future class: GroupedTimingPatterns
#
# Insert canonical example demonstrating:
# - AnimationGroup
# - LaggedStart
# - Succession
# - practical pacing for readability
```

---

## Pattern Family E: Graphing and Coordinate Systems

Doc-backed assertions:
- Graphing coordinate systems (for example `Axes`, `NumberPlane`) are documented mobject families.  
  Source: [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html), [Reference Manual](https://docs.manim.community/en/stable/reference.html)
- Plotting-oriented scene patterns are part of official tutorials and reference content.  
  Source: [Building Blocks Tutorial](https://docs.manim.community/en/stable/tutorials/building_blocks.html), [Reference Manual](https://docs.manim.community/en/stable/reference.html)

```python
# PLACEHOLDER: E1 Axes and Function Plot
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_graphing.py
# Future class: AxesAndFunctionPlot
#
# Insert canonical example demonstrating:
# - axis setup
# - function or parametric plot
# - labels/highlights tied to instructional intent
```

```python
# PLACEHOLDER: E2 Comparative Graph Narrative
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_graphing.py
# Future class: DataNarrativeGraphing
#
# Insert canonical example demonstrating:
# - progressive data/curve reveal
# - visual comparison pattern
# - cleanup between narrative beats
```

---

## Pattern Family F: 3D Scenes and Camera Control

Doc-backed assertions:
- 3D scene behavior is documented through `ThreeDScene` and camera APIs.  
  Source: [ThreeDScene Reference](https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html), [Cameras Index](https://docs.manim.community/en/stable/reference_index/cameras.html)
- Camera orientation/movement controls are explicit parts of the 3D scene API surface.  
  Source: [ThreeDScene Reference](https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html)

```python
# PLACEHOLDER: F1 3D Orientation Baseline
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_3d.py
# Future class: ThreeDOrientationBaseline
#
# Insert canonical example demonstrating:
# - ThreeDScene setup
# - camera orientation initialization
# - simple 3D object reveal with readable framing
```

```python
# PLACEHOLDER: F2 Camera Motion with Focus
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_3d.py
# Future class: CameraMotionAndFocus3D
#
# Insert canonical example demonstrating:
# - purposeful camera movement
# - object transformation under camera change
# - readability-oriented camera choices
```

---

## Pattern Family G: Dynamic Motion with Trackers and Updaters

Doc-backed assertions:
- `ValueTracker` is a documented mechanism for value-driven animation control.  
  Source: [ValueTracker Reference](https://docs.manim.community/en/stable/reference/manim.mobject.value_tracker.ValueTracker.html)
- Updater behavior is documented on mobject APIs and interacts with scene timing.  
  Source: [Mobject Reference](https://docs.manim.community/en/stable/reference/manim.mobject.mobject.Mobject.html), [Wait Reference](https://docs.manim.community/en/stable/reference/manim.animation.animation.Wait.html)

```python
# PLACEHOLDER: G1 ValueTracker + Updater Lifecycle
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_transitions.py
# Future class: ValueTrackerDrivenMotion
#
# Insert canonical example demonstrating:
# - ValueTracker-driven parameter updates
# - add_updater and remove_updater lifecycle
# - controlled motion window with clear start/stop behavior
```

---

## Pattern Family H: Color, Fill, Stroke, and Palette Behavior

Doc-backed assertions:
- Manim color utilities are documented under `manim.utils.color`.  
  Source: [Color Utilities Reference](https://docs.manim.community/en/stable/reference/manim.utils.color.html), [Utilities Index](https://docs.manim.community/en/stable/reference_index/utilities_misc.html)
- Mobject/VMobject styling APIs provide documented color/fill/stroke controls.  
  Source: [Mobject Reference](https://docs.manim.community/en/stable/reference/manim.mobject.mobject.Mobject.html), [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
- Color-related animation transitions are part of documented animation APIs (for example transform/fade families).  
  Source: [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)

```python
# PLACEHOLDER: H1 Color Palette and Semantic Mapping
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_2d.py
# Future class: ColorSemanticPalette
#
# Insert canonical example demonstrating:
# - a small, coherent palette
# - semantic color mapping (for example state A/state B/highlight)
# - consistent color reuse across scene beats
```

```python
# PLACEHOLDER: H2 Fill/Stroke/Opacity Styling Pattern
# Future source: docs/reference_docs/kitchen_sink/kitchen_sink_transitions.py
# Future class: FillStrokeStyleTransitions
#
# Insert canonical example demonstrating:
# - set_fill / set_stroke style changes
# - opacity and emphasis transitions
# - readability-preserving contrast choices
```

---

## Agent-Facing Quality Checklist (Doc-Backed)

- Is scene construction/animation flow consistent with documented scene APIs?  
  Source: [Scene Reference](https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html), [Animations Index](https://docs.manim.community/en/stable/reference_index/animations.html)
- Are used objects and methods documented in stable Manim CE references?  
  Source: [Reference Manual](https://docs.manim.community/en/stable/reference.html)
- Are text/math object choices aligned with official text/LaTeX guidance?  
  Source: [Using Text and LaTeX](https://docs.manim.community/en/stable/guides/using_text.html)
- Are 3D/camera choices aligned with documented 3D scene APIs (when applicable)?  
  Source: [ThreeDScene Reference](https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html), [Cameras Index](https://docs.manim.community/en/stable/reference_index/cameras.html)
- Are updater/tracker usages aligned with documented lifecycle behavior (when applicable)?  
  Source: [ValueTracker Reference](https://docs.manim.community/en/stable/reference/manim.mobject.value_tracker.ValueTracker.html), [Mobject Reference](https://docs.manim.community/en/stable/reference/manim.mobject.mobject.Mobject.html), [Wait Reference](https://docs.manim.community/en/stable/reference/manim.animation.animation.Wait.html)
- Are color/styling choices implemented through documented color/styling APIs?  
  Source: [Color Utilities Reference](https://docs.manim.community/en/stable/reference/manim.utils.color.html), [Mobjects Index](https://docs.manim.community/en/stable/reference_index/mobjects.html)
