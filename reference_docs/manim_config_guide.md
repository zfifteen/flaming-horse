# Manim Space Configuration Guide

## Optimal Settings (Locked In Template)

### Frame Dimensions
- `frame_height = 10` (25% larger than default)
- `frame_width = 17.78` (10 * 16/9 for proper aspect ratio)

### Resolution
- `pixel_height = 1440` (1440p for crisp text)
- `pixel_width = 2560`

## Why These Settings?

### Frame Size
The default Manim frame (8x14.22) was too small, causing content to appear zoomed in. Increasing to 10x17.78 provides 25% more space while keeping elements at readable sizes.

### Resolution
Higher pixel density (1440p vs default 1080p) ensures text remains sharp and professional-looking, especially for technical content with mathematical notation and detailed diagrams.

## Usage Instructions

1. **For New Scenes**: Copy `manim_template.py.txt` as your starting point
2. **Don't modify** the config values at the top
3. **Use the `safe_position()` helper function** to validate element positions
4. **Follow the sizing guidelines** in the template comments
5. **Render normally**: `manim <file>.py <SceneName>` (no flags needed)

## Sizing Quick Reference

### Font Sizes
| Element Type | Recommended Size |
|--------------|------------------|
| Main titles  | 40-48           |
| Sections     | 32-36           |
| Body text    | 18-24           |
| Labels       | 14-18           |
| Small text   | 12-14           |

### Object Sizes
| Category | Width | Height |
|----------|-------|--------|
| Large    | 4-8   | 3-6    |
| Medium   | 3-5   | 2-4    |
| Small    | 2-3   | 1-2    |

### Coordinate Space
- Horizontal range: -8.89 to +8.89 (keep content within +/-7 for safety)
- Vertical range: -5 to +5 (keep content within +/-4 for safety)

## LaTeX Rendering

### Tex vs MathTex

| Use Case | Class | Example |
|----------|-------|---------|
| Mathematical equations | `MathTex` | `MathTex(r"E = mc^2")` |
| Plain text with LaTeX formatting | `Tex` | `Tex(r"\textbf{Bold Text}")` |

**Rule**: If your string contains math operators (`=`, `+`, `\frac`, `\int`, etc.), use `MathTex`.

### Position Arrays Must Be 3D

Manim requires all position coordinates as 3D numpy arrays:

```python
# ✅ CORRECT
point = np.array([x, y, 0])
circle.move_to(np.array([1, 2, 0]))

# ❌ WRONG (will cause dimension errors)
point = np.array([x, y])
circle.move_to(np.array([1, 2]))
```

**Always include the z-coordinate (typically 0 for 2D scenes).**

## Critical Positioning Rules

### DO NOT Use `.to_edge(UP)` for Titles/Headers

**Why it causes clipping:**
- With `frame_height=10`, the vertical coordinate range is -5 to +5
- `.to_edge(UP, buff=0.4)` mathematically places the mobject's center at y~4.5
- Font ascenders (tall letters like "T", "h", "l") extend beyond the bounding box
- Result: Top of text gets clipped in rendered video, even though it looks fine in preview

**CORRECT approach:**
```python
title = Text("My Title", font_size=48)
title.move_to(UP * 3.8)  # Absolute positioning in safe zone
```

**WRONG approach:**
```python
title = Text("My Title", font_size=48)
title.to_edge(UP, buff=0.4)  # Will clip at top!
```

### Safe Top Positions
- Main scene titles: `UP * 3.5` to `UP * 4.0`
- Section headers: `UP * 3.0` to `UP * 3.5`
- Mid-screen content: `UP * 1.0` to `DOWN * 1.0`
- Bottom annotations: `DOWN * 3.0` to `DOWN * 4.0`

### WARNING: `.next_to()` Chain Cascading

**The Problem:**
`.next_to()` uses relative positioning and does NOT respect safe zone boundaries. When chaining multiple `.next_to()` calls, elements can cascade out of frame.

**Example of what goes wrong:**
```python
# This can push content out of bounds!
title.move_to(UP * 4.0)          # At top edge
subtitle.next_to(title, DOWN)    # Still safe
section.next_to(subtitle, DOWN)  # Might be safe
body.next_to(section, DOWN)      # Could be outside safe zone!
```

**SOLUTION: Always validate after `.next_to()`:**
```python
body = Text("Body text", font_size=24)
body.next_to(section, DOWN, buff=0.5)
safe_position(body)  # Clamps to safe zone if needed
```

### The `safe_position()` Helper Function

The template includes this utility function:

```python
def safe_position(mobject, max_y=4.0, min_y=-4.0):
    """
    Clamp mobject to safe vertical zone to prevent clipping.

    Returns the adjusted mobject for chaining.
    """
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]

    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))

    return mobject
```

**When to use it:**
- After any `.next_to()` positioning call
- After scaling operations that might change bounds
- When building complex VGroups with dynamic content
- Any time you're unsure if content fits in frame

**Usage example:**
```python
# Method 1: In-place adjustment
element = Text("Content", font_size=36)
element.next_to(previous, DOWN)
safe_position(element)

# Method 2: Chained (returns the mobject)
element = safe_position(
    Text("Content", font_size=36).next_to(previous, DOWN)
)
```

## Debugging Position Issues

### Check Coordinates Manually
```python
# Print position info during construct()
mobject_top = my_text.get_top()[1]
mobject_bottom = my_text.get_bottom()[1]
print(f"Top: {mobject_top:.2f}, Bottom: {mobject_bottom:.2f}")

# If top > 4.5 or bottom < -4.5, content will clip!
```

### Visual Debugging Helper
```python
def show_safe_zone(scene):
    """Add visible boundary markers to see safe zone"""
    top_line = Line(LEFT * 8, RIGHT * 8).move_to(UP * 4)
    top_line.set_color(RED)
    bottom_line = Line(LEFT * 8, RIGHT * 8).move_to(DOWN * 4)
    bottom_line.set_color(RED)
    scene.add(top_line, bottom_line)
```

## Troubleshooting

**If content looks too zoomed in:**
- Check that you're using the template config values
- Verify no `.scale()` operations are shrinking VGroups unnecessarily
- Ensure you're not applying camera transforms (not supported in 0.19.x)

**If text looks fuzzy:**
- Ensure `pixel_height = 1440` and `pixel_width = 2560` are set
- Don't use `-pql` flag (it overrides to 480p)
- Render with just: `manim file.py SceneName`

**If elements are cut off at top:**
- Remove any `.to_edge(UP)` calls for titles
- Use `.move_to(UP * 3.8)` instead
- Validate with `safe_position()` after `.next_to()` chains
- Check actual coordinates with `.get_top()[1]` (should be < 4.5)

**If elements are cut off at bottom:**
- Check if you have too many vertically stacked elements
- Use `safe_position()` on the entire VGroup
- Consider splitting content across multiple scenes

**If relative positioning feels unpredictable:**
- Switch to absolute positioning with `.move_to()` for key elements
- Use `.next_to()` only for tightly coupled elements
- Always validate positions after relative placement

## Best Practices Summary

1. **Always use absolute positioning for titles**: `title.move_to(UP * 3.8)`
2. **Validate after relative positioning**: `safe_position(element)` after `.next_to()`
3. **Stay within safe bounds**: horizontal +/-7, vertical +/-4
4. **Use the template's config block**: Don't modify `frame_height`, `frame_width`, resolution
5. **Test with `get_top()[1]` and `get_bottom()[1]`**: Verify < 4.5 and > -4.5
6. **Never use `.to_edge(UP)` for titles/headers**
7. **Never chain `.next_to()` without validation**
8. **Never exceed +/-4.0 for critical content**

## Layout Checklist (Mandatory)

- Title must exist and be visible at `UP * 3.8` (or via `adaptive_title_position`).
- Subtitle must be `.next_to(title, DOWN, buff=0.4)` and then `safe_position(subtitle)`.
- Graphs/diagrams must be offset downward (e.g., `DOWN * 0.6` to `DOWN * 1.2`) to avoid title overlap.
- Labels must attach to nearby elements (e.g., `label.next_to(curve.get_end(), UP, buff=0.2)`), then `safe_position(label)`.
- After positioning, run `safe_layout(...)` for any group of 2+ elements.
- ❌ NEVER use `.to_edge(...)` for titles or labels (causes clipping/edge drift).

## Quick Decision Tree

```
Need to position an element?
|
+-- Is it a title/header at top?
|   -> Use: element.move_to(UP * 3.8)
|
+-- Is it relative to another element?
|   -> Use: element.next_to(other, direction, buff=...)
|   -> Then: safe_position(element)
|
+-- Is it at bottom of screen?
|   -> Use: element.to_edge(DOWN, buff=0.5)  [safer than top]
|
+-- Is it a complex group?
    -> Position with: group.move_to(ORIGIN) or explicit coords
    -> Scale if needed: group.scale(factor)
    -> Validate: safe_position(group)
```
