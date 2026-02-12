#!/usr/bin/env bash
set -euo pipefail

echo "==========================================================="
echo "Rendering Chandler Wobble Diagnostic Video"
echo "Project: chandler_wobble_diagnostic"
echo "Started: $(date)"
echo "===========================================================\n"

# Navigate to project directory
cd "$(dirname "$0")"

# Check for ELEVENLABS_API_KEY
if [[ -z "${ELEVENLABS_API_KEY:-}" ]]; then
  echo "❌ ERROR: ELEVENLABS_API_KEY environment variable not set"
  echo "Please set it with: export ELEVENLABS_API_KEY='your_key'"
  exit 1
fi

echo "✓ ElevenLabs API key found\n"

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

# Render each scene
for i in "${!SCENES[@]}"; do
  IFS=':' read -r scene_file scene_class <<< "${SCENES[$i]}"
  scene_num=$((i + 1))
  
  echo "\n───────────────────────────────────────────────────────────"
  echo "🎥 Rendering Scene $scene_num/8: $scene_class"
  echo "   File: $scene_file"
  echo "───────────────────────────────────────────────────────────"
  
  # Render with manim
  if manim render "$scene_file" "$scene_class" -qh --disable_caching; then
    echo "✓ Scene $scene_num rendered successfully"
  else
    echo "❌ ERROR: Failed to render scene $scene_num"
    exit 1
  fi
done

echo "\n\n==========================================================="
echo "✅ All scenes rendered successfully!"
echo "===========================================================\n"

# Now assemble the final video
echo "🎬 Assembling final video...\n"

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
  echo "\n🎉 OUTPUT: final_video.mp4"
  
  # Get file size
  if [[ -f "final_video.mp4" ]]; then
    file_size=$(du -h final_video.mp4 | cut -f1)
    echo "   Size: $file_size"
  fi
else
  echo "\n❌ ERROR: Failed to assemble final video"
  exit 1
fi

echo "\n==========================================================="
echo "BUILD COMPLETE"
echo "Finished: $(date)"
echo "===========================================================\n"
