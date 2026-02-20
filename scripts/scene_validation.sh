#!/usr/bin/env bash
# Scene validation helper functions for build_video.sh
# Provides semantic validation and self-heal optimization

set -euo pipefail

# Configuration
SCENE_QC_MAX_ATTEMPTS="${SCENE_QC_MAX_ATTEMPTS:-15}"
SCENE_QC_BACKOFF_BASE="${SCENE_QC_BACKOFF_BASE:-2}"

resolve_scene_metadata() {
  local project_dir="$1"
  local scene_index="$2"
  local state_file="${project_dir}/project_state.json"

  python3 - "$state_file" "$scene_index" <<'PYSCENEMETA'
import json
import re
import sys
from pathlib import Path


def camel_from_scene_id(scene_id: str) -> str:
    m_simple = re.match(r"^scene_(\d+)$", scene_id)
    if m_simple:
        return f"Scene{m_simple.group(1)}"

    m = re.match(r"^scene_(\d+)_([a-z0-9_]+)$", scene_id)
    if m:
        number = m.group(1)
        slug = m.group(2)
        parts = [p for p in slug.split("_") if p]
        return "Scene" + number + "".join(p.capitalize() for p in parts)

    return "Scene" + "".join(ch for ch in scene_id if ch.isalnum() or ch == "_")


state_path = Path(sys.argv[1])
try:
    idx = int(sys.argv[2])
except (TypeError, ValueError):
    raise SystemExit(f"Invalid scene index: {sys.argv[2]!r}")

if not state_path.exists():
    raise SystemExit(f"project_state.json not found at {state_path}")

with state_path.open(encoding="utf-8") as f:
    state = json.load(f)

scenes = state.get("scenes")
if not isinstance(scenes, list):
    raise SystemExit("No scene list found in project_state.json (expected 'scenes').")

if not (0 <= idx < len(scenes)):
    raise SystemExit(f"Scene index {idx} out of range (have {len(scenes)} scenes).")

entry = scenes[idx]
if not isinstance(entry, dict):
    raise SystemExit(f"Scene entry at index {idx} is not an object.")

scene_id = entry.get("id") or entry.get("scene_id")
if not isinstance(scene_id, str) or not scene_id:
    raise SystemExit(f"Scene ID not found for index {idx}.")

scene_file = entry.get("file")
if not isinstance(scene_file, str) or not scene_file:
    scene_file = f"{scene_id}.py"

scene_class = entry.get("class_name")
if not isinstance(scene_class, str) or not scene_class:
    scene_class = camel_from_scene_id(scene_id)

sys.stdout.write(f"{scene_id}|{scene_file}|{scene_class}")
PYSCENEMETA
}

resolve_scene_path() {
  local project_dir="$1"
  local scene_file="$2"

  if [[ -f "${project_dir}/${scene_file}" ]]; then
    printf '%s\n' "${project_dir}/${scene_file}"
    return 0
  fi

  if [[ -f "${project_dir}/scenes/${scene_file}" ]]; then
    printf '%s\n' "${project_dir}/scenes/${scene_file}"
    return 0
  fi

  return 1
}

compute_file_hash() {
  local file_path="$1"
  python3 - "$file_path" <<'PYHASH'
import hashlib
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    print("missing")
    raise SystemExit(0)

digest = hashlib.sha256(path.read_bytes()).hexdigest()
print(digest)
PYHASH
}

# Semantic validation for scene files
# Returns 0 if valid, 1 if issues detected
validate_scene_semantics() {
  local project_dir="$1"
  local scene_index="$2"
  local scene_meta
  scene_meta="$(resolve_scene_metadata "$project_dir" "$scene_index")" || {
    echo "❌ Could not resolve scene metadata for index ${scene_index}" | tee -a "${project_dir}/build.log"
    return 1
  }

  local scene_id scene_file _scene_class
  IFS='|' read -r scene_id scene_file _scene_class <<< "$scene_meta"
  local scene_path
  scene_path="$(resolve_scene_path "$project_dir" "$scene_file")" || {
    echo "❌ Scene file missing for ${scene_id}: ${scene_file}" | tee -a "${project_dir}/build.log"
    return 1
  }

  local validation_log="${project_dir}/.scene_validation_${scene_id}.log"
  
  echo "🔍 Running semantic validation on ${scene_id} (${scene_file})..." | tee -a "${project_dir}/build.log"
  
  # Run Python-based semantic checks
  python3 - "$scene_path" "$validation_log" <<'PYVALIDATE'
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
    
    # Check 2: Scene must use SCRIPT[...] in voiceover call
    if not re.search(r'with\s+self\.voiceover\(\s*text\s*=\s*SCRIPT\[["\'][^"\']+["\']\]\s*\)\s+as\s+\w+\s*:', content):
        issues.append("Missing voiceover call using SCRIPT[...] narration key")
    
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
    if not re.search(r'class\s+[A-Za-z_][A-Za-z0-9_]*\(\s*VoiceoverScene\s*\)\s*:', content):
        issues.append("Missing proper Scene class definition inheriting VoiceoverScene")
    
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
    echo "❌ Semantic validation failed for ${scene_id}" | tee -a "${project_dir}/build.log"
    if [[ -f "$validation_log" ]]; then
      echo "Issues found:" | tee -a "${project_dir}/build.log"
      cat "$validation_log" | tee -a "${project_dir}/build.log"
    fi
    return 1
  fi
  
  echo "✅ Scene ${scene_id} passed semantic validation" | tee -a "${project_dir}/build.log"
  return 0
}

# Optimized self-heal loop with early termination
# Returns 0 if scene healed, 1 if max attempts reached
self_heal_scene_with_optimization() {
  local project_dir="$1"
  local scene_index="$2"
  local scene_meta
  scene_meta="$(resolve_scene_metadata "$project_dir" "$scene_index")" || {
    echo "❌ Could not resolve scene metadata for index ${scene_index}" | tee -a "${project_dir}/build.log"
    return 1
  }

  local scene_id scene_file scene_class
  IFS='|' read -r scene_id scene_file scene_class <<< "$scene_meta"

  local hash_file="${project_dir}/.scene_${scene_id}_hash.txt"
  local validation_log="${project_dir}/.scene_validation_${scene_id}.log"
  
  echo "🔄 Starting optimized self-heal loop for ${scene_id}..." | tee -a "${project_dir}/build.log"
  
  local attempt=0
  local max_attempts="$SCENE_QC_MAX_ATTEMPTS"
  local previous_hash=""
  
  while [[ $attempt -lt $max_attempts ]]; do
    attempt=$((attempt + 1))
    echo "Attempt ${attempt}/${max_attempts}" | tee -a "${project_dir}/build.log"
    
    local scene_path
    scene_path="$(resolve_scene_path "$project_dir" "$scene_file" || true)"

    # Compute current scene file hash
    local current_hash
    if [[ -n "$scene_path" ]]; then
      current_hash="$(compute_file_hash "$scene_path")"
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
      echo "✅ Scene ${scene_id} healed after ${attempt} attempt(s)" | tee -a "${project_dir}/build.log"
      rm -f "$hash_file"
      return 0
    fi

    local failure_reason="Semantic validation failed"
    if [[ -f "$validation_log" ]]; then
      failure_reason="$(python3 - "$validation_log" <<'PYMSG'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8", errors="replace").strip()
if not text:
    print("Semantic validation failed")
else:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    print("; ".join(lines[:6]))
PYMSG
)"
    fi

    # Invoke repair hook when available
    if command -v invoke_scene_fix_agent >/dev/null 2>&1; then
      echo "🔧 Requesting scene repair via invoke_scene_fix_agent..." | tee -a "${project_dir}/build.log"
      invoke_scene_fix_agent "$scene_id" "$scene_file" "$scene_class" "$failure_reason" "$attempt" || true
    elif command -v scene_repair >/dev/null 2>&1; then
      echo "🔧 Requesting scene repair via scene_repair..." | tee -a "${project_dir}/build.log"
      scene_repair "$project_dir" "$scene_index" || true
    else
      echo "⚠️  No repair hook available; continuing retry loop without auto-repair." | tee -a "${project_dir}/build.log"
    fi
    
    # Apply exponential backoff before retry
    if [[ $attempt -lt $max_attempts ]]; then
      local backoff_seconds=1
      local i
      for ((i = 1; i < attempt; i++)); do
        backoff_seconds=$((backoff_seconds * SCENE_QC_BACKOFF_BASE))
      done
      # Cap at 16 seconds max
      if [[ $backoff_seconds -gt 16 ]]; then
        backoff_seconds=16
      fi
      echo "⏳ Backing off ${backoff_seconds}s before retry..." | tee -a "${project_dir}/build.log"
      sleep "$backoff_seconds"
    fi
    
  done
  
  echo "❌ Scene ${scene_id} failed to heal after ${max_attempts} attempts" | tee -a "${project_dir}/build.log"
  rm -f "$hash_file"
  return 1
}

# Validate project_state scenes list matches actual files on disk
validate_scene_files_consistency() {
  local project_dir="$1"
  local state_file="${project_dir}/project_state.json"
  
  echo "🔍 Validating scenes consistency..." | tee -a "${project_dir}/build.log"
  
  python3 - "$state_file" "$project_dir" <<'PYCONSIST'
import json
import sys
from pathlib import Path

state_file = Path(sys.argv[1])
project_dir = Path(sys.argv[2])

try:
    state = json.loads(state_file.read_text(encoding="utf-8"))
    scenes = state.get("scenes")
    if not isinstance(scenes, list):
        raise ValueError("project_state.json missing 'scenes' list")

    expected_files = set()
    for scene in scenes:
        if not isinstance(scene, dict):
            continue
        scene_id = scene.get("id")
        if not isinstance(scene_id, str) or not scene_id:
            continue
        scene_file = scene.get("file")
        if not isinstance(scene_file, str) or not scene_file:
            scene_file = f"{scene_id}.py"
        expected_files.add(scene_file)

    def find_scene_file(file_name: str) -> Path | None:
        direct = project_dir / file_name
        nested = project_dir / "scenes" / file_name
        if direct.exists():
            return direct
        if nested.exists():
            return nested
        return None

    missing_on_disk = sorted(file_name for file_name in expected_files if find_scene_file(file_name) is None)
    
    actual_files = set(path.name for path in project_dir.glob("scene_*.py"))
    scenes_dir = project_dir / "scenes"
    if scenes_dir.exists():
        actual_files.update(path.name for path in scenes_dir.glob("scene_*.py"))

    extra_on_disk = sorted(actual_files - expected_files)
    
    if extra_on_disk:
        print(f"⚠️  Files on disk not referenced in state: {extra_on_disk}", file=sys.stderr)
    if missing_on_disk:
        print(f"⚠️  Files in state not found on disk: {missing_on_disk}", file=sys.stderr)
    
    if extra_on_disk or missing_on_disk:
        sys.exit(1)
    else:
        print("✅ scenes list consistent with disk")
        sys.exit(0)
        
except Exception as e:
    print(f"❌ Consistency check error: {e}", file=sys.stderr)
    sys.exit(1)
PYCONSIST
  
  if [[ $? -ne 0 ]]; then
    echo "❌ scenes consistency check failed" | tee -a "${project_dir}/build.log"
    return 1
  fi
  
  return 0
}

export -f validate_scene_semantics
export -f self_heal_scene_with_optimization
export -f validate_scene_files_consistency
