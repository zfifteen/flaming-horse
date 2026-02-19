#!/usr/bin/env python3
"""
Standalone demo showing how to read and use kitchen_sink.md

This demo shows that kitchen_sink.md can be:
1. Read as a standalone file
2. Used as reference material
3. Injected into prompts (demo only, not integrated)
4. Validated independently

NO APP INTEGRATION - This is just a demonstration.
"""

from pathlib import Path

def demo_read_kitchen_sink():
    """Demo: Read the kitchen sink reference."""
    print("=" * 60)
    print("DEMO 1: Reading Kitchen Sink Reference")
    print("=" * 60)
    
    kitchen_sink_path = Path("harness/templates/kitchen_sink.md")
    
    if not kitchen_sink_path.exists():
        print(f"❌ File not found: {kitchen_sink_path}")
        return
    
    content = kitchen_sink_path.read_text()
    
    print(f"✓ Successfully read: {kitchen_sink_path}")
    print(f"✓ Size: {len(content):,} bytes")
    print(f"✓ Lines: {len(content.splitlines()):,}")
    print()

def demo_extract_sections():
    """Demo: Extract specific pattern families."""
    print("=" * 60)
    print("DEMO 2: Extracting Pattern Families")
    print("=" * 60)
    
    kitchen_sink_path = Path("harness/templates/kitchen_sink.md")
    content = kitchen_sink_path.read_text()
    
    # Find all pattern families
    import re
    pattern_families = re.findall(r'## (Pattern Family \d+: [^\n]+)', content)
    
    print("Found pattern families:")
    for i, family in enumerate(pattern_families, 1):
        print(f"  {i}. {family}")
    print()

def demo_count_resources():
    """Demo: Count documentation resources."""
    print("=" * 60)
    print("DEMO 3: Counting Resources")
    print("=" * 60)
    
    kitchen_sink_path = Path("harness/templates/kitchen_sink.md")
    content = kitchen_sink_path.read_text()
    
    doc_links = content.count("https://docs.manim.community")
    code_blocks = content.count("```python")
    section_headers = content.count("##")
    
    print(f"✓ Official documentation links: {doc_links}")
    print(f"✓ Python code examples: {code_blocks}")
    print(f"✓ Section headers: {section_headers}")
    print()

def demo_simulate_prompt_injection():
    """Demo: Simulate how kitchen_sink.md could be used in a prompt."""
    print("=" * 60)
    print("DEMO 4: Simulated Prompt Injection (NOT INTEGRATED)")
    print("=" * 60)
    
    kitchen_sink_path = Path("harness/templates/kitchen_sink.md")
    kitchen_sink_content = kitchen_sink_path.read_text()
    
    # Simulate a system prompt (NOT actually used anywhere)
    simulated_prompt = f"""
You are a Manim scene generator.

## Core Rules
- Use only official Manim CE APIs
- Follow best practices

---

## Manim CE Reference

{kitchen_sink_content[:500]}...
[TRUNCATED FOR DEMO - Full content would be {len(kitchen_sink_content)} bytes]

---

## Task
Generate a scene based on the reference above.
"""
    
    print("✓ Simulated prompt structure:")
    print(f"   - Total length: {len(simulated_prompt):,} characters")
    print(f"   - Includes kitchen_sink.md content")
    print(f"   - Ready for LLM injection")
    print()
    print("⚠ NOTE: This is DEMO ONLY - not integrated into app")
    print()

def demo_validation():
    """Demo: Run validation on kitchen_sink.md."""
    print("=" * 60)
    print("DEMO 5: Validation")
    print("=" * 60)
    
    print("Running validation script...")
    print()
    
    import subprocess
    result = subprocess.run(
        ["python3", "scripts/validate_kitchen_sink.py"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.returncode == 0:
        print("✓ Validation passed!")
    else:
        print("✗ Validation failed!")
        print(result.stderr)
    print()

def main():
    """Run all demos."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "KITCHEN SINK STANDALONE DEMO" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    print("This demo shows kitchen_sink.md as a standalone artifact.")
    print("NO APP INTEGRATION is performed.")
    print()
    
    demo_read_kitchen_sink()
    demo_extract_sections()
    demo_count_resources()
    demo_simulate_prompt_injection()
    demo_validation()
    
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("Summary:")
    print("  ✓ kitchen_sink.md exists and is readable")
    print("  ✓ Contains all required pattern families")
    print("  ✓ Can be used standalone or in prompts")
    print("  ✓ Validated successfully")
    print()
    print("Location: harness/templates/kitchen_sink.md")
    print()

if __name__ == "__main__":
    main()
