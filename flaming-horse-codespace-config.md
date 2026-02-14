# Flaming Horse Codespace Configuration

Date: 2026-02-14  
Scope: reproducible Codespaces rebuild for Flaming Horse with local cached Qwen voice (CPU + float32), matching current scripts.

---

## 1) What this setup must satisfy

This document reflects the current behavior in:

- `scripts/create_video.sh`
- `scripts/build_video.sh`
- `scripts/new_project.sh`
- `scripts/prepare_qwen_voice.py`
- `scripts/precache_voiceovers_qwen.py`

Hard requirements enforced by the codebase:

- Qwen voice must run as local cached model, not network TTS.
- Voice config must be CPU + float32.
- Build flow runs offline for Hugging Face/Transformers.
- Each project must have `voice_clone_config.json` and `assets/voice_ref/ref.wav` + `assets/voice_ref/ref.txt`.
- `manim` must be on PATH for build/validation phases.
- `opencode` CLI must be available for full end-to-end agent phases.

---

## 2) Rebuild from a fresh Codespace

Run from repo root: `/workspaces/flaming-horse`.

### 2.1 System packages

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg sox git curl
```

### 2.2 Python venv for Qwen + Manim runtime

```bash
python3 -m venv "$HOME/qwen3-tts-local/.venv"
source "$HOME/qwen3-tts-local/.venv/bin/activate"
python -m pip install --upgrade pip wheel setuptools
pip install torch soundfile qwen-tts manim manim-voiceover-plus numpy moviepy
```

Quick check:

```bash
/home/codespace/qwen3-tts-local/.venv/bin/python -c "import manim; print(manim.__version__)"
```

---

## 3) Environment wiring used by this repo

### 3.1 Repo-level `.env`

The build scripts source `.env` automatically. Keep these values present:

```dotenv
AGENT_MODEL=xai/grok-4-1-fast
PROJECTS_BASE_DIR=/workspaces/flaming-horse/projects
PROJECT_DEFAULT_NAME=default_video
MAX_RUNS=50
PHASE_RETRY_LIMIT=4
PHASE_RETRY_BACKOFF_SECONDS=5
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
TOKENIZERS_PARALLELISM=false
PATH=/home/codespace/qwen3-tts-local/.venv/bin:$PATH
PYTHONPATH=/workspaces/flaming-horse:${PYTHONPATH:-}
```

### 3.2 Shell persistence (`~/.bashrc`)

Add this once so new terminals have `manim` and repo imports available:

```bash
cat >> ~/.bashrc <<'EOF'
if [[ ":$PATH:" != *":/home/codespace/qwen3-tts-local/.venv/bin:"* ]]; then
   export PATH="/home/codespace/qwen3-tts-local/.venv/bin:$PATH"
fi
case ":${PYTHONPATH:-}:" in
   *":/workspaces/flaming-horse:"*) ;;
   *) export PYTHONPATH="/workspaces/flaming-horse${PYTHONPATH:+:$PYTHONPATH}" ;;
esac
EOF
source ~/.bashrc
```

---

## 4) One-time Qwen model bootstrap (online)

`build_video.sh` and `create_video.sh` enforce offline mode during pipeline runs, so model weights must be cached first.

### 4.1 Set Hugging Face cache location

```bash
export HF_HOME="$HOME/.cache/huggingface"
export HF_HUB_ENABLE_HF_TRANSFER=1
```

### 4.2 Download model into local HF cache

```bash
source "$HOME/qwen3-tts-local/.venv/bin/activate"
HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0 \
python - <<'PY'
from qwen_tts import Qwen3TTSModel
import torch

Qwen3TTSModel.from_pretrained(
      "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
      device_map="cpu",
      dtype=torch.float32,
)
print("Qwen model cached successfully")
PY
```

Verify:

```bash
find "$HF_HOME/hub" -maxdepth 3 -type d -name "models--Qwen--Qwen3-TTS-12Hz-1.7B-Base" -print
```

---

## 5) Smoke test the Qwen runtime in Codespaces

Script: `scripts/qwen_codespace_smoke_test.py`

Required environment (this script enforces them):

```bash
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

If your installed `qwen_tts` runtime needs voice-clone mode, also set:

```bash
export QWEN_TTS_REF_AUDIO="/workspaces/flaming-horse/projects/matrix-multiplication/assets/voice_ref/ref.wav"
export QWEN_TTS_REF_TEXT="/workspaces/flaming-horse/projects/matrix-multiplication/assets/voice_ref/ref.txt"
```

Run:

```bash
source "$HOME/qwen3-tts-local/.venv/bin/activate"
python3 scripts/qwen_codespace_smoke_test.py
```

Success artifact: `outputs/custom_voice.wav`

---

## 6) Integrate Qwen into a project (framework path)

### 6.1 Create project with topic

```bash
./scripts/new_project.sh codespace-test --topic "Explain square roots"
```

This creates:

- `projects/codespace-test/project_state.json`
- `projects/codespace-test/voice_clone_config.json`
- `projects/codespace-test/assets/voice_ref/ref.wav`
- `projects/codespace-test/assets/voice_ref/ref.txt`

### 6.2 Confirm voice config

`projects/codespace-test/voice_clone_config.json` must keep:

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

### 6.3 Warmup + precache

```bash
python3 scripts/prepare_qwen_voice.py --project-dir projects/codespace-test
python3 scripts/precache_voiceovers_qwen.py projects/codespace-test
```

Expected outputs:

- `projects/codespace-test/media/voiceovers/qwen/ready.json`
- `projects/codespace-test/media/voiceovers/qwen/cache.json`
- `projects/codespace-test/media/voiceovers/qwen/*.mp3`

### 6.4 Optional integrated validator

```bash
python3 scripts/qwen_pipeline_preflight.py \
   --project-dir projects/codespace-test \
   --run-prepare \
   --run-precache
```

---

## 7) Full pipeline usage in Codespaces

Preferred end-user entry point:

```bash
./scripts/create_video.sh codespace-test --topic "Explain square roots"
```

This wrapper does:

1. project creation/resume
2. voice service preparation
3. full `build_video.sh` orchestration

Direct orchestration path:

```bash
./scripts/build_video.sh projects/codespace-test
```

Prerequisites for end-to-end run:

- `opencode` installed and authenticated
- API credential configured for your selected `AGENT_MODEL`
- Qwen model already cached locally

---

## 8) Common failure modes and exact fixes

1) `manim not found in PATH`

- Cause: venv bin not exported in current shell.
- Fix: source venv or set PATH in `.env` and `~/.bashrc` as above.

2) `Qwen model snapshot not found in local HuggingFace cache`

- Cause: offline pipeline before model bootstrap.
- Fix: perform Section 4 one-time online download.

3) `qwen_python not found`

- Cause: bad path in `voice_clone_config.json`.
- Fix: set to `~/qwen3-tts-local/.venv/bin/python`.

4) Missing reference assets

- Cause: no `assets/voice_ref/ref.wav` or `ref.txt` in project.
- Fix: restore these files in project and rerun warmup/precache.

5) Import failure for `flaming_horse_voice`

- Cause: repo root not on PYTHONPATH in shell/tooling.
- Fix: ensure `PYTHONPATH=/workspaces/flaming-horse:${PYTHONPATH:-}` via `.env` or shell startup.

6) Precache/build fails after narration changes

- Cause: stale cached voice files.
- Fix: rerun `scripts/precache_voiceovers_qwen.py <project_dir>`.

---

## 9) Day-1 verification checklist

- [ ] Qwen/Manim venv exists at `~/qwen3-tts-local/.venv`
- [ ] `manim` import works from venv python
- [ ] `.env` contains PATH/PYTHONPATH + retry/offline settings
- [ ] Shell startup includes PATH/PYTHONPATH persistence
- [ ] Qwen model exists in local HF cache
- [ ] Smoke test writes `outputs/custom_voice.wav`
- [ ] Project has `voice_clone_config.json` with CPU + float32
- [ ] Project has `assets/voice_ref/ref.wav` and `ref.txt`
- [ ] Warmup writes `ready.json`
- [ ] Precache writes `cache.json` and MP3 files
- [ ] `create_video.sh` can start and progress phases

---

## 10) Notes

- The repository also has mock voice paths for development, but production path in this Codespace guide is strict cached Qwen.
- If you only need pipeline readiness checks without a full agent run, use `scripts/qwen_pipeline_preflight.py` and a manual single-scene `manim render`.
