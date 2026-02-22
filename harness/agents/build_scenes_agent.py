import sys
from pathlib import Path
from harness.base_agent import BaseAgent
from harness.workflow.state import WorkflowState
from harness.workflow.config import (
    SCENE_LAYOUT_OPTIONS,
    LAYOUT_VALIDATION_RULES,
    PROJECT_DIR,
    DEFAULT_SCENE_MIN,
    DEFAULT_SCENE_MAX,
    DEFAULT_ASPECT_RATIO,
    FLAMING_HORSE_PROJECT_ASPECT_RATIO,
    DEFAULT_FPS
)
from harness.util.scene_spec import (
    SceneSpec,
    load_scene_specs,
    parse_scene_spec_text,
    scene_specs_to_json,
)
from harness.util.layout_validator import LayoutValidator


class BuildScenesAgent(BaseAgent):
    """
    Generates per-scene Manim specs: layout, text content, visuals, animation cues.
    """

    def run(self, state: WorkflowState) -> WorkflowState:
        self.log("Starting scene build generation...")

        plan = state.plan
        narration = state.narration
        aspect_ratio = state.get("aspect_ratio", DEFAULT_ASPECT_RATIO)

        # Determine min_scenes and max_scenes
        if "scenes" in plan:
            min_scenes = int(plan["scenes"])
            max_scenes = int(plan["scenes"])
        else:
            min_scenes = DEFAULT_SCENE_MIN
            max_scenes = DEFAULT_SCENE_MAX

        prompt = self._build_prompt(
            plan, narration, min_scenes, max_scenes, aspect_ratio
        )

        self.log("Requesting scene generation from LLM...")
        raw = self.call_llm(prompt, temperature=0.7, max_tokens=4096)

        # Parse scene specs from LLM output
        specs = parse_scene_spec_text(raw)
        if not specs:
            self.error("LLM returned no valid scene specifications.")
            sys.exit(1)

        # Validate layout tags
        validator = LayoutValidator(SCENE_LAYOUT_OPTIONS, LAYOUT_VALIDATION_RULES)
        for i, spec in enumerate(specs):
            errors = validator.validate_layout(spec.layout)
            if errors:
                # Format layout requirements for error message
                layout_reqs = "\n".join(
                    f"  - {layout}: {', '.join(reqs)}"
                    for layout, reqs in LAYOUT_VALIDATION_RULES.items()
                )
                self.error(
                    f"Scene {i+1} layout validation failed:\n"
                    f"  Layout: {spec.layout}\n"
                    f"  Errors:\n" + "\n".join(f"    - {e}" for e in errors) +
                    f"\n\nValid layouts and requirements:\n{layout_reqs}\n\n"
                    f"The agent must use valid layout tags that meet all requirements."
                )
                sys.exit(1)

        self.log(f"Generated {len(specs)} scene(s). Validating...")
        if len(specs) < min_scenes:
            self.error(
                f"Generated {len(specs)} scenes, but plan requires at least {min_scenes}."
            )
            sys.exit(1)
        if len(specs) > max_scenes:
            self.error(
                f"Generated {len(specs)} scenes, but plan allows at most {max_scenes}."
            )
            sys.exit(1)

        # Store validated specs
        state.data["scene_specs"] = scene_specs_to_json(specs)
        state.data["scene_count"] = len(specs)
        self.log(f"Scene build complete. {len(specs)} scenes validated.")
        return state

    def _build_prompt(
        self, plan: dict, narration: list[dict], min_scenes: int, max_scenes: int, aspect_ratio: str
    ) -> str:
        # Format aspect ratio for display
        ar_display = aspect_ratio.replace(":", "x")

        # Extract layout requirements for prompt
        layout_info = []
        for layout, reqs in LAYOUT_VALIDATION_RULES.items():
            layout_info.append(f"  - {layout}: {', '.join(reqs)}")
        layout_requirements = "\n".join(layout_info)

        return f"""Generate {min_scenes}-{max_scenes} Manim scene specifications for: {plan.get('title', 'video')}.

Narration:
{self._format_narration(narration)}

Aspect ratio: {ar_display}

For each scene, output:
```scene
SCENE_ID: <int>
LAYOUT: <tag>
TITLE: <text>
VISUALS: <description>
TEXT_CONTENT: <on-screen text>
ANIMATION: <cues>
```

Layout requirements:
{layout_requirements}

Ensure every scene uses a valid layout tag that meets all requirements."""

    def _format_narration(self, narration: list[dict]) -> str:
        lines = []
        for seg in narration:
            scene = seg.get("scene_number", "?")
            text = seg.get("text", "").strip()
            if text:
                lines.append(f"Scene {scene}: {text}")
        return "\n".join(lines)
