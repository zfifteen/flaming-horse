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
    Keep it conversational and engaging. Include beat markers for sync: e.g., "Hook: [beat1] Explanation: [beat2]". Estimate per-beat words using simple syllable count (add helper: `def estimate_beats(text): return len(text.split()) // 3`). Generate segmented SCRIPT: Split into 3-5 beats max per key for visual matching.""",
    
    "demo": """Second segment narration. Break into logical beats that
    match visual moments.""",
    
    "conclusion": """Closing remarks that tie everything together."""
}
```

**Output 2:** None (cached Qwen configuration lives in `voice_clone_config.json`)

**State Update:**
```python
state['narration_file'] = 'narration_script.py'
state['phase'] = 'build_scenes'
```
