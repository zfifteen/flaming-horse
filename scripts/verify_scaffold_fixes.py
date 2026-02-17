#!/usr/bin/env python3
"""
Verification script to ensure all scaffold and parser fixes are in place.
Run this to validate the fixes before running the actual smoke test.
"""

import sys
from pathlib import Path

# Add project root to path
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

def check_scaffold_template():
    """Verify scaffold template is correct."""
    print("\n📋 Checking scaffold template...")
    from scripts.scaffold_scene import TEMPLATE
    
    checks = [
        ("Has locked config", "config.frame_width = 10 * 16 / 9", True),
        ("Has SLOT_START marker", "# SLOT_START:scene_body", True),
        ("Has SLOT_END marker", "# SLOT_END:scene_body", True),
        ("Imports from scene_helpers", "from flaming_horse.scene_helpers import", True),
        ("Imports BeatPlan", "BeatPlan", True),
        ("Imports play_next", "play_next", True),
        ("Imports play_text_next", "play_text_next", True),
        ("NO duplicate play_next def", "def play_next(", False),
        ("NO duplicate play_text_next def", "def play_text_next(", False),
        ("NO play_in_slot reference", "play_in_slot", False),
    ]
    
    all_passed = True
    for check_name, check_str, should_exist in checks:
        present = check_str in TEMPLATE
        passed = present == should_exist
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed

def check_parser_functions():
    """Verify parser functions have proper validation."""
    print("\n🔍 Checking parser functions...")
    from harness import parser
    import inspect
    
    checks = []
    
    # Check parse_build_scenes_response
    build_source = inspect.getsource(parser.parse_build_scenes_response)
    checks.append(("build_scenes checks artifacts", "has_scaffold_artifacts", build_source))
    
    # Check parse_scene_repair_response
    repair_source = inspect.getsource(parser.parse_scene_repair_response)
    checks.append(("repair checks artifacts", "has_scaffold_artifacts", repair_source))
    
    # Check inject_body_into_scaffold
    inject_source = inspect.getsource(parser.inject_body_into_scaffold)
    checks.append(("inject validates empty body", "at least one non-comment statement", inject_source))
    checks.append(("inject handles indentation", "# Re-indent all lines to 12 spaces", inject_source))
    
    all_passed = True
    for check_name, check_str, source in checks:
        present = check_str in source
        status = "✅" if present else "❌"
        print(f"  {status} {check_name}")
        if not present:
            all_passed = False
    
    return all_passed

def check_scene_helpers():
    """Verify scene_helpers exports are correct."""
    print("\n🛠️  Checking scene_helpers exports...")
    scene_helpers_path = Path("flaming_horse/scene_helpers.py")
    content = scene_helpers_path.read_text()
    
    expected_exports = [
        "safe_position",
        "harmonious_color",
        "polished_fade_in",
        "adaptive_title_position",
        "safe_layout",
        "BeatPlan",
        "play_next",
        "play_text_next",
    ]
    
    has_all_declaration = "__all__" in content
    print(f"  {'✅' if has_all_declaration else '❌'} Has __all__ declaration")
    
    all_passed = has_all_declaration
    for export in expected_exports:
        # Check if it's in __all__ (rough check)
        in_all = f"'{export}'" in content or f'"{export}"' in content
        # Check if function/class is defined
        defined = f"def {export}(" in content or f"class {export}" in content
        passed = in_all and defined
        status = "✅" if passed else "❌"
        print(f"  {status} {export}")
        if not passed:
            all_passed = False
    
    return all_passed

def check_tests_exist():
    """Verify test files exist and are executable."""
    print("\n🧪 Checking test files...")
    
    test_files = [
        "tests/test_scaffold_and_parser.py",
        "tests/test_e2e_scaffold_workflow.py",
    ]
    
    all_passed = True
    for test_file in test_files:
        path = Path(test_file)
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {test_file}")
        if not exists:
            all_passed = False
    
    return all_passed

def run_quick_tests():
    """Run quick validation tests."""
    print("\n🔬 Running quick validation tests...")
    
    try:
        # Test 1: Parse valid body code
        from harness.parser import parse_build_scenes_response
        test_response = '''
```python
num_beats = 12
beats = BeatPlan(tracker.duration, [1] * num_beats)
title = Text("Test")
```
'''
        body = parse_build_scenes_response(test_response)
        test1_passed = body is not None and "BeatPlan" in body
        print(f"  {'✅' if test1_passed else '❌'} Parse valid body code")
        
        # Test 2: Reject scaffold placeholders
        bad_response = '```python\ntitle = Text("{{TITLE}}")\n```'
        body2 = parse_build_scenes_response(bad_response)
        test2_passed = body2 is None
        print(f"  {'✅' if test2_passed else '❌'} Reject scaffold placeholders")
        
        # Test 3: Inject with indentation
        import tempfile
        from harness.parser import inject_body_into_scaffold
        from scripts.scaffold_scene import TEMPLATE
        
        with tempfile.TemporaryDirectory() as tmpdir:
            scaffold_path = Path(tmpdir) / "test.py"
            scaffold_path.write_text(TEMPLATE.format(
                class_name="TestScene",
                narration_key="test"
            ))
            
            unindented_body = "num_beats = 12\ntitle = Text('Test')"
            full_code = inject_body_into_scaffold(scaffold_path, unindented_body)
            
            # Check that body is indented
            test3_passed = "            num_beats = 12" in full_code
            print(f"  {'✅' if test3_passed else '❌'} Auto-indent body code")
            
            # Check syntax is valid
            try:
                compile(full_code, "<string>", "exec")
                test4_passed = True
            except SyntaxError:
                test4_passed = False
            print(f"  {'✅' if test4_passed else '❌'} Injected code is valid Python")
        
        return test1_passed and test2_passed and test3_passed and test4_passed
        
    except Exception as e:
        print(f"  ❌ Error running tests: {e}")
        return False

def main():
    """Run all verification checks."""
    print("="*70)
    print("🔧 Scaffold and Parser Fix Verification")
    print("="*70)
    
    results = {
        "Scaffold Template": check_scaffold_template(),
        "Parser Functions": check_parser_functions(),
        "Scene Helpers": check_scene_helpers(),
        "Test Files": check_tests_exist(),
        "Quick Tests": run_quick_tests(),
    }
    
    print("\n" + "="*70)
    print("📊 Verification Summary")
    print("="*70)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {check_name}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 All verification checks passed!")
        print("✅ Ready to run smoke test: tests/smoke_test.sh")
        print()
        return 0
    else:
        print("\n⚠️  Some checks failed. Review the output above.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
