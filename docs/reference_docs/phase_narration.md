# Phase Narration Details

## Phase: `narration`

**Goal:** Generate narration scripts (cached Qwen configuration is already in `voice_clone_config.json`)

**Output 1: `narration_script.py`**

```python
"""
Narration script for: [Project Name]
Generated: [Date]
Duration: ~[X] seconds
"""

SCRIPT = {
    "intro": """Your intro narration here. Write naturally, as if speaking.
    Keep it conversational and engaging.""",
    
    "demo": """Second segment narration.""",
    
    "conclusion": """Closing remarks that tie everything together."""
}
```

**Output 2:** None (cached Qwen configuration lives in `voice_clone_config.json`)

## Voice Cache Optimization

After generating `narration_script.py`, the precache step:
1. Computes SHA256 hash of narration_script.py
2. Compares to `.cache_hash` file in project
3. Skips regeneration if hash matches (saves 2-5 minutes)

**Agent action:** None required. Orchestrator handles cache validation automatically.

## Non-Math Narration Guidance

For non-math topics, write narration so scene builders can sustain explainer-slide cadence:
- Include 4-8 short visual cues per scene (title setup, bullet progression, visual shift, recap).
- Keep transitions explicit ("First", "Next", "Now notice", "Finally").
- Avoid one long uninterrupted paragraph that only supports a single late animation.

**State Update:**
```python
state['narration_file'] = 'narration_script.py'
state['phase'] = 'build_scenes'
```
