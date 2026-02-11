#!/usr/bin/env bash
PROJECT_NAME="${1:?Usage: $0 <project_name> [projects_dir]}"
PROJECTS_DIR="${2:-./projects}"
PROJECT_DIR="${PROJECTS_DIR}/${PROJECT_NAME}"

mkdir -p "$PROJECT_DIR"

cat > "$PROJECT_DIR/project_state.json" <<EOF
{
  "project_name": "$PROJECT_NAME",
  "phase": "plan",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "run_count": 0,
  "plan_file": null,
  "narration_file": null,
  "voice_config_file": null,
  "scenes": [],
  "current_scene_index": 0,
  "errors": [],
  "history": [],
  "flags": {
    "needs_human_review": false,
    "dry_run": false,
    "force_replan": false
  }
}
EOF

echo "✅ Created project: $PROJECT_DIR"
echo "📝 State file: $PROJECT_DIR/project_state.json"
echo ""
echo "Next steps:"
echo "  1. Edit build_video.sh to configure your agent invocation"
echo "  2. Run: ./build_video.sh $PROJECT_DIR"
