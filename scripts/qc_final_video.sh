#!/bin/bash
# qc_final_video.sh - MANDATORY quality control before declaring success

VIDEO="$1"
PROJECT_DIR="$2"

if [[ -z "$VIDEO" ]] || [[ -z "$PROJECT_DIR" ]]; then
    echo "Usage: $0 <video_file> <project_dir>"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════"
echo "QUALITY CONTROL - Final Video Verification"
echo "═══════════════════════════════════════════════════════════════"

FAIL=0

# Test 1: File exists and has size > 0
if [[ ! -f "$VIDEO" ]] || [[ ! -s "$VIDEO" ]]; then
    echo "❌ Video file missing or empty"
    exit 1
fi
echo "✅ Video file exists ($(ls -lh "$VIDEO" | awk '{print $5}'))"

# Test 2: Get total duration
TOTAL_DURATION=$(ffprobe "$VIDEO" 2>&1 | grep "Duration:" | head -1 | awk '{print $2}' | tr -d ',')
if [[ -z "$TOTAL_DURATION" ]]; then
    echo "❌ Could not determine video duration"
    exit 1
fi
echo "✅ Total duration: $TOTAL_DURATION"

# Test 3: Extract full audio track
ffmpeg -i "$VIDEO" -vn -acodec copy "${PROJECT_DIR}/qc_audio.aac" -y &>/dev/null
if [[ ! -f "${PROJECT_DIR}/qc_audio.aac" ]]; then
    echo "❌ Could not extract audio track (video may have no audio)"
    FAIL=1
else
    AUDIO_DURATION=$(ffprobe "${PROJECT_DIR}/qc_audio.aac" 2>&1 | grep "Duration:" | awk '{print $2}' | tr -d ',')
    echo "Audio track duration: $AUDIO_DURATION"
    
    # Test 4: Compare audio vs video duration (must be within 90%)
    # Convert HH:MM:SS.ms to seconds
    VIDEO_SEC=$(echo "$TOTAL_DURATION" | awk -F: '{print ($1 * 3600) + ($2 * 60) + $3}')
    AUDIO_SEC=$(echo "$AUDIO_DURATION" | awk -F: '{print ($1 * 3600) + ($2 * 60) + $3}')
    
    # Calculate ratio (audio/video)
    RATIO=$(echo "scale=2; $AUDIO_SEC / $VIDEO_SEC" | bc -l 2>/dev/null || echo "0")
    
    if (( $(echo "$RATIO < 0.90" | bc -l) )); then
        echo "❌ CRITICAL: Audio is only ${RATIO}x the video duration"
        echo "   This indicates significant dead air / missing voiceover"
        FAIL=1
    else
        echo "✅ Audio coverage: ${RATIO}x (good)"
    fi
fi

# Test 5: Check for audio silence (advanced)
# Extract waveform, look for long stretches of near-zero amplitude
echo ""
echo "Checking for silent gaps..."
SILENCE_COUNT=0
while IFS= read -r line; do
    if echo "$line" | grep -q "silence_duration"; then
        duration=$(echo "$line" | grep -oE 'silence_duration: [0-9]+\.[0-9]+' | awk '{print $2}')
        if (( $(echo "$duration > 3.0" | bc -l 2>/dev/null || echo "0") )); then
            echo "⚠️  WARNING: Found ${duration}s of silence in video"
            echo "   May indicate voiceover sync issues"
            SILENCE_COUNT=$((SILENCE_COUNT + 1))
        fi
    fi
done < <(ffmpeg -i "$VIDEO" -af "silencedetect=n=-50dB:d=2" -f null - 2>&1)

if [[ $SILENCE_COUNT -gt 0 ]]; then
    echo "⚠️  Found $SILENCE_COUNT silent gap(s) > 3 seconds"
else
    echo "✅ No significant silent gaps detected"
fi

# Test 6: Verify audio codec
AUDIO_CODEC=$(ffprobe "$VIDEO" 2>&1 | grep "Stream.*Audio" | awk '{print $8}' | head -1)
if [[ -z "$AUDIO_CODEC" ]]; then
    echo "❌ No audio stream found"
    FAIL=1
else
    echo "✅ Audio codec: $AUDIO_CODEC"
fi

# Test 7: Check each scene's audio individually
echo ""
echo "Per-scene audio verification:"
SCENE_FAIL=0
SEEN_SCENES_FILE="$(mktemp "${TMPDIR:-/tmp}/fh_qc_seen.XXXXXX")"
for scene_video in "${PROJECT_DIR}"/media/videos/scene_*/1440p60/*.mp4 "${PROJECT_DIR}"/media/videos/s*/1440p60/*.mp4; do
    [[ -f "$scene_video" ]] || continue
    if grep -Fqx "$scene_video" "$SEEN_SCENES_FILE"; then
        continue
    fi
    printf '%s\n' "$scene_video" >> "$SEEN_SCENES_FILE"
    
    scene_name=$(basename "$scene_video" .mp4)
    scene_dur=$(ffprobe "$scene_video" 2>&1 | grep "Duration:" | head -1 | awk '{print $2}' | tr -d ',')
    
    # Extract just audio
    ffmpeg -i "$scene_video" -vn -acodec copy "/tmp/${scene_name}_audio.aac" -y &>/dev/null
    
    if [[ -f "/tmp/${scene_name}_audio.aac" ]]; then
        audio_dur=$(ffprobe "/tmp/${scene_name}_audio.aac" 2>&1 | grep "Duration:" | awk '{print $2}' | tr -d ',')
        
        echo "  $scene_name: video=$scene_dur, audio=$audio_dur"
        
        # Check ratio
        v_sec=$(echo "$scene_dur" | awk -F: '{print ($1 * 3600) + ($2 * 60) + $3}')
        a_sec=$(echo "$audio_dur" | awk -F: '{print ($1 * 3600) + ($2 * 60) + $3}')
        ratio=$(echo "scale=2; $a_sec / $v_sec" | bc -l 2>/dev/null || echo "0")
        
        if (( $(echo "$ratio < 0.90" | bc -l 2>/dev/null || echo "0") )); then
            echo "    ❌ Audio only ${ratio}x of video - SYNC ISSUE!"
            SCENE_FAIL=1
        fi
        
        rm -f "/tmp/${scene_name}_audio.aac"
    else
        echo "  $scene_name: ⚠️  Could not extract audio"
    fi
done

if [[ $SCENE_FAIL -gt 0 ]]; then
    echo "❌ Some scenes have audio/video sync issues"
    FAIL=1
fi

# Cleanup
rm -f "${PROJECT_DIR}/qc_audio.aac"
rm -f "$SEEN_SCENES_FILE"

echo ""
echo "═══════════════════════════════════════════════════════════════"
if [[ $FAIL -eq 0 ]]; then
    echo "✅ QUALITY CONTROL PASSED"
    echo "Video is ready for delivery"
    exit 0
else
    echo "❌ QUALITY CONTROL FAILED"
    echo "Video has issues that must be fixed"
    exit 1
fi
