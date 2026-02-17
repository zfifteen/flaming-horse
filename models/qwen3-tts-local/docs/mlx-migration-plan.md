# MLX Migration Plan for Qwen3-TTS on Apple Silicon (M1 Max) - Refined v1.2 (Full Review Integration)

## 1. Objective & Scope
- **Goal**: Migrate from PyTorch+MPS/CPU (slow decoder bottleneck, ~70% runtime) to MLX for 12-15x speedup on M1 Max (32GB unified memory). Preserve voice cloning with `voice_ref/ref.wav` (18.76s mono 24kHz math narration) + `ref.txt` (2-sentence transcript).
- **Out of Scope**: No Ollama integration (inefficient for TTS decoder); no iOS port; focus on offline batch narration (not real-time streaming unless requested).
- **Success Metrics**: Speed: <10s per 100-char segment (vs 400s+ CPU). Quality: Manual similarity score >7/10 vs ref (Audacity audit for timbre/prosody); WER <2% on math text (manual transcription). Workflow: Seamless Python API drop-in for caching/batching.
- **Risks/Mitigations**: Env conflicts (isolated venv); cloning fidelity (shorten ref to 3-6s if needed; test multiple refs); memory (4/8-bit quantization, <15GB peak). API changes: Use documented mlx-audio params only (no custom wrappers like instruct or precompute prompts; direct ref_audio/ref_text per call).

## 2. Architecture & Tradeoffs
- **Why MLX?**: Unified memory + fused Metal kernels accelerate conv1d-heavy decoder (45x) and quantizer (3.5x). Matches PyTorch output exactly if SnakeBeta (exp(alpha/beta)) and causal padding ((kernel-1)*dilation left-only) are correct—verified in mlx-community models.
- **Model Choices** (from mlx-community on HF; pin mlx-audio >=0.3.0rc1 via --pre for Qwen3-TTS fixes):
  - **Primary**: Qwen3-TTS-12Hz-1.7B-Base-8bit (~4GB, high fidelity cloning).
  - **Dev/Fast**: Qwen3-TTS-12Hz-0.6B-Base-4bit (~2GB, quick iterations).
  - **Optional Long-Form**: Qwen3-TTS-25Hz-1.7B-Base-4bit (cloning-compatible with ref_audio/ref_text; lowest WER for >5min concat, avoids CustomVoice's baked-in Aiden timbre override).
- **12Hz vs 25Hz Tradeoff**:
  - 12Hz: Low latency (97ms first packet), causal ConvNet decoder, ideal for segmented math videos + cloning. Use for 90% cases.
  - 25Hz: Better long-context stability (WER 1.2-1.5 vs 2.3+), but DiT+BigVGAN adds ~2x latency. Test only on full narrations >5min; use Base variant for your ref cloning (CustomVoice uses fixed speaker, not ref).
- **Quantization Tradeoff**: 8-bit for production (minimal quality loss, consensus for fidelity on finals). 4-bit for batches (faster, slight prosody drop—A/B test in validation; upgrade if audible on math text).
- **Ref Integration**: Pass `ref_audio` + `ref_text` directly to each call (no precompute; overhead <5% for 18s ref). Optional: Create short 3-6s `ref_short.wav` (e.g., trim first sentence via `ffmpeg -i ref.wav -t 6 ref_short.wav`) for faster batches if fidelity holds (test in validation).

## 3. Prerequisites & Setup (30 min)
- **Env Resolution**: Current .venv has transformers=4.57.3 conflict with mlx-audio. Solution: Isolated venv (`mlx_env`) using system python3.
- **Steps**:
  1. Confirm/clean: `cd /Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local && rm -rf mlx_env && ls -la mlx_env` (expect none).
  2. Create/activate: `/usr/bin/python3 -m venv mlx_env && source mlx_env/bin/activate`.
  3. Install: `pip install --upgrade pip && pip install --pre -U mlx-audio soundfile numpy` (pins pre-release for Qwen3-TTS). Verify: `python -c "import mlx_audio; print(mlx_audio.__version__)"` (expect >=0.3.0rc1) or fail/reinstall: `pip install git+https://github.com/Blaizzy/mlx-audio.git`.
  4. Sanity: `python -m mlx_audio.tts.generate --model mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit --text \"Baseline MLX test.\" --file_prefix sanity --verbose` (generates `sanity_000.wav`; time <5s).
- **Hardware Fit**: M1 Max GPU (32-core) + 32GB handles 1.7B-8bit + refs + batch (peak ~12GB); no MPS fallback needed.

## 4. Voice Cloning Validation (20 min)
- **Goal**: Confirm MLX preserves your voice (clear math tone) vs PyTorch baseline. A/B 4-bit vs 8-bit for quantization.
- **Steps**:
  1. Baseline PyTorch: `source .venv/bin/activate && QWEN_TTS_REF_AUDIO=voice_ref/ref.wav QWEN_TTS_REF_TEXT=\"$(cat voice_ref/ref.txt)\" QWEN_TTS_TEXT=\"Test cloning fidelity.\" QWEN_TTS_DEVICE=mps QWEN_TTS_DTYPE=float16 python voice_clone_from_ref.py` (saves `outputs/voice_clone.wav`; ~1-2min on MPS).
  2. MLX Clone (8-bit): In mlx_env, `python -m mlx_audio.tts.generate --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit --text \"Matrices multiply by summing products of corresponding rows and columns.\" --ref_audio voice_ref/ref.wav --ref_text \"$(cat voice_ref/ref.txt)\" --file_prefix clone_validate_8bit --verbose` (saves `clone_validate_8bit_000.wav`; expect <10s).
  3. MLX Clone (4-bit A/B): Repeat with `--model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-4bit --file_prefix clone_validate_4bit`.
  4. Short Ref Test (Optional): If low score, create `ref_short.wav` (3-6s trim), repeat 8-bit test with `--ref_audio ref_short.wav --ref_text \"Welcome to this video on matrix multiplication. Matrices are powerful mathematical tools...\"` (first sentence).
  5. Audit: Manual compare (Audacity: waveforms/spectrograms for timbre/prosody; play for prosody). Score 1-10 similarity. If low: Re-record cleaner ref (higher SNR). Threshold: >7/10 for proceed; prefer 8-bit if audible difference (e.g., prosody on equations).

## 5. Pipeline Integration (45-60 min)
- **Goal**: Drop-in Python service for flaming-horse/Manim caching (pre-generate segments, hash by text+ref+model).
- **Key Changes**: Direct `ref_audio`/`ref_text` per call (no precompute/instruct). Use `join_audio=True` for single WAV. Defensive cache clear. Subprocess for dual-env (isolates deps); optional uv for cross-env run.
- **New File**: `mlx_tts_service.py` (create via Write; run via subprocess from main scripts):
  ```python
  import hashlib
  import json
  import sys
  from pathlib import Path
  import soundfile as sf
  from mlx_audio.tts.utils import load_model
  from mlx_audio.tts.generate import generate_audio
  import mlx.core as mx  # For eval/cache

  # Config (pass via env/args for flexibility)
  MODEL_ID = sys.argv[2] if len(sys.argv) > 2 else "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"
  REF_AUDIO = "/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/voice_ref/ref.wav"
  REF_TEXT = Path(REF_AUDIO.replace('.wav', '.txt')).read_text().strip()
  OUTPUT_DIR = Path("mlx_outputs")
  OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

  # Load once (in subprocess to isolate)
  model = load_model(MODEL_ID)

  def cache_key(text: str) -> str:
      ref_hash = hashlib.md5(Path(REF_AUDIO).read_bytes()).hexdigest()[:8]
      return hashlib.md5(f"{MODEL_ID}:{text}:{ref_hash}".encode()).hexdigest()

  def synthesize_batch(segments: list[dict]) -> list[dict]:  # Returns [{"id": "seg1", "path": Path, "duration": float}]
      results = []
      for seg in segments:
          key = cache_key(seg["text"])
          cached_path = OUTPUT_DIR / f"{key}.wav"
          if cached_path.exists():
              duration = len(sf.read(cached_path)[0]) / 24000
              results.append({"id": seg["id"], "path": cached_path, "duration": duration, "from_cache": True})
              continue
          out_prefix = OUTPUT_DIR / seg["id"]
          generate_audio(
              model=model,
              text=seg["text"],
              ref_audio=REF_AUDIO,
              ref_text=REF_TEXT,
              file_prefix=str(out_prefix),
              audio_format="wav",
              join_audio=True,  # Single WAV, no chunks
              verbose=True,  # Timings
          )
          wav_path = OUTPUT_DIR / f"{seg['id']}_000.wav"
          if not wav_path.exists():
              raise FileNotFoundError(f"No output: {wav_path}")
          # Rename to cache key
          cached_path = OUTPUT_DIR / f"{key}.wav"
          wav_path.rename(cached_path)
          duration = len(sf.read(cached_path)[0]) / 24000
          results.append({"id": seg["id"], "path": cached_path, "duration": duration, "from_cache": False})
          mx.eval(model.parameters())  # Force eval
          if hasattr(mx, "metal") and hasattr(mx.metal, "clear_cache"):
              mx.metal.clear_cache()  # Memory hygiene
      return results

  # Example usage (run via subprocess: mlx_env/bin/python mlx_tts_service.py '[json segments]')
  if __name__ == "__main__":
      segments_str = sys.argv[1] if len(sys.argv) > 1 else json.dumps([{"id": "test1", "text": "Matrix A times B yields C where C_ij = sum(A_ik * B_kj)."}])
      segments = json.loads(segments_str)
      results = synthesize_batch(segments)
      print(json.dumps([{"id": r["id"], "path": str(r["path"]), "duration": r["duration"], "from_cache": r["from_cache"]} for r in results]))
  ```
- **Caching Tie-In**: In existing scripts (e.g., `generate_long_clone.py`), call via subprocess: `subprocess.run(['/path/to/mlx_env/bin/python', 'mlx_tts_service.py', json.dumps(segments)], capture_output=True, text=True)`. Parse JSON output for paths/durations. Key cache by `cache_key(text)` (includes MODEL_ID/ref_hash to avoid silent bugs on swaps). Optional uv: `uv run --with mlx-audio mlx_tts_service.py --segments '[{...}]'`.
- **Error Handling**: Check `wav_path.exists()`; OOM fallback: Pass MODEL_ID=4-bit via arg/env. Log timings; if multi-chunk despite join_audio, warn (rare). Version check in setup prevents API mismatches.

## 6. Benchmark & Optimization (20 min)
- **Test Workload**: 10 math segments (~100 chars each, ref style). Time end-to-end via subprocess.
- **Expected**: Per-segment: 5-15s (12Hz-1.7B-8bit). Batch: <2min total. Compare: Parallel PyTorch; delta >10x confirms.
- **Tune**:
  - If slow: 4-bit via arg; max_tokens=512.
  - Long-Form: Concat, test 25Hz-Base if WER >2% (manual).
  - Streaming: `--stream` for Manim previews (CLI) or API equiv.

## 7. Production Rollout & Revert (15 min)
- **Two-Tier**: 0.6B-4bit dev; 1.7B-8bit finals (A/B in validation).
- **Integration**: Subprocess to mlx_env/bin/python (defensive isolation, no merge); uv as alternative for cross-env.
- **Revert**: `rm -rf mlx_env`; fallback to .venv + PyTorch.
- **Monitoring**: RAM via Activity Monitor; quality via batch A/B (random 5% segments).

## 8. Next Steps
- Execute setup + validation (with A/B quant and short ref optional).
- Integrate via subprocess.
- A/B full video batch.
- If 25Hz needed, swap to Base + re-validate cloning.