#!/usr/bin/env python3
"""
Validate scene layout for overlaps using Manim.
Usage: python scripts/validate_layout.py <scene_file.py> <SceneClass>
"""

import sys
import re
from manim import *

if len(sys.argv) < 3:
    print("Usage: python validate_layout.py <scene_file> <SceneClass>")
    sys.exit(1)

scene_file = sys.argv[1]
scene_class = sys.argv[2]

# Dynamically load and run scene to position mobjects
config.pixel_height = 1080  # Low res for validation
config.pixel_width = 1920


class ValidatorScene(Scene):
    def construct(self):
        # Hack: Import and instantiate the target scene class
        module = __import__(scene_file.replace(".py", ""), fromlist=[scene_class])
        target_class = getattr(module, scene_class)
        target_scene = target_class()
        target_scene.construct()  # Run positioning (non-rendering)

        # Collect all mobjects on screen
        mobjects = self.mobjects  # Or extract from target_scene

        # Check for overlaps
        overlaps = []
        for i, mob1 in enumerate(mobjects):
            for j, mob2 in enumerate(mobjects[i + 1 :], i + 1):
                if mob1.get_bounding_box().intersects_box(mob2.get_bounding_box()):
                    overlaps.append((i, j))

        if overlaps:
            raise ValueError(f"Overlaps detected in {len(overlaps)} pairs: {overlaps}")
        else:
            print("Validation passed: No overlaps.")


# Run still render for validation
os.system(f"manim -s {scene_file} ValidatorScene")  # But adapt for actual class
print("Layout validation complete.")
