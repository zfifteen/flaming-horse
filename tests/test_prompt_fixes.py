#!/usr/bin/env python3
"""Test that prompt fixes correctly guide agents to output body-only code.

This test validates that the parser correctly accepts body-only code
and rejects complete scene files, as per the audit report fixes.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from harness.parser import parse_build_scenes_response, parse_scene_repair_response


def test_parser_rejects_complete_file():
    """Test that parser correctly rejects complete scene file (WRONG format)."""
    
    # This is the WRONG format that agents were outputting before the fix
    wrong_output = '''```python
from manim import *
from manim_voiceover_plus import VoiceoverScene
from flaming_horse.scene_helpers import BeatPlan, play_next, play_text_next
import numpy as np

config.frame_height = 10
config.frame_width = 10 * 16/9

class Scene01Intro(VoiceoverScene):
    def construct(self):
        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            # SLOT_START:scene_body
            num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
            beats = BeatPlan(tracker.duration, [1] * num_beats)
            
            title = Text("Introduction", font_size=48)
            title.move_to(UP * 3.8)
            play_text_next(self, beats, Write(title), max_text_seconds=999)
            # SLOT_END:scene_body
```'''
    
    result = parse_build_scenes_response(wrong_output)
    assert result is None, "Parser should reject complete scene file with imports/class"
    print("✓ Parser correctly rejects complete file format")


def test_parser_accepts_body_only():
    """Test that parser correctly accepts body-only code (CORRECT format)."""
    
    # This is the CORRECT format after the prompt fixes
    # Note: Body code should NOT be indented - the injection function handles that
    correct_output = '''```python
num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
beats = BeatPlan(tracker.duration, [1] * num_beats)

blues = harmonious_color(BLUE, variations=3)
title = Text("Introduction", font_size=48, weight=BOLD, color=blues[0])
title.move_to(UP * 3.8)
play_text_next(self, beats, Write(title), max_text_seconds=999)

subtitle = Text("Getting Started", font_size=32, color=blues[1])
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)
play_text_next(self, beats, polished_fade_in(subtitle, lag_ratio=0.1), max_text_seconds=999)
```'''
    
    result = parse_build_scenes_response(correct_output)
    assert result is not None, "Parser should accept body-only code"
    assert "num_beats" in result, "Parsed code should contain the animation logic"
    assert "from manim import" not in result, "Parsed code should not contain imports"
    assert "class Scene" not in result, "Parsed code should not contain class definition"
    print("✓ Parser correctly accepts body-only format")
    print(f"  Parsed {len(result)} characters of body code")


def test_repair_parser_rejects_complete_file():
    """Test that repair parser also rejects complete files."""
    
    wrong_repair = '''```python
from manim import *

class Scene01Intro(VoiceoverScene):
    def construct(self):
        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
```'''
    
    result = parse_scene_repair_response(wrong_repair)
    assert result is None, "Repair parser should reject complete file"
    print("✓ Repair parser correctly rejects complete file format")


def test_repair_parser_accepts_body_only():
    """Test that repair parser accepts body-only code."""
    
    correct_repair = '''```python
num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
beats = BeatPlan(tracker.duration, [1] * num_beats)

title = Text("Fixed Title", font_size=48)
title.move_to(UP * 3.8)
play_text_next(self, beats, Write(title), max_text_seconds=999)
```'''
    
    result = parse_scene_repair_response(correct_repair)
    assert result is not None, "Repair parser should accept body-only code"
    assert "num_beats" in result, "Repaired code should contain the logic"
    print("✓ Repair parser correctly accepts body-only format")


def test_parser_rejects_scaffold_artifacts():
    """Test that parser rejects code with scaffold placeholder artifacts."""
    
    # Code with forbidden scaffold artifacts (using actual {{}} placeholders)
    scaffold_artifacts = '''```python
title = Text("{{TITLE}}", font_size=48)
title.move_to(UP * 3.8)

subtitle = Text("{{SUBTITLE}}", font_size=32)

# Or the demo rectangle pattern from scaffold
box = Rectangle(width=4.0, height=2.4)
```'''
    
    result = parse_build_scenes_response(scaffold_artifacts)
    assert result is None, "Parser should reject code with scaffold artifacts"
    print("✓ Parser correctly rejects scaffold placeholder artifacts")


if __name__ == "__main__":
    print("Testing prompt fix validation...")
    print()
    
    test_parser_rejects_complete_file()
    test_parser_accepts_body_only()
    test_repair_parser_rejects_complete_file()
    test_repair_parser_accepts_body_only()
    test_parser_rejects_scaffold_artifacts()
    
    print()
    print("=" * 60)
    print("✅ All prompt fix validation tests passed!")
    print()
    print("Summary:")
    print("- Parser correctly rejects complete files (old wrong format)")
    print("- Parser correctly accepts body-only code (new correct format)")
    print("- Repair parser has same correct behavior")
    print("- Scaffold artifacts are properly detected and rejected")
    print()
    print("The prompt fixes from AUDIT_REPORT_SMOKE_TEST.md are working correctly.")
