#!/usr/bin/env bash
# QC Validation Functions for build_video.sh
# These functions should be added to build_video.sh after the validation functions section

# ═══════════════════════════════════════════════════════════════
# QC Protection Functions
# ═══════════════════════════════════════════════════════════════

backup_scene_files() {
  echo "→ Backing up scene files before QC..." | tee -a "$LOG_FILE"
  
  local backup_dir="${PROJECT_DIR}/.qc_backup_$(date +%s)"
  mkdir -p "$backup_dir"
  
  # Extract scene files from state
  python3 - <<PY > "${backup_dir}/scene_list.txt"
import json
with open("${STATE_FILE}", "r") as f:
    state = json.load(f)
for scene in state.get("scenes", []):
    if isinstance(scene, dict) and "file" in scene:
        print(scene["file"])
PY

  local scene_file
  while IFS= read -r scene_file; do
    if [[ -f "${PROJECT_DIR}/${scene_file}" ]]; then
      cp "${PROJECT_DIR}/${scene_file}" "${backup_dir}/"
      echo "  Backed up: ${scene_file}" | tee -a "$LOG_FILE"
    fi
  done < "${backup_dir}/scene_list.txt"
  
  echo "${backup_dir}" > "${PROJECT_DIR}/.latest_qc_backup"
  echo "✓ Scene backup complete: ${backup_dir}" | tee -a "$LOG_FILE"
}

restore_scene_files() {
  local backup_dir="$1"
  
  if [[ ! -d "$backup_dir" ]]; then
    echo "✗ Backup directory not found: ${backup_dir}" | tee -a "$LOG_FILE" >&2
    return 1
  fi
  
  echo "→ Restoring scene files from backup..." | tee -a "$LOG_FILE"
  
  local scene_file
  while IFS= read -r scene_file; do
    if [[ -f "${backup_dir}/${scene_file}" ]]; then
      cp "${backup_dir}/${scene_file}" "${PROJECT_DIR}/"
      echo "  Restored: ${scene_file}" | tee -a "$LOG_FILE"
    fi
  done < "${backup_dir}/scene_list.txt"
  
  echo "✓ Scene files restored from: ${backup_dir}" | tee -a "$LOG_FILE"
}

validate_qc_results() {
  echo "→ Validating QC results..." | tee -a "$LOG_FILE"
  
  # Check 1: QC report exists and is non-empty
  local qc_report="${PROJECT_DIR}/scene_qc_report.md"
  if [[ ! -f "$qc_report" ]]; then
    echo "✗ QC report missing: scene_qc_report.md" | tee -a "$LOG_FILE" >&2
    return 1
  fi
  
  if [[ ! -s "$qc_report" ]]; then
    echo "✗ QC report is empty" | tee -a "$LOG_FILE" >&2
    return 1
  fi
  
  echo "✓ QC report exists and is non-empty" | tee -a "$LOG_FILE"
  
  # Check 2: All scene files have valid Python syntax
  echo "→ Running syntax validation on all scene files..." | tee -a "$LOG_FILE"
  
  if python3 "${SCRIPT_DIR}/validate_qc_scenes.py" "${PROJECT_DIR}" \
    > >(tee -a "$LOG_FILE") \
    2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2); then
    echo "✓ All scene files have valid syntax" | tee -a "$LOG_FILE"
    return 0
  else
    echo "✗ Syntax validation failed" | tee -a "$LOG_FILE" >&2
    return 1
  fi
}

# Integration point for scene_qc phase
# This block should replace the existing scene_qc handler in build_video.sh

handle_scene_qc_phase() {
  echo "[Phase: scene_qc] Validating and patching scene quality..." | tee -a "$LOG_FILE"
  
  # Step 1: Backup scene files before QC
  if ! backup_scene_files; then
    echo "✗ Failed to backup scene files" | tee -a "$LOG_FILE" >&2
    return 1
  fi
  
  local backup_dir
  backup_dir="$(cat "${PROJECT_DIR}/.latest_qc_backup")"
  
  # Step 2: Prepare and render QC prompt
  local scene_files_list
  scene_files_list=$(python3 - <<PY
import json
with open("${STATE_FILE}", "r") as f:
    state = json.load(f)
for scene in state.get("scenes", []):
    if isinstance(scene, dict) and "file" in scene:
        print(f"  - {scene['file']}")
PY
)
  
  local qc_prompt_file="${PROJECT_DIR}/.agent_prompt_scene_qc.md"
  render_template_file \
    "${SCENE_QC_TEMPLATE}" \
    "${qc_prompt_file}" \
    "PROJECT_DIR=${PROJECT_DIR}" \
    "STATE_FILE=${STATE_FILE}" \
    "SCENE_FILES=${scene_files_list}"
  
  # Step 3: Invoke QC agent
  echo "→ Invoking QC agent..." | tee -a "$LOG_FILE"
  
  local agent_output_file="${PROJECT_DIR}/.agent_output_scene_qc.jsonl"
  
  if ! opencode -m "${AGENT_MODEL}" \
    --prompt "${qc_prompt_file}" \
    --file "${STATE_FILE}" \
    --cwd "${PROJECT_DIR}" \
    > "${agent_output_file}" \
    2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2); then
    echo "✗ QC agent failed" | tee -a "$LOG_FILE" >&2
    return 1
  fi
  
  # Step 4: Validate QC results
  if validate_qc_results; then
    echo "✓ QC validation passed" | tee -a "$LOG_FILE"
    rm -f "${PROJECT_DIR}/.latest_qc_backup"  # Success, remove backup reference
    return 0
  else
    echo "✗ QC validation failed - rolling back" | tee -a "$LOG_FILE" >&2
    
    # Rollback to backup
    if restore_scene_files "$backup_dir"; then
      echo "✓ Scene files restored from backup" | tee -a "$LOG_FILE"
      
      # Set human review flag
      python3 - <<PY
import json
from datetime import datetime

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

state.setdefault("errors", []).append(
    "scene_qc validation failed: syntax errors or missing report after QC. "
    "Scene files restored from backup. Manual inspection required."
)
state.setdefault("flags", {})["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
      
      echo "⚠️  QC failed validation. Scene files restored. Human review needed." | tee -a "$LOG_FILE" >&2
      return 1
    else
      echo "✗ CRITICAL: Failed to restore scene files from backup" | tee -a "$LOG_FILE" >&2
      return 1
    fi
  fi
}
