#!/usr/bin/env python3
"""
Regression tests for scaffold generation and parser functionality.

Tests ensure that:
1. Generated scaffolds keep locked header and slot markers
2. Import statements are correct (no missing/wrong imports)
3. Parser correctly handles body code injection
4. harmonious_color works with expected argument patterns
"""

import sys
from pathlib import Path
import tempfile

# Add project root to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from harness.parser import (
    inject_body_into_scaffold,
    parse_build_scenes_response,
    parse_scene_repair_response,
    has_scaffold_artifacts,
)
from scripts.scaffold_scene import TEMPLATE


class TestScaffoldGeneration:
    """Test scaffold template generation."""

    def test_scaffold_has_locked_config(self):
        """Scaffold must have locked configuration header."""
        assert "config.frame_height = 10" in TEMPLATE
        assert "config.frame_width = 10 * 16 / 9" in TEMPLATE
        assert "config.pixel_height = 1440" in TEMPLATE
        assert "config.pixel_width = 2560" in TEMPLATE

    def test_scaffold_has_slot_markers(self):
        """Scaffold must have both SLOT markers."""
        assert "# SLOT_START:scene_body" in TEMPLATE
        assert "# SLOT_END:scene_body" in TEMPLATE

    def test_scaffold_imports_helpers_correctly(self):
        """Scaffold must import helpers from flaming_horse.scene_helpers."""
        assert "from flaming_horse.scene_helpers import" in TEMPLATE
        assert "safe_position" in TEMPLATE
        assert "harmonious_color" in TEMPLATE

    def test_scaffold_no_beat_imports(self):
        """Scaffold must not import beat-related helpers."""
        assert "BeatPlan" not in TEMPLATE
        assert "play_next" not in TEMPLATE
        assert "play_text_next" not in TEMPLATE


class TestParserBodyExtraction:
    """Test parser correctly extracts body code."""

    def test_parse_valid_body_code(self):
        """Parser should extract valid body code."""
        response = """
Here's the scene body:

```python
title = Text("Welcome", font_size=48)
title.move_to(UP * 3.8)
self.play(Write(title))
```
"""
        body = parse_build_scenes_response(response)
        assert body is not None
        assert "Write(title)" in body

    def test_reject_scene_body_wrappers_in_build_scenes(self):
        """Build-scenes parser is strict fenced-only body and rejects XML wrappers."""
        response = """
```python
<scene_body>
title = Text("Welcome", font_size=48)
self.play(Write(title))
</scene_body>
```
"""
        body = parse_build_scenes_response(response)
        assert body is None

    def test_require_exactly_one_fenced_block(self):
        """Build-scenes parser should reject responses without exactly one fenced block."""
        raw_response = """
title = Text("Welcome", font_size=48)
self.play(Write(title))
"""
        assert parse_build_scenes_response(raw_response) is None

        multi_block_response = """
```python
title = Text("A")
```
```python
self.play(Write(title))
```
"""
        assert parse_build_scenes_response(multi_block_response) is None

    def test_strip_harness_preamble_for_build_scenes(self):
        """Build-scenes parser should ignore harness logging lines before fenced code."""
        response = """
🤖 Harness using:
Provider: XAI
Base URL: https://api.x.ai/v1
Model: grok-4-1-fast-reasoning
```python
title = Text("Welcome", font_size=48)
self.play(Write(title))
```
"""
        body = parse_build_scenes_response(response)
        assert body is not None
        assert body.splitlines()[0].startswith('title = Text("Welcome"')

    def test_reject_scaffold_placeholders(self):
        """Parser should reject code with scaffold placeholders."""
        responses = [
            '```python\ntitle = Text("{{TITLE}}", font_size=48)\n```',
            "```python\nsubtitle = Text('{{SUBTITLE}}', font_size=32)\n```",
            '```python\nbullet = Text("{{KEY_POINT_1}}")\n```',
        ]
        for response in responses:
            body = parse_build_scenes_response(response)
            assert body is None, f"Should reject: {response}"

    def test_reject_header_tokens(self):
        """Parser should reject code with header/scaffold structure."""
        response = """
```python
from manim import *
config.frame_width = 10 * 16 / 9

class MyScene(VoiceoverScene):
    def construct(self):
        pass
```
"""
        body = parse_build_scenes_response(response)
        assert body is None

    def test_reject_slot_markers(self):
        """Parser should reject code containing SLOT markers."""
        response = """
```python
# SLOT_START:scene_body
title = Text("Hello")
# SLOT_END:scene_body
```
"""
        body = parse_build_scenes_response(response)
        assert body is None


class TestBodyInjection:
    """Test body code injection into scaffolds."""

    def test_inject_valid_body(self):
        """Should successfully inject valid body code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scaffold_path = Path(tmpdir) / "test_scene.py"
            scaffold_path.write_text(
                TEMPLATE.format(class_name="TestScene", narration_key="test")
            )

            body_code = """            title = Text("Test", font_size=48)
            title.move_to(UP * 3.8)
            self.play(Write(title))"""

            full_code = inject_body_into_scaffold(scaffold_path, body_code)

            # Verify markers are preserved
            assert "# SLOT_START:scene_body" in full_code
            assert "# SLOT_END:scene_body" in full_code

            # Verify locked config is preserved
            assert "config.frame_width = 10 * 16 / 9" in full_code

            # Verify body is present
            assert "Write(title)" in full_code

    def test_reject_empty_body(self):
        """Should reject body with only comments/whitespace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scaffold_path = Path(tmpdir) / "test_scene.py"
            scaffold_path.write_text(
                TEMPLATE.format(class_name="TestScene", narration_key="test")
            )

            empty_bodies = [
                "    # Just a comment",
                "    \n    \n    ",
                "            # Comment 1\n            # Comment 2",
            ]

            for empty_body in empty_bodies:
                try:
                    inject_body_into_scaffold(scaffold_path, empty_body)
                    raise AssertionError(
                        f"Should have raised ValueError for: {empty_body}"
                    )
                except ValueError as e:
                    assert "at least one non-comment statement" in str(e)

    def test_injected_code_is_valid_python(self):
        """Injected code should be syntactically valid Python."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scaffold_path = Path(tmpdir) / "test_scene.py"
            scaffold_path.write_text(
                TEMPLATE.format(class_name="TestScene", narration_key="test")
            )

            # Body code should be unindented (parser provides it this way)
            body_code = """title = Text("Test")
self.play(FadeIn(title))"""

            full_code = inject_body_into_scaffold(scaffold_path, body_code)

            # Should compile without syntax errors
            compile(full_code, "<string>", "exec")


class TestScaffoldArtifactsDetection:
    """Test detection of scaffold artifacts."""

    def test_detect_placeholder_literals(self):
        """Should detect forbidden placeholder tokens."""
        bad_codes = [
            'title = Text("{{TITLE}}")',
            "subtitle = Text('{{SUBTITLE}}')",
            'Text("{{KEY_POINT_1}}")',
        ]
        for code in bad_codes:
            assert has_scaffold_artifacts(code), f"Should detect: {code}"

    def test_detect_demo_rectangle(self):
        """Should detect demo Rectangle from scaffold."""
        demo_code = "box = Rectangle(width=4.0, height=2.4, color=BLUE)"
        assert has_scaffold_artifacts(demo_code)

    def test_clean_code_passes(self):
        """Should not flag clean production code."""
        clean_codes = [
            'title = Text("Real Title", font_size=48)',
            "subtitle = Text('Actual Subtitle')",
            "box = Rectangle(width=3.0, height=2.0)",
        ]
        for code in clean_codes:
            assert not has_scaffold_artifacts(code), f"Should pass: {code}"


class TestHarmoniousColorContract:
    """Test harmonious_color helper function."""

    def test_harmonious_color_with_strings(self):
        """harmonious_color should accept string color names."""
        # This test verifies the contract mentioned in the issue
        # We can't import manim here, so we test the logic
        try:
            from flaming_horse.scene_helpers import harmonious_color

            # These should not raise (testing contract, not functionality)
            harmonious_color("primary")
            harmonious_color("secondary")
            harmonious_color("accent")
            print("      ✓ harmonious_color accepts string color names")
        except ImportError:
            # Expected when manim not installed
            print("      ⊘ Skipped (Manim not installed)")
        except AttributeError as e:
            # If we get AttributeError about to_rgb(), the contract is broken
            raise AssertionError(f"harmonious_color should handle strings: {e}")


class TestSceneRepairParser:
    """Test scene repair response parser."""

    def test_repair_parser_checks_artifacts(self):
        """Repair parser should reject code with scaffold artifacts."""
        response = """
Fixed code:
```python
title = Text("{{TITLE}}", font_size=48)
```
"""
        body = parse_scene_repair_response(response)
        assert body is None, "Should reject repair code with placeholders"

    def test_repair_parser_accepts_clean_code(self):
        """Repair parser should accept clean repaired code."""
        response = """
Fixed:
```python
title = Text("Fixed Title", font_size=48)
self.play(Write(title))
```
"""
        body = parse_scene_repair_response(response)
        assert body is not None
        assert "Fixed Title" in body


def run_tests():
    """Run all tests."""
    test_classes = [
        TestScaffoldGeneration,
        TestParserBodyExtraction,
        TestBodyInjection,
        TestScaffoldArtifactsDetection,
        TestHarmoniousColorContract,
        TestSceneRepairParser,
    ]

    total = 0
    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith("test_")]

        for method_name in methods:
            total += 1
            try:
                method = getattr(instance, method_name)
                method()
                print(f"  ✓ {method_name}")
                passed += 1
            except Exception as e:
                print(f"  ✗ {method_name}: {e}")
                failed += 1

    print(f"\n{'=' * 60}")
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"{'=' * 60}")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
