#!/usr/bin/env bash
# Scene validation helper functions for build_video.sh
# Provides semantic validation and self-heal optimization

set -euo pipefail

# Configuration
SCENE_QC_MAX_ATTEMPTS="${SCENE_QC_MAX_ATTEMPTS:-15}"
SCENE_QC_BACKOFF_BASE="${SCENE_QC_BACKOFF_BASE:-2}"

# Semantic validation for scene files
# Returns 0 if valid, 1 if issues detected
validate_scene_semantics() {
  local project_dir="$1"
  local scene_index="$2"
  local scene_file="${project_dir}/scenes/scene_${scene_index}.py"
  local validation_log="${project_dir}/.scene_validation_${scene_index}.log"
  
  echo "🔍 Running semantic validation on scene ${scene_index}..." | tee -a "${project_dir}/build.log"
  
  # Check if scene file exists
  if [[ ! -f "$scene_file" ]]; then
    echo "❌ Scene file missing: $scene_file" | tee -a "$validation_log"
    return 1
  fi
  
  local issues_found=0
  
  # Run Python-based semantic checks
  python3 - "$scene_file" "$validation_log" <<'PYVALIDATE'
import ast
import sys
import re
from pathlib import Path

scene_file = Path(sys.argv[1])
log_file = Path(sys.argv[2])
issues = []

try:
    content = scene_file.read_text(encoding="utf-8")
    
    # Check 1: Parse for syntax errors
    try:
        tree = ast.parse(content, filename=str(scene_file))
    except SyntaxError as e:
        issues.append(f"Syntax error at line {e.lineno}: {e.msg}")
        print(f"❌ Syntax error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check 2: Validate narration_text presence and non-empty
    narration_match = re.search(r'narration_text\s*=\s*["\']([^"\']*)["\']', content)
    if not narration_match:
        issues.append("Missing narration_text assignment")
    elif not narration_match.group(1).strip():
        issues.append("Empty narration_text (no content)")
    
    # Check 3: Validate construct() method exists and has body
    construct_pattern = r'def\s+construct\(self\):(.*?)(?=\n(?:def|class|\Z))'
    construct_match = re.search(construct_pattern, content, re.DOTALL)
    if not construct_match:
        issues.append("Missing construct() method")
    else:
        construct_body = construct_match.group(1).strip()
        # Check for empty or only-pass construct
        if not construct_body or construct_body == "pass":
            issues.append("Empty construct() method body")
        # Check for placeholder comments
        elif "# TODO" in construct_body or "# FIXME" in construct_body:
            issues.append("construct() contains TODO/FIXME placeholders")
    
    # Check 4: Validate imports (basic Manim imports present)
    if "from manim import" not in content and "import manim" not in content:
        issues.append("Missing Manim imports")
    
    # Check 5: Scene class definition
    if not re.search(r'class\s+\w+Scene\w*\(Scene\):', content):
        issues.append("Missing proper Scene class definition")
    
    # Check 6: Detect common runtime issues
    # - Empty self.play() calls
    if re.search(r'self\.play\(\s*\)', content):
        issues.append("Empty self.play() call detected")
    # - Missing self.wait() after animations
    if "self.play(" in content and "self.wait(" not in content:
        issues.append("No self.wait() calls found (animations need timing)")
    
    # Write findings
    if issues:
        log_file.write_text("\n".join(issues), encoding="utf-8")
        for issue in issues:
            print(f"⚠️  {issue}", file=sys.stderr)
        sys.exit(1)
    else:
        log_file.write_text("✅ All semantic checks passed", encoding="utf-8")
        print("✅ Scene passed semantic validation")
        sys.exit(0)
        
except Exception as e:
    print(f"❌ Validation error: {e}", file=sys.stderr)
    sys.exit(1)
PYVALIDATE
  
  local exit_code=$?
  if [[ $exit_code -ne 0 ]]; then
    echo "❌ Semantic validation failed for scene ${scene_index}" | tee -a "${project_dir}/build.log"
    if [[ -f "$validation_log" ]]; then
      echo "Issues found:" | tee -a "${project_dir}/build.log"
      cat "$validation_log" | tee -a "${project_dir}/build.log"
    fi
    return 1
  fi
  
  echo "✅ Scene ${scene_index} passed semantic validation" | tee -a "${project_dir}/build.log"
  return 0
}

# Optimized self-heal loop with early termination
# Returns 0 if scene healed, 1 if max attempts reached
self_heal_scene_with_optimization() {
  local project_dir="$1"
  local scene_index="$2"
  local scene_file="${project_dir}/scenes/scene_${scene_index}.py"
  local hash_file="${project_dir}/.scene_${scene_index}_hash.txt"
  
  echo "🔄 Starting optimized self-heal loop for scene ${scene_index}..." | tee -a "${project_dir}/build.log"
  
  local attempt=0
  local max_attempts="$SCENE_QC_MAX_ATTEMPTS"
  local previous_hash=""
  
  while [[ $attempt -lt $max_attempts ]]; do
    attempt=$((attempt + 1))
    echo "Attempt ${attempt}/${max_attempts}" | tee -a "${project_dir}/build.log"
    
    # Compute current scene file hash
    local current_hash
    if [[ -f "$scene_file" ]]; then
      current_hash=$(sha256sum "$scene_file" | awk '{print $1}')
    else
      current_hash="missing"
    fi
    
    # Early termination: No changes detected
    if [[ -n "$previous_hash" && "$current_hash" == "$previous_hash" ]]; then
      echo "⚠️  No changes detected between attempts. Terminating early." | tee -a "${project_dir}/build.log"
      return 1
    fi
    
    # Store hash for next iteration
    echo "$current_hash" > "$hash_file"
    previous_hash="$current_hash"
    
    # Run validation
    if validate_scene_semantics "$project_dir" "$scene_index"; then
      echo "✅ Scene ${scene_index} healed after ${attempt} attempt(s)" | tee -a "${project_dir}/build.log"
      rm -f "$hash_file"
      return 0
    fi
    
    # Apply exponential backoff before retry
    if [[ $attempt -lt $max_attempts ]]; then
      local backoff_seconds=$((SCENE_QC_BACKOFF_BASE ** (attempt - 1)))
      # Cap at 16 seconds max
      if [[ $backoff_seconds -gt 16 ]]; then
        backoff_seconds=16
      fi
      echo "⏳ Backing off ${backoff_seconds}s before retry..." | tee -a "${project_dir}/build.log"
      sleep "$backoff_seconds"
    fi
    
    # Invoke repair (would call agent here in actual implementation)
    # This is a placeholder - actual repair happens via phase transition
    echo "🔧 Requesting scene repair..." | tee -a "${project_dir}/build.log"
  done
  
  echo "❌ Scene ${scene_index} failed to heal after ${max_attempts} attempts" | tee -a "${project_dir}/build.log"
  rm -f "$hash_file"
  return 1
}

# Validate scene_files list matches actual files on disk
validate_scene_files_consistency() {
  local project_dir="$1"
  local state_file="${project_dir}/project_state.json"
  
  echo "🔍 Validating scene_files consistency..." | tee -a "${project_dir}/build.log"
  
  python3 - "$state_file" "$project_dir" <<'PYCONSIST'
import json
import sys
from pathlib import Path

state_file = Path(sys.argv[1])
project_dir = Path(sys.argv[2])
scenes_dir = project_dir / "scenes"

try:
    state = json.loads(state_file.read_text(encoding="utf-8"))
    scene_files_in_state = set(state.get("scene_files", []))
    
    # Get actual scene files on disk
    actual_files = set()
    if scenes_dir.exists():
        actual_files = {f.name for f in scenes_dir.glob("scene_*.py")}
    
    # Compare
    missing_in_state = actual_files - scene_files_in_state
    missing_on_disk = scene_files_in_state - actual_files
    
    if missing_in_state:
        print(f"⚠️  Files on disk not in state: {missing_in_state}", file=sys.stderr)
    if missing_on_disk:
        print(f"⚠️  Files in state not on disk: {missing_on_disk}", file=sys.stderr)
    
    if missing_in_state or missing_on_disk:
        sys.exit(1)
    else:
        print("✅ scene_files list consistent with disk")
        sys.exit(0)
        
except Exception as e:
    print(f"❌ Consistency check error: {e}", file=sys.stderr)
    sys.exit(1)
PYCONSIST
  
  if [[ $? -ne 0 ]]; then
    echo "❌ scene_files consistency check failed" | tee -a "${project_dir}/build.log"
    return 1
  fi
  
  return 0
}

export -f validate_scene_semantics
export -f self_heal_scene_with_optimization
export -f validate_scene_files_consistency
