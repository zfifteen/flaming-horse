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
from datetime import datetime, UTC

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
      "id": "scene_01_intro",
      "title": "Introduction",
      "narration_key": "scene_01_intro",
      "description": "Introduce the Pythagorean theorem",
      "estimated_duration_seconds": 30,
      "narrative_beats": ["Welcome", "State the theorem"],
      "visual_ideas": ["Title card", "Simple right triangle"]
    },
    {
      "id": "scene_02_formula",
      "title": "The Formula",
      "narration_key": "scene_02_formula",
      "description": "Explain a² + b² = c²",
      "estimated_duration_seconds": 40,
      "narrative_beats": ["Show formula", "Explain each component"],
      "visual_ideas": ["MathTex formula", "Labeled triangle"]
    },
    {
      "id": "scene_03_visual_proof",
      "title": "Visual Proof",
      "narration_key": "scene_03_visual_proof",
      "description": "Show visual proof with squares",
      "estimated_duration_seconds": 60,
      "narrative_beats": ["Draw squares on sides", "Show area relationship"],
      "visual_ideas": ["Animated squares", "Area calculations"]
    },
    {
      "id": "scene_04_conclusion",
      "title": "Conclusion",
      "narration_key": "scene_04_conclusion",
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
    return """
```json
{
  "script": {
    "scene_01_intro": "Welcome! Today we're going to explore one of the most famous theorems in mathematics: the Pythagorean theorem.",
    "scene_02_formula": "The Pythagorean theorem states that in a right triangle, the square of the hypotenuse equals the sum of the squares of the other two sides.",
    "scene_03_visual_proof": "A visual proof shows that the areas of the two smaller squares exactly equal the area of the largest square.",
    "scene_04_conclusion": "The theorem is used in construction, navigation, computer graphics, and many other fields."
  }
}
```
"""


def create_mock_scene_response():
    """Create a mock response for the build_scenes phase."""
    return """
```json
{
  "scene_body": "title = Text(\\"The Pythagorean Theorem\\", font_size=48, weight=BOLD)\\ntitle.move_to(UP * 3.8)\\nself.play(Write(title))\\nsubtitle = Text(\\"a² + b² = c²\\", font_size=36)\\nsubtitle.next_to(title, DOWN, buff=0.4)\\nsafe_position(subtitle)\\nself.play(FadeIn(subtitle))"
}
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
    assert "scene_01_intro" in code, "Narration missing scene_01_intro"

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
    assert "with self.voiceover" not in code, "Scene should be body-only code"
    assert "self.play(" in code, "Scene missing animation call"

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
        assert "unresolved placeholders like `{{...}}`" in user_prompt
        assert "Scene file:" not in user_prompt
        assert "{{scene_file_name}}" not in user_prompt
        assert (
            "File naming/path selection is orchestrator-owned; "
            "do not produce or reason about filenames."
        ) in user_prompt

    print("✅ Build scenes prompt uses current scene narration only")


def test_scene_repair_prompt_omits_filename_contract():
    """Scene repair prompt should not ask model for file naming decisions."""
    print("Testing scene_repair prompt filename contract...")

    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        scene_file = project_dir / "scene_02_focus.py"
        scene_file.write_text(
            "from manim import *\nclass Scene02Focus(Scene):\n    pass\n",
            encoding="utf-8",
        )

        plan = {
            "title": "Repair filename contract test",
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
                    "file": "scene_02_focus.py",
                },
            ],
            "current_scene_index": 1,
        }

        _, user_prompt = compose_prompt(
            phase="scene_repair",
            state=state,
            retry_context="TypeError: example",
            scene_file=scene_file,
            project_dir=project_dir,
        )

        assert "Expected File Name:" not in user_prompt
        assert "{{scene_file_name}}" not in user_prompt
        assert (
            "File naming/path selection is orchestrator-owned; "
            "do not produce or reason about filenames."
        ) in user_prompt
        assert 'SCRIPT["scene_02_focus"]' in user_prompt

    print("✅ Scene repair prompt omits filename contract")


def test_prompt_manifests_do_not_declare_output_file():
    """Build/repair manifests should describe body payload only, not filenames."""
    print("Testing prompt manifest output contract...")

    build_manifest = (
        REPO_ROOT / "harness" / "prompts" / "04_build_scenes" / "manifest.yaml"
    ).read_text(encoding="utf-8")
    repair_manifest = (
        REPO_ROOT / "harness" / "prompts" / "06_scene_repair" / "manifest.yaml"
    ).read_text(encoding="utf-8")

    assert "\n  file:" not in build_manifest
    assert "\n  file:" not in repair_manifest
    assert "scene_body" in build_manifest
    assert "scene_body" in repair_manifest

    print("✅ Prompt manifests declare body-only output contract")


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
            "created_at": datetime.now(UTC).isoformat() + "Z",
            "updated_at": datetime.now(UTC).isoformat() + "Z",
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
        test_scene_repair_prompt_omits_filename_contract()
        test_prompt_manifests_do_not_declare_output_file()

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
