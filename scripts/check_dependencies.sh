#!/usr/bin/env bash
# Verify all required dependencies before running pipeline

set -euo pipefail

errors=0

echo "Checking dependencies..."
echo ""

# Python
if command -v python3 >/dev/null; then
  version=$(python3 --version | awk '{print $2}')
  echo "✓ Python $version"
else
  echo "✗ Python 3 not found"
  errors=$((errors+1))
fi

# Manim
if command -v manim >/dev/null; then
  version=$(manim --version 2>&1 | head -1 || echo "unknown")
  echo "✓ Manim ($version)"
else
  echo "✗ Manim not found (install: pip install manim)"
  errors=$((errors+1))
fi

# FFmpeg
if command -v ffmpeg >/dev/null; then
  version=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')
  echo "✓ FFmpeg $version"
else
  echo "✗ FFmpeg not found (install: brew install ffmpeg)"
  errors=$((errors+1))
fi

# Sox
if command -v sox >/dev/null; then
  version=$(sox --version 2>&1 | head -1 | awk '{print $3}')
  echo "✓ Sox $version"
else
  echo "✗ Sox not found (install: brew install sox)"
  errors=$((errors+1))
fi

# Voice reference
if [[ -f "assets/voice_ref/ref.wav" ]] && [[ -f "assets/voice_ref/ref.txt" ]]; then
  echo "✓ Voice reference assets"
else
  echo "✗ Voice reference missing (create: assets/voice_ref/ref.wav + ref.txt)"
  errors=$((errors+1))
fi

# Python packages
if python3 -c "import manim" 2>/dev/null; then
  echo "✓ manim package"
else
  echo "✗ manim package not installed (install: pip install manim)"
  errors=$((errors+1))
fi

if python3 -c "import manim_voiceover_plus" 2>/dev/null; then
  echo "✓ manim-voiceover-plus package"
else
  echo "✗ manim-voiceover-plus not installed (install: pip install manim-voiceover-plus)"
  errors=$((errors+1))
fi

echo ""
if [[ $errors -eq 0 ]]; then
  echo "✅ All dependencies satisfied - ready to build videos"
  exit 0
else
  echo "❌ $errors missing dependencies - see docs/INSTALLATION.md"
  exit 1
fi
