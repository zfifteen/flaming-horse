# Scene QC Validation Gate - Verification Guide

## Overview

This document provides verification steps for the scene_qc validation gate enhancement that addresses corruption and missing report issues.

## What Was Fixed

### Problem 1: Missing or Empty `scene_qc_report.md`
**Before**: QC could complete without producing a report, causing phase to fail with unclear error.

**After**: Report validation now includes:
- Check for file existence
- Check for non-zero size
- Explicit error message requiring report creation
- Automatic rollback if report is missing

### Problem 2: QC Edits Introduce Syntax Errors
**Before**: QC agent could corrupt scene files (e.g., double-escaped `\\n` sequences), and corrupted files would be committed.

**After**: Post-QC syntax validation gate:
- All scene files validated with `python3 -m py_compile`
- Syntax errors detected before phase advancement
- Corrupted files automatically rolled back
- Clear error reporting showing which files failed

### Problem 3: No Recovery Mechanism
**Before**: Corrupted files required manual intervention to fix.

**After**: Automatic backup/rollback:
- Pre-QC backups created (`.pre_qc` extension)
- Rollback triggered on: agent failure, missing report, syntax errors
- All files restored atomically
- Backups cleaned up on success

## Verification Steps

### 1. Test Rollback Mechanism

Run the automated test:
```bash
cd /path/to/flaming-horse
bash tests/test_scene_qc_rollback.sh
```

**Expected output**:
```
=== ✓ All tests passed ===
The rollback mechanism works correctly:
  - Backups are created before QC
  - Corrupted files can be detected
  - Files can be restored from backup
  - Restored files are valid
```

### 2. Manual Integration Test

Create a test project and verify the full workflow:

```bash
# Set up test project
cd /path/to/test-projects
mkdir test_qc_validation
cd test_qc_validation

# Create minimal project_state.json
cat > project_state.json <<'JSON'
{
  "project_name": "test_qc_validation",
  "phase": "scene_qc",
  "scenes": [
    {
      "id": "scene_01",
      "file": "scene_01.py",
      "status": "built"
    }
  ],
  "flags": {"needs_human_review": false}
}
JSON

# Create a valid scene file
cat > scene_01.py <<'PYTHON'
from manim import *
from manim_voiceover_plus import VoiceoverScene

class Scene01(VoiceoverScene):
    def construct(self):
        title = Text("Test", font_size=48)
        title.move_to(UP * 3.8)
        self.play(Write(title))
        self.wait(1)
PYTHON

# Run QC phase (this will call the agent)
bash /path/to/flaming-horse/scripts/build_video.sh --project-dir "$(pwd)"
```

### 3. Verify Backup Creation

During QC execution, check that backups are created:

```bash
# In project directory while QC is running
ls -la *.pre_qc
# Should show: scene_01.py.pre_qc, scene_02.py.pre_qc, etc.
```

### 4. Verify Syntax Validation

Check the build log for validation output:

```bash
tail -f build.log
```

**Expected log entries**:
```
→ Creating pre-QC backups...
  Backed up 3 scene files
🧪 Running scene QC pass...
[... QC agent output ...]
→ Validating Python syntax of QC-edited scene files...
  ✓ Syntax valid: scene_01.py
  ✓ Syntax valid: scene_02.py
  ✓ Syntax valid: scene_03.py
→ QC validation passed. Removing backups...
✓ Scene QC complete: 3 files validated, scene_qc_report.md
```

### 5. Test Corruption Detection

Manually corrupt a scene file after QC to verify detection:

```bash
# After QC creates backups but before validation
echo "syntax error here" >> scene_01.py

# The validation will catch this and trigger rollback
```

**Expected log output**:
```
→ Validating Python syntax of QC-edited scene files...
  ✗ Syntax error in: scene_01.py
SyntaxError in scene_01.py:15:0: invalid syntax
  Rolling back all scene files to pre-QC state...
  ↺ Restored: scene_01.py
  ↺ Restored: scene_02.py
❌ Scene QC failed validation. Corrupted files rolled back.
```

### 6. Verify Phase Does Not Advance on Failure

Check `project_state.json` after a failed QC:

```bash
cat project_state.json | grep '"phase"'
```

**Expected**: Phase remains `"scene_qc"` (not advanced to `precache_voiceovers`)

### 7. Verify Error Logging

Check that errors go to both `build.log` and `errors.log`:

```bash
# Stderr should be captured in errors.log
grep "QC introduced syntax errors" errors.log

# Should also be in build.log
grep "QC introduced syntax errors" build.log
```

## Success Criteria

All of the following must be true:

- ✅ **Backup creation**: `.pre_qc` files created before QC runs
- ✅ **Report validation**: Missing/empty report triggers rollback
- ✅ **Syntax validation**: All scene files checked with `py_compile`
- ✅ **Corruption detection**: Syntax errors caught and reported
- ✅ **Atomic rollback**: All files restored if any fail validation
- ✅ **Cleanup**: Backups removed on success
- ✅ **Phase control**: Phase only advances when validation passes
- ✅ **Error logging**: Failures logged to both build.log and errors.log
- ✅ **Clear messages**: User knows exactly which files failed and why

## Common Test Scenarios

### Scenario A: QC Agent Crashes
- **Input**: Agent fails with non-zero exit code
- **Expected**: Backups restored, phase remains `scene_qc`
- **Log**: "Scene QC agent failed with exit code: N"

### Scenario B: Missing Report
- **Input**: Agent completes but doesn't create `scene_qc_report.md`
- **Expected**: Backups restored, phase remains `scene_qc`
- **Log**: "scene_qc_report.md missing or empty after scene QC"

### Scenario C: Corrupted Scene Files
- **Input**: Agent edits introduce syntax errors (e.g., `\\n` instead of `\n`)
- **Expected**: Errors detected, backups restored, phase remains `scene_qc`
- **Log**: "QC introduced syntax errors in N file(s): file1.py file2.py"

### Scenario D: Successful QC
- **Input**: Agent produces valid edits and report
- **Expected**: Backups removed, phase advances to `precache_voiceovers`
- **Log**: "Scene QC complete: N files validated, scene_qc_report.md"

## Troubleshooting

### Backups Not Created
**Symptom**: No `.pre_qc` files in project directory

**Check**:
```bash
# Verify scene files exist in project_state.json
cat project_state.json | grep '"file"'

# Check build log for backup creation
grep "Creating pre-QC backups" build.log
```

### Syntax Validation Skipped
**Symptom**: Corrupted files not detected

**Check**:
```bash
# Verify scene_python_syntax_ok function exists
grep -A 10 "scene_python_syntax_ok()" scripts/build_video.sh

# Test function directly
cd project_dir
source ../scripts/build_video.sh
scene_python_syntax_ok "scene_01.py"
echo $?  # Should be 0 for valid, 1 for invalid
```

### Rollback Not Triggered
**Symptom**: Corrupted files not restored

**Check**:
```bash
# Verify backup files exist
ls -la *.pre_qc

# Check if syntax validation ran
grep "Validating Python syntax" build.log

# Check if rollback logic triggered
grep "Rolling back all scene files" build.log
```

## Related Documentation

- `docs/SCENE_QC_AGENT_PROMPT.md` - Agent instructions (updated with escape prevention)
- `scripts/build_video.sh:handle_scene_qc()` - Implementation (lines 1696-1883)
- `tests/test_scene_qc_rollback.sh` - Automated test

## Changelog

**2026-02-15**: Initial validation gate implementation
- Added pre-QC backup mechanism
- Added post-QC syntax validation
- Added automatic rollback on failure
- Enhanced error messages and logging
- Updated agent prompt to prevent escape corruption
