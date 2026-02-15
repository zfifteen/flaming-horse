#!/usr/bin/env bash
PROJECT_DIR="${1:?Usage: $0 <project_dir> <phase>}"
NEW_PHASE="${2:?Usage: $0 <project_dir> <phase>}"

VALID_PHASES=("init" "plan" "review" "narration" "build_scenes" "final_render" "assemble" "complete")
if [[ ! " ${VALID_PHASES[*]} " =~ " ${NEW_PHASE} " ]]; then
  echo "❌ Invalid phase: $NEW_PHASE" >&2
  echo "Valid phases: ${VALID_PHASES[*]}" >&2
  exit 1
fi

STATE_FILE="${PROJECT_DIR}/project_state.json"
if [[ ! -f "$STATE_FILE" ]]; then
  echo "❌ State file not found: $STATE_FILE" >&2
  exit 1
fi

cp "$STATE_FILE" "${PROJECT_DIR}/.state_before_reset.json"
echo "💾 Backed up current state to .state_before_reset.json"

python3 <<EOF
import json
from datetime import datetime

with open('${STATE_FILE}', 'r') as f:
    state = json.load(f)

old_phase = state['phase']
state['phase'] = '${NEW_PHASE}'
state['updated_at'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

state['history'].append({
    'timestamp': state['updated_at'],
    'phase': 'manual_reset',
    'message': f"Phase manually reset from '{old_phase}' to '${NEW_PHASE}'"
})

with open('${STATE_FILE}', 'w') as f:
    json.dump(state, f, indent=2)

print(f"✅ Reset phase: {old_phase} → ${NEW_PHASE}")
EOF
