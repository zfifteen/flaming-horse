#!/usr/bin/env python3
"""
Mock-based end-to-end test for harness.

This test simulates xAI API responses to validate the complete pipeline
without requiring an actual API key.
"""

import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from harness.prompts import compose_prompt
from harness.parser import (
    parse_plan_response,
    parse_narration_response,
    parse_build_scenes_response,
    parse_and_write_artifacts,
)


def create_mock_plan_response():
    """Create a mock response for the plan phase."""
    return """
Here is the video plan:

```json
{
  "title": "Understanding the Pythagorean Theorem",
  "description": "A visual explanation of the Pythagorean theorem and its applications",
  "target_duration_seconds": 180,
  "scenes": [
    {
      "id": "scene_01",
      "title": "Introduction",
      "description": "Introduce the Pythagorean theorem",
      "estimated_duration_seconds": 30,
      "narrative_beats": ["Welcome", "State the theorem"],
      "visual_ideas": ["Title card", "Simple right triangle"]
    },
    {
      "id": "scene_02",
      "title": "The Formula",
      "description": "Explain a² + b² = c²",
      "estimated_duration_seconds": 40,
      "narrative_beats": ["Show formula", "Explain each component"],
      "visual_ideas": ["MathTex formula", "Labeled triangle"]
    },
    {
      "id": "scene_03",
      "title": "Visual Proof",
      "description": "Show visual proof with squares",
      "estimated_duration_seconds": 60,
      "narrative_beats": ["Draw squares on sides", "Show area relationship"],
      "visual_ideas": ["Animated squares", "Area calculations"]
    },
    {
      "id": "scene_04",
      "title": "Conclusion",
      "description": "Recap and applications",
      "estimated_duration_seconds": 50,
      "narrative_beats": ["Recap key points", "Real-world uses"],
      "visual_ideas": ["Summary text", "Application examples"]
    }
  ]
}
```
"""


def create_mock_narration_response():
    """Create a mock response for the narration phase."""
    return '''
```python
# Voiceover script for Understanding the Pythagorean Theorem

SCRIPT = {
    "scene_01": """
    Welcome! Today we're going to explore one of the most famous theorems
    in mathematics: the Pythagorean theorem. This ancient discovery has been
    fundamental to mathematics for over two thousand years.
    """,
    
    "scene_02": """
    The Pythagorean theorem states that in a right triangle, the square of
    the length of the hypotenuse equals the sum of the squares of the other
    two sides. We write this as: a squared plus b squared equals c squared.
    """,
    
    "scene_03": """
    Let's see why this works with a visual proof. If we draw squares on each
    side of our right triangle, the areas of the two smaller squares will
    exactly equal the area of the largest square. It's a beautiful geometric
    relationship that we can see with our own eyes.
    """,
    
    "scene_04": """
    The Pythagorean theorem isn't just theoretical. It's used in construction,
    navigation, computer graphics, and countless other fields. Whenever you need
    to find distances or work with right angles, this theorem is there to help.
    Thanks for watching!
    """
}
```
'''


def create_mock_scene_response():
    """Create a mock response for the build_scenes phase."""
    return """
```python
from manim import *
import numpy as np
from pathlib import Path
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

# LOCKED CONFIGURATION
config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

def safe_position(mobject, max_y=3.8, min_y=-3.8, buff=0.2):
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y - buff:
        mobject.shift(DOWN * (top - (max_y - buff)))
    if bottom < min_y + buff:
        mobject.shift(UP * (bottom - (min_y + buff)))
    return mobject

class Scene01Introduction(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
        with self.voiceover(text=SCRIPT["scene_01"]) as tracker:
            title = Text("The Pythagorean Theorem", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            
            subtitle = Text("a² + b² = c²", font_size=36)
            subtitle.next_to(title, DOWN, buff=0.4)
            safe_position(subtitle)
            
            self.play(Write(title), run_time=tracker.duration * 0.3)
            self.play(FadeIn(subtitle), run_time=tracker.duration * 0.3)
            
            triangle = Polygon(
                [-2, -1, 0], [2, -1, 0], [2, 2, 0],
                color=BLUE, fill_opacity=0.3
            )
            triangle.move_to(ORIGIN)
            
            self.play(Create(triangle), run_time=tracker.duration * 0.3)
            self.wait(tracker.duration * 0.1)
```
"""


def test_plan_phase():
    """Test plan phase with mock response."""
    print("Testing plan phase...")

    response = create_mock_plan_response()
    plan = parse_plan_response(response)

    assert plan is not None, "Failed to parse plan"
    assert "title" in plan, "Plan missing title"
    assert "scenes" in plan, "Plan missing scenes"
    assert len(plan["scenes"]) == 4, f"Expected 4 scenes, got {len(plan['scenes'])}"

    print("✅ Plan phase parsing works")
    return plan


def test_narration_phase():
    """Test narration phase with mock response."""
    print("Testing narration phase...")

    response = create_mock_narration_response()
    code = parse_narration_response(response)

    assert code is not None, "Failed to parse narration"
    assert "SCRIPT = {" in code, "Narration missing SCRIPT dict"
    assert "scene_01" in code, "Narration missing scene_01"

    # Verify it's valid Python
    try:
        compile(code, "<string>", "exec")
    except SyntaxError as e:
        raise AssertionError(f"Narration code has syntax error: {e}")

    print("✅ Narration phase parsing works")
    return code


def test_build_scenes_phase():
    """Test build_scenes phase with mock response."""
    print("Testing build_scenes phase...")

    response = create_mock_scene_response()
    code = parse_build_scenes_response(response)

    assert code is not None, "Failed to parse scene"
    assert "from manim import" in code, "Scene missing manim import"
    assert "VoiceoverScene" in code, "Scene missing VoiceoverScene"
    assert "from narration_script import SCRIPT" in code, "Scene missing SCRIPT import"

    # Verify it's valid Python
    try:
        compile(code, "<string>", "exec")
    except SyntaxError as e:
        raise AssertionError(f"Scene code has syntax error: {e}")

    print("✅ Build scenes phase parsing works")
    return code


def test_build_scenes_prompt_uses_current_scene_narration_only():
    """Build scene prompt should include only current scene narration text."""
    print("Testing build_scenes prompt narration scoping...")

    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        plan = {
            "title": "Scoped narration test",
            "scenes": [
                {
                    "id": "scene_01_intro",
                    "title": "Intro",
                    "narration_key": "scene_01_intro",
                    "narrative_beats": ["Beat A"],
                    "visual_ideas": ["Idea A"],
                },
                {
                    "id": "scene_02_focus",
                    "title": "Focus",
                    "narration_key": "scene_02_focus",
                    "narrative_beats": ["Beat B"],
                    "visual_ideas": ["Idea B"],
                },
            ],
        }
        (project_dir / "plan.json").write_text(
            json.dumps(plan, indent=2), encoding="utf-8"
        )

        narration_text = """SCRIPT = {
    "scene_01_intro": "NARRATION_ONE_UNIQUE",
    "scene_02_focus": "NARRATION_TWO_UNIQUE"
}
"""
        (project_dir / "narration_script.py").write_text(
            narration_text, encoding="utf-8"
        )

        state = {
            "plan_file": "plan.json",
            "narration_file": "narration_script.py",
            "scenes": [
                {
                    "id": "scene_01_intro",
                    "title": "Intro",
                    "narration_key": "scene_01_intro",
                },
                {
                    "id": "scene_02_focus",
                    "title": "Focus",
                    "narration_key": "scene_02_focus",
                },
            ],
            "current_scene_index": 1,
        }

        _, user_prompt = compose_prompt(
            phase="build_scenes",
            state=state,
            project_dir=project_dir,
        )

        assert "NARRATION_TWO_UNIQUE" in user_prompt
        assert "NARRATION_ONE_UNIQUE" not in user_prompt
        assert "Forbidden placeholder strings" in user_prompt

    print("✅ Build scenes prompt uses current scene narration only")


def test_full_pipeline():
    """Test full pipeline with mock responses."""
    print("\n" + "=" * 50)
    print("Mock-based End-to-End Test")
    print("=" * 50 + "\n")

    # Create temporary project directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Initialize project state
        state = {
            "project_name": "mock_test",
            "topic": "Pythagorean Theorem",
            "phase": "plan",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "run_count": 0,
            "plan_file": "plan.json",
            "narration_file": "narration_script.py",
            "scenes": [],
            "current_scene_index": 0,
            "errors": [],
            "history": [],
            "flags": {"needs_human_review": False, "dry_run": False},
        }

        state_file = project_dir / "project_state.json"
        state_file.write_text(json.dumps(state, indent=2))

        # Test plan phase
        plan = test_plan_phase()
        plan_file = project_dir / "plan.json"
        plan_file.write_text(json.dumps(plan, indent=2))

        # Update state for narration
        state["phase"] = "narration"
        state["scenes"] = [
            {
                "id": scene["id"],
                "title": scene["title"],
                "file": f"{scene['id']}.py",
                "class_name": "",
                "status": "pending",
            }
            for scene in plan["scenes"]
        ]
        state_file.write_text(json.dumps(state, indent=2))

        # Test narration phase
        narration = test_narration_phase()
        narration_file = project_dir / "narration_script.py"
        narration_file.write_text(narration)

        # Update state for build_scenes
        state["phase"] = "build_scenes"
        state["current_scene_index"] = 0
        state_file.write_text(json.dumps(state, indent=2))

        # Test build_scenes phase
        scene_code = test_build_scenes_phase()
        scene_file = project_dir / "scene_01.py"
        scene_file.write_text(scene_code)

        # Test prompt narration scoping
        test_build_scenes_prompt_uses_current_scene_narration_only()

        # Verify all files exist
        assert plan_file.exists(), "plan.json not created"
        assert narration_file.exists(), "narration_script.py not created"
        assert scene_file.exists(), "scene_01.py not created"

        print("\n" + "=" * 50)
        print("✅ All mock tests passed!")
        print("=" * 50)
        print("\nArtifacts created:")
        print(f"  - plan.json ({plan_file.stat().st_size} bytes)")
        print(f"  - narration_script.py ({narration_file.stat().st_size} bytes)")
        print(f"  - scene_01.py ({scene_file.stat().st_size} bytes)")
        print("\nThe pipeline correctly parses and writes all artifacts.")
        print("\nTo test with real xAI API:")
        print("  1. Set XAI_API_KEY in .env")
        print("  2. Run: ./tests/test_harness_e2e.sh")


if __name__ == "__main__":
    try:
        test_full_pipeline()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
