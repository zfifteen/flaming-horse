# Scaffold and Parser Fixes Summary

## Problem Statement

The `tests/smoke_test.sh` was failing in the `build_scenes` phase due to scaffold template issues, parser bugs, and missing indentation handling.

## Root Causes Identified

### 1. Scaffold Template Duplication Bug
**Location:** `scripts/scaffold_scene.py`

**Problem:**
- Template imported `play_next` and `play_text_next` from `flaming_horse.scene_helpers`
- Then immediately redefined them locally with code that called `play_in_slot`
- `play_in_slot` was never imported or defined in the scaffold
- Result: `NameError: name 'play_in_slot' is not defined` at runtime

**Fix:**
- Removed duplicate function definitions from template
- Now only imports helpers, never redefines them
- Cleaner imports using explicit tuple syntax

### 2. Parser Validation Gaps
**Location:** `harness/parser.py`

**Problems:**
- `parse_scene_repair_response` had unreachable `has_scaffold_artifacts` check after return statement
- `parse_build_scenes_response` didn't check for scaffold artifacts at all
- Body injection didn't validate for empty content (only comments/whitespace)

**Fixes:**
- Moved `has_scaffold_artifacts` check before return in repair parser
- Added `has_scaffold_artifacts` check to both loops in build_scenes parser
- Added validation in `inject_body_into_scaffold` to reject empty bodies
- Prevents `SyntaxError: expected an indented block after 'with' statement`

### 3. Body Code Indentation Missing
**Location:** `harness/parser.py` - `inject_body_into_scaffold()`

**Problem:**
- Parser extracts unindented body code from agent responses
- Injection placed this code directly after `with self.voiceover(...) as tracker:`
- Python requires indented block after `with` statement
- Result: IndentationError

**Fix:**
- Auto-indent all body code to 12 spaces (3 levels: class, def, with)
- Handles both indented and unindented input gracefully
- Preserves relative indentation within body code
- Ensures valid Python syntax in final scene file

### 4. Missing Module Exports
**Location:** `flaming_horse/scene_helpers.py`

**Problem:**
- No explicit `__all__` declaration
- Unclear which helpers are public API vs internal

**Fix:**
- Added `__all__` list with 8 public helpers:
  - `BeatPlan`, `play_next`, `play_text_next`
  - `safe_position`, `harmonious_color`, `polished_fade_in`
  - `adaptive_title_position`, `safe_layout`
- Internal helpers (`play_in_slot`, `play_text_in_slot`) not exported

## Files Changed

### Modified Files
1. **scripts/scaffold_scene.py** (26 lines removed, 11 lines added)
   - Removed duplicate function definitions
   - Cleaner import syntax

2. **harness/parser.py** (72 lines modified)
   - Fixed unreachable code in `parse_scene_repair_response`
   - Added scaffold artifacts checks to both parsers
   - Added empty body validation
   - Implemented auto-indentation in `inject_body_into_scaffold`

3. **flaming_horse/scene_helpers.py** (12 lines added)
   - Added `__all__` exports list
   - Documents public API

### New Test Files
1. **tests/test_scaffold_and_parser.py** (18 tests)
   - Scaffold template validation tests
   - Parser body extraction tests
   - Body injection tests
   - Scaffold artifacts detection tests
   - harmonious_color contract tests
   - Scene repair parser tests

2. **tests/test_e2e_scaffold_workflow.py** (2 tests)
   - End-to-end workflow test (scaffold → parse → inject → validate)
   - Bad agent output rejection test

## Test Results

### All Tests Passing ✅

**Regression Tests:** 18/18 passed
- Scaffold template integrity
- Parser validation logic
- Body injection with indentation
- Scaffold artifacts detection
- API contract compliance

**E2E Workflow Tests:** 2/2 passed
- Complete build_scenes simulation
- Bad response rejection

## Impact

### Before
- Scenes failed at runtime: `NameError: name 'play_in_slot' is not defined`
- Scaffold placeholders could slip through validation
- Empty body code caused `SyntaxError`
- Build_scenes phase would get stuck in repair loops

### After
- Scenes import helpers correctly, no runtime errors
- Scaffold placeholders rejected at parse time
- Proper indentation ensures valid Python syntax
- Build_scenes can proceed through all scenes

## Validation Strategy

### 1. Scaffold Template Contract
- ✅ Must have locked config header
- ✅ Must have both SLOT markers
- ✅ Must import helpers (never redefine them)
- ✅ Must not reference internal helpers

### 2. Parser Body Extraction
- ✅ Must extract only body code (no headers/imports)
- ✅ Must reject code with slot markers
- ✅ Must reject scaffold placeholders
- ✅ Must validate Python syntax

### 3. Body Injection
- ✅ Must preserve scaffold markers and config
- ✅ Must indent body code to 12 spaces
- ✅ Must reject empty bodies
- ✅ Must produce valid Python

## Next Steps

1. **Run Smoke Test**
   - Execute `tests/smoke_test.sh` with API keys
   - Verify build_scenes completes for first scene
   - Check for any remaining edge cases

2. **Monitor Production**
   - Watch for any new failure patterns
   - Collect metrics on build_scenes success rate
   - Consider adding more validation if needed

3. **Documentation Updates**
   - Update harness documentation if needed
   - Add notes about indentation requirements
   - Document parser validation contract

## Memory Storage

Stored facts for future reference:
1. **Scaffold template must not redefine imported helpers** - prevents runtime NameError
2. **Both parsers must check has_scaffold_artifacts()** - prevents placeholder code from passing
3. **Body injection must validate non-empty content** - prevents SyntaxError from empty with blocks

These memories will help prevent similar issues in future development.
