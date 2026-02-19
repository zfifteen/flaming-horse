#!/usr/bin/env python3
"""
Validation script for harness/templates/kitchen_sink.md

Ensures the kitchen sink reference meets all requirements:
- File exists and is readable
- Contains all required sections
- Has sufficient documentation links
- Is agent-facing (no operational guidance)
- Contains code examples
"""

import sys
from pathlib import Path

def validate_kitchen_sink():
    """Validate kitchen_sink.md structure and content."""
    
    # File path
    repo_root = Path(__file__).parent.parent
    kitchen_sink = repo_root / "harness" / "templates" / "kitchen_sink.md"
    
    # Check 1: File exists
    if not kitchen_sink.exists():
        print(f"❌ FAIL: {kitchen_sink} does not exist")
        return False
    print(f"✓ File exists: {kitchen_sink}")
    
    # Read content
    content = kitchen_sink.read_text()
    
    # Check 2: File size
    if len(content) < 20000:
        print(f"❌ FAIL: Content too small ({len(content)} bytes, expected >20000)")
        return False
    print(f"✓ Content size: {len(content)} bytes")
    
    # Check 3: Required sections
    required_sections = [
        "Source Policy",
        "Core Contract for Agent Usage",
        "Pattern Family 1: Scene Lifecycle",
        "Pattern Family 2: 2D Geometry and Grouping",
        "Pattern Family 3: Text and Math Typesetting",
        "Pattern Family 4: Transition Choreography",
        "Pattern Family 5: Graphing and Coordinate Systems",
        "Pattern Family 6: 3D Scene and Camera Control",
        "Pattern Family 7: Trackers and Updaters",
        "Pattern Family 8: Color, Fill, Stroke",
        "Agent-Facing Quality Checklist",
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ FAIL: Missing required sections:")
        for section in missing_sections:
            print(f"   - {section}")
        return False
    print(f"✓ All {len(required_sections)} required sections present")
    
    # Check 4: Documentation links
    doc_link_count = content.count("https://docs.manim.community")
    if doc_link_count < 30:
        print(f"❌ FAIL: Insufficient documentation links ({doc_link_count}, expected ≥30)")
        return False
    print(f"✓ Documentation links: {doc_link_count}")
    
    # Check 5: Code examples
    code_block_count = content.count("```python")
    if code_block_count < 30:
        print(f"❌ FAIL: Insufficient code examples ({code_block_count}, expected ≥30)")
        return False
    print(f"✓ Code examples: {code_block_count}")
    
    # Check 6: No third-party sources in content (except forbidden list)
    third_party = [
        "stackoverflow.com",
        "youtube.com",
        "github.io",
        "manimclass.com",
        "devtaoism.com",
        "deepwiki.com"
    ]
    
    violations = []
    for source in third_party:
        if source in content:
            # Check if it's only in the forbidden section
            lines_with_source = [
                (i, line) for i, line in enumerate(content.split('\n'), 1)
                if source in line
            ]
            for line_num, line in lines_with_source:
                if "Forbidden" not in line and "blogs" not in line and "third-party" not in line.lower():
                    violations.append(f"Line {line_num}: {source}")
    
    if violations:
        print(f"❌ FAIL: Third-party sources found in content:")
        for v in violations:
            print(f"   - {v}")
        return False
    print(f"✓ No third-party sources in content")
    
    # Check 7: Source policy present
    if "STRICT REQUIREMENT" not in content or "Allowed Sources:" not in content:
        print(f"❌ FAIL: Source policy section incomplete")
        return False
    print(f"✓ Source policy section complete")
    
    # Check 8: Agent-facing (no installation/CLI guidance)
    operational_terms = ["install manim", "pip install", "manim render", "command line"]
    found_operational = []
    for term in operational_terms:
        if term.lower() in content.lower():
            found_operational.append(term)
    
    if found_operational:
        print(f"⚠ WARNING: Possible operational guidance found:")
        for term in found_operational:
            print(f"   - {term}")
        # This is a warning, not a failure
    else:
        print(f"✓ No operational guidance found")
    
    # All checks passed
    print("")
    print("=" * 50)
    print("✓ All validation checks passed!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = validate_kitchen_sink()
    sys.exit(0 if success else 1)
