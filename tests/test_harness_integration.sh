#!/usr/bin/env bash
# Integration test for harness - validates integration without API calls

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"

cd "${REPO_ROOT}"
export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH:-}"

echo "🧪 Harness Integration Test (Mock Mode)"
echo "========================================"
echo ""

# Test 1: Verify harness module is importable
echo "Test 1: Module import..."
if python3 -c "import harness; print('✅ harness module imported')" 2>/dev/null; then
  echo "✅ PASS: Harness module is importable"
else
  echo "❌ FAIL: Cannot import harness module"
  exit 1
fi
echo ""

# Test 2: Verify all components are present
echo "Test 2: Component verification..."
python3 - <<'PY'
import sys
try:
    from harness import client, prompts, parser, cli
    print("✅ All components imported successfully")
    
    # Check key functions exist
    assert hasattr(client, 'call_xai_api'), "Missing call_xai_api"
    assert hasattr(prompts, 'compose_prompt'), "Missing compose_prompt"
    assert hasattr(parser, 'parse_and_write_artifacts'), "Missing parse_and_write_artifacts"
    assert hasattr(cli, 'main'), "Missing main"
    
    print("✅ All required functions present")
    sys.exit(0)
except Exception as e:
    print(f"❌ Component verification failed: {e}")
    sys.exit(1)
PY

if [ $? -eq 0 ]; then
  echo "✅ PASS: All components verified"
else
  echo "❌ FAIL: Component verification failed"
  exit 1
fi
echo ""

# Test 3: Verify CLI help works
echo "Test 3: CLI help..."
if python3 -m harness --help >/dev/null 2>&1; then
  echo "✅ PASS: CLI help works"
else
  echo "❌ FAIL: CLI help failed"
  exit 1
fi
echo ""

# Test 4: Verify dry-run mode works (uses test project)
echo "Test 4: Dry-run mode..."
TEST_PROJECT="${REPO_ROOT}/projects/matrix-multiplication"

if [ -d "$TEST_PROJECT" ]; then
  if python3 -m harness --phase plan --project-dir "$TEST_PROJECT" --topic "Test" --dry-run >/dev/null 2>&1; then
    echo "✅ PASS: Dry-run mode works"
  else
    echo "❌ FAIL: Dry-run mode failed"
    exit 1
  fi
else
  echo "⚠️  SKIP: Test project not found, skipping dry-run test"
fi
echo ""

# Test 5: Verify prompt templates exist
echo "Test 5: Prompt templates..."
TEMPLATES=(
  "core_rules.md"
  "plan_system.md"
  "narration_system.md"
  "build_scenes_system.md"
  "scene_qc_system.md"
  "repair_system.md"
)

ALL_FOUND=true
for template in "${TEMPLATES[@]}"; do
  if [ -f "${REPO_ROOT}/harness/prompt_templates/${template}" ]; then
    echo "  ✅ ${template}"
  else
    echo "  ❌ Missing: ${template}"
    ALL_FOUND=false
  fi
done

if $ALL_FOUND; then
  echo "✅ PASS: All prompt templates found"
else
  echo "❌ FAIL: Some prompt templates missing"
  exit 1
fi
echo ""

# Test 6: Verify build_video.sh integration
echo "Test 6: build_video.sh integration..."
if grep -q "python3 -m harness" "${REPO_ROOT}/scripts/build_video.sh"; then
  echo "✅ PASS: build_video.sh has harness integration"
else
  echo "❌ FAIL: build_video.sh missing harness invocation"
  exit 1
fi
echo ""

# Test 7: Verify parser can handle sample responses
echo "Test 7: Parser functionality..."
python3 - <<'PY'
import sys
import json
from pathlib import Path
import tempfile
from harness.parser import (
    extract_json_block,
    extract_python_code_blocks,
    sanitize_code,
    verify_python_syntax
)

# Test JSON extraction
json_text = """
Here is the plan:
```json
{"title": "Test", "scenes": []}
```
"""

extracted = extract_json_block(json_text)
if extracted and "title" in json.loads(extracted):
    print("✅ JSON extraction works")
else:
    print("❌ JSON extraction failed")
    sys.exit(1)

# Test Python code extraction
python_text = """
Here is the code:
```python
def hello():
    print("world")
```
"""

code_blocks = extract_python_code_blocks(python_text)
if code_blocks and "def hello" in code_blocks[0][1]:
    print("✅ Python extraction works")
else:
    print("❌ Python extraction failed")
    sys.exit(1)

# Test code sanitization
dirty_code = "<script>alert('xss')</script>\ndef clean():\n    pass"
clean = sanitize_code(dirty_code)
if "<script>" not in clean and "def clean" in clean:
    print("✅ Code sanitization works")
else:
    print("❌ Code sanitization failed")
    sys.exit(1)

# Test syntax verification
valid_code = "def test():\n    pass"
if verify_python_syntax(valid_code):
    print("✅ Syntax verification works")
else:
    print("❌ Syntax verification failed")
    sys.exit(1)

print("✅ Parser tests passed")
PY

if [ $? -eq 0 ]; then
  echo "✅ PASS: Parser functionality verified"
else
  echo "❌ FAIL: Parser tests failed"
  exit 1
fi
echo ""

# Summary
echo "=========================================="
echo "📊 Integration Test Summary"
echo "=========================================="
echo ""
echo "✅ All integration tests passed!"
echo ""
echo "The harness is properly integrated and ready for use."
echo "To test with actual xAI API, set XAI_API_KEY and run:"
echo "  ./tests/test_harness_e2e.sh"
echo ""

exit 0
