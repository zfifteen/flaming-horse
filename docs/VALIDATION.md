# Scene Validation System

Comprehensive semantic validation for Manim scene files in the flaming-horse pipeline.

## Overview

The validation system ensures scene files meet semantic requirements before rendering, reducing failed renders and improving the self-heal loop efficiency.

## Semantic Validation Checks

### 1. Syntax Validation
**Check**: Python syntax is valid (no SyntaxError)
**Why**: Prevents immediate failure during import or execution
**Fix**: Correct syntax errors in the scene file

### 2. narration_text Presence
**Check**: Scene assigns `narration_text` variable with non-empty content
**Why**: Voiceover system requires narration text for TTS generation
**Failure**: Missing assignment or empty string `narration_text = ""`
**Fix**: Add proper narration text: `narration_text = "Your narration here"`

### 3. construct() Method Validation
**Check**: Scene has `construct(self)` method with substantive body
**Why**: Empty or placeholder construct() produces blank renders
**Failure patterns**:
- Missing construct() method
- Empty body (only whitespace)
- Only contains `pass`
- Only contains TODO/FIXME comments
**Fix**: Implement actual animation logic with self.play(), self.wait(), mobject creation

### 4. Import Validation
**Check**: Required Manim imports are present
**Why**: Missing imports cause NameError at runtime
**Required**: `from manim import *` or `import manim`
**Fix**: Add Manim imports at top of scene file

### 5. Scene Class Definition
**Check**: Proper Scene class inheriting from Scene
**Why**: Manim requires Scene subclass for rendering
**Pattern**: `class SceneN(Scene):`
**Fix**: Ensure class definition matches pattern

### 6. Animation Validation
**Check**: No empty `self.play()` calls
**Why**: Empty play() calls cause runtime errors
**Failure**: `self.play()` with no arguments
**Fix**: Add animation arguments: `self.play(Create(mobject))`

### 7. Timing Validation
**Check**: Scene includes `self.wait()` calls for timing
**Why**: Animations need pacing; continuous play() chains look wrong
**Failure**: Scene has self.play() but no self.wait()
**Fix**: Add self.wait() between animation sequences

### 8. Placeholder Detection
**Check**: No TODO/FIXME in construct() body
**Why**: Placeholder code indicates incomplete implementation
**Fix**: Complete implementation, remove placeholders

## Self-Heal Loop Optimization

### Features

#### 1. Early Termination
Detects when scene file stops changing between repair attempts.
- Computes SHA256 hash of scene file after each attempt
- Terminates if hash unchanged (no progress made)
- Prevents infinite loops on unfixable issues

#### 2. Exponential Backoff
Applies increasing delays between retry attempts.
- Base delay: configurable (default 2 seconds)
- Formula: `base^(attempt-1)` seconds
- Cap: 16 seconds maximum
- Reduces API hammering and gives agent processing time

#### 3. Configurable Limits
Tunable parameters via environment variables:
```bash
# Maximum retry attempts (default: 15)
export SCENE_QC_MAX_ATTEMPTS=15

# Backoff base in seconds (default: 2)
export SCENE_QC_BACKOFF_BASE=2
```

#### 4. Hash-Based Convergence Detection
Tracks scene file state:
- Stores hash in `.scene_N_hash.txt`
- Compares hash before/after repair
- Detects no-change condition
- Provides early feedback on convergence failure

### Backoff Schedule Example

With `SCENE_QC_BACKOFF_BASE=2`:

| Attempt | Backoff Delay | Cumulative Time |
|---------|---------------|------------------|
| 1       | 0s (1st try)  | 0s               |
| 2       | 1s (2^0)      | 1s               |
| 3       | 2s (2^1)      | 3s               |
| 4       | 4s (2^2)      | 7s               |
| 5       | 8s (2^3)      | 15s              |
| 6       | 16s (2^4)     | 31s              |
| 7+      | 16s (capped)  | 31s + 16s×(n-6)  |

## Configuration

### Environment Variables

```bash
# Scene QC retry limit
SCENE_QC_MAX_ATTEMPTS=15

# Exponential backoff base (seconds)
SCENE_QC_BACKOFF_BASE=2

# Enable/disable semantic validation
ENABLE_SEMANTIC_VALIDATION=1
```

### .env File Example

```bash
# Increase retry limit for complex scenes
SCENE_QC_MAX_ATTEMPTS=20

# Slower backoff for rate-limited APIs
SCENE_QC_BACKOFF_BASE=3
```

## Integration Points

### build_video.sh

1. **Initialization** (line ~30)
   - Load configuration variables
   - Export to environment

2. **Helper Sourcing** (line ~110)
   - Source `scene_validation.sh`
   - Check availability of validation functions

3. **scene_qc Phase** (main integration point)
   - Run `validate_scene_files_consistency()`
   - Run `validate_scene_semantics()` for current scene
   - On failure: invoke `self_heal_scene_with_optimization()`
   - On success: proceed to render test

### Validation Flow

```
scene_qc phase start
  ↓
validate_scene_files_consistency()
  ├─ success → continue
  └─ failure → log warning, continue
  ↓
validate_scene_semantics(scene_N)
  ├─ success → proceed to render test
  └─ failure → self_heal_scene_with_optimization()
      ├─ healed → proceed to render test
      └─ max attempts → error phase
```

## Troubleshooting

### Validation Keeps Failing

**Symptom**: Scene fails validation repeatedly
**Check**:
1. Review `.scene_validation_N.log` for specific issues
2. Check if hash is changing (`.scene_N_hash.txt`)
3. Verify agent has write access to scene file
4. Review `build.log` for repair attempt details

### Self-Heal Not Converging

**Symptom**: Hits max attempts without fixing
**Causes**:
1. Agent making same mistake repeatedly
2. Structural issue preventing valid fix
3. Conflicting requirements in prompts

**Solutions**:
1. Increase `SCENE_QC_MAX_ATTEMPTS`
2. Review repair prompt for clarity
3. Check if validation requirements are achievable
4. Manual intervention: fix scene file directly

### Validation False Positives

**Symptom**: Valid scene marked as failing
**Check**:
1. Review validation logic in `scene_validation.sh`
2. Check for overly strict regex patterns
3. Verify scene follows expected patterns

**Workaround**:
```bash
# Temporarily disable semantic validation
export ENABLE_SEMANTIC_VALIDATION=0
```

### Hash Not Changing

**Symptom**: Early termination after 2 attempts
**Meaning**: Agent not modifying scene file
**Causes**:
1. Agent thinks scene is already correct
2. Agent doesn't understand repair instructions
3. File permission issue

**Debug**:
```bash
# Check hash file
cat projects/my_video/.scene_0_hash.txt

# Check scene file modification time
ls -l projects/my_video/scenes/scene_0.py

# Check agent has write permission
touch projects/my_video/scenes/scene_0.py
```

## Examples

### Valid Scene Structure

```python
from manim import *

narration_text = "This scene demonstrates a circle transformation."

class Scene0(Scene):
    def construct(self):
        # Create mobjects
        circle = Circle()
        square = Square()
        
        # Animate
        self.play(Create(circle))
        self.wait(1)
        self.play(Transform(circle, square))
        self.wait(2)
```

✅ **Passes all checks**:
- Valid syntax
- Non-empty narration_text
- Substantive construct() body
- Proper imports
- Valid Scene class
- No empty play() calls
- Has self.wait() timing
- No TODO placeholders

### Common Validation Failures

#### Empty construct()

```python
class Scene0(Scene):
    def construct(self):
        pass  # ❌ Empty body
```

**Fix**:
```python
class Scene0(Scene):
    def construct(self):
        title = Text("My Title")
        self.play(Write(title))
        self.wait(2)
```

#### Missing narration_text

```python
from manim import *

# ❌ No narration_text assignment

class Scene0(Scene):
    def construct(self):
        ...
```

**Fix**:
```python
from manim import *

narration_text = "Actual narration content here."  # ✅

class Scene0(Scene):
    def construct(self):
        ...
```

#### No timing

```python
def construct(self):
    self.play(Create(obj1))
    self.play(FadeIn(obj2))  # ❌ No wait() between
    self.play(Transform(obj1, obj2))
    # ❌ No final wait
```

**Fix**:
```python
def construct(self):
    self.play(Create(obj1))
    self.wait(1)  # ✅ Pause after create
    self.play(FadeIn(obj2))
    self.wait(0.5)  # ✅ Brief pause
    self.play(Transform(obj1, obj2))
    self.wait(2)  # ✅ Final pause
```

## Performance Impact

### Validation Overhead

- **Semantic validation**: ~0.5-1 second per scene
- **Hash computation**: ~0.1 second per attempt
- **Backoff delays**: Configurable (default: 2^n seconds)

### Benefits

- **Reduced render failures**: Catch issues before expensive render
- **Faster convergence**: Early termination saves wasted attempts
- **Better diagnostics**: Specific validation failure messages
- **API efficiency**: Backoff reduces rate limit issues

## Future Enhancements

1. **Semantic depth analysis**: Detect trivial animations (single object)
2. **Cross-scene consistency**: Validate transitions between scenes
3. **Narration-animation sync**: Verify timing matches narration length
4. **Manim version compatibility**: Automatic API version checks
5. **Custom validation rules**: User-defined validation plugins
6. **Validation caching**: Skip re-validation of unchanged scenes

## See Also

- [AGENTS.md](../AGENTS.md) - Agent behavior guidelines
- [scripts/scene_validation.sh](../scripts/scene_validation.sh) - Validation implementation
- [prompts/scene_fix_prompt.md](../prompts/scene_fix_prompt.md) - Repair prompt
- [prompts/phase_build_scenes.md](../prompts/phase_build_scenes.md) - Build scenes guidance
