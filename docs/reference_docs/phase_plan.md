# Phase Plan and Review Details

## Phase: `plan`

**Goal:** Generate comprehensive video plan from project requirements

**Actions:**
1. Read `topic` from `project_state.json` and analyze project topic + target audience
2. Break content into logical scenes (typically 3-8 scenes). If the user did not provide one, ALWAYS generate a final, 
   recap scene that summarizes and re-states the content of the video.
3. Estimate narration word count (150 words/minute speaking pace)
4. Flag animation complexity and risks
5. For non-math topics, plan scenes as explainer slides with progressive bullet structure and evolving diagrams/timelines

**Output:** `plan.json`

```json
{
  "title": "Video Title",
  "topic_summary": "Brief description",
  "target_audience": "Target viewers",
  "estimated_duration_seconds": 180,
  "total_estimated_words": 450,
  "scenes": [
    {
      "id": "scene_01_intro",
      "title": "Introduction",
      "narration_key": "intro",
      "narration_summary": "Hook and topic introduction",
      "estimated_words": 75,
      "estimated_duration": "30s",
      "animations": ["Write title", "FadeIn graphic"],
      "complexity": "low",
      "risk_flags": []
    }
  ]
}
```

**State Update:**
```python
state['plan_file'] = 'plan.json'
state['scenes'] = plan['scenes']
state['phase'] = 'review'
```

---

## Phase: `review`

**Goal:** Validate plan for technical feasibility

**Actions:**
1. Check narrative flow and coherence
2. Verify animation feasibility (avoid unsupported Manim features)
3. Estimate accurate timing per scene
4. Flag high-risk scenes

**Validation Checks:**
- ✅ Scene progression is logical
- ✅ 3D is allowed and often preferred when it improves clarity/engagement; flag only if unusually complex (camera rotations, heavy surfaces, many moving objects)
- ✅ No custom mobject definitions without clear implementation
- ✅ Timing allows for both narration + animation
- ⚠️ Flag scenes with >5 simultaneous objects
- ⚠️ Flag scenes requiring bookmark synchronization
- ✅ For non-math topics, each scene plan should imply continuous motion (new visual state every ~1.5-3s) and avoid sparse placeholder visuals

**Quality Scoring (New):**
Compute score = 10 - (risk_flags * 1.5) + (3d_used ? 2 : 0). If <7, suggest simplifications (e.g., "Reduce to 2D for scene X").

**State Update:**
- If approved: `state['phase'] = 'narration'`
- If critical issues: `state['flags']['needs_human_review'] = True`
