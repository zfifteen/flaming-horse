# Phase Plan and Review Details

## Phase: `plan`

**Goal:** Generate video plan from project requirements using the active harness contract.

**Actions:**
1. Read `topic` from `project_state.json` and analyze project topic + target audience
2. Break content into logical scenes (default 12-24 scenes, 20-45 seconds per scene, total 480-960 seconds unless user topic overrides)
3. ALWAYS generate a final recap scene that summarizes and re-states the content of the video
4. For non-math topics, plan scenes as explainer slides with progressive bullet structure and evolving diagrams/timelines
5. Ensure scene visuals are concrete and reference Manim CE mobject classes without assuming external image/SVG assets

**Output:** `plan.json`

```json
{
  "title": "Video Title",
  "description": "Brief description",
  "target_duration_seconds": 600,
  "scenes": [
    {
      "title": "Introduction",
      "description": "What this scene teaches and shows",
      "estimated_duration_seconds": 30,
      "visual_ideas": [
        "Create a Text mobject for the title and center it near the top of the frame.",
        "Use a NumberLine mobject below the title to introduce progression through the topic."
      ]
    }
  ]
}
```

Notes:
- The harness assigns `id` and `narration_key` deterministically by scene order.
- `plan.title` and `plan.scenes` are the required parse keys; additional fields are allowed but optional.

**State Update:**
```python
state['plan_file'] = 'plan.json'
state['scenes'] = plan['scenes']
state['phase'] = 'review'
```

---

## Phase: `review`

**Goal:** Deterministic structural gate before narration (currently stubbed in harness prompt layer).

**Current behavior notes:**
- Review phase is currently a stub and should not be invoked by the harness CLI prompt.
- Build orchestration still performs deterministic structural checks (e.g., `plan.json` object shape and non-empty `scenes`) before advancing.

**State Update:**
- If approved: `state['phase'] = 'narration'`
- If critical issues: `state['flags']['needs_human_review'] = True`
