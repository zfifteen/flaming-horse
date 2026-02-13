#!/usr/bin/env python3
"""
Unit tests for generate_scenes_txt.py

Run:
    python scripts/test_generate_scenes_txt.py

Author: Big D
Date: 2026-02-12
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent))
import generate_scenes_txt


class TestGenerateScenesTxt(unittest.TestCase):
    """Test suite for scenes.txt generator."""
    
    def setUp(self):
        """Create temporary directory for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Cleanup temporary directory."""
        self.temp_dir.cleanup()
    
    def create_state_file(self, state_data: dict):
        """Helper to create project_state.json."""
        state_file = self.project_dir / "project_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2)
    
    def test_load_project_state_success(self):
        """Test successful state loading."""
        state_data = {
            "project_name": "test_project",
            "scenes": [
                {"id": "scene_01", "class_name": "Scene01"}
            ]
        }
        self.create_state_file(state_data)
        
        state = generate_scenes_txt.load_project_state(self.project_dir)
        self.assertEqual(state['project_name'], 'test_project')
    
    def test_load_project_state_missing_file(self):
        """Test error when state file is missing."""
        with self.assertRaises(FileNotFoundError) as ctx:
            generate_scenes_txt.load_project_state(self.project_dir)
        
        self.assertIn("project_state.json not found", str(ctx.exception))
    
    def test_load_project_state_invalid_json(self):
        """Test error when JSON is malformed."""
        state_file = self.project_dir / "project_state.json"
        with open(state_file, 'w') as f:
            f.write("{ invalid json }")
        
        with self.assertRaises(ValueError) as ctx:
            generate_scenes_txt.load_project_state(self.project_dir)
        
        self.assertIn("Invalid JSON", str(ctx.exception))
    
    def test_validate_state_structure_missing_scenes(self):
        """Test error when 'scenes' key is missing."""
        state = {"project_name": "test"}
        
        with self.assertRaises(ValueError) as ctx:
            generate_scenes_txt.validate_state_structure(state)
        
        self.assertIn("missing 'scenes' key", str(ctx.exception))
    
    def test_validate_state_structure_scenes_not_list(self):
        """Test error when 'scenes' is not a list."""
        state = {"scenes": "not a list"}
        
        with self.assertRaises(ValueError) as ctx:
            generate_scenes_txt.validate_state_structure(state)
        
        self.assertIn("must be a list", str(ctx.exception))
    
    def test_validate_state_structure_empty_scenes(self):
        """Test error when scenes list is empty."""
        state = {"scenes": []}
        
        with self.assertRaises(ValueError) as ctx:
            generate_scenes_txt.validate_state_structure(state)
        
        self.assertIn("No scenes defined", str(ctx.exception))
    
    def test_extract_video_paths_with_explicit_paths(self):
        """Test extracting paths when video_file is set."""
        state = {
            "scenes": [
                {
                    "id": "scene_01_intro",
                    "class_name": "Scene01Intro",
                    "video_file": "media/videos/scene_01_intro/1440p60/Scene01Intro.mp4"
                },
                {
                    "id": "scene_02_demo",
                    "class_name": "Scene02Demo",
                    "video_file": "media/videos/scene_02_demo/1440p60/Scene02Demo.mp4"
                }
            ]
        }
        
        paths = generate_scenes_txt.extract_video_paths(state)
        
        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0], "media/videos/scene_01_intro/1440p60/Scene01Intro.mp4")
        self.assertEqual(paths[1], "media/videos/scene_02_demo/1440p60/Scene02Demo.mp4")
    
    def test_extract_video_paths_with_default_paths(self):
        """Test extracting paths when video_file is not set."""
        state = {
            "scenes": [
                {
                    "id": "scene_01_intro",
                    "class_name": "Scene01Intro"
                },
                {
                    "id": "scene_02_demo",
                    "class_name": "Scene02Demo"
                }
            ]
        }
        
        paths = generate_scenes_txt.extract_video_paths(state)
        
        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0], "media/videos/scene_01_intro/1440p60/Scene01Intro.mp4")
        self.assertEqual(paths[1], "media/videos/scene_02_demo/1440p60/Scene02Demo.mp4")
    
    def test_extract_video_paths_missing_id(self):
        """Test error when scene is missing 'id' field."""
        state = {
            "scenes": [
                {"class_name": "Scene01"}
            ]
        }
        
        with self.assertRaises(ValueError) as ctx:
            generate_scenes_txt.extract_video_paths(state)
        
        self.assertIn("missing 'id' field", str(ctx.exception))
    
    def test_extract_video_paths_missing_class_name(self):
        """Test error when scene is missing 'class_name' field."""
        state = {
            "scenes": [
                {"id": "scene_01"}
            ]
        }
        
        with self.assertRaises(ValueError) as ctx:
            generate_scenes_txt.extract_video_paths(state)
        
        self.assertIn("missing 'class_name' field", str(ctx.exception))
    
    def test_generate_scenes_txt_creates_file(self):
        """Test that scenes.txt is created with correct content."""
        video_paths = [
            "media/videos/scene_01_intro/1440p60/Scene01Intro.mp4",
            "media/videos/scene_02_demo/1440p60/Scene02Demo.mp4"
        ]
        
        output_file = generate_scenes_txt.generate_scenes_txt(self.project_dir, video_paths)
        
        self.assertTrue(output_file.exists())
        self.assertEqual(output_file.name, "scenes.txt")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], "file 'media/videos/scene_01_intro/1440p60/Scene01Intro.mp4'\n")
        self.assertEqual(lines[1], "file 'media/videos/scene_02_demo/1440p60/Scene02Demo.mp4'\n")
    
    def test_end_to_end_with_explicit_paths(self):
        """Test full workflow with explicit video_file paths."""
        state_data = {
            "project_name": "test_video",
            "phase": "assemble",
            "scenes": [
                {
                    "id": "scene_01_intro",
                    "class_name": "Scene01Intro",
                    "video_file": "media/videos/scene_01_intro/1440p60/Scene01Intro.mp4"
                },
                {
                    "id": "scene_02_conclusion",
                    "class_name": "Scene02Conclusion",
                    "video_file": "media/videos/scene_02_conclusion/1440p60/Scene02Conclusion.mp4"
                }
            ]
        }
        self.create_state_file(state_data)
        
        state = generate_scenes_txt.load_project_state(self.project_dir)
        generate_scenes_txt.validate_state_structure(state)
        video_paths = generate_scenes_txt.extract_video_paths(state)
        output_file = generate_scenes_txt.generate_scenes_txt(self.project_dir, video_paths)
        
        self.assertTrue(output_file.exists())
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        expected = (
            "file 'media/videos/scene_01_intro/1440p60/Scene01Intro.mp4'\n"
            "file 'media/videos/scene_02_conclusion/1440p60/Scene02Conclusion.mp4'\n"
        )
        self.assertEqual(content, expected)
    
    def test_end_to_end_with_default_paths(self):
        """Test full workflow with default video paths."""
        state_data = {
            "project_name": "test_video",
            "phase": "assemble",
            "scenes": [
                {
                    "id": "scene_01_intro",
                    "class_name": "Scene01Intro"
                },
                {
                    "id": "scene_02_conclusion",
                    "class_name": "Scene02Conclusion"
                }
            ]
        }
        self.create_state_file(state_data)
        
        state = generate_scenes_txt.load_project_state(self.project_dir)
        generate_scenes_txt.validate_state_structure(state)
        video_paths = generate_scenes_txt.extract_video_paths(state)
        output_file = generate_scenes_txt.generate_scenes_txt(self.project_dir, video_paths)
        
        self.assertTrue(output_file.exists())
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        expected = (
            "file 'media/videos/scene_01_intro/1440p60/Scene01Intro.mp4'\n"
            "file 'media/videos/scene_02_conclusion/1440p60/Scene02Conclusion.mp4'\n"
        )
        self.assertEqual(content, expected)


if __name__ == "__main__":
    # Run tests with verbose output
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGenerateScenesTxt)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
