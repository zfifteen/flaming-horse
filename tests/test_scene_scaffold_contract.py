# tests/test_scene_scaffold_contract.py
import importlib.util
from pathlib import Path


REQUIRED_MARKERS = [
    "config.frame_width = 10 * 16 / 9",
    "SLOT_START_SCENE_BODY",
]


def test_scene_scaffolds_preserve_markers():
    # Example: Adjust path for actual test
    scene_path = Path("generated/smoke-test-5/scene01intro.py")
    if scene_path.exists():
        text = scene_path.read_text()
        for marker in REQUIRED_MARKERS:
            assert marker in text, f"Missing scaffold marker: {marker}"


def test_scene_imports_without_syntax_error():
    scene_path = Path("generated/smoke-test-5/scene01intro.py")
    if scene_path.exists():
        spec = importlib.util.spec_from_file_location("scene01intro", scene_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # should raise if syntax is invalid
