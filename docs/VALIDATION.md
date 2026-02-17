# Scene Validation System

Semantic validation checks for scaffolded Manim + Voiceover scenes in the flaming-horse pipeline.

## Overview

The scene validation layer catches scene issues before expensive render checks, then drives a repair loop when validation fails.

## Semantic Validation Checks

### 1) Syntax validation
- **Check**: Scene parses without `SyntaxError`
- **Why**: Parse errors fail immediately at import/runtime validation
- **Fix**: Correct invalid Python syntax in the scene file

### 2) Voiceover narration wiring
- **Check**: Scene uses a voiceover context with `SCRIPT[...]`, for example:
  - `with self.voiceover(text=SCRIPT["scene_01_intro"]) as tracker:`
- **Why**: Scaffolded scenes use narration keys from `narration_script.py` rather than inline narration variables
- **Fix**: Import `SCRIPT` and wire the voiceover call to the proper narration key

### 3) `construct()` method validation
- **Check**: `construct(self)` exists and is substantive (not empty / not only `pass`)
- **Why**: Empty construct blocks create blank scenes
- **Fix**: Add meaningful mobject creation/animation logic

### 4) Import validation
- **Check**: Scene includes Manim imports
- **Why**: Missing imports produce `NameError`
- **Fix**: Include `from manim import *` (or equivalent valid import pattern)

### 5) Scene class validation
- **Check**: Scene class inherits from `VoiceoverScene`
- **Why**: Scaffold + voiceover flow is built around `VoiceoverScene`
- **Fix**: Use class definitions such as `class Scene01Intro(VoiceoverScene):`

### 6) Animation validation
- **Check**: No empty `self.play()` calls
- **Why**: Empty play calls are runtime errors
- **Fix**: Supply animation args (e.g. `self.play(Create(circle))`)

### 7) Timing validation
- **Check**: If scene uses `self.play(...)`, it should include `self.wait(...)`
- **Why**: Scenes need pacing and time allocation
- **Fix**: Add waits between/after animation groups

### 8) Placeholder detection
- **Check**: No TODO/FIXME placeholders inside `construct()`
- **Why**: Placeholders indicate unfinished implementation
- **Fix**: Replace placeholders with implemented scene logic

## Scene Resolution Rules

Validation resolves scenes from `project_state.json` using:
- `current_scene_index` / requested scene index
- `scenes[idx].id` (or fallback `scene_id`)
- `scenes[idx].file` if present, else `${id}.py`

Scene files are searched in:
- `${project_dir}/${scene_file}`
- `${project_dir}/scenes/${scene_file}`

## Self-Heal Optimization

### Features
- **Early termination**: Stops when file hash is unchanged between attempts
- **Exponential backoff**: Retries with increasing delay (capped)
- **Repair hook**: Calls repair hook when available (`invoke_scene_fix_agent`, fallback `scene_repair`)
- **Max attempts**: Controlled by env var

### Configuration

```bash
# Maximum retry attempts (default: 15)
export SCENE_QC_MAX_ATTEMPTS=15

# Backoff multiplier base (default: 2)
export SCENE_QC_BACKOFF_BASE=2
```

### Backoff schedule example (`SCENE_QC_BACKOFF_BASE=2`)

| Attempt | Backoff |
| --- | --- |
| 1 | 0s |
| 2 | 1s |
| 3 | 2s |
| 4 | 4s |
| 5 | 8s |
| 6+ | 16s (capped) |

## Integration Points

### `build_video.sh`
- Source `scripts/scene_validation.sh`
- During `scene_qc`:
  - run `validate_scene_files_consistency`
  - run `validate_scene_semantics`
  - on failure, run `self_heal_scene_with_optimization`

### Validation flow

```text
scene_qc
  -> validate_scene_files_consistency
  -> validate_scene_semantics
      -> pass: continue render validation
      -> fail: self_heal_scene_with_optimization
          -> healed: continue render validation
          -> exhausted: fail phase
```

## Troubleshooting

### Validation keeps failing
- Inspect `.scene_validation_<scene_id>.log`
- Confirm scene file path resolves from `project_state.json`
- Check repair hook availability and logs in `build.log`

### Self-heal does not converge
- Increase `SCENE_QC_MAX_ATTEMPTS`
- Improve scene repair prompt constraints
- Check whether repairs are modifying the file (hash should change)

### Suspected false positives
- Compare scene code against scaffold conventions in `scripts/scaffold_scene.py`
- Verify class inheritance and voiceover `SCRIPT[...]` usage

## Examples

### Valid scaffold-aligned structure

```python
from manim import *
from manim_voiceover_plus import VoiceoverScene
from narration_script import SCRIPT


class Scene01Intro(VoiceoverScene):
    def construct(self):
        with self.voiceover(text=SCRIPT["scene_01_intro"]) as tracker:
            title = Text("Introduction")
            self.play(Write(title))
            self.wait(tracker.duration * 0.2)
```

### Common failure: wrong base class

```python
class Scene01Intro(Scene):  # invalid for scaffolded voiceover flow
    ...
```

### Common failure: missing SCRIPT voiceover wiring

```python
class Scene01Intro(VoiceoverScene):
    def construct(self):
        narration_text = "..."  # not scaffold convention
```

## See Also

- `AGENTS.md`
- `scripts/scene_validation.sh`
- `harness/prompt_templates/scene_fix_prompt.md`
- `harness/prompt_templates/phase_build_scenes.md`
