# Scene QC Corruption Fix - Integration Guide

## Problem Statement

The `scene_qc` phase was failing due to:

1. **Missing Report Validation**: No check for `scene_qc_report.md` existence
2. **Escaped Newline Corruption**: QC agent writing literal `\\n` into Python files causing syntax errors
3. **No Syntax Gate**: No post-QC validation of scene file syntax
4. **No Rollback**: Corrupted files would persist with no recovery mechanism

## Solution Overview

**Three-Layer Defense:**

1. **Pre-QC Backup**: Snapshot all scene files before QC runs
2. **Post-QC Syntax Validation**: `python3 -m py_compile` on all scenes
3. **Report Verification**: Check `scene_qc_report.md` exists and is non-empty
4. **Automatic Rollback**: If validation fails, restore backup and flag for review

## Files Modified

### 1. `prompts/scene_qc_prompt.md`

**Changes:**
- Added explicit `scene_qc_report.md` creation requirement
- Added **CRITICAL FILE EDITING RULES** section warning against `\\n` literals
- Provided correct vs incorrect examples

### 2. `scripts/validate_qc_scenes.py` (NEW)

**Purpose:** Deterministic syntax validation of all scene files.

**Usage:**
```bash
python3 scripts/validate_qc_scenes.py /path/to/project
```

**Exit codes:**
- `0`: All scenes compile successfully
- `1`: Syntax errors found (details to stderr)

### 3. `scripts/build_video_qc_patch.sh` (NEW)

**Contains:**
- `backup_scene_files()` - Create timestamped backup
- `restore_scene_files()` - Rollback from backup
- `validate_qc_results()` - Check report + syntax
- `handle_scene_qc_phase()` - Complete QC workflow

## Integration Steps

### Step 1: Backup Current build_video.sh

```bash
cp scripts/build_video.sh scripts/build_video.sh.backup
```

### Step 2: Locate scene_qc Phase Handler

Search for the existing scene_qc phase handler in `scripts/build_video.sh`. It should be in the main loop, likely within a case statement like:

```bash
scene_qc)
  # existing scene_qc code here
  ;;
```

### Step 3: Integrate QC Validation Functions

**Option A: Merge Functions (Recommended)**

1. Open `scripts/build_video.sh`
2. Locate the "Validation Functions" section (after `validate_voiceover_sync`)
3. Add the following functions from `scripts/build_video_qc_patch.sh`:
   - `backup_scene_files()`
   - `restore_scene_files()`
   - `validate_qc_results()`

**Option B: Source the Patch File**

Add near the top of `build_video.sh`:

```bash
source "${SCRIPT_DIR}/build_video_qc_patch.sh"
```

### Step 4: Replace scene_qc Phase Handler

Find the existing `scene_qc)` case in the main loop and replace its contents with the code from `handle_scene_qc_phase()` in the patch file.

**Before:**
```bash
scene_qc)
  # old scene_qc logic
  ;;
```

**After:**
```bash
scene_qc)
  # QC with backup/validate/rollback
  if ! backup_scene_files; then
    echo "✗ Failed to backup scene files" | tee -a "$LOG_FILE" >&2
    continue
  fi
  
  backup_dir="$(cat "${PROJECT_DIR}/.latest_qc_backup")"
  
  # Prepare QC prompt
  scene_files_list=$(python3 - <<PY
import json
with open("${STATE_FILE}", "r") as f:
    state = json.load(f)
for scene in state.get("scenes", []):
    if isinstance(scene, dict) and "file" in scene:
        print(f"  - {scene['file']}")
PY
)
  
  qc_prompt_file="${PROJECT_DIR}/.agent_prompt_scene_qc.md"
  render_template_file \
    "${SCENE_QC_TEMPLATE}" \
    "${qc_prompt_file}" \
    "PROJECT_DIR=${PROJECT_DIR}" \
    "STATE_FILE=${STATE_FILE}" \
    "SCENE_FILES=${scene_files_list}"
  
  # Invoke QC agent
  agent_output_file="${PROJECT_DIR}/.agent_output_scene_qc.jsonl"
  if ! opencode -m "${AGENT_MODEL}" \
    --prompt "${qc_prompt_file}" \
    --file "${STATE_FILE}" \
    --cwd "${PROJECT_DIR}" \
    > "${agent_output_file}" \
    2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2); then
    echo "✗ QC agent failed" | tee -a "$LOG_FILE" >&2
    continue
  fi
  
  # Validate and rollback if needed
  if validate_qc_results; then
    echo "✓ QC validation passed" | tee -a "$LOG_FILE"
    rm -f "${PROJECT_DIR}/.latest_qc_backup"
  else
    echo "✗ QC validation failed - rolling back" | tee -a "$LOG_FILE" >&2
    
    if restore_scene_files "$backup_dir"; then
      python3 - <<PY
import json
from datetime import datetime
with open("${STATE_FILE}", "r") as f:
    state = json.load(f)
state.setdefault("errors", []).append(
    "scene_qc validation failed: syntax errors or missing report. "
    "Scene files restored from backup. Manual inspection required."
)
state.setdefault("flags", {})["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
      echo "⚠️  QC failed. Files restored. Human review needed." | tee -a "$LOG_FILE" >&2
    fi
  fi
  ;;
```

### Step 5: Test the Fix

```bash
# Navigate to failing project
cd /Users/velocityworks/IdeaProjects/flaming-horse-projects/copilot-test-video-2

# Reset phase to retry scene_qc
python3 - <<PY
import json
with open("project_state.json", "r") as f:
    state = json.load(f)
state["phase"] = "scene_qc"
state.setdefault("flags", {})["needs_human_review"] = False
state["errors"] = []
with open("project_state.json", "w") as f:
    json.dump(state, f, indent=2)
PY

# Run build script
../../flaming-horse/scripts/build_video.sh .
```

## Verification Checklist

### Success Criteria

- [ ] `scene_qc_report.md` is created and non-empty
- [ ] All scene files pass `python3 -m py_compile` validation
- [ ] No literal `\\n` sequences in scene Python files
- [ ] `project_state.json` shows `phase: "precache_voiceovers"` (next phase)
- [ ] `needs_human_review: false`

### Failure Behavior (Expected)

If QC produces invalid files:

- [ ] Backup created in `.qc_backup_<timestamp>/`
- [ ] Syntax validation detects errors
- [ ] Scene files automatically restored from backup
- [ ] `needs_human_review: true` in state
- [ ] Error logged with "syntax errors or missing report" message
- [ ] Phase remains `scene_qc`

### Log Inspection

```bash
# Check for backup creation
grep "Backing up scene files" build.log

# Check syntax validation
grep "syntax valid\|SYNTAX ERROR" build.log

# Check report validation
grep "QC report" build.log

# Check rollback (if validation failed)
grep "rolling back\|restored from backup" build.log
```

## Debugging

### If QC Still Produces Corrupted Files

1. **Check prompt was updated:**
   ```bash
   grep "CRITICAL FILE EDITING RULES" prompts/scene_qc_prompt.md
   ```

2. **Manually inspect QC output:**
   ```bash
   cat .agent_prompt_scene_qc.md
   cat .agent_output_scene_qc.jsonl
   ```

3. **Check for literal backslash-n patterns:**
   ```bash
   grep -n '\\n' scene_*.py
   ```

4. **Verify backup exists:**
   ```bash
   ls -ld .qc_backup_*/
   cat .latest_qc_backup
   ```

### If Syntax Validation Fails

1. **Run validation manually:**
   ```bash
   python3 ../../flaming-horse/scripts/validate_qc_scenes.py .
   ```

2. **Check specific scene:**
   ```bash
   python3 -m py_compile scene_01_intro.py
   ```

3. **Inspect corrupted content:**
   ```bash
   cat -A scene_01_intro.py | grep '\\'
   ```

## Rationale

### Why Three Layers?

1. **Backup**: Safety net if agent corrupts files
2. **Report Check**: Ensures agent completed its task
3. **Syntax Validation**: Deterministic Python compilation test

### Why Rollback Instead of Retry?

If QC corrupts files, the issue is likely in:
- Agent's string escaping behavior
- Model hallucination of escape sequences
- Prompt ambiguity

Retrying without human inspection would likely repeat the corruption. Better to:
1. Restore clean state
2. Flag for review
3. Allow human to diagnose root cause

### Why `py_compile` Instead of Import?

- **Deterministic**: Syntax-only check, no side effects
- **Fast**: No module initialization
- **Safe**: Runs in subprocess, isolated from pipeline
- **Precise**: Reports exact syntax errors

## Next Steps

After verifying this fix:

1. Monitor several builds to confirm stability
2. If QC continues to corrupt files, investigate agent model behavior
3. Consider adding pre-QC linting (e.g., `black --check`) for additional safety
4. Add QC retry logic with exponential backoff if agent improves

## Rollback Plan

If this fix causes issues:

```bash
# Restore original build script
cp scripts/build_video.sh.backup scripts/build_video.sh

# Remove new files
rm scripts/validate_qc_scenes.py
rm scripts/build_video_qc_patch.sh

# Revert prompt
git checkout main -- prompts/scene_qc_prompt.md
```
