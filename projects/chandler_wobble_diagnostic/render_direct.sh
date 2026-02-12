#!/usr/bin/env bash
set -euo pipefail

echo "==========================================================="
echo "Rendering Chandler Wobble Diagnostic Video (Direct Mode)"
echo "Project: chandler_wobble_diagnostic"
echo "Started: $(date)"
echo "===========================================================\n"

# Navigate to project directory
PROJECT_DIR="/Users/velocityworks/IdeaProjects/flaming-horse/projects/chandler_wobble_diagnostic"
cd "$PROJECT_DIR"

echo "Working directory: $PWD\n"

# Check for ElevenLabs API key in common locations
if [[ -f "$HOME/.elevenlabs_api_key" ]]; then
  export ELEVENLABS_API_KEY=$(cat "$HOME/.elevenlabs_api_key" | tr -d '\n')
  echo "✓ Loaded ElevenLabs API key from ~/.elevenlabs_api_key\n"
elif [[ -n "${ELEVENLABS_API_KEY:-}" ]]; then
  echo "✓ Using ElevenLabs API key from environment\n"
else
  echo "⚠️  WARNING: ELEVENLABS_API_KEY not found"
  echo "Voice synthesis may fail. To set it:"
  echo "  1. export ELEVENLABS_API_KEY='your_key', OR"
  echo "  2. echo 'your_key' > ~/.elevenlabs_api_key"
  echo "\nContinuing anyway...\n"
fi

# Create media directory if it doesn't exist
mkdir -p media/videos

# Scene list
SCENES=(
  "scene_01_phase_flip.py:Scene01PhaseFlip"
  "scene_02_debunk_standard.py:Scene02DebunkStandard"
  "scene_03_modulated_envelope.py:Scene03ModulatedEnvelope"
  "scene_04_lod_connection.py:Scene04LODConnection"
  "scene_05_prediction.py:Scene05Prediction"
  "scene_06_paradigm_shift.py:Scene06ParadigmShift"
  "scene_07_utility.py:Scene07Utility"
  "scene_08_conclusion.py:Scene08Conclusion"
)

echo "Rendering ${#SCENES[@]} scenes...\n"

# Track successful renders
SUCCESS_COUNT=0
FAILED_SCENES=()

# Render each scene
for i in "${!SCENES[@]}"; do
  IFS=':' read -r scene_file scene_class <<< "${SCENES[$i]}"
  scene_num=$((i + 1))
  
  echo "\n───────────────────────────────────────────────────────────"
  echo "🎥 Scene $scene_num/8: $scene_class"
  echo "   File: $scene_file"
  echo "───────────────────────────────────────────────────────────"
  
  # Render with manim
  echo "Running: manim render $scene_file $scene_class -qh --disable_caching"
  if manim render "$scene_file" "$scene_class" -qh --disable_caching 2>&1 | tee "scene_${scene_num}.log"; then
    echo "✓ Scene $scene_num rendered successfully"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  else
    echo "❌ Failed to render scene $scene_num"
    FAILED_SCENES+=("$scene_num:$scene_class")
  fi
done

echo "\n\n==========================================================="
echo "RENDER SUMMARY"
echo "===========================================================" 
echo "Successfully rendered: $SUCCESS_COUNT/${#SCENES[@]} scenes"

if [[ ${#FAILED_SCENES[@]} -gt 0 ]]; then
  echo "\n❌ Failed scenes:"
  for failed in "${FAILED_SCENES[@]}"; do
    echo "  - $failed"
  done
  echo "\nCheck individual scene logs for details: scene_N.log"
else
  echo "\n✅ All scenes rendered successfully!"
fi

echo "\n==========================================================="

if [[ $SUCCESS_COUNT -eq ${#SCENES[@]} ]]; then
  echo "\n🎬 Assembling final video...\n"
  
  # Create scenes.txt for ffmpeg concat
  cat > scenes.txt <<EOF
file 'media/videos/scene_01_phase_flip/1440p60/Scene01PhaseFlip.mp4'
file 'media/videos/scene_02_debunk_standard/1440p60/Scene02DebunkStandard.mp4'
file 'media/videos/scene_03_modulated_envelope/1440p60/Scene03ModulatedEnvelope.mp4'
file 'media/videos/scene_04_lod_connection/1440p60/Scene04LODConnection.mp4'
file 'media/videos/scene_05_prediction/1440p60/Scene05Prediction.mp4'
file 'media/videos/scene_06_paradigm_shift/1440p60/Scene06ParadigmShift.mp4'
file 'media/videos/scene_07_utility/1440p60/Scene07Utility.mp4'
file 'media/videos/scene_08_conclusion/1440p60/Scene08Conclusion.mp4'
EOF
  
  echo "✓ Created scenes.txt file list\n"
  
  # Concatenate with ffmpeg
  if ffmpeg -f concat -safe 0 -i scenes.txt -c copy final_video.mp4 -y; then
    echo "\n✓ Final video assembled successfully!"
    echo "\n🎉 OUTPUT: $PROJECT_DIR/final_video.mp4"
    
    # Get file size and duration
    if [[ -f "final_video.mp4" ]]; then
      file_size=$(du -h final_video.mp4 | cut -f1)
      echo "   Size: $file_size"
      
      # Try to get duration with ffprobe
      if command -v ffprobe &> /dev/null; then
        duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 final_video.mp4 2>/dev/null || echo "unknown")
        if [[ "$duration" != "unknown" ]]; then
          duration_formatted=$(printf "%.1f" "$duration")
          echo "   Duration: ${duration_formatted}s"
        fi
      fi
    fi
  else
    echo "\n❌ ERROR: Failed to assemble final video"
    exit 1
  fi
  
  echo "\n==========================================================="
  echo "BUILD COMPLETE"
  echo "Finished: $(date)"
  echo "===========================================================\n"
else
  echo "\n❌ Cannot assemble final video due to rendering failures"
  echo "Fix errors and re-run: ./render_direct.sh\n"
  exit 1
fi
