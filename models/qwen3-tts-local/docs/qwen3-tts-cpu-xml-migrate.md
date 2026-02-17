<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## Qwen3‑TTS Inference: Migration from CPU/Ollama to MLX on Apple Silicon

### 1. Objective and Context

Qwen3‑TTS is a multi‑stage, multilingual TTS system with 3‑second voice cloning, instruction‑driven voice design, and streaming support. Your current setup runs Qwen3‑TTS locally on an M1 Max MacBook Pro (10‑core CPU, 32GB unified memory), with inference going through CPU and/or Ollama, which you have found effective but slow for batch video narration. The goal is to migrate inference to MLX on Apple Silicon to achieve practical throughput for long‑form, high‑quality narration, while preserving your cloned voice and existing caching architecture.[^1][^2][^3][^4]

***

### 2. Qwen3‑TTS Architecture in Inference Terms

#### 2.1 Model family and variants

Qwen3‑TTS ships two main tokenizer tracks, each with 0.6B and 1.7B LM sizes:[^2][^1]


| Track | Tokenizer | Token rate | Decoder type | Typical use |
| :-- | :-- | :-- | :-- | :-- |
| 25Hz | Qwen‑TTS‑Tokenizer‑25Hz | 25 fps | DiT (Flow Matching) → BigVGAN | Long‑form stability, SOTA WER |
| 12Hz | Qwen‑TTS‑Tokenizer‑12Hz | 12.5 fps | Causal ConvNet | Ultra‑low latency, streaming, cloning |

Core properties:[^1][^2]

- Dual‑track LM: concatenates text and acoustic tokens, enabling real‑time prediction of acoustic tokens as text arrives.
- Two tokenizers: 25Hz single‑codebook (semantic+acoustic) and 12Hz multi‑codebook RVQ (1 semantic + 15 acoustic layers).
- Speaker encoder: joint training for identity control and voice cloning.


#### 2.2 Inference pipeline stages

Conceptual inference stack:

1. Text tokenization
    - Standard Qwen tokenizer over input text.[^1]
    - Negligible compute cost.
2. Autoregressive LM (Qwen3 backbone)
    - Processes dual‑track sequence: text tokens + prior acoustic tokens.[^1]
    - For 12Hz: Multi‑Token Prediction (MTP) produces all residual RVQ codebooks per frame.
3. Code‑to‑waveform decoder
    - 25Hz: codes → DiT (block‑wise Flow Matching) → mel spectrogram → BigVGAN vocoder.[^5][^1]
    - 12Hz: RVQ codes → lightweight causal ConvNet directly to waveform.[^5][^1]
4. Output
    - PCM waveform (typically 24kHz), saved as WAV/other formats via library code.[^6][^7][^8]

Profiling on Apple Silicon CPU shows the Audio Decoder conv1d path dominating runtime:

- conv1d in Audio Decoder: 28.0s out of 39.7s, about **71%** of total time.[^9][^10]
- Quantizer decode: 13.8% of runtime.[^10][^9]
- Remaining transformer + glue: ~15% of runtime.[^9][^10]

This profile explains your observed “it works but it’s slow” behavior when running CPU‑bound.[^10][^9]

***

### 3. CPU / Ollama Baseline and Limitations

#### 3.1 CPU runtime characteristics

Measured on an M3 Air 8GB (CPU‑bound):[^10][^9]


| Text length | PyTorch CPU total | Notes |
| :-- | :-- | :-- |
| 5 chars | 16s | Short test |
| 28 chars | 98s | “Unusable” latency |
| 97 chars | 462s | >7 minutes |

Key observations:[^9][^10]

- Audio Decoder conv1d (14‑layer stack with upsample blocks and ConvNeXt units) is the primary bottleneck.
- Quantizer further adds significant overhead.
- LM backbone is a secondary, but not dominant, contributor.


#### 3.2 PyTorch MPS constraints

For some conv1d shapes, the PyTorch MPS backend historically had channel count limitations (e.g., 65536 channels), blocking GPU execution for certain decoder layers on older macOS versions. The optimization report notes that MPS becomes viable on macOS 15.1+, but chose MLX to simplify and future‑proof Apple Silicon acceleration.[^10][^9]

#### 3.3 Ollama’s fit for Qwen3‑TTS

Ollama and llama.cpp are optimized for text LLMs, where the heavy compute is attention + FFN in the transformer. Qwen3‑TTS’s dominant cost is the audio decoder, which:

- Is not part of the standard LLaMA‑style transformer stack.
- Is unlikely to benefit from Ollama’s Metal kernels for the LM backbone.
- Therefore often falls back to CPU, leaving 70%+ of the pipeline unaccelerated.[^9][^10]

Net result: even if Ollama accelerates the LM, the end‑to‑end TTS latency remains CPU‑dominated.

***

### 4. MLX Execution Model and Performance Gains

#### 4.1 MLX on Apple Silicon: key properties

MLX is Apple’s tensor framework tuned for M‑series chips:[^3][^11]

- **Unified memory**: CPU and GPU share 32GB unified memory on M1 Max, avoiding explicit host/device copies.
- **Lazy evaluation**: builds expression graphs and fuses ops, then schedules to Metal GPU kernels at eval boundaries.
- **Automatic device placement**: ops run on CPU or GPU as appropriate without manual `.to(device)` calls.

For Qwen3‑TTS, this maps well onto:

- LM backbone: GPU‑accelerated attention and FFN with fused kernels.
- Audio decoder: conv1d heavy, ideal for GPU parallelism with large channel counts.
- Quantizer: vectorized operations with EMA‑based codebook reconstructions.[^10][^9]


#### 4.2 Decoder and quantizer MLX port

The Apple Silicon optimization work details the Audio Decoder architecture:[^9][^10]

- Pre‑conv: 1×1 convolution projecting hidden states.
- Upsample blocks ×4: each block contains
    - Transposed conv (upsampling).
    - ConvNeXt block with depthwise conv (7×1 kernel), SnakeBeta activation, pointwise convs.
- Post‑conv: final conv to waveform.

Key implementation pitfalls during MLX port:[^10][^9]

- **SnakeBeta activation**
    - α, β stored as log‑scale parameters: weights contain log(α), log(β).
    - Correct MLX loading requires `alpha = mx.exp(weights["alpha"])` and similarly for β.
    - Missing exp leads to silent or unstable outputs.
- **Causal convolution padding**
    - Causal conv must not use future context.
    - Correct padding: `padding = (kernel_size - 1) * dilation` applied on the left only.
    - Incorrect padding yields phase‑shifted or noisy audio.
- **Weight loading indentation bug**
    - Bias and weight assignments must be outside conditional blocks for optional parameters.
    - A misplaced indent caused only the final decoder layer to get proper bias, degrading quality.
- **Quantizer EMA codebook reconstruction**
    - Codebook learned via EMA: weights contain `embedding_sum` and `cluster_usage`.
    - Correct recon: `embedding = embedding_sum / cluster_usage.reshape(-1, 1)`.
    - Also renaming and reshaping embed → embedding.

All of these were resolved in the MLX implementation, enabling correct and fast audio decoding.[^9][^10]

#### 4.3 Measured speedups with MLX

Benchmarks on M3 Air 8GB for a “hybrid” pipeline (decoder + quantizer in MLX, LM still in PyTorch):[^10][^9]

**Component‑level:**


| Component | PyTorch CPU | MLX | Speedup |
| :-- | :-- | :-- | :-- |
| Audio Decoder | 93.85s | 2.07s | **45.3x** |
| Quantizer | 47.56s | 13.55s | **3.5x** |

**End‑to‑end pipeline:**


| Text length | PyTorch CPU | MLX hybrid | Speedup |
| :-- | :-- | :-- | :-- |
| 5 chars | 16s | ~3s | ~5x |
| 28 chars | 98s | ~8s | ~12x |
| 97 chars | 462s | 31s | **14.8x** |

On your M1 Max (32‑core GPU vs 8‑core on M3 Air), you should expect comparable or better end‑to‑end speedups for decoder‑dominated workloads, while LM speedups may be modestly above the published numbers due to higher GPU compute and memory bandwidth.[^12][^13][^14]

***

### 5. MLX‑Native Runtime: mlx‑audio + mlx‑community Models

#### 5.1 mlx‑audio library

`mlx-audio` is an open‑source library built on MLX for TTS, STT, and STS on Apple Silicon:[^15][^16][^3]

- Supports Qwen3‑TTS and other TTS models.
- Provides CLI, Python API, web UI, and REST API interfaces.
- Handles model loading, voice cloning, streaming, quantization, and audio output.

Installation example:[^3][^15]

```bash
pip install -U mlx-audio
```

Core Python usage pattern (simplified):[^7][^8][^6]

```python
from mlx_audio.tts.utils import load_model
from mlx_audio.tts.generate import generate_audio

model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit")

generate_audio(
    model=model,
    text="Hello, this is a test.",
    ref_audio="path_to_audio.wav",  # optional voice cloning
    file_prefix="test_audio",
)
```

CLI example with voice cloning and playback:[^8][^17][^18]

```bash
python -m mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit \
  --text "Hello, this is a test." \
  --ref_audio voice.wav \
  --ref_text "Transcript of the reference audio." \
  --play
```


#### 5.2 MLX‑converted Qwen3‑TTS checkpoints

The `mlx-community` org on Hugging Face hosts pre‑converted, quantized Qwen3‑TTS models tailored for MLX + mlx‑audio:[^11][^19]

Representative entries:

- `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` (full precision)[^20]
- `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit` (4‑bit quantized)[^6]
- `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit`[^21][^8]
- `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit/6bit/8bit`[^22][^23][^24]
- `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit`[^25][^26]

All model cards document consistent CLI and Python usage with `mlx_audio.tts.generate` and `generate_audio`.[^23][^27][^7][^8][^22][^6]

For your 32GB M1 Max:

- **Development / integration**: 0.6B 4‑bit or 8‑bit (fast, small footprint).[^8][^6]
- **Production narration**: 1.7B VoiceDesign or CustomVoice 4‑bit or 6‑bit for best quality.[^24][^28][^22]

***

### 6. 12Hz vs 25Hz for Your Workload

#### 6.1 12Hz track

Characteristics:[^5][^1]

- 12.5 Hz multi‑codebook tokenizer (semantic + 15 acoustic RVQ layers).
- Causal ConvNet decoder, no DiT or BigVGAN.
- Fully causal streaming, extremely low end‑to‑end latency (first packet ~97ms for 0.6B).[^29][^1]
- Strong zero‑shot voice cloning and controllable speech metrics.

Recommended for:

- Streaming or near‑real‑time applications.
- Short to medium narration segments.
- Workflows emphasizing voice cloning and instruction‑based voice design.


#### 6.2 25Hz track

Characteristics:[^5][^1]

- 25 Hz single‑codebook tokenizer with semantic+acoustic content.
- Diffusion Transformer (DiT) with Flow Matching for mel reconstruction.
- BigVGAN for waveform, uses chunked streaming with look‑ahead (DiT + vocoder).
- In long‑speech benchmarks, 25Hz‑1.7B‑CustomVoice achieves the lowest WER for >10 minute sequences (e.g., ~1.517 zh / 1.225 en).[^1]

Recommended when:

- You need maximum stability over >10 minute continuous speech.
- You are willing to trade some latency for long‑context robustness.

Given your current workflow (many segments of math narration rather than a single unbroken 10‑minute take), 12Hz‑1.7B‑4bit is usually the better default. You can A/B test 25Hz on your longest segments if you want to chase minimal WER on extended monologues.[^4][^1]

***

### 7. Migration Plan: CPU/Ollama → MLX

#### 7.1 High‑level strategy

1. Stop using Ollama for TTS; shift all TTS calls to `mlx-audio`.
2. Use `mlx-community` Qwen3‑TTS MLX checkpoints as the model source.
3. Integrate via Python API inside your flaming‑horse / Manim pipeline to preserve your caching and batch strategies.
4. Tune quantization and model variant per stage (draft vs final render).

#### 7.2 Concrete steps

**Step 1: Environment**

```bash
pip install -U mlx-audio soundfile numpy
```

Sanity check on a small model:[^6][^8]

```bash
python -m mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit \
  --text "Hello, this is a test."
```

**Step 2: Voice cloning baseline**

Use your existing cloned voice sample:

```bash
python -m mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit \
  --text "Short reference narration for testing." \
  --ref_audio ./my_voice_sample.wav \
  --ref_text  "Transcript of the reference audio." \
  --file_prefix cloned_test \
  --play
```

Confirm audio quality vs your current CPU/Ollama output.

**Step 3: Integrate into Python service**

Example service‑style wrapper:

```python
from pathlib import Path
from mlx_audio.tts.utils import load_model
from mlx_audio.tts.generate import generate_audio

MODEL_ID = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-4bit"
OUTPUT_DIR = Path("tts_cache")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

model = load_model(MODEL_ID)

def synthesize_segment(segment_id: str, text: str, ref_audio: str | None = None) -> Path:
    out_prefix = OUTPUT_DIR / segment_id
    generate_audio(
        model=model,
        text=text,
        ref_audio=ref_audio,
        file_prefix=str(out_prefix),
        audio_format="wav",
        verbose=False,
    )
    # mlx-audio names files like "<prefix>_000.wav" etc.
    return next(OUTPUT_DIR.glob(f"{segment_id}_*.wav"))
```

Wire this into your existing caching layer (replacing Ollama calls with this function), preserving your current “pre‑cache narration segments before Manim render” strategy.[^4]

**Step 4: Benchmark real workload**

Measure on your M1 Max:

- Typical segment length: e.g., 2–4 sentences.
- Number of segments per video.
- Time to synthesize all segments with and without voice cloning.

Compare end‑to‑end times against your prior CPU pipeline.

**Step 5: Optional 25Hz test for long‑form**

If you have continuous narrations > 5–10 minutes, test a 25Hz 1.7B‑CustomVoice MLX model and evaluate intelligibility/WER vs 12Hz output on the same scripts.[^1]

***

### 8. Engineering Notes and Gotchas

1. **MLX lazy evaluation and cache**
    - On iOS, developers report the compute graph can grow until iOS kills the app if `eval()` and `Memory.clearCache()` are not called at chunk boundaries.[^30]
    - On macOS, with long‑running batch jobs, explicit eval/flush calls between segments can prevent runaway memory use.
2. **SnakeBeta correctness**
    - Ensure any custom forks of the decoder preserve the `exp()` of alpha and beta parameters, as in the MLX port.[^9][^10]
3. **Causal padding**
    - For any conv layer you modify, use `padding = (kernel_size - 1) * dilation` on the left only to preserve causality.[^10][^9]
4. **Quantization trade‑offs**
    - 4‑bit: best speed and RAM usage, slight quality drop possible on fringe cases.[^22][^6]
    - 8‑bit: higher fidelity, still fast on M1 Max.
    - You can adopt a two‑tier strategy: 0.6B‑4bit for iterative dev, 1.7B‑4/6/8bit for final renders.
5. **Concurrency and model budget**
    - With 32GB unified memory, Qwen3‑TTS‑1.7B‑4bit (~2GB) plus your main LLM and tools fits comfortably.[^23][^22][^6]
    - Avoid loading redundant model variants concurrently unless needed for A/B testing.

***

### 9. Summary of Expected Benefits

- **Throughput**: ~12–15x faster end‑to‑end TTS on Apple Silicon compared to CPU‑only, based on measured benchmarks.[^9][^10]
- **Quality**: Same Qwen3‑TTS architecture and training; all improvements are at the runtime level, not model approximations.[^2][^1]
- **Workflow fit**: Direct Python API fits your flaming‑horse/Manim pipeline and supports your existing caching and batch processing design.[^3][^4][^6]
- **Portability**: Same MLX‑based stack can later be moved to iOS (with MLX Swift bindings) if you want on‑device narration on iPhone/iPad.[^31][^32][^3]
<span style="display:none">[^33][^34][^35]</span>

<div align="center">⁂</div>

[^1]: https://arxiv.org/html/2601.15621v1

[^2]: https://arxiv.org/abs/2601.15621

[^3]: work.device

[^4]: interests.tts_research.qwen3_tts

[^5]: interests.tts_research

[^6]: https://github.com/Blaizzy/mlx-audio

[^7]: https://www.perplexity.ai/search/82e3e849-226d-432b-89d8-da5226c12ae1

[^8]: https://www.themoonlight.io/tw/review/qwen3-tts-technical-report

[^9]: https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit

[^10]: https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16

[^11]: https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit

[^12]: https://note.com/anotete_cto/n/nc332da37912f

[^13]: https://note.com/eris_ths/n/n0b039eec4eae

[^14]: https://huggingface.co/mlx-community

[^15]: https://www.reddit.com/r/LocalLLaMA/comments/1r082v1/qwen3codernext_performance_on_mlx_vs_llamacpp/

[^16]: https://www.reddit.com/r/LocalLLaMA/comments/1ltg9ji/m4_max_vs_m3_ultra_qwen3_mlx_inference/

[^17]: https://www.reddit.com/r/LocalLLaMA/comments/1j0c53c/inference_speed_comparisons_between_m1_pro_and/

[^18]: https://pypi.org/project/mlx-audio/

[^19]: https://pypi.org/project/mlx-audio/0.2.9/

[^20]: https://news.ycombinator.com/item?id=46719229

[^21]: https://news.ycombinator.com/item?id=46735711

[^22]: https://huggingface.co/models?search=qwen3-tts+mlx

[^23]: https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16

[^24]: https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit/commit/4addb03177a4f581502fc279585b190f47728e3f

[^25]: https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit

[^26]: https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit

[^27]: https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-6bit

[^28]: https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit/commit/0dd38641071d6916d898fd144e3677e567ca27dc

[^29]: https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit/tree/main

[^30]: https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-5bit

[^31]: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign

[^32]: https://qwen3tts.art

[^33]: https://www.reddit.com/r/LocalLLaMA/comments/1qot50u/got_qwen3tts_running_on_iphone_with_mlx/

[^34]: https://www.youtube.com/watch?v=vCIA3N0s3es

[^35]: https://www.reddit.com/r/Qwen_AI/comments/1r3ixmk/i_opensourced_qwen3asrswift_native_ondevice_asr/

