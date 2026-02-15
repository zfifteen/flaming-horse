# Scene QC Phase Fix - Complete Solution

## Problem Statement Response

This document provides the complete solution to the scene_qc phase failures as requested in the issue.

---

## 1. Findings

### Root Cause Analysis

#### Issue 1: Missing `scene_qc_report.md`

**Cause**: 
- The QC agent could complete execution (exit code 0) without producing the required report
- Report check existed but didn't trigger recovery mechanism
- Project would remain stuck in `scene_qc` phase with `needs_human_review: true`

**Evidence**:
```bash
# scripts/build_video.sh:1805-1808 (before fix)
if [[ ! -s "scene_qc_report.md" ]]; then
  echo "❌ scene_qc_report.md missing or empty after scene QC" | tee -a "$LOG_FILE" >&2
  return 1  # ← No rollback, files remain in potentially corrupted state
fi
```

#### Issue 2: Invalid `\\n` Escape Sequences

**Cause**: 
- LLM-based text patching can introduce double-escaped sequences when editing strings
- No post-QC syntax validation to catch corruption
- Corrupted files would advance to next phase, causing render failures

**Example Corruption**:
```python
# BEFORE QC (valid):
text = "Hello\nWorld"  # \n = newline character

# AFTER QC (broken):
text = "Hello\\nWorld"  # \\n = literal backslash + 'n'
```

**Evidence**:
- Problem statement: "QC edits introduce invalid literal `\\n` sequences into scene files"
- Files affected: `2.py`, `4.py`, `6.py`
- No syntax checking after QC edits in original code

#### Issue 3: No Recovery Path

**Cause**:
- No backups created before QC modifications
- No rollback mechanism on validation failure
- Required manual git operations or file restoration

---

## 2. Patch Plan

### Strategy: 5-Step Validation Gate

Implement a comprehensive validation pipeline with automatic recovery:

```
Pre-QC → QC Agent → Report Check → Syntax Check → Success/Rollback
  ↓         ↓           ↓              ↓              ↓
Backup   Edits       Validate       Validate       Cleanup/Restore
```

### Implementation Overview

**Component**: `scripts/build_video.sh:handle_scene_qc()`

**Changes**:
1. Create `.pre_qc` backups of all scene files
2. Run QC agent (existing code)
3. Validate report exists and is non-empty (enhanced with rollback)
4. Validate Python syntax of all scene files (new gate)
5. Rollback all files if any validation fails OR cleanup backups on success

**Additional Changes**:
- Update `docs/SCENE_QC_AGENT_PROMPT.md` to prevent escape corruption
- Create automated test for rollback mechanism
- Fix outdated test expectations

---

## 3. Exact Diffs

### Change 1: `scripts/build_video.sh`

**Location**: Lines 1737-1882 (enhanced `handle_scene_qc` function)

**Key additions** (87 lines total):

```bash
# STEP 1: Create backups (lines 1737-1748)
echo "→ Creating pre-QC backups..." | tee -a "$LOG_FILE"
local -a scene_file_array
mapfile -t scene_file_array <<< "$qc_scene_files"
local backup_count=0
for scene_file in "${scene_file_array[@]}"; do
  if [[ -n "$scene_file" && -f "$scene_file" ]]; then
    cp "$scene_file" "${scene_file}.pre_qc"
    ((backup_count++))
  fi
done

# STEP 2: Enhanced report validation with rollback (lines 1825-1837)
if [[ ! -s "scene_qc_report.md" ]]; then
  echo "❌ scene_qc_report.md missing or empty after scene QC" | tee -a "$LOG_FILE" >&2
  echo "  QC agent must create a report documenting all changes." | tee -a "$LOG_FILE" >&2
  echo "→ Restoring pre-QC backups due to missing report..." | tee -a "$LOG_FILE"
  for scene_file in "${scene_file_array[@]}"; do
    if [[ -n "$scene_file" && -f "${scene_file}.pre_qc" ]]; then
      mv "${scene_file}.pre_qc" "$scene_file"
    fi
  done
  return 1
fi

# STEP 3: Syntax validation gate (lines 1839-1856)
echo "→ Validating Python syntax of QC-edited scene files..." | tee -a "$LOG_FILE"
local syntax_errors=0
local -a corrupted_files=()
for scene_file in "${scene_file_array[@]}"; do
  if [[ -z "$scene_file" || ! -f "$scene_file" ]]; then
    continue
  fi
  
  if ! scene_python_syntax_ok "$scene_file"; then
    ((syntax_errors++))
    corrupted_files+=("$scene_file")
    echo "  ✗ Syntax error in: $scene_file" | tee -a "$LOG_FILE" >&2
    scene_python_syntax_error_excerpt "$scene_file" | tee -a "$LOG_FILE" >&2
  else
    echo "  ✓ Syntax valid: $scene_file" | tee -a "$LOG_FILE"
  fi
done

# STEP 4: Rollback on failure (lines 1858-1870)
if [[ $syntax_errors -gt 0 ]]; then
  echo "❌ QC introduced syntax errors in ${syntax_errors} file(s): ${corrupted_files[*]}" | tee -a "$LOG_FILE" >&2
  echo "  Rolling back all scene files to pre-QC state..." | tee -a "$LOG_FILE"
  for scene_file in "${scene_file_array[@]}"; do
    if [[ -n "$scene_file" && -f "${scene_file}.pre_qc" ]]; then
      mv "${scene_file}.pre_qc" "$scene_file"
      echo "  ↺ Restored: $scene_file" | tee -a "$LOG_FILE"
    fi
  done
  echo "❌ Scene QC failed validation. Corrupted files rolled back." | tee -a "$LOG_FILE" >&2
  return 1
fi

# STEP 5: Cleanup on success (lines 1872-1878)
echo "→ QC validation passed. Removing backups..." | tee -a "$LOG_FILE"
for scene_file in "${scene_file_array[@]}"; do
  if [[ -n "$scene_file" && -f "${scene_file}.pre_qc" ]]; then
    rm -f "${scene_file}.pre_qc"
  fi
done
```

**Also added rollback to existing agent failure path** (lines 1815-1822):
```bash
if [[ $exit_code -ne 0 ]]; then
  echo "❌ Scene QC agent failed with exit code: $exit_code" | tee -a "$LOG_FILE"
  # NEW: Restore backups on agent failure
  echo "→ Restoring pre-QC backups due to agent failure..." | tee -a "$LOG_FILE"
  for scene_file in "${scene_file_array[@]}"; do
    if [[ -n "$scene_file" && -f "${scene_file}.pre_qc" ]]; then
      mv "${scene_file}.pre_qc" "$scene_file"
    fi
  done
  return 1
fi
```

### Change 2: `docs/SCENE_QC_AGENT_PROMPT.md`

**Added new requirement #6** (after line 46):

```markdown
6. **CRITICAL: Prevent escape corruption when editing strings.**
   - When editing Python string literals, preserve single escape sequences (`\n`, `\t`, etc.).
   - Do NOT introduce double-escaped sequences like `\\n` (literal backslash-n).
   - Example CORRECT: `text = "Hello\nWorld"` (actual newline in string).
   - Example WRONG: `text = "Hello\\nWorld"` (literal backslash-n characters).
   - After editing any file, verify all strings compile correctly with `python3 -m py_compile`.
```

**Enhanced validation checklist** (lines 54-60):

```markdown
Validation checklist before finishing:
- [ ] No non-positive waits
- [ ] No run_time below 0.3
- [ ] No obvious timing over-allocation per voiceover block
- [ ] No major overlaps in active scene layout
- [ ] Prior section content cleaned up before new dense section
- [ ] No double-escaped sequences (e.g., `\\n` instead of `\n`) in string literals
- [ ] All edited files compile successfully with `python3 -m py_compile <file>`
```

### Change 3: `scripts/test_update_project_state.py`

**Fixed outdated test expectation** (line 225):

```python
# BEFORE:
require(
    state["phase"] == "final_render",
    "single scene should advance to final_render",
)

# AFTER:
require(
    state["phase"] == "scene_qc",
    "single scene should advance to scene_qc",
)
```

**Rationale**: Pipeline now includes `scene_qc` phase between `build_scenes` and `precache_voiceovers`.

---

## 4. Verification Checklist

### Automated Tests

```bash
# Test 1: Rollback mechanism
cd /path/to/flaming-horse
bash tests/test_scene_qc_rollback.sh
# ✅ Expected: "=== ✓ All tests passed ==="

# Test 2: Python script tests
python3 scripts/test_update_project_state.py
# ✅ Expected: "OK"

python3 scripts/test_generate_scenes_txt.py
# ✅ Expected: "OK"

# Test 3: Bash syntax check
bash -n scripts/build_video.sh
# ✅ Expected: No output (syntax valid)
```

### Integration Tests

#### Test Case A: Successful QC

**Setup**:
```bash
cd test-project
# Ensure project has valid scene files in scene_qc phase
```

**Expected log output**:
```
🧪 Running scene QC pass...
→ Creating pre-QC backups...
  Backed up 3 scene files
[... QC agent runs ...]
→ Validating Python syntax of QC-edited scene files...
  ✓ Syntax valid: scene_01_intro.py
  ✓ Syntax valid: scene_02_main.py
  ✓ Syntax valid: scene_03_conclusion.py
→ QC validation passed. Removing backups...
✓ Scene QC complete: 3 files validated, scene_qc_report.md
```

**Expected state**:
- Phase advances to `precache_voiceovers`
- No `.pre_qc` files remain
- `scene_qc_report.md` exists and has content

#### Test Case B: Missing Report

**Setup**:
```bash
# Simulate agent completing without creating report
# (e.g., agent error or misconfiguration)
```

**Expected log output**:
```
❌ scene_qc_report.md missing or empty after scene QC
  QC agent must create a report documenting all changes.
→ Restoring pre-QC backups due to missing report...
```

**Expected state**:
- Phase remains `scene_qc`
- Scene files restored from backups
- No `.pre_qc` files remain (moved back to originals)
- Exit code 1

#### Test Case C: Syntax Corruption

**Setup**:
```bash
# Simulate QC introducing syntax errors
# (e.g., double-escaped \n sequences)
```

**Expected log output**:
```
→ Validating Python syntax of QC-edited scene files...
  ✗ Syntax error in: scene_02_main.py
SyntaxError in scene_02_main.py:42:15: invalid syntax
  Rolling back all scene files to pre-QC state...
  ↺ Restored: scene_01_intro.py
  ↺ Restored: scene_02_main.py
  ↺ Restored: scene_03_conclusion.py
❌ Scene QC failed validation. Corrupted files rolled back.
```

**Expected state**:
- Phase remains `scene_qc`
- All scene files restored to pre-QC state
- No `.pre_qc` files remain
- Exit code 1

#### Test Case D: Agent Crash

**Setup**:
```bash
# Simulate agent failure (non-zero exit code)
```

**Expected log output**:
```
❌ Scene QC agent failed with exit code: 1
→ Restoring pre-QC backups due to agent failure...
```

**Expected state**:
- Phase remains `scene_qc`
- Scene files restored from backups
- Exit code 1

### Success Criteria Summary

All of the following must be verified:

- ✅ **Backup creation**: `.pre_qc` files created before QC runs
- ✅ **Report validation**: Missing/empty report triggers rollback
- ✅ **Syntax validation**: `python3 -m py_compile` runs on all scene files
- ✅ **Corruption detection**: Syntax errors caught and reported with file/line info
- ✅ **Atomic rollback**: All files restored if any validation fails
- ✅ **Cleanup**: Backups removed on success
- ✅ **Phase control**: Phase only advances when all validations pass
- ✅ **Error logging**: Failures logged to both `build.log` and `errors.log`
- ✅ **Clear messages**: User knows exactly which files failed and why
- ✅ **No side effects**: Other phases and functionality unaffected

### Commands to Run

From the project directory experiencing QC failures:

```bash
# 1. Verify the fix is applied
cd /path/to/flaming-horse
git log --oneline -3
# Should show commits related to scene_qc validation gate

# 2. Check the enhanced function
grep -A 5 "Creating pre-QC backups" scripts/build_video.sh
# Should show the backup creation code

# 3. Run automated tests
bash tests/test_scene_qc_rollback.sh
python3 scripts/test_update_project_state.py

# 4. Run on failing project
cd /path/to/failing-project
bash /path/to/flaming-horse/scripts/build_video.sh --project-dir "$(pwd)"

# 5. Check logs for validation steps
grep -E "(Creating pre-QC|Validating Python|Syntax valid|Rolling back)" build.log

# 6. Verify phase state
cat project_state.json | jq '.phase, .flags.needs_human_review'
# On success: "precache_voiceovers", false
# On failure: "scene_qc", true (but files are safe)
```

---

## What Cannot Recur

### Problem: Missing Report
**Prevention**:
- Report check now triggers rollback
- Clear error message explains requirement
- Files restored to working state

### Problem: Escape Corruption
**Prevention**:
- Syntax validation gate catches all Python errors
- Agent prompt explicitly warns against double-escaping
- Validation checklist includes compile step

### Problem: No Recovery
**Prevention**:
- Automatic backups before QC
- Atomic rollback on any failure
- No manual intervention needed

### Enforcement Mechanisms

1. **Pre-QC Snapshot**: Always creates backups (logged)
2. **Post-QC Gates**: Multiple validation layers (report + syntax)
3. **Fail-Safe Rollback**: Triggered on agent failure, missing report, or syntax errors
4. **Deterministic Scripts**: Validation runs in build script, not agent
5. **Clear Logging**: Every step logged with ✓/✗ indicators

---

## Files Changed

### Production Code
- `scripts/build_video.sh` (+87 lines in `handle_scene_qc`)
- `docs/SCENE_QC_AGENT_PROMPT.md` (+8 lines)

### Tests
- `scripts/test_update_project_state.py` (2 lines changed)
- `tests/test_scene_qc_rollback.sh` (new file, 143 lines)

### Documentation
- `docs/SCENE_QC_FIX_ANALYSIS.md` (new file)
- `docs/SCENE_QC_VALIDATION_VERIFICATION.md` (new file)

**Total**: 2 files modified, 3 files added, 240+ new lines

---

## Impact

### Fixes
1. ✅ Missing `scene_qc_report.md` now triggers safe rollback
2. ✅ Syntax corruption (including `\\n`) detected and prevented
3. ✅ Automatic recovery from QC failures
4. ✅ Clear error messages identifying exact issues

### Preserves
1. ✅ Agent autonomy (agent still does QC work)
2. ✅ Infrastructure separation (scripts handle validation)
3. ✅ stderr to `errors.log` (unchanged)
4. ✅ Existing tests and functionality

### No Breaking Changes
- All changes are additive (new validation layers)
- Existing successful QC runs unaffected
- Only difference: backups created and cleaned up (transparent)

---

## Related Documentation

For complete details, see:
- `docs/SCENE_QC_FIX_ANALYSIS.md` - Root cause analysis and patch details
- `docs/SCENE_QC_VALIDATION_VERIFICATION.md` - Complete verification guide
- `docs/SCENE_QC_AGENT_PROMPT.md` - Updated agent instructions
- `tests/test_scene_qc_rollback.sh` - Automated rollback test

---

**Status**: ✅ Complete and ready for merge

All requirements from the problem statement addressed:
1. ✅ Root-cause analysis provided
2. ✅ Concrete fixes implemented in build script and prompts
3. ✅ Minimal patch with exact diffs documented
4. ✅ Verification steps and success criteria defined
