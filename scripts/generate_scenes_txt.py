#!/usr/bin/env python3
"""
Generate scenes.txt for ffmpeg concatenation.

Reads project_state.json and creates scenes.txt with correct format:
    file 'media/videos/scene_01_intro/1440p60/Scene01Intro.mp4'
    file 'media/videos/scene_02_demo/1440p60/Scene02Demo.mp4'

Usage:
    python scripts/generate_scenes_txt.py projects/my_video

Author: Big D
Date: 2026-02-12
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def load_project_state(project_dir: Path) -> Dict:
    """Load and validate project_state.json."""
    state_file = project_dir / "project_state.json"
    
    if not state_file.exists():
        raise FileNotFoundError(
            f"project_state.json not found in {project_dir}\n"
            f"Expected: {state_file}"
        )
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {state_file}: {e}")
    
    return state


def validate_state_structure(state: Dict) -> None:
    """Validate that state has required fields."""
    if 'scenes' not in state:
        raise ValueError("project_state.json missing 'scenes' key")
    
    if not isinstance(state['scenes'], list):
        raise ValueError("'scenes' must be a list")
    
    if len(state['scenes']) == 0:
        raise ValueError("No scenes defined in project_state.json")


def extract_video_paths(state: Dict) -> List[str]:
    """Extract video file paths from state, validating each scene."""
    video_paths = []
    
    for i, scene in enumerate(state['scenes']):
        # Validate scene structure
        if 'id' not in scene:
            raise ValueError(f"Scene {i} missing 'id' field")
        
        if 'class_name' not in scene:
            raise ValueError(f"Scene {i} (id={scene['id']}) missing 'class_name' field")
        
        # Check if video_file is explicitly set
        if 'video_file' in scene and scene['video_file']:
            video_path = scene['video_file']
        else:
            # Construct default path from scene metadata
            scene_id = scene['id']
            class_name = scene['class_name']
            video_path = f"media/videos/{scene_id}/1440p60/{class_name}.mp4"
        
        video_paths.append(video_path)
    
    return video_paths


def generate_scenes_txt(project_dir: Path, video_paths: List[str]) -> Path:
    """Generate scenes.txt file in project directory."""
    output_file = project_dir / "scenes.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for video_path in video_paths:
            # ffmpeg concat format requires single quotes around paths
            f.write(f"file '{video_path}'\n")
    
    return output_file


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/generate_scenes_txt.py <project_dir>")
        print("")
        print("Example:")
        print("  python scripts/generate_scenes_txt.py projects/my_video")
        sys.exit(1)
    
    project_dir = Path(sys.argv[1])
    
    if not project_dir.exists():
        print(f"Error: Project directory does not exist: {project_dir}")
        sys.exit(1)
    
    if not project_dir.is_dir():
        print(f"Error: Not a directory: {project_dir}")
        sys.exit(1)
    
    try:
        # Load state
        print(f"Loading project state from {project_dir}...")
        state = load_project_state(project_dir)
        
        # Validate
        print("Validating state structure...")
        validate_state_structure(state)
        
        # Extract paths
        print(f"Extracting video paths for {len(state['scenes'])} scenes...")
        video_paths = extract_video_paths(state)
        
        # Generate scenes.txt
        print("Generating scenes.txt...")
        output_file = generate_scenes_txt(project_dir, video_paths)
        
        print(f"\u2713 Successfully created: {output_file}")
        print(f"")
        print(f"Contents:")
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                print(f"  {line.rstrip()}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
