# Flaming Horse Codespace Configuration

Date: 2026-02-14  
Scope: Create a reproducible Flaming Horse test environment in GitHub Codespaces using local Qwen3 TTS on CPU/float32.

---

## 1) Goal and Constraints

This setup aligns with both:

- Your Codespaces Qwen requirements (Python 3.12, CPU, float32, HF cache at `$HOME/.cache/huggingface`)
- Flaming Horse repo policy (cached Qwen audio only, no network TTS fallback)

Important repo behavior to account for:

- `scripts/build_video.sh` forces offline mode:
  - `HF_HUB_OFFLINE=1`
  - `TRANSFORMERS_OFFLINE=1`
- `scripts/prepare_qwen_voice.py` and `scripts/precache_voiceovers_qwen.py` require:
  - `device == "cpu"`
  - `dtype == "float32"`
- If cached audio is missing, scene render fails by design.

So the practical flow is:

1. **One-time online model bootstrap** (download model into HF cache)
2. **Offline Flaming Horse execution** (warmup, precache, render/build)

---

## 2) Codespace Base Setup

Run in repo root (`/workspaces/flaming-horse`).

### 2.1 System packages

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg sox git curl
```

Notes:

- `ffmpeg` is required by precache worker (WAV -> MP3 conversion) and final assembly.
- `sox` is helpful for voice-related tooling and optional mock flows.

### 2.2 Python environment (3.12)

Create a dedicated venv for Qwen runtime (matching your local pattern):

```bash
python3.12 -m venv "$HOME/qwen3-tts-local/.venv"
source "$HOME/qwen3-tts-local/.venv/bin/activate"
python -m pip install --upgrade pip wheel setuptools
```

Install runtime dependencies used by this repo’s Qwen workers:

```bash
pip install torch soundfile qwen-tts
```

Install Flaming Horse Python dependencies into the same venv:

```bash
pip install manim manim-voiceover-plus numpy moviepy
```

---

## 3) Environment Variables (Session)

Export your baseline config:

```bash
export HF_HOME="$HOME/.cache/huggingface"
export HF_HUB_ENABLE_HF_TRANSFER=1

export QWEN_TTS_MODEL="Qwen/Qwen3-TTS-12Hz-1.7B-Base"
export QWEN_TTS_DEVICE="cpu"
export QWEN_TTS_DTYPE="float32"

export QWEN_TTS_MAX_NEW_TOKENS=256
export QWEN_TTS_DO_SAMPLE=0
export QWEN_TTS_TEMPERATURE=0.7
export QWEN_TTS_TOP_P=0.9
export QWEN_TTS_REPETITION_PENALTY=1.05
export QWEN_TTS_INSTRUCT="Speak in clear English only. Do not switch languages."

export QWEN_TTS_SPEAKER="Ryan"
export QWEN_TTS_LANG="English"
export QWEN_TTS_TEXT="This is a local Qwen3 TTS smoke test running in Codespaces."
```

Optional persistence for future shells:

```bash
cat >> ~/.bashrc <<'EOF'
export HF_HOME="$HOME/.cache/huggingface"
export HF_HUB_ENABLE_HF_TRANSFER=1
export QWEN_TTS_MODEL="Qwen/Qwen3-TTS-12Hz-1.7B-Base"
export QWEN_TTS_DEVICE="cpu"
export QWEN_TTS_DTYPE="float32"
EOF
```

---

## 4) One-Time Online Model Bootstrap

Because Flaming Horse runs offline during build, do this once while internet access to Hugging Face is available.

### 4.1 Verify HF cache location

```bash
python - <<'PY'
import os
print("HF_HOME=", os.environ.get("HF_HOME"))
PY
```

Expected: `HF_HOME=/home/codespace/.cache/huggingface` (or your Codespace user path).

### 4.2 Trigger model download into local cache

Use your smoke test script below (Section 5). The first successful load will populate:

- `$HF_HOME/hub/models--Qwen--Qwen3-TTS-12Hz-1.7B-Base/...`

---

## 5) Qwen Smoke Test (`outputs/custom_voice.wav`)

This verifies the exact requirements you listed.

### 5.1 Run smoke test

```bash
source "$HOME/qwen3-tts-local/.venv/bin/activate"
python3 scripts/qwen_codespace_smoke_test.py
```

Success criteria:

- File exists: `outputs/custom_voice.wav`
- Command exits with code `0`
- Prints model/device/dtype/knobs/elapsed time

Script location:

- `scripts/qwen_codespace_smoke_test.py`

Failure behavior:

- Any model load or generation error should fail non-zero and print exact exception.

---

## 6) Configure Flaming Horse to Use This Environment

### 6.1 Create or select a project

```bash
./scripts/new_project.sh codespace-test --topic "Explain square roots"
```

Project path:

- `projects/codespace-test`

### 6.2 Update project voice config

Edit:

- `projects/codespace-test/voice_clone_config.json`

Set:

```json
{
  "qwen_python": "~/qwen3-tts-local/.venv/bin/python",
  "model_id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
  "device": "cpu",
  "dtype": "float32",
  "language": "English",
  "ref_audio": "assets/voice_ref/ref.wav",
  "ref_text": "assets/voice_ref/ref.txt",
  "output_dir": "media/voiceovers/qwen"
}
```

### 6.3 Verify project voice reference assets

Required files:

- `projects/codespace-test/assets/voice_ref/ref.wav`
- `projects/codespace-test/assets/voice_ref/ref.txt`

If they are missing or not your intended voice, replace them before warmup/precache.

---

## 7) Warmup + Precache (Repo-Aligned)

### 7.1 Warmup Qwen (recommended)

```bash
source "$HOME/qwen3-tts-local/.venv/bin/activate"
python3 scripts/prepare_qwen_voice.py --project-dir projects/codespace-test
```

Expected artifact:

- `projects/codespace-test/media/voiceovers/qwen/ready.json`

### 7.2 Precache narration audio

Requires `narration_script.py` to exist for the project.

```bash
python3 scripts/precache_voiceovers_qwen.py projects/codespace-test
```

Expected artifacts:

- `projects/codespace-test/media/voiceovers/qwen/cache.json`
- `projects/codespace-test/media/voiceovers/qwen/*.mp3`

### 7.3 Run integration preflight (recommended)

This validates config/assets/cache and can run prepare+precache in one command.

```bash
python3 scripts/qwen_pipeline_preflight.py \
    --project-dir projects/codespace-test \
    --run-prepare \
    --run-precache
```

Script location:

- `scripts/qwen_pipeline_preflight.py`

---

## 8) Validate Environment Before Full Build

### 8.1 Quick policy checks

```bash
python3 - <<'PY'
import json
from pathlib import Path

cfg = json.loads(Path('projects/codespace-test/voice_clone_config.json').read_text())
assert cfg['device'] == 'cpu'
assert cfg['dtype'] == 'float32'
print('voice_clone_config: cpu/float32 ✅')
PY
```

### 8.2 Verify HF cache contains model snapshot

```bash
find "$HF_HOME/hub" -maxdepth 3 -type d -name "models--Qwen--Qwen3-TTS-12Hz-1.7B-Base" -print
```

### 8.3 Verify cached audio exists

```bash
test -f projects/codespace-test/media/voiceovers/qwen/cache.json && echo "cache.json ✅"
ls -1 projects/codespace-test/media/voiceovers/qwen/*.mp3 | head
```

---

## 9) Running Flaming Horse in Codespaces

### Option A: Full agent-driven pipeline

```bash
./scripts/build_video.sh projects/codespace-test
```

Prerequisites:

- Agent CLI path used by this repo (`opencode`) must be installed and authenticated.
- Project must have valid `topic`, voice refs, and cached model availability.

### Option B: Framework test without end-to-end agent orchestration

Useful when agent CLI is not configured yet:

1. Use an existing project that already contains scene files and narration.
2. Run warmup + precache.
3. Render a scene manually with Manim to verify voice cache integration.

Example:

```bash
cd projects/123-square-roots
python3 ../../scripts/prepare_qwen_voice.py --project-dir .
python3 ../../scripts/precache_voiceovers_qwen.py .
manim render scene_01_intro.py Scene01Intro -ql
```

---

## 10) Common Failure Modes and Fixes

1. **`Qwen model snapshot not found in local HuggingFace cache`**
   - Cause: Offline scripts running before model is downloaded.
   - Fix: Run Section 5 smoke test once with network access.

2. **`qwen_python not found`**
   - Cause: `voice_clone_config.json` points to wrong venv path.
   - Fix: Set `qwen_python` to `~/qwen3-tts-local/.venv/bin/python`.

3. **`Missing ref audio/ref text`**
   - Cause: Missing `assets/voice_ref` files.
   - Fix: Provide explicit `ref.wav` and matching transcript `ref.txt`.

4. **Build fails for missing cached audio**
   - Cause: `precache_voiceovers_qwen.py` not run (or narration changed after precache).
   - Fix: Re-run precache for the project.

5. **CPU generation appears slow/hung**
   - Cause: Expected CPU behavior for Qwen TTS.
   - Fix: Keep test text short and `QWEN_TTS_MAX_NEW_TOKENS` low (e.g., 128-256).

---

## 11) Recommended Day-1 Bring-Up Checklist

- [ ] Create Python 3.12 venv at `~/qwen3-tts-local/.venv`
- [ ] Install `torch`, `qwen-tts`, `soundfile`, `manim`, `manim-voiceover-plus`
- [ ] Export HF + Qwen env vars
- [ ] Run smoke test and confirm `outputs/custom_voice.wav`
- [ ] Create test project with `new_project.sh`
- [ ] Verify `voice_clone_config.json` points to Codespace venv
- [ ] Confirm `assets/voice_ref/ref.wav` + `ref.txt`
- [ ] Run `prepare_qwen_voice.py`
- [ ] Run `precache_voiceovers_qwen.py`
- [ ] Run `build_video.sh` (or manual scene render if agent CLI unavailable)

---

## 12) Notes on Policy Consistency

This repo contains mock-voice docs and helpers, but core policy/docs for production pipeline require cached Qwen voice without fallback. For this Codespace test environment, keep focus on the strict cached-Qwen path above so behavior matches the enforced build scripts and project expectations.
