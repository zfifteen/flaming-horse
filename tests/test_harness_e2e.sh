#!/usr/bin/env bash
# End-to-end test for the harness with actual xAI API calls

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 End-to-End Harness Test with xAI API"
echo "========================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check XAI_API_KEY
if [ -f "${REPO_ROOT}/.env" ]; then
  source "${REPO_ROOT}/.env"
fi

if [ -z "${XAI_API_KEY:-}" ]; then
  echo -e "${RED}❌ XAI_API_KEY not set${NC}"
  echo "Please set XAI_API_KEY in .env file or environment"
  exit 1
fi

echo -e "${GREEN}✅ XAI_API_KEY is set (${#XAI_API_KEY} chars)${NC}"

# Check USE_HARNESS
export USE_HARNESS=1
echo -e "${GREEN}✅ USE_HARNESS=1 (using harness)${NC}"

# Test topic
TEST_TOPIC="The Pythagorean Theorem"
TEST_PROJECT_NAME="e2e_test_harness_$(date +%s)"
TEST_PROJECT_DIR="${REPO_ROOT}/projects/${TEST_PROJECT_NAME}"

echo ""
echo "📁 Test Configuration:"
echo "  Topic: ${TEST_TOPIC}"
echo "  Project: ${TEST_PROJECT_NAME}"
echo "  Directory: ${TEST_PROJECT_DIR}"
echo ""

# Create test project
echo "🔨 Creating test project..."
mkdir -p "${TEST_PROJECT_DIR}"

# Initialize project state
cat > "${TEST_PROJECT_DIR}/project_state.json" <<EOF
{
  "project_name": "${TEST_PROJECT_NAME}",
  "topic": "${TEST_TOPIC}",
  "phase": "plan",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "run_count": 0,
  "plan_file": "plan.json",
  "narration_file": "narration_script.py",
  "voice_config_file": null,
  "scenes": [],
  "current_scene_index": 0,
  "errors": [],
  "history": [],
  "flags": {
    "needs_human_review": false,
    "dry_run": false
  }
}
EOF

echo -e "${GREEN}✅ Test project initialized${NC}"
echo ""

# Test Phase 1: Plan
echo "=== Phase 1: Plan ==="
echo "Testing harness plan phase with real API..."

cd "${TEST_PROJECT_DIR}"

python3 -m harness \
  --phase plan \
  --project-dir "${TEST_PROJECT_DIR}" \
  --topic "${TEST_TOPIC}"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Plan phase completed${NC}"
else
  echo -e "${RED}❌ Plan phase failed${NC}"
  exit 1
fi

# Validate plan.json
if [ -f "plan.json" ]; then
  echo "📄 Validating plan.json..."
  
  # Check if it's valid JSON
  if python3 -c "import json; json.load(open('plan.json'))" 2>/dev/null; then
    echo -e "${GREEN}✅ plan.json is valid JSON${NC}"
    
    # Check required fields
    TITLE=$(python3 -c "import json; print(json.load(open('plan.json')).get('title', ''))")
    SCENES_COUNT=$(python3 -c "import json; print(len(json.load(open('plan.json')).get('scenes', [])))")
    
    echo "  Title: ${TITLE}"
    echo "  Scenes: ${SCENES_COUNT}"
    
    if [ ${SCENES_COUNT} -ge 3 ] && [ ${SCENES_COUNT} -le 8 ]; then
      echo -e "${GREEN}✅ Scene count is valid (${SCENES_COUNT})${NC}"
    else
      echo -e "${YELLOW}⚠️  Scene count unusual: ${SCENES_COUNT}${NC}"
    fi
  else
    echo -e "${RED}❌ plan.json is not valid JSON${NC}"
    exit 1
  fi
else
  echo -e "${RED}❌ plan.json not found${NC}"
  exit 1
fi

echo ""

# Test Phase 2: Narration
echo "=== Phase 2: Narration ==="
echo "Testing harness narration phase with real API..."

# Update state to narration phase
python3 - <<PY
import json
from datetime import datetime

with open("project_state.json", "r") as f:
    state = json.load(f)

with open("plan.json", "r") as f:
    plan = json.load(f)

state["phase"] = "narration"
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

# Add scenes from plan
state["scenes"] = []
for i, scene in enumerate(plan.get("scenes", [])):
    scene_id = scene.get("id", f"scene_{i+1:02d}")
    state["scenes"].append({
        "id": scene_id,
        "title": scene.get("title", ""),
        "file": f"{scene_id}.py",
        "class_name": "",
        "status": "pending"
    })

with open("project_state.json", "w") as f:
    json.dump(state, f, indent=2)
PY

python3 -m harness \
  --phase narration \
  --project-dir "${TEST_PROJECT_DIR}"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Narration phase completed${NC}"
else
  echo -e "${RED}❌ Narration phase failed${NC}"
  exit 1
fi

# Validate narration_script.py
if [ -f "narration_script.py" ]; then
  echo "📄 Validating narration_script.py..."
  
  # Check if it's valid Python
  if python3 -m py_compile narration_script.py 2>/dev/null; then
    echo -e "${GREEN}✅ narration_script.py is valid Python${NC}"
    
    # Check for SCRIPT dict
    if grep -q "SCRIPT = {" narration_script.py; then
      echo -e "${GREEN}✅ SCRIPT dict found${NC}"
      
      # Count scene keys
      SCRIPT_KEYS=$(python3 -c "exec(open('narration_script.py').read()); print(len(SCRIPT))")
      echo "  Script keys: ${SCRIPT_KEYS}"
    else
      echo -e "${RED}❌ SCRIPT dict not found${NC}"
      exit 1
    fi
  else
    echo -e "${RED}❌ narration_script.py has syntax errors${NC}"
    exit 1
  fi
else
  echo -e "${RED}❌ narration_script.py not found${NC}"
  exit 1
fi

echo ""

# Test Phase 3: Build Scenes (just first scene)
echo "=== Phase 3: Build Scenes (First Scene) ==="
echo "Testing harness build_scenes phase with real API..."

# Update state to build_scenes phase
python3 - <<PY
import json
from datetime import datetime

with open("project_state.json", "r") as f:
    state = json.load(f)

state["phase"] = "build_scenes"
state["current_scene_index"] = 0
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open("project_state.json", "w") as f:
    json.dump(state, f, indent=2)
PY

python3 -m harness \
  --phase build_scenes \
  --project-dir "${TEST_PROJECT_DIR}"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Build scenes phase completed${NC}"
else
  echo -e "${RED}❌ Build scenes phase failed${NC}"
  exit 1
fi

# Validate first scene file
FIRST_SCENE_FILE=$(python3 -c "import json; scenes = json.load(open('project_state.json')).get('scenes', []); print(scenes[0]['file'] if scenes else '')")

if [ -n "${FIRST_SCENE_FILE}" ] && [ -f "${FIRST_SCENE_FILE}" ]; then
  echo "📄 Validating ${FIRST_SCENE_FILE}..."
  
  # Check if it's valid Python
  if python3 -m py_compile "${FIRST_SCENE_FILE}" 2>/dev/null; then
    echo -e "${GREEN}✅ ${FIRST_SCENE_FILE} is valid Python${NC}"
    
    # Check for required imports
    if grep -q "from manim import" "${FIRST_SCENE_FILE}"; then
      echo -e "${GREEN}✅ Manim imports found${NC}"
    fi
    
    if grep -q "from manim_voiceover_plus import VoiceoverScene" "${FIRST_SCENE_FILE}"; then
      echo -e "${GREEN}✅ VoiceoverScene import correct (underscores)${NC}"
    fi
    
    if grep -q "from narration_script import SCRIPT" "${FIRST_SCENE_FILE}"; then
      echo -e "${GREEN}✅ SCRIPT import found${NC}"
    fi
    
    # Check for VoiceoverScene class
    if grep -q "class.*VoiceoverScene" "${FIRST_SCENE_FILE}"; then
      echo -e "${GREEN}✅ Scene class inherits VoiceoverScene${NC}"
    fi
  else
    echo -e "${RED}❌ ${FIRST_SCENE_FILE} has syntax errors${NC}"
    cat "${FIRST_SCENE_FILE}"
    exit 1
  fi
else
  echo -e "${RED}❌ Scene file not found: ${FIRST_SCENE_FILE}${NC}"
  exit 1
fi

echo ""

# Summary
echo "=========================================="
echo "🎉 End-to-End Test Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}✅ All phases completed successfully!${NC}"
echo ""
echo "Artifacts created:"
echo "  - plan.json ($(wc -l < plan.json) lines)"
echo "  - narration_script.py ($(wc -l < narration_script.py) lines)"
echo "  - ${FIRST_SCENE_FILE} ($(wc -l < "${FIRST_SCENE_FILE}") lines)"
echo ""
echo "Test project location: ${TEST_PROJECT_DIR}"
echo ""
echo -e "${GREEN}✅ Harness is working correctly with xAI API!${NC}"
echo ""

# Optional: Show token usage if available in logs
if [ -f "build.log" ]; then
  echo "📊 Token usage (if logged):"
  grep -i "token" build.log | tail -5 || echo "  No token usage data found"
fi

exit 0
