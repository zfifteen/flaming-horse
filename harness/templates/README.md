# Harness Templates

This directory contains static reference documents designed for agent prompt injection.

## Files

### kitchen_sink.md

**Purpose:** Comprehensive Manim Community Edition reference for scene generation agents.

**Content:**
- Official Manim CE API patterns and documentation links
- 8 pattern families covering all major scene-building topics
- Agent-facing quality checklist
- Canonical code examples

**Source Policy:** All content derived exclusively from official Manim CE documentation (docs.manim.community). No third-party sources.

**Usage:** 
This file is intended for direct injection into build-scenes phase system prompts. To integrate:

```python
# In harness/prompts.py
TEMPLATES_DIR = Path(__file__).parent / "templates"
kitchen_sink = read_file(TEMPLATES_DIR / "kitchen_sink.md")

# Then include in system prompt:
system_prompt = f"""
{core_rules}

---

## Manim Reference

{kitchen_sink}

---

{build_scenes_system}
"""
```

**Validation:** See issue requirements for validation criteria.

---

## Design Principles

1. **Static Content:** Documents in this directory are static references, not dynamically generated.
2. **Agent-Facing:** Content is structured for LLM consumption, not human operational use.
3. **Source-Backed:** All technical assertions include official documentation links.
4. **Prompt-Ready:** Documents are formatted for direct system-prompt injection.

## Maintenance

When updating these references:
- Maintain strict adherence to source policy (official docs only)
- Update version numbers and dates in document headers
- Validate all documentation links remain active
- Ensure markdown structure remains consistent for parsing
