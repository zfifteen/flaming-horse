#!/usr/bin/env bash
# Test harness invocation in dry-run mode for all phases

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"

TMP_ROOT="$(mktemp -d /tmp/flaming-horse-dry-run.XXXXXX)"
TEST_PROJECT="${TMP_ROOT}/project"
mkdir -p "${TEST_PROJECT}"
trap 'rm -rf "${TMP_ROOT}"' EXIT

cat > "${TEST_PROJECT}/project_state.json" <<'EOF'
{
  "project_name": "dry_run_fixture",
  "topic": "Dry-run harness fixture",
  "phase": "build_scenes",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z",
  "run_count": 0,
  "plan_file": "plan.json",
  "narration_file": "narration_script.py",
  "voice_config_file": null,
  "scenes": [
    {
      "id": "scene_01_intro",
      "title": "Intro",
      "file": "scene_01_intro.py",
      "class_name": "Scene01Intro",
      "narration_key": "scene_01_intro",
      "status": "pending"
    }
  ],
  "current_scene_index": 0,
  "errors": [],
  "history": [],
  "flags": {
    "needs_human_review": false,
    "dry_run": true
  }
}
EOF

cat > "${TEST_PROJECT}/plan.json" <<'EOF'
{
  "title": "Dry-run Fixture",
  "scenes": [
    {
      "id": "scene_01_intro",
      "title": "Intro",
      "narrative_beats": ["Beat 1", "Beat 2"],
      "visual_ideas": ["Bullet list", "Simple diagram"]
    }
  ]
}
EOF

cat > "${TEST_PROJECT}/narration_script.py" <<'EOF'
SCRIPT = {
    "scene_01_intro": "This is a dry-run narration fixture for scene one."
}
EOF

cat > "${TEST_PROJECT}/scene_01_intro.py" <<'EOF'
from manim import *
from manim_voiceover_plus import VoiceoverScene
from narration_script import SCRIPT

class Scene01Intro(VoiceoverScene):
    def construct(self):
        title = Text("Intro")
        self.add(title)
EOF

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
