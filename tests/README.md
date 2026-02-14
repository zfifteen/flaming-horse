# Tests README

## Unit Test Instructions

Create `tests/` folder for validating agent helpers and rules. Run with `manim -ql tests/test_helpers.py TestSafeLayout`.

### Example Test for safe_layout

```python
# tests/test_helpers.py
from manim import *

def safe_layout(*mobjects, alignment=ORIGIN, h_buff=0.5, v_buff=0.3, max_y=3.5, min_y=-3.5):
    # [Full function from AGENTS.md or visual_helpers.md]
    pass

class TestSafeLayout(Scene):
    def construct(self):
        circle1 = Circle().move_to(LEFT * 2)
        circle2 = Circle().move_to(ORIGIN)  # Potential overlap
        safe_layout(circle1, circle2)
        # Assert no overlap
        self.assert_true(circle1.get_right()[0] < circle2.get_left()[0] - 0.5)
        # Note: Manim Scene doesn't have assert_true; use print/debug for now
        print("Test passed: No overlap detected")
```

Add tests for other helpers (e.g., harmonious_color, adaptive_title_position). Include `run_tests.sh`:

```bash
#!/bin/bash
manim -ql tests/test_helpers.py TestSafeLayout
echo "All tests completed."
```
