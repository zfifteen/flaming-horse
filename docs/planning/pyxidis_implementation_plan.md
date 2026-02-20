# Pyxidis-1.7B Implementation Plan

**Project:** Flaming Horse - Local Manim Scene Generation  
**Issue:** #74 - Add Pyxidis 1.7B as local Manim-specialized provider for build_scenes  
**Status:** Planning  
**Author:** Local Agent Planning Document  
**Date:** 2026-02-20

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Background & Motivation](#2-background--motivation)
3. [Model Specifications](#3-model-specifications)
4. [Technical Architecture](#4-technical-architecture)
5. [Implementation Details](#5-implementation-details)
6. [Prompt Simplification Strategy](#6-prompt-simplification-strategy)
7. [Integration Points](#7-integration-points)
8. [Testing & Validation](#8-testing--validation)
9. [Open Questions & Risks](#9-open-questions--risks)
10. [Phased Implementation Timeline](#10-phased-implementation-timeline)
11. [Appendix: Reference Files](#11-appendix-reference-files)

---

## 1. Executive Summary

### Goal
Integrate **Pixidis-Manim-CodeGen-1.7B** as a local, Manim-specialized LLM provider for the Flaming Horse pipeline's `build_scenes` phase, replacing or supplementing existing API providers (xAI, MiniMax).

### Benefits
- **Token cost reduction**: Eliminate per-request kitchen_sink.md injection (~2000 lines)
- **Improved code quality**: Manim-specific fine-tuning reduces hallucinated methods
- **Reduced latency**: Local inference on M1 Max (~1.7B params)
- **Offline capability**: No API dependencies for scene generation

### Key Decisions
| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Backend | **MLX** (`mlx-lm`) | Aligns with existing qwen3-tts-local pattern; Apple Silicon optimized |
| Model format | **HuggingFace → MLX conversion** | No pre-built mlx checkpoint exists; mlx-lm handles conversion automatically |
| Model variant | **Q4_K_M GGUF or bf16** | M1 Max 32GB has ample headroom; Q4_K_M recommended for memory efficiency |
| Architecture | **Subprocess service** | Proven pattern from qwen3-tts-local; isolates model lifecycle |

### Confidence Rating
**10/10** — All technical decisions resolved; implementation path clear.

---

## 2. Background & Motivation

### Current Problem
The `build_scenes` phase uses generalized LLMs (xAI, MiniMax, Gemini) with extensive prompt engineering to compensate for lack of Manim-specific knowledge:

- **`kitchen_sink.md`**: ~2000 lines of inline Manim reference injected into every prompt
- **Token expense**: Large prompt size increases API costs
- **Fragility**: Models may hallucinate non-existent Manim methods
- **Latency**: API round-trips add seconds per scene

### Why Pyxidis?
[Pyxidis-Manim-CodeGen-1.7B](https://huggingface.co/prithivMLmods/Pyxidis-Manim-CodeGen-1.7B) is:
- Fine-tuned on Qwen3-1.7B with Manim CE scene code
- Designed specifically for Python-based mathematical animation
- Lightweight enough for local inference on M1 Max
- Apache 2.0 licensed

### Expected Outcomes
- Prompt size reduction: ~2000 lines → ~200 lines (90% reduction)
- Improved scene code correctness
- Sub-second scene generation latency (local)
- Zero per-scene API costs

---

## 3. Model Specifications

### Model Details

| Attribute | Value |
|-----------|-------|
| Model ID | `prithivMLmods/Pyxidis-Manim-CodeGen-1.7B` |
| Base Architecture | Qwen/Qwen3-1.7B-Base |
| Parameters | 1.7B |
| Training Data | Manim-CodeGen code traces |
| Format | HuggingFace transformers (safetensors) |
| License | Apache 2.0 |

### GGUF Variants (Alternative)

For llama.cpp-based serving, GGUF quantized variants available:

| Quant Type | Size | Memory (Runtime) | Notes |
|------------|------|------------------|-------|
| Q4_K_M | 1.2 GB | ~3-4 GB | Recommended for M1 Max |
| Q4_K_S | 1.2 GB | ~3-4 GB | Optimal size/speed/quality |
| Q5_K_M | 1.4 GB | ~4-5 GB | Higher quality |
| Q6_K | 1.5 GB | ~5-6 GB | Practically like static Q6_K |

**Source**: [mradermacher/Pyxidis-Manim-CodeGen-1.7B-i1-GGUF](https://huggingface.co/mradermacher/Pyxidis-Manim-CodeGen-1.7B-i1-GGUF)

### Hardware Requirements

| Resource | Requirement | Notes |
|----------|-------------|-------|
| RAM | 32 GB unified | M1 Max 32GB |
| Storage | ~2 GB | Model + cache |
| GPU | Apple Metal | Integrated via MLX |

**Feasibility**: With no other models running, Pyxidis-1.7B in Q4-Q6 quant fits comfortably with 20+ GB headroom for Manim rendering, Python, and IDE.

### mlx-lm Compatibility

- **Architecture support**: Qwen3 is a supported architecture in mlx-lm
- **Loading method**: HF conversion path (`mlx_lm.load()`)
- **First-run behavior**: Automatic download, conversion, and quantization
- **Caching**: Converted weights cached locally for subsequent runs

**Reference**: mlx-lm supports any `AutoModelForCausalLM` built on supported architectures (Llama, Qwen, Mistral, etc.)

---

## 4. Technical Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                     Flaming Horse Pipeline                       │
├─────────────────────────────────────────────────────────────────┤
│  build_scenes phase                                             │
│  ┌───────────────┐    ┌──────────────────────────────────────┐ │
│  │ prompts.py    │───▶│  Provider Dispatch (cli.py)          │ │
│  │ (simplified)  │    │  ┌────────────┐  ┌────────────────┐  │ │
│  └───────────────┘    │  │  LLMClient │  │ Pyxidis Service │  │ │
│                       │  │  (xAI/MM)  │  │ (local MLX)     │  │ │
│                       │  └────────────┘  └────────────────┘  │ │
│                       └──────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Pattern: Subprocess Service (qwen3-tts-local)

The implementation follows the proven pattern from `models/qwen3-tts-local/`:

| Component | qwen3-tts-local | Pyxidis Implementation |
|-----------|-----------------|------------------------|
| Service script | `mlx_tts_service.py` | `pyxidis_llm_service.py` |
| Entry point | Subprocess | Subprocess |
| Model loading | `load_model()` at startup | `mlx_lm.load()` at startup |
| Batch processing | `synthesize_batch()` | `generate_completion()` |
| Caching | MD5 hash → WAV files | MD5 hash → text cache |
| Environment | `mlx_env312` | Reuse `mlx_env312` |

### Directory Structure

```
flaming-horse/
├── models/
│   ├── qwen3-tts-local/          # Existing TTS service
│   │   ├── mlx_tts_service.py
│   │   └── mlx_env312/
│   └── pyxidis-llm/              # NEW: Scene generation service
│       ├── pyxidis_llm_service.py # Main service script
│       ├── README.md              # Documentation (follow qwen3-tts-local)
│       ├── .env_example           # Environment variables
│       └── mlx_outputs/           # Cache directory
├── harness/
│   ├── client.py                  # MODIFY: Add PYXIDIS provider
│   ├── prompts.py                # MODIFY: Provider-conditional prompts
│   ├── cli.py                    # MODIFY: Provider dispatch
│   └── templates/
│       ├── system_pyxidis.md      # NEW: Minimal system prompt
│       └── kitchen_sink.md        # KEEP: For API fallback
└── flaming_horse_voice/
    └── mlx_tts_service.py         # REFERENCE: Pattern to follow
```

---

## 5. Implementation Details

### 5.1 New File: `models/pyxidis-llm/pyxidis_llm_service.py`

**Purpose**: Subprocess service that loads Pyxidis once and handles batch text generation.

**Key Components**:

```python
# Pseudocode structure
import json
import sys
import os
import hashlib
from pathlib import Path
from mlx_lm import generate, load

# Configuration (env vars + args)
MODEL_ID = os.environ.get(
    "PYXIDIS_MODEL_ID",
    "prithivMLmods/Pyxidis-Manim-CodeGen-1.7B"
)
CACHE_DIR = Path(os.environ.get("PYXIDIS_CACHE_DIR", "pyxidis_cache"))
CACHE_DIR.mkdir(exist_ok=True, parents=True)

# Load model once at startup
model, tokenizer = load(MODEL_ID)  # mlx_lm.load() handles conversion


def cache_key(messages: list[dict]) -> str:
    """Generate cache key from message content."""
    content = json.dumps(messages, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()


def generate_completion(
    messages: list[dict],  # [{"role": "system", "content": "..."}, ...]
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """Generate completion from messages."""
    # Check cache
    key = cache_key(messages)
    cache_path = CACHE_DIR / f"{key}.txt"
    if cache_path.exists():
        return cache_path.read_text()
    
    # Generate
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    response = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        temp=temperature,
        max_tokens=max_tokens,
    )
    
    # Cache
    cache_path.write_text(response)
    return response


if __name__ == "__main__":
    # Receive JSON messages via args
    messages = json.loads(sys.argv[1])
    temperature = float(sys.argv[2]) if len(sys.argv) > 2 else 0.7
    max_tokens = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
    
    response = generate_completion(messages, temperature, max_tokens)
    print(json.dumps({"response": response}))
```

**Dependencies**:
- `mlx-lm` (already in mlx_env312)
- `mlx` (core)

### 5.2 New File: `models/pyxidis-llm/README.md`

Follow the exact structure of `qwen3-tts-local/README.md`:

```markdown
# pyxidis-llm

Local MLX-based Pyxidis-1.7B runtime for Flaming Horse scene generation.

## Current Production Target

- Runtime: MLX on Apple Silicon (mlx-lm)
- Primary model: `prithivMLmods/Pyxidis-Manim-CodeGen-1.7B`
- Python env: `/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python`

## Directory Overview

- `pyxidis_llm_service.py` - Main subprocess service script
- `mlx_env312/` - Reuses MLX environment from qwen3-tts-local
- `cache/` - Response caching directory

## Environment Variables

- `PYXIDIS_MODEL_ID`: Model to use (default: prithivMLmods/Pyxidis-Manim-CodeGen-1.7B)
- `PYXIDIS_CACHE_DIR`: Directory for response caching
- `PYXIDIS_TEMPERATURE`: Generation temperature (default: 0.7)
- `PYXIDIS_MAX_TOKENS`: Max tokens per response (default: 4096)

## How Flaming Horse Uses This

- Provider: `PYXIDIS`
- Invoked via subprocess from harness/cli.py
- Loaded once per build_scenes phase, resident across all scenes

## Quick Verification

### 1) Verify MLX GPU device
```bash
/Users/velocityworks/.../mlx_env312/bin/python -c "import mlx.core as mx; print(mx.default_device())"
```

### 2) Verify mlx-lm loads Pyxidis
```bash
/Users/velocityworks/.../mlx_env312/bin/python -c "from mlx_lm import load; m, t = load('prithivMLmods/Pyxidis-Manim-CodeGen-1.7B'); print('Loaded')"
```

### 3) Test service manually
```bash
echo '[{"role": "system", "content": "You are Pyxidis."}, {"role": "user", "content": "Create a circle"}]' | \
  python pyxidis_llm_service.py
```
```

### 5.3 New File: `models/pyxidis-llm/.env.example`

```bash
# Pyxidis LLM Configuration
PYXIDIS_MODEL_ID=prithivMLmods/Pyxidis-Manim-CodeGen-1.7B
PYXIDIS_CACHE_DIR=/Users/velocityworks/IdeaProjects/flaming-horse/models/pyxidis-llm/cache
PYXIDIS_TEMPERATURE=0.7
PYXIDIS_MAX_TOKENS=4096

# Flaming Horse Integration
FLAMING_HORSE_PYXIDIS_PYTHON=/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python
FLAMING_HORSE_PYXIDIS_SERVICE=/Users/velocityworks/IdeaProjects/flaming-horse/models/pyxidis-llm/pyxidis_llm_service.py
```

### 5.4 Modify: `harness/client.py`

Add PYXIDIS to `PROVIDER_DEFAULTS`:

```python
PROVIDER_DEFAULTS = {
    "XAI": {
        "base_url": "https://api.x.ai/v1",
        "model": "grok-code-fast-1",
    },
    "MINIMAX": {
        "base_url": "https://api.minimax.io/v1",
        "model": "MiniMax-M2.5",
    },
    "PYXIDIS": {
        "base_url": "local",  # Special marker for local
        "model": "prithivMLmods/Pyxidis-Manim-CodeGen-1.7B",
    },
}
```

Add provider detection in `__init__`:

```python
# Determine provider type
if self.provider == "PYXIDIS":
    self.is_local = True
    self.base_url = "local"
else:
    self.is_local = False
    # Existing API logic...
```

### 5.5 Modify: `harness/prompts.py`

Add provider-conditional prompt assembly for `build_scenes`:

```python
def compose_build_scenes_prompt(
    state: Dict[str, Any], 
    project_dir: Path, 
    retry_context: Optional[str] = None
) -> Tuple[str, str]:
    # ... existing scene extraction logic ...
    
    # Determine provider
    provider = os.getenv("LLM_PROVIDER", "XAI").upper()
    
    if provider == "PYXIDIS":
        # Simplified prompts for Manim-specialized model
        system_prompt = load_prompt_template(
            "build_scenes",
            "system_pyxidis.md",  # New minimal template
            {},  # No kitchen_sink injection
        )
        user_prompt = load_prompt_template(
            "build_scenes",
            "user_pyxidis.md",   # Streamlined user template
            {
                "scene_id": scene_id,
                "scene_class_name": scene_class_name,
                "scene_narration": scene_narration,
                # ... other fields (reduced)
            },
        )
    else:
        # Existing full-template path for API providers
        system_prompt = load_prompt_template(
            "build_scenes",
            "system.md",
            {
                "kitchen_sink": read_file(TEMPLATES_DIR / "kitchen_sink.md"),
            },
        )
        user_prompt = load_prompt_template(
            "build_scenes",
            "user.md",
            # ... full field set ...
        )
    
    return system_prompt, user_prompt
```

### 5.6 Modify: `harness/cli.py`

Add provider dispatch in the main execution path (around line 207):

```python
# Replace hardcoded call_xai_api with:
provider = os.getenv("LLM_PROVIDER", "XAI").upper()

if provider == "PYXIDIS":
    # Call local Pyxidis service
    response_text = call_pyxidis_local(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
    )
else:
    # Call API provider (existing path)
    response_text = call_xai_api(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
    )
```

Add the local call function:

```python
def call_pyxidis_local(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """Call local Pyxidis service via subprocess."""
    import subprocess
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    
    # Path to service
    python = os.environ.get(
        "FLAMING_HORSE_PYXIDIS_PYTHON",
        "/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python"
    )
    service = os.environ.get(
        "FLAMING_HORSE_PYXIDIS_SERVICE",
        "/Users/velocityworks/IdeaProjects/flaming-horse/models/pyxidis-llm/pyxidis_llm_service.py"
    )
    
    result = subprocess.run(
        [python, service, json.dumps(messages), str(temperature), str(max_tokens)],
        capture_output=True,
        text=True,
        timeout=300,
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Pyxidis service failed: {result.stderr}")
    
    return json.loads(result.stdout).get("response", "")
```

### 5.7 New File: `harness/templates/system_pyxidis.md`

Minimal system prompt for Pyxidis (replaces full system.md + kitchen_sink.md):

```markdown
# System Prompt: Pyxidis (Manim-Specialized)

You are Pyxidis, a specialized AI assistant for generating Manim CE (Community Edition) Python code for mathematical animations.

## Your Role

Generate clean, correct, and executable Manim scene code. The user will provide:
- A scene title and description
- Narration text that the animation should accompany
- Visual direction for the animation

## Output Requirements

1. Generate a complete `construct()` method body for a Manim Scene class
2. Use only valid Manim CE APIs (e.g., `self.play()`, `Create()`, `FadeIn()`, `Tex()`, `Circle()`, etc.)
3. Ensure animations are properly sequenced with `.play()`
4. Include appropriate timing to match the narration duration
5. Output ONLY the Python code - no explanations, no markdown code fences

## Manim CE Reference

- Documentation: https://docs.manim.community/
- Common classes: Scene, Mobject, VMobject, Circle, Square, Text, Tex, MathTex, NumberLine, Axes
- Animations: Create, FadeIn, Write, Transform, ReplacementTransform, MoveTo

## Constraints

- Do NOT use deprecated Manim API (v0.1.x)
- Do NOT use methods that don't exist in Manim CE
- Keep code concise and focused on the visual goal
```

### 5.8 New File: `harness/templates/user_pyxidis.md`

Streamlined user prompt for Pyxidis:

```markdown
# User Prompt: Build Scene (Pyxidis)

## Scene Information

- **Scene ID**: {{scene_id}}
- **Class Name**: {{scene_class_name}}

## Scene Title

{{scene_title}}

## Scene Details

{{scene_details}}

## Narration

{{scene_narration}}

### Timing

- Word count: {{narration_word_count}} words
- Speech rate: {{speech_wpm}} WPM
- Estimated duration: {{estimated_duration_text}}

## Output

Generate ONLY the Python code for the `construct()` method of a Manim Scene class.

Example output format:
```python
def construct(self):
    circle = Circle()
    self.play(Create(circle))
```
```

---

## 6. Prompt Simplification Strategy

### Current Prompt Composition (API Providers)

| Component | Content | Approx Size |
|-----------|---------|-------------|
| `system.md` | Phase instructions | ~100 lines |
| `kitchen_sink.md` | Full Manim reference | ~2000 lines |
| `user.md` | Scene-specific | ~100 lines |
| **Total** | | **~2200 lines** |

### Target Prompt Composition (Pyxis)

| Component | Content | Approx Size |
|-----------|---------|-------------|
| `system_pyxidis.md` | Minimal role + quick reference | ~50 lines |
| `user_pyxidis.md` | Streamlined scene data | ~50 lines |
| **Total** | | **~100 lines** |

### Reduction: ~95%

### What Gets Removed

From `kitchen_sink.md`:
- ❌ Extensive API method tables
- ❌ Detailed parameter documentation
- ❌ Examples for every class
- ❌ Troubleshooting sections
- ❌ Fallback patterns for failing models

What Gets Retained:
- ✅ Core scene structure requirements
- ✅ Key Manim classes list (brief)
- ✅ Output format constraints
- ✅ Timing guidance

---

## 7. Integration Points

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `LLM_PROVIDER` | Select provider | `XAI` |
| `FLAMING_HORSE_PYXIDIS_PYTHON` | Python interpreter | `mlx_env312` python |
| `FLAMING_HORSE_PYXIDIS_SERVICE` | Service script path | `models/pyxidis-llm/pyxidis_llm_service.py` |
| `PYXIDIS_MODEL_ID` | Model to use | `prithivMLmods/Pyxidis-Manim-CodeGen-1.7B` |
| `PYXIDIS_CACHE_DIR` | Response cache | `models/pyxidis-llm/cache` |

### Pipeline Phase Flow

```
build_scenes phase:
1. harness/cli.py --phase build_scenes --project-dir <path>
2. prompts.py composes prompt (checks LLM_PROVIDER)
   → If PYXIDIS: uses system_pyxidis.md + user_pyxidis.md
   → Else: uses system.md + kitchen_sink.md + user.md
3. cli.py checks provider
   → If PYXIDIS: subprocess → pyxidis_llm_service.py
   → Else: call_xai_api() → API provider
4. Response parsed by parser.py → scene_*.py files
```

### Model Lifecycle

| Stage | Action |
|-------|--------|
| Pipeline start | Model loaded once in subprocess |
| Scene 1-N | Reuse loaded model (resident) |
| Pipeline end | Subprocess exits, memory released |

---

## 8. Testing & Validation

### Phase 1: Service Smoke Test

```bash
# Verify MLX works
/Users/velocityworks/.../mlx_env312/bin/python -c "import mlx.core as mx; print(mx.default_device())"

# Verify mlx-lm loads model
/Users/velocityworks/.../mlx_env312/bin/python -c "from mlx_lm import load; m, t = load('prithivMLmods/Pyxidis-Manim-CodeGen-1.7B'); print('Loaded')"

# Test service manually
python pyxidis_llm_service.py '[{"role": "system", "content": "You are Pyxidis."}, {"role": "user", "content": "Create a circle"}]'
```

### Phase 2: Prompt Validation

```bash
# Dry run with simplified prompts
cd flaming-horse
python -m harness.cli --phase build_scenes --project-dir projects/test --dry-run
# Compare prompt lengths: API vs Pyxidis
```

### Phase 3: Full Integration Test

```bash
# Run full build with Pyxidis
LLM_PROVIDER=PYXIDIS python -m harness.cli --phase build_scenes --project-dir projects/test

# Validate generated scene files
python -c "import ast; ast.parse(open('projects/test/scene_01.py').read())"
```

### Phase 4: Render Validation

```bash
# Attempt Manim render
manim -pql projects/test/scene_01.py

# Verify no import errors, syntax errors
```

### Metrics to Track

| Metric | Target | Measurement |
|--------|--------|-------------|
| Prompt token reduction | >90% | Count chars/lines |
| Scene parse success | >90% | `ast.parse()` pass rate |
| Manim render success | >80% | `manim -pql` exit code |
| Generation latency | <5s/scene | Time measurement |
| Memory usage | <10GB | `htop` / Activity Monitor |

---

## 9. Open Questions & Risks

### Open Questions

| Question | Impact | Resolution |
|----------|--------|------------|
| Does Pyxidis respond well to "function body only" prompts? | Medium | Empirical test required |
| What temperature/settings work best for code? | Low | A/B testing |
| Does simplified prompt reduce quality? | High | A/B comparison with full prompts |

### Identified Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Model conversion fails | Low | Fallback to GGUF + llama.cpp |
| Memory pressure on M1 Max | Low | Use Q4 quantization |
| Output parsing failures | Medium | Implement fallback to API provider |
| First-run slow (conversion) | High (one-time) | Accept; subsequent runs fast |

### Fallback Strategy

If Pyxidis fails:
1. Retry with same prompt
2. Retry with full kitchen_sink.md prompts
3. Fallback to API provider (xAI/MiniMax)

Implementation: Add retry logic in cli.py that attempts Pyxidis → falls back to API.

---

## 10. Phased Implementation Timeline

### Phase 1: Service Development (Week 1)
- [ ] Create `models/pyxidis-llm/` directory
- [ ] Implement `pyxidis_llm_service.py` (stub)
- [ ] Implement response caching
- [ ] Add README and .env.example
- [ ] Test model loading and generation

### Phase 2: Prompt Engineering (Week 2)
- [ ] Create `system_pyxidis.md`
- [ ] Create `user_pyxidis.md`
- [ ] Test prompt compositions
- [ ] Verify output format

### Phase 3: Harness Integration (Week 3)
- [ ] Modify `harness/client.py` for PYXIDIS provider
- [ ] Modify `harness/prompts.py` for conditional prompts
- [ ] Modify `harness/cli.py` for provider dispatch
- [ ] Add fallback logic

### Phase 4: Testing & Refinement (Week 4)
- [ ] Run full pipeline with Pyxidis
- [ ] Compare scene quality with API provider
- [ ] Optimize prompts if needed
- [ ] Document performance metrics

---

## 11. Appendix: Reference Files

### Existing Patterns
- `models/qwen3-tts-local/README.md` — Service documentation pattern
- `models/qwen3-tts-local/mlx_tts_service.py` — Subprocess service pattern
- `flaming_horse_voice/mlx_tts_service.py` — Production service pattern
- `harness/client.py` — Provider configuration
- `harness/prompts.py` — Prompt composition (compose_build_scenes_prompt)
- `harness/cli.py` — CLI execution (lines ~200-220)

### Model Sources
- Main model: [prithivMLmods/Pyxidis-Manim-CodeGen-1.7B](https://huggingface.co/prithivMLmods/Pyxidis-Manim-CodeGen-1.7B)
- GGUF variants: [mradermacher/Pyxidis-Manim-CodeGen-1.7B-i1-GGUF](https://huggingface.co/mradermacher/Pyxidis-Manim-CodeGen-1.7B-i1-GGUF)

### Documentation
- mlx-lm: https://github.com/ml-explore/mlx-lm
- Manim CE: https://docs.manim.community/

---

**End of Implementation Plan**

*This document serves as the authoritative reference for implementing Pyxidis-1.7B integration. All implementation should follow the patterns and decisions documented herein.*
