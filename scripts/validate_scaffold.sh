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
check "reference_docs"
check "example_project"
echo ""

echo "Reference Placeholders:"
check "reference_docs/manim_content_pipeline.md"
check "reference_docs/manim_voiceover.md"
check "reference_docs/manim_template.py.txt"
check "reference_docs/manim_config_guide.md"
echo ""

echo "Example Files:"
check "example_project/plan.json.example"
check "example_project/narration_script.py.example"
check "example_project/voice_config.py.example"
echo ""

echo "══════════════════════════════════════════════════════"
echo "Results: $PASS passed, $FAIL failed"
echo "══════════════════════════════════════════════════════"

if [[ $FAIL -eq 0 ]]; then
  echo "✅ Scaffold complete!"
  echo ""
  echo "Next steps:"
  echo "  1. Update reference_docs/ with your actual Manim documentation:"
  echo "     cd reference_docs"
  echo "     ln -sf /path/to/your/manim_content_pipeline.md ."
  echo "     ln -sf /path/to/your/manim_voiceover.md ."
  echo "     ln -sf /path/to/your/manim_template.py.txt ."
  echo "     ln -sf /path/to/your/manim_config_guide.md ."
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
