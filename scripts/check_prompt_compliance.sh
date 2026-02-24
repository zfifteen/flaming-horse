#!/usr/bin/env bash
# Prompt Compliance Checker
# Validates that all LLM prompts are in harness_responses/prompts/
# Exit code 0 = compliant, 1 = infractions found

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Prompt Compliance Checker"
echo "=========================================="
echo ""

INFRACTIONS=0

# Check 1: Search for embedded prompt patterns in Python files (excluding templates)
echo "Check 1: Searching for embedded prompts in Python files..."
PYTHON_PROMPTS=$(grep -r "user_prompt.*=.*f\"\"\"" \
    --include="*.py" \
    --exclude-dir=".git" \
    --exclude-dir="__pycache__" \
    --exclude-dir="harness_responses/prompts" \
    harness_responses/ scripts/ 2>/dev/null || true)

if [[ -n "$PYTHON_PROMPTS" ]]; then
    echo -e "${RED}✗ FAIL: Found embedded prompts in Python files:${NC}"
    echo "$PYTHON_PROMPTS" | head -10
    ((INFRACTIONS++))
else
    echo -e "${GREEN}✓ PASS: No embedded prompts in Python files${NC}"
fi
echo ""

# Check 2: Search for "You are" prompt patterns (common prompt opening)
echo "Check 2: Searching for 'You are' prompt patterns..."
YOU_ARE_PROMPTS=$(grep -rn "You are.*\(creating\|writing\|generating\|repair\)" \
    --include="*.py" \
    --exclude-dir=".git" \
    --exclude-dir="__pycache__" \
    --exclude-dir="harness_responses/prompts" \
    harness_responses/ scripts/ 2>/dev/null || true)

if [[ -n "$YOU_ARE_PROMPTS" ]]; then
    echo -e "${RED}✗ FAIL: Found 'You are' prompt patterns in code:${NC}"
    echo "$YOU_ARE_PROMPTS" | head -10
    ((INFRACTIONS++))
else
    echo -e "${GREEN}✓ PASS: No 'You are' patterns in code${NC}"
fi
echo ""

# Check 3: Search for "Please" instruction patterns
echo "Check 3: Searching for 'Please' instruction patterns..."
PLEASE_PROMPTS=$(grep -rn "\"\"\"Please.*\(create\|write\|generate\|review\|repair\)" \
    --include="*.py" \
    --exclude-dir=".git" \
    --exclude-dir="__pycache__" \
    --exclude-dir="harness_responses/prompts" \
    harness_responses/ scripts/ 2>/dev/null || true)

if [[ -n "$PLEASE_PROMPTS" ]]; then
    echo -e "${YELLOW}⚠ WARNING: Found 'Please' instruction patterns:${NC}"
    echo "$PLEASE_PROMPTS" | head -10
    ((INFRACTIONS++))
else
    echo -e "${GREEN}✓ PASS: No 'Please' patterns in code${NC}"
fi
echo ""

# Check 4: Check for duplicate prompts in docs (excluding templates)
echo "Check 4: Checking for prompt content in documentation..."
DOC_PROMPTS=$(find docs/ -name "*.md" -exec grep -l "You are.*agent\|Your job is to" {} \; 2>/dev/null || true)

if [[ -n "$DOC_PROMPTS" ]]; then
    echo -e "${YELLOW}⚠ WARNING: Found potential prompt content in documentation:${NC}"
    echo "$DOC_PROMPTS"
    echo "  Review these files to ensure they don't duplicate prompts/"
else
    echo -e "${GREEN}✓ PASS: No obvious prompt duplication in docs${NC}"
fi
echo ""

# Check 5: Verify pipeline-ordered prompt structure exists
echo "Check 5: Verifying pipeline-ordered prompt structure..."
REQUIRED_DIRS=(
  "harness_responses/prompts/plan"
  "harness_responses/prompts/narration"
  "harness_responses/prompts/build_scenes"
  "harness_responses/prompts/scene_qc"
  "harness_responses/prompts/scene_repair"
)

REQUIRED_FILES=(
  "harness_responses/prompts/plan/system.md"
  "harness_responses/prompts/plan/user.md"
  "harness_responses/prompts/narration/system.md"
  "harness_responses/prompts/narration/user.md"
  "harness_responses/prompts/build_scenes/system.md"
  "harness_responses/prompts/build_scenes/user.md"
  "harness_responses/prompts/scene_qc/system.md"
  "harness_responses/prompts/scene_qc/user.md"
  "harness_responses/prompts/scene_repair/system.md"
  "harness_responses/prompts/scene_repair/user.md"
)

for d in "${REQUIRED_DIRS[@]}"; do
  if [[ ! -d "$d" ]]; then
    echo -e "${RED}✗ FAIL: Missing directory: $d${NC}"
    ((INFRACTIONS++))
  fi
done

for f in "${REQUIRED_FILES[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo -e "${RED}✗ FAIL: Missing file: $f${NC}"
    ((INFRACTIONS++))
  fi
done

if [[ $INFRACTIONS -eq 0 ]]; then
  echo -e "${GREEN}✓ PASS: Prompt structure present${NC}"
fi
echo ""

# Summary
echo "=========================================="
if [[ $INFRACTIONS -eq 0 ]]; then
    echo -e "${GREEN}✓ COMPLIANT: No infractions found${NC}"
    echo "=========================================="
    exit 0
else
    echo -e "${RED}✗ NON-COMPLIANT: $INFRACTIONS check(s) failed${NC}"
    echo "=========================================="
    echo ""
    echo "See PROMPT_INFRACTION_REPORT.md for details and remediation plan."
    exit 1
fi
