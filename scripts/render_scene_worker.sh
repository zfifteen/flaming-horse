#!/usr/bin/env bash
# Parallel scene rendering worker for Manim video pipeline
# 
# This script is called by GNU parallel or xargs to render multiple scenes concurrently.
# It handles a single scene's rendering with retry logic and error reporting.
#
# Usage:
#   render_scene_worker.sh <project_dir> <scene_id> <scene_file> <scene_class> <est_duration>
#
# Exit codes:
#   0 - Scene rendered and verified successfully
#   1 - Scene rendering failed after all retries

set -euo pipefail

PROJECT_DIR="${1:-}"
SCENE_ID="${2:-}"
SCENE_FILE="${3:-}"
SCENE_CLASS="${4:-}"
EST_DURATION="${5:-}"

if [[ -z "$PROJECT_DIR" || -z "$SCENE_ID" || -z "$SCENE_FILE" || -z "$SCENE_CLASS" ]]; then
    echo "❌ Usage: $0 <project_dir> <scene_id> <scene_file> <scene_class> <est_duration>" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"
export PYTHONPATH="${REPO_ROOT}:${SCRIPT_DIR}:${PYTHONPATH:-}"

LOG_FILE="${PROJECT_DIR}/render_${SCENE_ID}.log"
ERROR_LOG="${PROJECT_DIR}/render_${SCENE_ID}.err"

# Force offline mode for HuggingFace
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false

# Detect manim binary
manim_bin="manim"
if command -v manim-ce &> /dev/null; then
    manim_bin="manim-ce"
fi

cd "$PROJECT_DIR"

# Check if scene is already rendered and verified
verify_scene_video() {
    local out_video="media/videos/${SCENE_ID}/1440p60/${SCENE_CLASS}.mp4"
    
    if [[ ! -f "$out_video" ]]; then
        return 1
    fi
    
    # Verify video has audio track
    if ! ffprobe -v error -select_streams a:0 -show_entries stream=codec_type \
        -of default=noprint_wrappers=1:nokey=1 "$out_video" 2>/dev/null | grep -q audio; then
        echo "⚠ Video exists but has no audio track: $out_video" >> "$LOG_FILE"
        return 1
    fi
    
    return 0
}

if verify_scene_video; then
    echo "✓ Scene $SCENE_ID already rendered and verified (skipping)" | tee -a "$LOG_FILE"
    exit 0
fi

# Clean stale/corrupted partials
partial_dir="media/videos/${SCENE_ID}/1440p60/partial_movie_files/${SCENE_CLASS}"
out_video="media/videos/${SCENE_ID}/1440p60/${SCENE_CLASS}.mp4"
if [[ -d "$partial_dir" ]]; then
    echo "→ Removing stale partials: $partial_dir" >> "$LOG_FILE"
    rm -rf "$partial_dir"
fi
if [[ -f "$out_video" ]]; then
    echo "→ Removing stale output: $out_video" >> "$LOG_FILE"
    rm -f "$out_video"
fi

echo "🎬 Rendering scene: $SCENE_ID ($SCENE_CLASS)" | tee -a "$LOG_FILE"
echo "$ manim render $SCENE_FILE $SCENE_CLASS -qh" >> "$LOG_FILE"

# Render with retry logic (up to 3 attempts)
RETRY_LIMIT=3
attempt=0
ok=0

while [[ $attempt -lt $RETRY_LIMIT ]]; do
    attempt=$((attempt + 1))
    
    if "$manim_bin" render "$SCENE_FILE" "$SCENE_CLASS" -qh \
        >> "$LOG_FILE" 2>> "$ERROR_LOG"; then
        ok=1
        break
    fi
    
    if [[ $attempt -lt $RETRY_LIMIT ]]; then
        echo "⚠ Render attempt $attempt failed for $SCENE_ID, retrying..." | tee -a "$LOG_FILE"
        sleep 2
    fi
done

if [[ $ok -ne 1 ]]; then
    echo "❌ Render failed for $SCENE_ID after $RETRY_LIMIT attempts" | tee -a "$ERROR_LOG"
    exit 1
fi

# Verify the rendered output
if ! verify_scene_video; then
    echo "❌ Verification failed for $SCENE_ID: missing or invalid video" | tee -a "$ERROR_LOG"
    exit 1
fi

echo "✓ Successfully rendered: $SCENE_ID ($SCENE_CLASS)" | tee -a "$LOG_FILE"
exit 0
