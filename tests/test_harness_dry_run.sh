#!/usr/bin/env bash
# Test harness invocation in dry-run mode for all phases

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"

# Use matrix-multiplication project as test fixture
TEST_PROJECT="${REPO_ROOT}/projects/matrix-multiplication"

if [[ ! -d "$TEST_PROJECT" ]]; then
  echo "❌ Test project not found: $TEST_PROJECT"
  exit 1
fi

echo "🧪 Testing harness dry-run mode for all phases"
echo "Test project: $TEST_PROJECT"
echo ""

# Test plan phase
echo "=== Testing plan phase ==="
python3 -m harness \
  --phase plan \
  --project-dir "$TEST_PROJECT" \
  --topic "Matrix multiplication test" \
  --dry-run
echo "✅ Plan phase dry-run passed"
echo ""

# Test narration phase
echo "=== Testing narration phase ==="
python3 -m harness \
  --phase narration \
  --project-dir "$TEST_PROJECT" \
  --dry-run
echo "✅ Narration phase dry-run passed"
echo ""

# Test build_scenes phase
echo "=== Testing build_scenes phase ==="
python3 -m harness \
  --phase build_scenes \
  --project-dir "$TEST_PROJECT" \
  --dry-run
echo "✅ Build scenes phase dry-run passed"
echo ""

# Test scene_qc phase
echo "=== Testing scene_qc phase ==="
python3 -m harness \
  --phase scene_qc \
  --project-dir "$TEST_PROJECT" \
  --dry-run
echo "✅ Scene QC phase dry-run passed"
echo ""

# Test scene_repair phase
echo "=== Testing scene_repair phase ==="
if [[ -f "$TEST_PROJECT/scene_01_intro.py" ]]; then
  python3 -m harness \
    --phase scene_repair \
    --project-dir "$TEST_PROJECT" \
    --scene-file "$TEST_PROJECT/scene_01_intro.py" \
    --retry-context "Test error context" \
    --dry-run
  echo "✅ Scene repair phase dry-run passed"
else
  echo "⚠️  Skipping scene_repair test (no scene file found)"
fi
echo ""

echo "✅ All harness dry-run tests passed!"
