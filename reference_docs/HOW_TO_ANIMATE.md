# HOW_TO_ANIMATE.md: Manim Animation Kitchen Sink

This comprehensive guide serves as a "kitchen sink" reference for coding agents tasked with creating Manim animations for 3Blue1Brown-style mathematical videos. It focuses on recent work from _2026/ (hairy ball theorem) and _2025/ (Laplace transforms), providing diverse examples of animations including geometry, timing, and placement.

## Introduction

### Manim Fundamentals
- **Import Pattern**: Always start with `from manim_imports_ext import *`
- **Scene Classes**:
  - `InteractiveScene`: For development with interactive features
  - `TeacherStudentsScene`: For scenes with Pi creature characters
  - `Scene`: Basic scenes
- **Rendering**: `manimgl <file.py> <SceneClass>` for interactive development
- **Key Concepts**:
  - **Geometry**: Shapes, positions, layouts (to_edge, arrange, move_to)
  - **Timing**: run_time, lag_ratio, rate_func
  - **Placement**: Frame management, camera controls

### Best Practices
- Use `self.play()` for animations
- `self.wait()` for pauses
- Group objects with `VGroup()` for collective operations
- Set colors consistently: BLUE, YELLOW, RED, GREEN
- Use `fix_in_frame()` for UI elements that shouldn't move with camera

## Text and Equations

### Basic Text Writing with Staggered Animation
From _2026/hairy_ball/supplements.py:

```python
class StatementOfTheorem(InteractiveScene):
    def construct(self):
        # Geometry: Title positioned at top-left corner
        title = Text("Hairy Ball Theorem", font_size=72)
        title.to_corner(UL)  # Placement: corner positioning
        underline = Underline(title)

        self.add(title, underline)

        # Multi-line text with left alignment
        statement = Text("""
            Any continuous vector field
            on a sphere must have at least
            one null vector.
        """, alignment="LEFT")
        statement.next_to(underline, DOWN, buff=MED_LARGE_BUFF)
        statement.to_edge(LEFT)  # Placement: edge alignment

        # Timing: 3-second write with 0.1 lag ratio for staggered effect
        self.play(Write(statement, run_time=3, lag_ratio=1e-1))
        self.wait()

        statement.set_backstroke(BLACK, 5)  # Visual enhancement

        # Highlight key terms with flash animation
        for text, color in [("continuous", BLUE), ("one null vector", YELLOW)]:
            self.play(
                FlashUnder(statement[text], time_width=1.5, run_time=2, color=color),
                statement[text].animate.set_fill(color)
            )
            self.wait()
```

**Key Elements**:
- **Geometry**: Text positioning with corners and edges
- **Timing**: run_time=3 for main write, run_time=2 for highlights
- **Placement**: next_to() for relative positioning

### Incremental Equation Building
From _2025/laplace/supplements.py:

```python
class IntroduceTrilogy(InteractiveScene):
    def construct(self):
        # Full screen background for UI elements
        self.add(FullScreenRectangle().fix_in_frame())

        # Title at top edge
        name = Text("Laplace Transform", font_size=60)
        name.to_edge(UP)

        # Equation with color mapping
        t2c = {"s": YELLOW, "{t}": BLUE}
        laplace = Tex(R"F(s) = \int_0^\infty f({t}) e^{\minus s{t}} d{t}", font_size=36, t2c=t2c)
        laplace.next_to(name, DOWN)

        # Frame squares for layout
        frames = Square().replicate(3)
        frames.set_stroke(WHITE, 1).set_fill(BLACK, 1)
        frames.set_width(0.3 * FRAME_WIDTH)
        frames.arrange(RIGHT, buff=MED_LARGE_BUFF)  # Placement: horizontal arrangement
        frames.set_y(-1.0)
        frames.fix_in_frame()
        name.fix_in_frame()

        # Camera matching for smooth transitions
        frame = self.frame
        frame.match_x(laplace["f({t})"])

        # Initial animations with lag
        self.play(
            Write(name),
            FadeIn(frames, lag_ratio=0.25, run_time=2)  # Timing: staggered fade-in
        )

        # Incremental equation building
        self.play(Write(laplace["f({t})"]))
        self.play(
            Write(laplace[R"e^{\minus s"]),
            TransformFromCopy(*laplace["{t}"][0:2]),  # Transform animation
            frame.animate.match_x(laplace[R"f({t}) e^{\minus s{t}}"])  # Dynamic camera
        )
        self.play(
            FadeIn(laplace[R"\int_0^\infty"], shift=0.25 * RIGHT, scale=1.5),
            FadeIn(laplace[R"d{t}"], shift=0.25 * LEFT, scale=1.5),
        )

        # Final transformation with path arcs
        self.play(
            FadeTransform(laplace["f("].copy(), laplace["F("], path_arc=-PI / 2),
            TransformFromCopy(laplace[")"][1], laplace[")"][0], path_arc=-PI / 2),
            TransformFromCopy(laplace["s"][1], laplace["s"][0], path_arc=-PI / 4),
            Write(laplace["="]),
            frame.animate.center(),  # Camera centering
        )
        self.wait()
```

**Key Elements**:
- **Geometry**: Equation components built incrementally
- **Timing**: Sequential plays with varying run_times
- **Placement**: Dynamic camera matching, fixed UI elements

## Geometric Objects and Transformations

### Sphere with Mesh and Clipping
From _2026/hairy_ball/spheres.py:

```python
class StereographicProjection(InteractiveScene):
    def construct(self):
        # 3D coordinate system setup
        frame = self.frame
        x_max = 20
        axes = ThreeDAxes((-x_max, x_max), (-x_max, x_max), (-2, 2))
        plane = NumberPlane((-x_max, x_max), (-x_max, x_max))
        plane.background_lines.set_stroke(BLUE, 1, 0.5)
        plane.faded_lines.set_stroke(BLUE, 0.5, 0.25)
        axes.apply_depth_test()
        plane.apply_depth_test()

        # Sphere geometry with transparency and mesh
        sphere = Sphere(radius=1)
        sphere.set_opacity(0.5)
        sphere.always_sort_to_camera(self.camera)
        mesh = SurfaceMesh(sphere)
        mesh.set_stroke(WHITE, 1, 0.25)

        self.add(sphere, mesh, axes, plane)

        # Initial camera position
        frame.reorient(-15, 64, 0, (0.0, 0.1, -0.09), 4.0)

        # Cross-section visualization
        frame.clear_updaters()
        sphere.set_clip_plane(UP, 1)  # Clipping geometry

        # Sample points on sphere equator
        n_dots = 20
        sample_points = np.array([
            math.cos(theta) * OUT + math.sin(theta) * RIGHT
            for theta in np.linspace(0, TAU, n_dots + 2)[1:-1]
        ])
        sphere_dots, plane_dots, proj_lines = self.get_dots_and_lines(sample_points)

        # Combined animation: clipping, camera move, dots, lines
        self.play(
            sphere.animate.set_clip_plane(UP, 0),  # Remove clipping
            frame.animate.reorient(-43, 74, 0, (0.0, 0.0, -0.0), 3.50),  # Camera transition
            FadeIn(sphere_dots, time_span=(1, 2)),
            ShowCreation(proj_lines, lag_ratio=0, time_span=(1, 2)),  # Projection lines
            run_time=2
        )

        # Continuous rotation
        frame.add_ambient_rotation(2 * DEG)
```

**Key Elements**:
- **Geometry**: 3D axes, sphere with mesh, clipping planes
- **Timing**: Combined multi-element animation with time_spans
- **Placement**: Camera reorientation with specific angles and focus points

### Vector Field on Sphere
From _2026/hairy_ball/spheres.py:

```python
class SingleNullPointHairyBall(InteractiveScene):
    hide_top = True

    def construct(self):
        # Sphere setup with lighting
        frame = self.frame
        radius = 3
        sphere = Sphere(radius=radius)
        sphere.set_color(GREY_E, 1)
        sphere.set_shading(0.1, 0.1, 0.3)
        sphere.always_sort_to_camera(self.camera)

        axes = ThreeDAxes((-2, 2), (-2, 2), (-2, 2))
        axes.scale(radius)

        self.camera.light_source.move_to(3 * LEFT + 12 * UP + 3 * OUT)

        frame.reorient(-3, 161, 0)
        self.add(sphere)

        # Vector field computation using stereographic projection
        def v_func(points3d):
            new_points = stereographic_vector_field(points3d, right_func)
            norms = np.linalg.norm(new_points, axis=1)
            new_points *= 0.2 / norms[:, np.newaxis]  # Normalization
            return new_points

        # Sample points with optional top hiding
        n_points = 50_000
        v_range = (-0.95, 1) if self.hide_top else (-1, 1)
        points = np.array([
            normalize(sphere.uv_func(TAU * random.random(), math.acos(pre_v)))
            for pre_v in np.random.uniform(*v_range, n_points)
        ])

        # Create vector field visualization
        field = get_sphereical_vector_field(
            v_func, axes, points,
            stroke_width=3,
            mvltss=3,  # max vector length to step size
        )
        field.set_stroke(BLUE_E, opacity=0.75)

        # Question mark overlay for hidden region
        q_marks = Tex(R"???", font_size=72)
        q_marks.rotate(-90 * DEG)
        q_marks.move_to(sphere.get_zenith())
        disk = Circle(radius=radius, v_range=(0.9 * PI, PI))
        disk.set_color(BLACK)
        disk.deactivate_depth_test()
        top_q = Group(disk, q_marks)
        top_q.set_z_index(1)

        if not self.hide_top:
            top_q.set_opacity(0)

        # Animation sequence
        self.add(field, sphere)
        self.play(
            field.animate.set_stroke(opacity=0.75),  # Fade in field
            frame.animate.reorient(-92, 11, 0).set_anim_args(run_time=7),  # Slow camera move
            FadeIn(top_q, time_span=(3.5, 5)),  # Delayed question mark
        )
        self.play(
            frame.animate.reorient(-168, 127, 0),  # Continue rotation
            FadeOut(top_q, time_span=(4.2, 5)),  # Fade out question
            run_time=10
        )
```

**Key Elements**:
- **Geometry**: Spherical vector field with stereographic mapping
- **Timing**: Long camera animations (7-10 seconds) with overlapping fades
- **Placement**: Zenith positioning, z-index management

## Character Scenes

### Teacher-Student Dialogue
From _2026/hairy_ball/supplements.py:

```python
class WhyDoWeCare(TeacherStudentsScene):
    def construct(self):
        stds = self.students
        morty = self.teacher

        # Initial reactions
        self.play(
            self.change_students("confused", "erm", "concentrating", look_at=self.screen),
        )
        self.wait(3)

        # Student question with speech bubble
        self.play(
            stds[2].change("erm", stds[1].eyes),
            stds[1].says("I'm sorry, why\ndo we care?", mode="sassy"),
            stds[0].change("thinking", self.screen),
            morty.change("well"),
        )
        self.wait(2)

        # Group reaction change
        self.play(self.change_students("pondering", "maybe", "pondering", look_at=self.screen))
```

**Key Elements**:
- **Geometry**: Character positioning managed by scene class
- **Timing**: Sequential dialogue with pauses
- **Placement**: look_at() for gaze direction, speech bubbles

### Challenging Assumptions
From _2026/hairy_ball/supplements.py:

```python
class PedanticStudent(TeacherStudentsScene):
    def construct(self):
        morty = self.teacher
        stds = self.students

        # Teacher gesture
        self.play(
            morty.change('raise_right_hand'),
            self.change_students("pondering", "pondering", "pondering", look_at=self.screen)
        )
        self.wait()

        # Angry student outburst with reactions
        self.play(LaggedStart(
            stds[2].says("But atmosphere\nis 3D!", mode="angry", look_at=morty.eyes, bubble_direction=LEFT),
            morty.change("guilty"),
            stds[0].change("hesitant", look_at=stds[2].eyes),
            stds[1].change("hesitant", look_at=stds[2].eyes),
        ))
        self.wait(2)

        # Refocus on screen
        self.look_at(self.screen)
        self.wait(3)
```

**Key Elements**:
- **Geometry**: Automatic character layout and expressions
- **Timing**: LaggedStart for overlapping reactions
- **Placement**: Dynamic look_at() and bubble_direction

## Vector Fields and Flow

### Animated Streamlines on Sphere
From _2026/hairy_ball/spheres.py:

```python
# Within StereographicProjection construct:

# Show a vector field
xy_field = VectorField(lambda ps: np.array([RIGHT for p in ps]), plane)
xy_field.set_stroke(BLUE)
xy_field.save_state()
xy_field.set_stroke(width=1e-6)  # Initially invisible

self.play(Restore(xy_field))  # Fade in
self.wait(5)

# Project to 3D sphere
proj_field = xy_field.copy()
proj_field.apply_points_function(lambda p: inv_streographic_proj(p[:, :2]), about_point=ORIGIN)
proj_field.replace(sphere)

# Update plane appearance
proj_plane.background_lines.set_stroke(BLUE, 1, 0.5)
proj_plane.faded_lines.set_stroke(BLUE, 0.5, 0.25)
proj_plane.axes.set_stroke(WHITE, 0)

# Transform plane and field
self.play(
    Transform(plane, proj_plane),
    Transform(xy_field, proj_field),
    run_time=5,
)

# Create animated streamlines
proto_stream_lines = VGroup(
    Line([x, y, 0], [x + 20, y, 0]).insert_n_curves(25)
    for x in range(-100, 100, 10)
    for y in np.arange(-100, 100, 0.25)
)
for line in proto_stream_lines:
    line.virtual_time = 1
proto_stream_lines.set_stroke(WHITE, 2, 0.8)

# Project to sphere surface
proto_stream_lines.apply_points_function(lambda p: inv_streographic_proj(p[:, :2]), about_point=ORIGIN)
proto_stream_lines.scale(1.01)
proto_stream_lines.make_smooth()

animated_lines = AnimatedStreamLines(proto_stream_lines, rate_multiple=0.2)

# Update sphere appearance
sphere.set_color(GREY_E, 1)
sphere.set_clip_plane(UP, 1)
sphere.set_height(1.98).center()

# Apply depth testing
xy_field.apply_depth_test()
animated_lines.apply_depth_test()

self.add(sphere, mesh, plane, animated_lines, xy_field)
```

**Key Elements**:
- **Geometry**: 2D→3D field projection, streamline curves
- **Timing**: Long animation (5+ seconds) for complex transformations
- **Placement**: Surface projection, depth sorting

### Simple 2D Flow
From _2026/hairy_ball/spheres.py:

```python
class SimpleRightwardFlow(InteractiveScene):
    def construct(self):
        # Set up 2D coordinate system
        frame = self.frame
        x_max = 20
        axes = ThreeDAxes((-x_max, x_max), (-x_max, x_max), (-2, 2))
        plane = NumberPlane((-x_max, x_max), (-x_max, x_max))
        plane.background_lines.set_stroke(BLUE, 1, 0.5)
        plane.faded_lines.set_stroke(BLUE, 0.5, 0.25)
        axes.apply_depth_test()
        plane.apply_depth_test()

        # Simple flow setup
        frame.set_height(4)

        xy_field = VectorField(lambda ps: np.array([RIGHT for p in ps]), plane)
        xy_field.set_stroke(BLUE)
        self.add(xy_field)

        # Create dense streamline grid
        proto_stream_lines = VGroup(
            Line([x, y, 0], [x + 1, y, 0]).insert_n_curves(20)
            for x in np.arange(-10, 10, 0.5)
            for y in np.arange(-10, 10, 0.1)
        )
        for line in proto_stream_lines:
            line.virtual_time = 1
        proto_stream_lines.set_stroke(WHITE, 2, 0.8)

        animated_plane_lines = AnimatedStreamLines(proto_stream_lines, rate_multiple=0.2)

        self.add(animated_plane_lines)
        self.wait(30)  # Long animation time for flow visualization
```

**Key Elements**:
- **Geometry**: Dense grid of streamlines
- **Timing**: Extended animation (30 seconds) for flow observation
- **Placement**: Regular grid spacing for coverage

## Homotopies and Deformations

### Surface Wiggle Deformation
From _2026/hairy_ball/spheres.py:

```python
# Within AskAboutOutside construct:

# Define homotopy function
def homotopy(x, y, z, t):
    alpha = clip((x + 3) / 6 - 1 + 2 * t, 0, 1)
    shift = wiggle(alpha, 3)  # Wiggle function for deformation
    return (x, y, z + 0.35 * shift)

# Prepare objects for homotopy
sphere_group = Group(sphere, mesh)

self.play(
    FadeOut(vects, time_span=(0, 1)),
    FadeOut(dot, time_span=(0, 1)),
    Homotopy(homotopy, sphere_group),  # Apply deformation
    frame.animate.reorient(-47, 81, 0, (-0.55, 0.17, 0.13), 0.65),
    run_time=6,
)
```

**Key Elements**:
- **Geometry**: Parametric deformation of surface
- **Timing**: 6-second homotopy with camera movement
- **Placement**: Combined with object fading

### Parametric Surface Deformations
From _2026/hairy_ball/spheres.py:

```python
# Within FlowingWater construct:

# Define alternative UV function with wiggle parameters
def alt_uv_func(u, v, params, wiggle_size=1.0, max_freq=4):
    x, y, z = sphere.uv_func(u, v)
    return (
        x + wiggle_size * params[0] * np.cos(max_freq * params[1] * y),
        y + wiggle_size * params[4] * np.cos(max_freq * params[5] * z),
        z + wiggle_size * params[2] * np.cos(max_freq * params[3] * x),
    )

sphere_group = Group(sphere, mesh)

# Apply random deformations
np.random.seed(3)
for n in range(20):
    params = np.random.random(6)
    new_sphere = ParametricSurface(
        lambda u, v: alt_uv_func(u, v, params),
        u_range=sphere.u_range,
        v_range=sphere.v_range,
        resolution=sphere.resolution
    )
    new_sphere.match_style(sphere)
    new_mesh = SurfaceMesh(new_sphere, resolution=mesh.resolution)
    new_mesh.match_style(mesh)
    new_group = Group(new_sphere, new_mesh)

    # Special positioning for certain iterations
    if 10 < n < 13:
        new_group.shift(1.75 * radius * RIGHT)

    self.play(Transform(sphere_group, new_group, run_time=2))
    self.wait(2)
```

**Key Elements**:
- **Geometry**: Parametric surface with frequency-based deformations
- **Timing**: Rapid succession of transformations (2 seconds each)
- **Placement**: Conditional positioning during animation sequence

## Camera and Frame Control

### Dynamic Camera Reorientation
From _2026/hairy_ball/spheres.py:

```python
# Within StereographicProjection construct:

# Initial position
frame.reorient(-15, 64, 0, (0.0, 0.1, -0.09), 4.0)

# Transition to cross-section view
frame.clear_updaters()
self.play(
    sphere.animate.set_clip_plane(UP, 0),
    frame.animate.reorient(-43, 74, 0, (0.0, 0.0, -0.0), 3.50),
    FadeIn(sphere_dots, time_span=(1, 2)),
    ShowCreation(proj_lines, lag_ratio=0, time_span=(1, 2)),
    run_time=2
)

# Add continuous rotation
frame.add_ambient_rotation(2 * DEG)
```

**Key Elements**:
- **Geometry**: Camera positioned relative to sphere
- **Timing**: Synchronized with object animations
- **Placement**: Specific angles (θ, φ) and focus points

### Complex Multi-Stage Camera Movement
From _2026/hairy_ball/spheres.py:

```python
# Within SingleNullPointHairyBall construct:

frame.reorient(-3, 161, 0)
self.add(sphere)

self.play(
    ReplacementTransform(pre_field, field, run_time=2),
    frame.animate.reorient(-92, 11, 0).set_anim_args(run_time=7),  # Slow 7-second move
    FadeIn(top_q, time_span=(3.5, 5)),
)

self.play(
    frame.animate.reorient(-168, 127, 0),  # Continue rotation
    FadeOut(top_q, time_span=(4.2, 5)),
    run_time=10  # Longer animation
)
```

**Key Elements**:
- **Geometry**: Extreme angle changes (161° to -168°)
- **Timing**: Extended animations with overlapping elements
- **Placement**: Smooth transitions between viewpoints

## Interactive Elements

### Real-Time Particle System
From _2026/hairy_ball/spheres.py:

```python
# Within FlowingWater construct:

# Particle system setup
n_samples = 50_000
x_max = axes.x_range[1]
sample_points = np.random.uniform(-x_max, x_max, (n_samples, 3))
sample_points[:, 2] = 0
particles = DotCloud(sample_points)
particles.set_radius(0.015)
particles.set_color(BLUE)
particles.make_3d()

# Opacity and radius trackers
particle_opacity_tracker = ValueTracker(1)
proj_particle_radius_tracker = ValueTracker(0.01)

# Projected particles on sphere
proj_particles = particles.copy()
proj_particles.set_opacity(1)

x_vel = 0.5  # Flow velocity

# Updater function for real-time animation
def update_particles(particles, dt):
    particles.shift(dt * x_vel * RIGHT)  # Move particles
    points = particles.get_points()
    points[points[:, 0] > x_max, 0] -= 2 * x_max  # Wrap around
    particles.set_points(points)
    particles.set_opacity(particle_opacity_tracker.get_value())

    # Project to sphere
    sphere_points = inv_streographic_proj(points[:, :2])
    zs = sphere_points[:, 2]
    proj_particles.set_points(sphere_points)
    proj_particles.set_radius((proj_particle_radius_tracker.get_value() * (1.5 - zs)).reshape(-1, 1))

particles.add_updater(update_particles)

self.add(particles, sphere)
self.wait(7)
```

**Key Elements**:
- **Geometry**: 2D particles projected to 3D sphere
- **Timing**: Real-time updates with dt parameter
- **Placement**: Dynamic radius based on z-coordinate

### Dynamic Normal Vectors
From _2026/hairy_ball/spheres.py:

```python
# Within UnitNormals construct:

# Surface setup
surface = Torus()
surface.set_color(GREY_D)

# UV sampling for normal vectors
uv_samples = np.array([
    [u, v]
    for v in np.linspace(0, TAU, 25)
    for u in np.linspace(0, TAU, 50)
])
points = np.array([surface.uv_to_point(u, v) for u, v in uv_samples])

# Create normal vector objects
normal_vectors = VGroup(
    VMobject().set_points_as_corners([ORIGIN, RIGHT, RIGHT, 2 * RIGHT])
    for sample in uv_samples
)
for vect in normal_vectors:
    vect.set_stroke(BLUE_D, width=[2, 2, 2, 12, 6, 0], opacity=0.5)
normal_vectors.set_stroke(WHITE)
normal_vectors.apply_depth_test()
normal_vectors.set_flat_stroke(False)

# Updater for normal vectors
def update_normal_vectors(normal_vectors):
    points = np.array([surface.uv_to_point(u, v) for u, v in uv_samples])
    du_points = np.array([surface.uv_to_point(u + 0.1, v) for u, v in uv_samples])
    dv_points = np.array([surface.uv_to_point(u, v + 0.1) for u, v in uv_samples])
    normals = normalize_along_axis(np.cross(du_points - points, dv_points - points), 1)
    for point, normal, vector in zip(points, normals, normal_vectors):
        vector.put_start_and_end_on(point, point + 0.5 * normal)

update_normal_vectors(normal_vectors)

self.play(ShowCreation(normal_vectors, run_time=3))
```

**Key Elements**:
- **Geometry**: Surface normals computed from UV derivatives
- **Timing**: One-time update then static display
- **Placement**: Vectors positioned at surface points

### Interactive Coordinate Display
From _2026/hairy_ball/spheres.py:

```python
# Within DefineOrientation construct:

# Movable point on sphere
uv_tracker = ValueTracker(np.array([180 * DEG, 90 * DEG]))

dot = TrueDot()
dot.set_color(YELLOW)
dot.add_updater(lambda m: m.move_to(sphere.uv_func(*uv_tracker.get_value())))
dot.set_z_index(2)

# Dynamic labels
lat_label, lon_label = lat_lon_labels = VGroup(
    Tex(R"\text{Lat: }\, 10^\circ"),
    Tex(R"\text{Lon: }\, 10^\circ"),
)
lat_lon_labels.arrange(DOWN, aligned_edge=LEFT)
lat_lon_labels.fix_in_frame()
lat_lon_labels.to_corner(UL)

# Make labels update with tracker
lat_label.make_number_changeable("10", edge_to_fix=RIGHT).add_updater(
    lambda m: m.set_value(np.round(self.get_lat_lon(*uv_tracker.get_value())[0]))
)
lon_label.make_number_changeable("10", edge_to_fix=RIGHT).add_updater(
    lambda m: m.set_value(np.round(self.get_lat_lon(*uv_tracker.get_value())[1]))
)

lat_lon_labels.add_updater(lambda m: m.fix_in_frame())

self.add(sphere, mesh)
self.add(lat_lon_labels)
frame.reorient(-66, 85, 0, (-0.06, 0.18, 0.06), 6.78)
self.play(FadeIn(dot))
```

**Key Elements**:
- **Geometry**: Point movement on spherical surface
- **Timing**: Continuous updates via updaters
- **Placement**: Fixed UI labels with dynamic values

## Common Patterns and Tips

### Animation Timing Guidelines
- **Short animations** (1-2s): Quick transitions, highlights
- **Medium animations** (3-5s): Main content reveals, transformations
- **Long animations** (6-10s+): Complex movements, flow visualizations

### Layout Best Practices
- Use `arrange()` for regular spacing
- `to_edge()` and `to_corner()` for screen positioning
- `fix_in_frame()` for UI elements
- `next_to()` for relative positioning

### Color Schemes
- BLUE: Mathematical objects, vectors
- YELLOW: Highlights, important points
- RED: Contradictions, special cases
- GREEN: Correct results, positive outcomes

### Debugging Tips
- Use `self.add()` to visualize intermediate states
- Check `frame.reorient()` parameters for camera issues
- Verify `apply_depth_test()` for 3D layering
- Test with simple geometries before complex scenes

This guide provides a comprehensive foundation for creating mathematical animations. Each example demonstrates key Manim concepts while showing the evolution of techniques in recent 3Blue1Brown videos.