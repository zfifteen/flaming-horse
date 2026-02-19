# Manim Community Edition Kitchen Sink Reference

**Purpose:** Agent-facing reference for Manim CE scene generation in stateless pipeline contexts.  
**Version:** Manim Community Edition v0.19.2  
**Target:** Backend prompt injection for build-scenes phase

---

## Source Policy

**STRICT REQUIREMENT:** All technical patterns, code examples, and assertions in this document are derived exclusively from official Manim Community Edition documentation.

**Allowed Sources:**
- https://docs.manim.community/en/stable/
- https://docs.manim.community/en/stable/reference.html
- https://docs.manim.community/en/stable/reference_index/
- https://docs.manim.community/en/stable/tutorials_guides.html
- https://docs.manim.community/en/stable/guides/using_text.html
- https://docs.manim.community/en/stable/examples.html

**Forbidden:** Third-party blogs, videos, forums, non-official tutorials.

---

## Core Contract for Agent Usage

This document provides canonical Manim CE patterns for scene body generation. When building scenes:

1. **Use only documented Manim CE APIs** from the sources listed above
2. **Reference official documentation links** when uncertain about API usage
3. **Follow established patterns** for common tasks (text, geometry, animation composition)
4. **Validate color types** - use built-in color constants, hex strings, or RGB tuples
5. **Test positioning** - ensure all elements stay within frame bounds
6. **Compose animations** using self.play() with proper timing

This reference is static and suitable for direct system-prompt injection.

---

## Pattern Family 1: Scene Lifecycle and self.play()

### Scene Class Hierarchy

**Documentation:** [Scene API Reference](https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html)

All Manim scenes inherit from the `Scene` class and override the `construct()` method:

```python
from manim import *

class MyScene(Scene):
    def construct(self):
        # Animation code goes here
        pass
```

### Scene Lifecycle Methods

1. **setup()** - Optional initialization before animations (variables, configurations)
2. **construct()** - Required; contains all animation code
3. **tear_down()** - Optional cleanup after rendering

**Execution Order:** setup() → construct() → tear_down()

**Important:** Do not override `__init__`; use `setup()` for pre-render initialization.

### self.play() - The Core Animation Method

**Documentation:** [Scene.play()](https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html#manim.scene.scene.Scene.play)

The `self.play()` method is the primary way to animate objects in Manim:

```python
# Single animation
self.play(Write(text))

# Multiple simultaneous animations
self.play(FadeIn(circle), FadeOut(square))

# With timing parameters
self.play(Transform(obj1, obj2), run_time=2, rate_func=smooth)
```

**Key Parameters:**
- `run_time` - Duration of animation in seconds
- `rate_func` - Easing function (linear, smooth, etc.)

### self.add() vs self.play()

- **self.add(mobject)** - Adds object instantly without animation
- **self.play(Animation(mobject))** - Animates the appearance/transformation

```python
# Instant appearance
self.add(circle)

# Animated appearance
self.play(FadeIn(circle))
```

### Animation Sequencing

**Sequential:** Multiple `self.play()` calls execute one after another:

```python
self.play(Write(title))
self.play(FadeIn(subtitle))
self.play(Create(diagram))
```

**Parallel:** Multiple animations in one `self.play()` execute simultaneously:

```python
self.play(
    Write(title),
    FadeIn(subtitle),
    Create(diagram)
)
```

---

## Pattern Family 2: 2D Geometry and Grouping

### Basic 2D Shapes

**Documentation:** 
- [Arc and Circles](https://docs.manim.community/en/stable/reference/manim.mobject.geometry.arc.html)
- [Lines and Arrows](https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.html)
- [Polygons](https://docs.manim.community/en/stable/reference/manim.mobject.geometry.polygram.html)

```python
# Circles and Arcs
circle = Circle(radius=1.5, color=BLUE)
dot = Dot(point=ORIGIN, color=RED)
arc = Arc(radius=2, angle=PI/2)

# Lines and Arrows
line = Line(start=LEFT, end=RIGHT)
arrow = Arrow(start=DOWN, end=UP)
vector = Vector(direction=RIGHT*2)

# Polygons
square = Square(side_length=2)
rectangle = Rectangle(width=4, height=2)
triangle = Triangle()
polygon = Polygon(UP, RIGHT, DOWN, LEFT)
rounded_rect = RoundedRectangle(corner_radius=0.2)
```

### VGroup - Grouping Objects

**Documentation:** [VGroup API](https://docs.manim.community/en/stable/reference/manim.mobject.types.vectorized_mobject.VGroup.html)

`VGroup` is the primary way to group multiple VMobjects for collective transformation, movement, or styling:

```python
# Create group with multiple objects
circle = Circle(color=RED)
square = Square(color=GREEN)
triangle = Triangle(color=BLUE)

group = VGroup(circle, square, triangle)

# Apply transformations to entire group
group.arrange(RIGHT, buff=0.5)
self.play(group.animate.shift(UP))

# Add/remove elements
group.add(Dot())
group += Circle()  # Alternative syntax
group -= square    # Remove element
```

**Key VGroup Methods:**
- `.arrange(direction, buff=0.5)` - Arrange objects in line
- `.arrange_in_grid(rows, cols, buff=0.5)` - Grid layout
- `.scale(factor)` - Scale entire group
- `.shift(vector)` - Move entire group
- `.set_color(color)` - Color all elements

**Indexing and Iteration:**
```python
group[0]           # First element
group[-1]          # Last element
for obj in group:  # Iterate over elements
    obj.set_opacity(0.5)
```

---

## Pattern Family 3: Text and Math Typesetting

### Text Objects

**Documentation:** [Text Mobject](https://docs.manim.community/en/stable/reference/manim.mobject.text.text_mobject.html)

Use `Text` for simple text without LaTeX:

```python
# Basic text
text = Text("Hello, World!", font_size=48)

# With styling
text = Text("Styled Text", font_size=36, color=BLUE, weight=BOLD)

# Font selection
text = Text("Code Text", font="Courier New", font_size=28)
```

### Mathematical Typesetting with MathTex

**Documentation:** 
- [MathTex API](https://docs.manim.community/en/stable/reference/manim.mobject.text.tex_mobject.MathTex.html)
- [Text and Formulas Guide](https://docs.manim.community/en/stable/guides/using_text.html)

Use `MathTex` for mathematical expressions (compiled in LaTeX math mode):

```python
# Basic formula
formula = MathTex(r"\int_a^b f'(x)\,dx = f(b)-f(a)")

# Multiple parts for animation
parts = MathTex(r"E", r"=", r"mc^2")

# With color mapping
equation = MathTex(
    r"\frac{d}{dx}",
    r"f(x)",
    r"=",
    r"f'(x)",
    tex_to_color_map={r"f(x)": BLUE, r"f'(x)": RED}
)
```

**Important:** Use `MathTex` for equations, not `Tex`. The `MathTex` class automatically wraps content in math mode.

### Tex for General LaTeX

Use `Tex` for general LaTeX formatting (not just math):

```python
# General LaTeX
text = Tex(r"This is \textbf{bold} text")
greek = Tex(r"$\alpha + \beta = \gamma$")
```

### Text vs MathTex vs Tex Decision Matrix

| Content Type | Use | Example |
|--------------|-----|---------|
| Plain text | `Text` | `Text("Hello")` |
| Code/monospace | `Text` with font | `Text("code", font="Courier New")` |
| Equations | `MathTex` | `MathTex(r"a^2 + b^2")` |
| LaTeX formatting | `Tex` | `Tex(r"\alpha + \beta")` |

**Never use:** `\texttt`, `\verb`, or `\begin{verbatim}` in Tex - use `Text()` with `font="Courier New"` instead.

---

## Pattern Family 4: Transition Choreography and Animation Composition

### Creation Animations

**Documentation:** [Creation Animations](https://docs.manim.community/en/stable/reference/manim.animation.creation.html)

```python
# Writing text
self.play(Write(text))

# Creating shapes
self.play(Create(circle))

# Drawing borders then filling
self.play(DrawBorderThenFill(square))

# Uncreating (reverse)
self.play(Uncreate(shape))
```

### Fading Animations

**Documentation:** [Fading Animations](https://docs.manim.community/en/stable/reference/manim.animation.fading.html)

```python
# Fade in
self.play(FadeIn(mobject))

# Fade out
self.play(FadeOut(mobject))

# Fade multiple objects
self.play(FadeIn(obj1), FadeOut(obj2))
```

### Transform Animations

**Documentation:** [Transform Animations](https://docs.manim.community/en/stable/reference/manim.animation.transform.html)

```python
# Transform one object into another
self.play(Transform(square, circle))

# Replacement transform (better for most cases)
self.play(ReplacementTransform(square, circle))

# Fade transform
self.play(FadeTransform(obj1, obj2))

# Color change
self.play(FadeToColor(mobject, RED))

# Rotation
self.play(Rotate(mobject, angle=PI/2))
```

### Growing Animations

**Documentation:** [Growing Animations](https://docs.manim.community/en/stable/reference/manim.animation.growing.html)

```python
# Grow from center
self.play(GrowFromCenter(circle))

# Grow from edge
self.play(GrowFromEdge(rectangle, UP))

# Grow arrow
self.play(GrowArrow(arrow))

# Spin in
self.play(SpinInFromNothing(mobject))
```

### Indication Animations

**Documentation:** [Indication Animations](https://docs.manim.community/en/stable/reference/manim.animation.indication.html)

```python
# Indicate (highlight briefly)
self.play(Indicate(mobject))

# Flash
self.play(Flash(point=ORIGIN))

# Focus on
self.play(FocusOn(mobject))

# Circumscribe (draw circle around)
self.play(Circumscribe(mobject))

# Wiggle
self.play(Wiggle(mobject))
```

### Animation Composition - LaggedStart

**Documentation:** [LaggedStart](https://docs.manim.community/en/stable/reference/manim.animation.composition.LaggedStart.html)

`LaggedStart` staggers animations with overlapping starts:

```python
# Staggered fade-in
self.play(
    LaggedStart(
        FadeIn(obj1),
        FadeIn(obj2),
        FadeIn(obj3),
        lag_ratio=0.25,  # Start next when current is 25% done
        run_time=3
    )
)

# With multiple objects
dots = VGroup(*[Dot() for _ in range(5)])
dots.arrange(RIGHT)
self.play(
    LaggedStart(
        *[FadeIn(dot) for dot in dots],
        lag_ratio=0.2
    )
)
```

**Key Parameter:**
- `lag_ratio` (default 0.05) - Fraction of animation completed before next starts (0 to 1)

### Animation Composition - Succession

**Documentation:** [Succession](https://docs.manim.community/en/stable/reference/manim.animation.composition.Succession.html)

`Succession` plays animations sequentially (one after another):

```python
# Sequential animations in one play call
self.play(
    Succession(
        Write(text1),
        Write(text2),
        Write(text3),
        lag_ratio=1.0  # Default: wait for previous to finish
    )
)
```

### Rate Functions

**Documentation:** [Rate Functions](https://docs.manim.community/en/stable/reference/manim.utils.rate_functions.html)

Rate functions control animation easing (acceleration/deceleration):

```python
# Linear (constant speed)
self.play(Write(text), rate_func=linear)

# Smooth (sigmoid easing)
self.play(Create(circle), rate_func=smooth)

# Ease in/out
self.play(FadeIn(obj), rate_func=ease_in_cubic)
self.play(FadeOut(obj), rate_func=ease_out_quad)

# Special effects
self.play(Rotate(obj, PI), rate_func=there_and_back)
self.play(Wiggle(obj), rate_func=wiggle)
```

**Common Rate Functions:**
- `linear` - Constant speed
- `smooth` - Smooth start and end (sigmoid)
- `ease_in_*` - Slow start, fast end
- `ease_out_*` - Fast start, slow end
- `there_and_back` - Go and return
- `wiggle` - Oscillating motion

---

## Pattern Family 5: Graphing and Coordinate Systems

### Axes - Cartesian Coordinate System

**Documentation:** [Axes API](https://docs.manim.community/en/stable/reference/manim.mobject.graphing.coordinate_systems.Axes.html)

```python
# Basic axes
axes = Axes(
    x_range=[0, 10, 1],    # [min, max, step]
    y_range=[0, 8, 1],
    x_length=10,
    y_length=6,
    axis_config={"color": BLUE}
)

# Plotting functions
graph = axes.plot(lambda x: x**2, color=RED)
self.play(Create(axes), Create(graph))

# Labels
labels = axes.get_axis_labels(x_label="t", y_label="f(t)")
self.play(Write(labels))
```

**Key Methods:**
- `axes.coords_to_point(x, y)` or `axes.c2p(x, y)` - Convert coordinates to scene point
- `axes.point_to_coords(point)` or `axes.p2c(point)` - Convert scene point to coordinates
- `axes.plot(function, x_range)` - Plot a function
- `axes.get_axis_labels()` - Add axis labels

### NumberPlane - Grid Background

**Documentation:** [NumberPlane API](https://docs.manim.community/en/stable/reference/manim.mobject.graphing.coordinate_systems.NumberPlane.html)

`NumberPlane` extends `Axes` with a visible grid:

```python
# Number plane with grid
plane = NumberPlane(
    x_range=[-5, 5, 1],
    y_range=[-3, 3, 1],
    background_line_style={
        "stroke_color": TEAL,
        "stroke_width": 2,
        "stroke_opacity": 0.4
    }
)
self.add(plane)

# Plot on number plane
graph = plane.plot(np.sin, color=YELLOW)
self.play(Create(graph))
```

### NumberLine - 1D Number Line

**Documentation:** [NumberLine API](https://docs.manim.community/en/stable/reference/manim.mobject.graphing.number_line.NumberLine.html)

```python
# Number line
line = NumberLine(
    x_range=[0, 10, 1],
    length=10,
    include_numbers=True
)

# Add point on line
point = Dot(color=RED).move_to(line.number_to_point(5))
self.play(Create(line), FadeIn(point))
```

### Function Plotting

**Documentation:** [Function Graphs](https://docs.manim.community/en/stable/reference/manim.mobject.graphing.functions.html)

```python
# Plot function
axes = Axes(x_range=[-3, 3], y_range=[-2, 2])
graph = axes.plot(lambda x: x**2 - 1, color=GREEN)

# Parametric function
parametric = ParametricFunction(
    lambda t: np.array([np.cos(t), np.sin(t), 0]),
    t_range=[0, TAU],
    color=BLUE
)

# Implicit function
implicit = ImplicitFunction(
    lambda x, y: x**2 + y**2 - 4,
    color=RED
)
```

---

## Pattern Family 6: 3D Scene and Camera Control

### ThreeDScene Class

**Documentation:** [ThreeDScene API](https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html)

Inherit from `ThreeDScene` for 3D animations:

```python
from manim import *

class My3DScene(ThreeDScene):
    def construct(self):
        # 3D content here
        pass
```

### 3D Objects

**Documentation:** 
- [3D Primitives](https://docs.manim.community/en/stable/reference/manim.mobject.three_d.three_dimensions.html)
- [Polyhedra](https://docs.manim.community/en/stable/reference/manim.mobject.three_d.polyhedra.html)

```python
# Basic 3D shapes
sphere = Sphere(radius=1, color=BLUE)
cube = Cube(side_length=2, fill_opacity=0.7)
cone = Cone(base_radius=1, height=2)
cylinder = Cylinder(radius=1, height=2)
torus = Torus(major_radius=2, minor_radius=0.5)

# 3D primitives
arrow_3d = Arrow3D(start=ORIGIN, end=UP*2)
line_3d = Line3D(start=LEFT, end=RIGHT)
dot_3d = Dot3D(point=ORIGIN)

# Polyhedra
tetrahedron = Tetrahedron()
octahedron = Octahedron()
dodecahedron = Dodecahedron()
icosahedron = Icosahedron()
```

### 3D Axes

```python
# 3D coordinate system
axes = ThreeDAxes(
    x_range=[-5, 5, 1],
    y_range=[-5, 5, 1],
    z_range=[-3, 3, 1]
)

# Surface plot
surface = Surface(
    lambda u, v: np.array([u, v, u**2 - v**2]),
    u_range=[-2, 2],
    v_range=[-2, 2]
)
```

### Camera Control

**Documentation:** [ThreeDScene Camera Methods](https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html)

#### Set Camera Orientation (Instant)

```python
# Set camera view instantly
self.set_camera_orientation(
    phi=70 * DEGREES,     # Vertical angle
    theta=240 * DEGREES,  # Horizontal angle
    gamma=0,              # Roll angle
    distance=8            # Distance from origin
)
```

#### Move Camera (Animated)

```python
# Animate camera movement
self.move_camera(
    phi=60 * DEGREES,
    theta=45 * DEGREES,
    run_time=3,
    rate_func=smooth
)
```

#### Ambient Camera Rotation

```python
# Start continuous rotation
self.begin_ambient_camera_rotation(
    rate=0.2,        # Rotation speed
    about="theta"    # Rotate around theta or phi
)

# Do other animations while camera rotates
self.play(Write(text))
self.wait(2)

# Stop rotation
self.stop_ambient_camera_rotation()
```

### Fixed Frame Objects

Objects that stay fixed relative to camera:

```python
# Add objects that don't move with camera
title = Text("3D Animation")
self.add_fixed_in_frame_mobjects(title)
title.to_corner(UL)

# Objects that maintain orientation
label = Text("Label")
self.add_fixed_orientation_mobjects(label)
```

---

## Pattern Family 7: Trackers and Updaters

### ValueTracker

**Documentation:** [ValueTracker](https://docs.manim.community/en/stable/reference/manim.mobject.value_tracker.ValueTracker.html)

`ValueTracker` stores a numerical value that can be animated:

```python
# Create tracker
alpha = ValueTracker(0)

# Animate tracker value
self.play(alpha.animate.set_value(1), run_time=3)

# Access current value
current = alpha.get_value()
```

### Updaters

**Documentation:** [Updater Utilities](https://docs.manim.community/en/stable/reference/manim.animation.updaters.mobject_update_utils.html)

Updaters execute every frame to update object properties:

```python
# Define updater function
def update_position(mobject):
    mobject.next_to(other_object, UP)

# Add updater to mobject
square.add_updater(update_position)

# Updaters run automatically on every frame
self.play(other_object.animate.shift(RIGHT * 3))

# Remove updater when done
square.remove_updater(update_position)

# Or clear all updaters
square.clear_updaters()
```

### always_redraw

**Documentation:** [always_redraw](https://docs.manim.community/en/stable/reference/manim.animation.updaters.mobject_update_utils.html#manim.animation.updaters.mobject_update_utils.always_redraw)

`always_redraw` regenerates a mobject every frame based on a function:

```python
# Create axes and tracker
axes = Axes()
alpha = ValueTracker(0)

# Point that tracks along a curve
sine_curve = axes.plot(np.sin)
moving_point = always_redraw(
    lambda: Dot(
        sine_curve.point_from_proportion(alpha.get_value()),
        color=RED
    )
)

# Tangent line that updates as point moves
tangent = always_redraw(
    lambda: TangentLine(
        sine_curve,
        alpha=alpha.get_value(),
        length=3,
        color=YELLOW
    )
)

# Add and animate
self.add(axes, sine_curve, moving_point, tangent)
self.play(alpha.animate.set_value(1), run_time=4, rate_func=linear)
```

**Key Point:** The lambda function is called every frame to regenerate the mobject.

### Updater Control Methods

```python
# Pause updaters temporarily
mobject.suspend_updating()

# Resume updaters
mobject.resume_updating()

# Check if updaters are active
is_updating = mobject.updating_suspended
```

---

## Pattern Family 8: Color, Fill, Stroke, and Palette Behavior

### Color Types in Manim

**Documentation:** 
- [Color Utilities](https://docs.manim.community/en/stable/reference/manim.utils.color.html)
- [Predefined Colors](https://docs.manim.community/en/stable/reference/manim.utils.color.manim_colors.html)

Manim accepts three color types:

1. **Built-in color constants** (uppercase names)
2. **Hex strings** (e.g., "#FF5500")
3. **RGB tuples** (values 0.0 to 1.0)

```python
# Built-in color constants
circle = Circle(color=BLUE)
square = Square(color=RED)
triangle = Triangle(color=GREEN)

# Hex strings
custom1 = Circle(color="#FF5500")
custom2 = Square(color="#3498db")

# RGB tuples
custom3 = Triangle(color=(0.8, 0.2, 0.4))  # RGB values 0.0-1.0
```

### Predefined Color Constants

**Documentation:** [manim_colors](https://docs.manim.community/en/stable/reference/manim.utils.color.manim_colors.html)

Common colors available by name:

```python
# Basic colors
RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, PINK
WHITE, BLACK, GRAY, GREY

# Extended colors
TEAL, MAROON, GOLD, DARK_BLUE, DARK_BROWN
LIGHT_GRAY, LIGHT_PINK, LIGHT_BROWN

# Special color sets
BLUE_A, BLUE_B, BLUE_C, BLUE_D, BLUE_E
RED_A, RED_B, RED_C, RED_D, RED_E
# (Similar patterns for GREEN, YELLOW, etc.)
```

### XKCD and SVG Color Names

Some colors require explicit import:

```python
from manim import XKCD

# XKCD survey colors
color1 = XKCD.AVOCADO
color2 = XKCD.SEAFOAM
```

### Setting Fill Color

**Documentation:** [VMobject.set_fill()](https://docs.manim.community/en/stable/reference/manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject.set_fill)

```python
# Set fill color and opacity
square = Square()
square.set_fill(RED, opacity=0.7)

# Fill without opacity change
circle.set_fill(BLUE)

# Multiple objects
group = VGroup(Circle(), Square())
group.set_fill(YELLOW, opacity=0.5)
```

### Setting Stroke Color

**Documentation:** [VMobject.set_stroke()](https://docs.manim.community/en/stable/reference/manim.mobject.types.vectorized_mobject.VMobject.html#manim.mobject.types.vectorized_mobject.VMobject.set_stroke)

```python
# Set stroke (border) color and width
square = Square()
square.set_stroke(BLUE, width=4)

# Stroke with opacity
circle.set_stroke(RED, width=2, opacity=0.8)
```

### Setting Both Fill and Stroke

```python
# Set both at once with set_style()
rectangle = Rectangle()
rectangle.set_style(
    fill_color=YELLOW,
    fill_opacity=0.6,
    stroke_color=BLACK,
    stroke_width=3
)

# Or chain methods
square = Square()
square.set_fill(RED, opacity=0.5).set_stroke(BLUE, width=2)
```

### Setting Object Color (Both Fill and Stroke)

```python
# Set both fill and stroke to same color
circle = Circle()
circle.set_color(GREEN)

# This affects both fill and stroke
```

### Color Gradients

```python
# Gradient fill
rectangle = Rectangle(height=4, width=6)
rectangle.set_sheen_direction(RIGHT)
rectangle.set_color_by_gradient(BLUE, GREEN, YELLOW)
```

### Color in Constructors

Most geometry constructors accept color parameters:

```python
# Color in constructor
circle = Circle(color=BLUE, fill_opacity=0.5, stroke_width=3)
square = Square(color=RED, fill_opacity=0.8)
line = Line(start=LEFT, end=RIGHT, color=YELLOW, stroke_width=5)
```

### Invalid Color Patterns (Common Errors)

```python
# ❌ WRONG - Function return value not a color
blues = harmonious_color(BLUE, variations=3)
circle = Circle(color=blues[0])  # blues[0] is a list, not a color

# ✅ CORRECT - Extract actual color value
blues = harmonious_color(BLUE, variations=3)
circle = Circle(color=BLUE)  # Use built-in color constant instead

# ❌ WRONG - Undefined color variable
circle = Circle(color=my_custom_blue)  # my_custom_blue not defined

# ✅ CORRECT - Use defined color
my_custom_blue = "#3498db"
circle = Circle(color=my_custom_blue)
```

### Color Animation

```python
# Animate color change
self.play(FadeToColor(mobject, RED))

# Or using animate syntax
self.play(mobject.animate.set_color(BLUE))
```

---

## Agent-Facing Quality Checklist

Use this checklist to validate scene code quality before rendering:

### API Correctness
- [ ] All classes and methods are from official Manim CE documentation
- [ ] No deprecated APIs or undefined functions
- [ ] Color types are valid (constants, hex strings, or RGB tuples)
- [ ] MathTex used for equations, Text for plain text
- [ ] Scene inherits from Scene or ThreeDScene

### Positioning and Layout
- [ ] All objects positioned with explicit coordinates
- [ ] No objects placed off-screen (check frame bounds)
- [ ] Proper spacing between elements (use buff parameter)
- [ ] Text uses appropriate font_size (24-48 typical range)

### Animation Quality
- [ ] self.play() used for all animations
- [ ] Appropriate animation types chosen (Write for text, Create for shapes)
- [ ] run_time and rate_func specified when needed
- [ ] No empty waits or static frames > 2 seconds
- [ ] Proper cleanup (FadeOut) before scene transitions

### Code Structure
- [ ] No imports (scene body only in template context)
- [ ] No class definitions (already in scaffold)
- [ ] No loops (use explicit values or VGroup operations)
- [ ] No random functions (deterministic only)
- [ ] Proper indentation (4 spaces)

### 3D Specific (if applicable)
- [ ] Camera orientation set explicitly
- [ ] 3D objects use appropriate primitives
- [ ] Fixed-frame objects added for HUD elements
- [ ] Ambient rotation started/stopped properly

### Visual Polish
- [ ] Consistent color scheme throughout scene
- [ ] Text readable (sufficient contrast)
- [ ] Smooth transitions between states
- [ ] LaggedStart used for staggered reveals when appropriate
- [ ] rate_func selected for desired easing effect

---

## Technical Validation Patterns

### Before Rendering: Code Self-Check

1. **Verify all color assignments:**
   - Built-in constants (BLUE, RED, etc.)
   - Hex strings ("#FF5500")
   - RGB tuples (0.5, 0.3, 0.8)
   - No function returns or undefined variables

2. **Validate positioning:**
   - All coordinates within frame bounds (-8.89 to 8.89 horizontal, -5 to 5 vertical)
   - Explicit `.move_to()` or `.shift()` calls
   - Proper `.next_to()` usage with buff parameter

3. **Check animation flow:**
   - Every visible object has FadeIn/Create or is added with self.add()
   - Cleanup (FadeOut) before major transitions
   - No orphaned objects left on screen

4. **Confirm imports not needed:**
   - No `from manim import *` in scene body
   - All Manim classes available from scaffold
   - Custom helpers already imported in template

---

## Canonical Code Patterns

### Pattern: Basic Scene with Text and Shape

```python
# Title
title = Text("Scene Title", font_size=48, color=BLUE)
title.move_to(UP * 3)
self.play(Write(title))

# Subtitle
subtitle = Text("Subtitle text", font_size=32)
subtitle.next_to(title, DOWN, buff=0.5)
self.play(FadeIn(subtitle))

# Visual element
circle = Circle(radius=1.5, color=GREEN, fill_opacity=0.5)
circle.move_to(ORIGIN)
self.play(Create(circle))

# Cleanup
self.play(FadeOut(title), FadeOut(subtitle), FadeOut(circle))
```

### Pattern: Mathematical Formula Reveal

```python
# Equation parts
eq = MathTex(r"E", r"=", r"mc^2")
eq.move_to(ORIGIN)

# Animate writing
self.play(Write(eq))
self.wait(1)

# Highlight specific part
self.play(Indicate(eq[2]))  # Highlight "mc^2"
self.wait(1)

# Transform to expanded form
expanded = MathTex(r"E = m \cdot (3 \times 10^8)^2")
expanded.move_to(ORIGIN)
self.play(ReplacementTransform(eq, expanded))
```

### Pattern: Graph with Function Plot

```python
# Create axes
axes = Axes(
    x_range=[0, 4, 1],
    y_range=[0, 4, 1],
    x_length=6,
    y_length=6
)
axes.move_to(ORIGIN)

# Plot function
graph = axes.plot(lambda x: x**2, color=RED)

# Labels
labels = axes.get_axis_labels(x_label="x", y_label="f(x)")

# Animate creation
self.play(Create(axes))
self.play(Write(labels))
self.play(Create(graph), run_time=2)
```

### Pattern: 3D Object with Camera Movement

```python
# Create 3D object
cube = Cube(side_length=2, fill_opacity=0.8)
self.add(cube)

# Set initial camera
self.set_camera_orientation(phi=70*DEGREES, theta=45*DEGREES)

# Start rotation
self.begin_ambient_camera_rotation(rate=0.15)
self.wait(3)
self.stop_ambient_camera_rotation()

# Move camera to new position
self.move_camera(phi=30*DEGREES, theta=90*DEGREES, run_time=2)
```

### Pattern: Staggered Group Animation

```python
# Create group of objects
dots = VGroup(*[Dot() for _ in range(5)])
dots.arrange(RIGHT, buff=0.5)
dots.move_to(ORIGIN)

# Staggered fade-in
self.play(
    LaggedStart(
        *[FadeIn(dot) for dot in dots],
        lag_ratio=0.2,
        run_time=2
    )
)

# Collective transformation
self.play(dots.animate.shift(UP * 2))
```

---

## End of Kitchen Sink Reference

**Remember:** All patterns in this document are derived from official Manim Community Edition documentation. When in doubt, consult:
- https://docs.manim.community/en/stable/reference.html
- https://docs.manim.community/en/stable/guides/using_text.html
- https://docs.manim.community/en/stable/examples.html

This document is static and suitable for direct injection into agent system prompts for the build-scenes phase.
