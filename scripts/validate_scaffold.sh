#!/usr/bin/env bash
echo "══════════════════════════════════════════════════════"
echo "Scaffold Validation - Incremental Manim Video Builder"
echo "══════════════════════════════════════════════════════"
echo "Location: $(pwd)"
echo ""

PASS=0
FAIL=0

check() {
  if [[ -f "$1" ]] || [[ -d "$1" ]]; then
    echo "✅ $1"
    ((PASS++))
  else
    echo "❌ $1 (missing)"
    ((FAIL++))
  fi
}

echo "Core Scripts:"
check "build_video.sh"
check "new_project.sh"
check "reset_phase.sh"
echo ""

echo "Documentation:"
check "README.md"
check "system_prompt.md"
echo ""

echo "Directories:"
check "harness_responses/prompts"
check "harness_responses/templates"
echo ""

echo "Reference Placeholders:"
check "harness_responses/prompts/plan/system.md"
check "harness_responses/prompts/narration/system.md"
check "harness_responses/prompts/build_scenes/system.md"
check "harness_responses/templates/phase_scenes.md"
echo "══════════════════════════════════════════════════════"
echo "Results: $PASS passed, $FAIL failed"
echo "══════════════════════════════════════════════════════"

if [[ $FAIL -eq 0 ]]; then
  echo "✅ Scaffold complete!"
  echo ""
  echo "Next steps:"
  echo "  1. Validate harness_responses prompts are current for your pipeline policy."
  echo ""
  echo "  2. Edit build_video.sh → invoke_agent() function with your CLI tool"
  echo ""
  echo "  3. Create a test project:"
  echo "     ./new_project.sh test_video ~/manim_projects"
  echo ""
echo "  4. Precache Qwen voiceovers:"
echo "     python3 scripts/precache_voiceovers_qwen.py ~/manim_projects/test_video"
echo ""
echo "  5. Run the build:"
  echo "     ./build_video.sh ~/manim_projects/test_video"
else
  echo "❌ Some files missing"
  exit 1
fi
