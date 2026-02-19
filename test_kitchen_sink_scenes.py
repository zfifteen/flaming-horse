#!/usr/bin/env python3
"""
Test script for kitchen_sink.md Manim CE examples.

This script extracts all Python code blocks from kitchen_sink.md and tests them
by actually rendering with Manim CE.

Requirements:
- manim >= 0.18.0
- System packages: libpango1.0-dev libcairo2-dev pkg-config

Usage:
    python3 test_kitchen_sink_scenes.py [--output-dir OUTPUT_DIR]
    
Example:
    python3 test_kitchen_sink_scenes.py --output-dir /tmp/kitchen_sink_test
"""

import argparse
import re
import sys
import tempfile
from pathlib import Path
import subprocess
import json

def extract_code_blocks(md_file):
    """Extract all Python code blocks from markdown file."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all code blocks
    pattern = r'```python\n(.*?)\n```'
    blocks = re.findall(pattern, content, re.DOTALL)
    
    # Extract class names
    scenes = []
    for i, block in enumerate(blocks, 1):
        class_match = re.search(r'^class\s+(\w+)\s*\(', block, re.MULTILINE)
        if class_match:
            class_name = class_match.group(1)
            scenes.append({
                'index': i,
                'class_name': class_name,
                'code': block
            })
    
    return scenes

def test_scene(scene, output_dir):
    """Test a single scene by rendering with Manim."""
    scene_name = scene['class_name']
    temp_file = output_dir / f"scene_{scene['index']:02d}_{scene_name}.py"
    
    # Write scene to temporary file
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(scene['code'])
    
    print(f"\n{'='*60}")
    print(f"Testing scene {scene['index']}: {scene_name}")
    print(f"{'='*60}")
    
    # Try to render with Manim (low quality for speed)
    cmd = [
        'manim',
        '-ql',  # low quality
        '--disable_caching',
        '--format', 'png',  # Just render a frame to test
        str(temp_file),
        scene_name
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=output_dir
        )
        
        if result.returncode == 0:
            print(f"✅ PASS: {scene_name}")
            return {
                'scene': scene_name,
                'index': scene['index'],
                'status': 'PASS',
                'error': None
            }
        else:
            print(f"❌ FAIL: {scene_name}")
            print(f"Error output:\n{result.stderr}")
            return {
                'scene': scene_name,
                'index': scene['index'],
                'status': 'FAIL',
                'error': result.stderr
            }
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT: {scene_name}")
        return {
            'scene': scene_name,
            'index': scene['index'],
            'status': 'TIMEOUT',
            'error': 'Rendering exceeded 60 second timeout'
        }
    except Exception as e:
        print(f"❌ ERROR: {scene_name}")
        print(f"Exception: {e}")
        return {
            'scene': scene_name,
            'index': scene['index'],
            'status': 'ERROR',
            'error': str(e)
        }

def main():
    parser = argparse.ArgumentParser(description='Test kitchen_sink.md Manim scenes')
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        help='Output directory for test files and renders'
    )
    parser.add_argument(
        '--kitchen-sink',
        type=Path,
        default=Path('harness/templates/kitchen_sink.md'),
        help='Path to kitchen_sink.md file'
    )
    
    args = parser.parse_args()
    
    # Setup output directory
    if args.output_dir:
        output_dir = args.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(tempfile.mkdtemp(prefix='kitchen_sink_test_'))
    
    print(f"Output directory: {output_dir}")
    print(f"Testing kitchen sink: {args.kitchen_sink}")
    
    # Check if Manim is available
    try:
        result = subprocess.run(
            ['manim', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"Manim version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Manim not available: {e}")
        print("Install with: pip install manim")
        return 1
    
    # Extract scenes
    scenes = extract_code_blocks(args.kitchen_sink)
    print(f"\nFound {len(scenes)} scenes to test\n")
    
    # Test each scene
    results = []
    for scene in scenes:
        result = test_scene(scene, output_dir)
        results.append(result)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] in ('ERROR', 'TIMEOUT'))
    
    print(f"Total: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"❌ Errors: {errors}")
    
    # Save detailed results
    results_file = output_dir / 'test_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {results_file}")
    
    # List failed scenes
    if failed > 0 or errors > 0:
        print("\nFailed scenes:")
        for r in results:
            if r['status'] != 'PASS':
                print(f"  - {r['index']:02d}. {r['scene']}: {r['status']}")
                if r['error']:
                    print(f"    Error: {r['error'][:200]}")
    
    return 0 if (failed == 0 and errors == 0) else 1

if __name__ == '__main__':
    sys.exit(main())
