#!/usr/bin/env python3
"""
End-to-end integration test for scaffold generation and body injection.

Simulates the full build_scenes workflow:
1. Generate scaffold with scaffold_scene.py
2. Parse agent response with parse_build_scenes_response
3. Inject body into scaffold with inject_body_into_scaffold
4. Verify final scene file is valid Python with all components
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from harness.parser import (
    inject_body_into_scaffold,
    parse_build_scenes_response,
)
from scripts.scaffold_scene import TEMPLATE


def test_e2e_scaffold_workflow():
    """Test complete scaffold generation and injection workflow."""
    print("\n" + "="*70)
    print("End-to-End Scaffold Workflow Test")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Generate scaffold (simulates scaffold_scene.py)
        print("\n1. Generating scaffold...")
        scaffold_path = Path(tmpdir) / "scene_01_intro.py"
        scaffold_content = TEMPLATE.format(
            class_name="Scene01Intro",
            narration_key="intro"
        )
        scaffold_path.write_text(scaffold_content)
        print(f"   ✓ Created scaffold: {scaffold_path}")
        
        # Verify scaffold has required components
        assert "# SLOT_START:scene_body" in scaffold_content
        assert "# SLOT_END:scene_body" in scaffold_content
        assert "config.frame_width = 10 * 16 / 9" in scaffold_content
        assert "from flaming_horse.scene_helpers import" in scaffold_content
        assert "def play_next(" not in scaffold_content  # Should NOT be redefined
        print("   ✓ Scaffold structure validated")
        
        # Step 2: Parse agent response (simulates build_scenes phase)
        print("\n2. Parsing agent response...")
        agent_response = '''
Here's the scene implementation:

```python
num_beats = max(12, min(30, int(np.ceil(tracker.duration / 1.8))))
beats = BeatPlan(tracker.duration, [1] * num_beats)

# Title
title = Text("Welcome to the Matrix", font_size=48, weight=BOLD, color=GREEN)
title.move_to(UP * 3.8)
play_text_next(self, beats, Write(title), max_text_seconds=999)

# Subtitle
subtitle = Text("Reality is a choice", font_size=32, color=BLUE)
subtitle.next_to(title, DOWN, buff=0.4)
safe_position(subtitle)
play_text_next(self, beats, FadeIn(subtitle), max_text_seconds=999)

# Visual element
diagram = Circle(radius=2.0, color=RED).move_to(DOWN * 0.6)
play_next(self, beats, Create(diagram, rate_func=smooth))
```
'''
        body_code = parse_build_scenes_response(agent_response)
        assert body_code is not None
        print(f"   ✓ Parsed body code ({len(body_code)} bytes)")
        
        # Verify body doesn't have forbidden elements
        assert "from manim import" not in body_code
        assert "config.frame" not in body_code
        assert "SLOT_START" not in body_code
        print("   ✓ Body validation passed")
        
        # Step 3: Inject body into scaffold (simulates parse_and_write_artifacts)
        print("\n3. Injecting body into scaffold...")
        full_code = inject_body_into_scaffold(scaffold_path, body_code)
        print(f"   ✓ Generated full scene ({len(full_code)} bytes)")
        
        # Step 4: Verify final scene file
        print("\n4. Validating final scene file...")
        
        # Check all required components are present
        checks = [
            ("Locked config header", "config.frame_width = 10 * 16 / 9"),
            ("SLOT_START marker", "# SLOT_START:scene_body"),
            ("SLOT_END marker", "# SLOT_END:scene_body"),
            ("Class definition", "class Scene01Intro(VoiceoverScene):"),
            ("VoiceoverScene import", "from manim_voiceover_plus import VoiceoverScene"),
            ("Helper imports", "from flaming_horse.scene_helpers import"),
            ("BeatPlan usage", "BeatPlan"),
            ("play_text_next usage", "play_text_next"),
            ("safe_position usage", "safe_position"),
            ("Scene body content", "Welcome to the Matrix"),
        ]
        
        for check_name, check_str in checks:
            assert check_str in full_code, f"Missing: {check_name}"
            print(f"   ✓ {check_name}")
        
        # Verify no duplicate function definitions
        assert full_code.count("def play_next(") == 0, "play_next should not be redefined"
        assert full_code.count("def play_text_next(") == 0, "play_text_next should not be redefined"
        print("   ✓ No duplicate function definitions")
        
        # Step 5: Verify Python syntax
        print("\n5. Checking Python syntax...")
        try:
            compile(full_code, "<string>", "exec")
            print("   ✓ Syntax is valid")
        except SyntaxError as e:
            print(f"   ✗ Syntax error: {e}")
            raise
        
        # Save for inspection
        output_path = Path(tmpdir) / "final_scene.py"
        output_path.write_text(full_code)
        print(f"\n   ✓ Final scene saved to: {output_path}")
        
        # Step 6: Verify body is between markers
        print("\n6. Verifying body placement...")
        start_idx = full_code.find("# SLOT_START:scene_body")
        end_idx = full_code.find("# SLOT_END:scene_body")
        body_section = full_code[start_idx:end_idx]
        
        assert "Welcome to the Matrix" in body_section
        assert "BeatPlan" in body_section
        assert "play_text_next" in body_section
        print("   ✓ Body is correctly placed between SLOT markers")
        
        print("\n" + "="*70)
        print("✅ All checks passed! End-to-end workflow is working correctly.")
        print("="*70 + "\n")
        
        return True


def test_e2e_reject_bad_agent_output():
    """Test that workflow correctly rejects bad agent responses."""
    print("\n" + "="*70)
    print("Bad Agent Output Rejection Test")
    print("="*70)
    
    bad_responses = [
        # Response with scaffold placeholders
        ('Scaffold placeholders', '''
```python
title = Text("{{TITLE}}", font_size=48)
subtitle = Text("{{SUBTITLE}}")
```
'''),
        # Response with full scene (not just body)
        ('Full scene instead of body', '''
```python
from manim import *

class Scene01(VoiceoverScene):
    def construct(self):
        pass
```
'''),
        # Response with config header
        ('Config header', '''
```python
config.frame_width = 10 * 16 / 9
title = Text("Test")
```
'''),
        # Response with slot markers
        ('Slot markers', '''
```python
# SLOT_START:scene_body
title = Text("Test")
# SLOT_END:scene_body
```
'''),
    ]
    
    print()
    for test_name, bad_response in bad_responses:
        body = parse_build_scenes_response(bad_response)
        assert body is None, f"Should reject: {test_name}"
        print(f"   ✓ Correctly rejected: {test_name}")
    
    print("\n" + "="*70)
    print("✅ All bad responses correctly rejected.")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        test_e2e_scaffold_workflow()
        test_e2e_reject_bad_agent_output()
        print("\n🎉 All end-to-end tests passed!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
