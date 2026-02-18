# xAI Collections Integration Report for Flaming Horse

## Context

This report summarizes a design conversation about integrating xAI's Collections feature into the Flaming Horse agentic Manim video production pipeline. Collections is a managed RAG (Retrieval-Augmented Generation) system available through the xAI Cloud Console and API. It allows you to upload documents, automatically index them with vector embeddings, and make them searchable by Grok during chat completion calls.

The goal: make Grok a more intelligent Manim scene writer and narrative producer by grounding its generation in verified reference material rather than relying on parametric memory alone.

---

## Flaming Horse Architecture Recap

Flaming Horse separates concerns into two strict domains:

- **Creative (Agent-driven):** Grok imagines animations and writes Manim scene code. Grok produces narrative/voiceover text from user-supplied concepts.
- **Infrastructure (Deterministic/Scripted):** State machine transitions, file I/O, Manim rendering, voiceover precaching (via custom local Qwen3-TTS plugin), QC checks, video assembly. All on rails, no agent involvement.

This boundary exists because video production requires consistency. LLMs are creative but unreliable executors. Grok does only what it is good at; everything else is scripted.

---

## What Collections Does

Collections lets you create a named group of documents that get chunked, embedded, and indexed server-side. When the harness makes a chat completions API call, it can pass `collections_search(collection_ids=["..."])` as an available tool. Grok then autonomously decides when and how to search the collection during generation, issuing multiple refined queries as needed.

Key mechanics:
- Retrieval uses semantic search, keyword search, or hybrid (reranker + reciprocal rank fusion)
- Responses include `collections://` URI citations pointing to exact source files
- Pricing: $2.50 per 1,000 searches; free indexing and storage for the first week
- Upload limits: 100MB per file, 100,000 files globally, 100GB total storage
- SDK naming: `collections_search` in native xAI SDK, `file_search` in OpenAI-compatible Responses API
- Can be combined with `web_search()`, `x_search()`, and `code_execution()` in a single request

---

## What to Put in the Collection

Four categories, all scoped to creative generation, zero infrastructure:

### 1. Manim CE API Docs
- Class references for Mobjects, Animations, Cameras, and coordinate utilities
- Focus on classes actually used in Flaming Horse scenes
- This is what Grok hallucinates most: method signatures, parameter names, deprecated vs. current API
- Smaller collection means more relevant search hits

### 2. Manim CE Examples
- Official gallery examples and community examples demonstrating patterns Grok struggles with
- Complex VGroup manipulation, AnimationGroup timing, updater functions, ValueTracker usage
- These serve as syntactically verified few-shot references

### 3. Style Guide
- Visual conventions: color palette, default font sizes, object positioning rules, screen region usage, transition preferences
- Narrative conventions: tone, sentence structure, pacing relationship between spoken words and on-screen motion
- This is what makes Flaming Horse output distinctive rather than generic Manim output

### 4. Code Generation Rules
- Import constraints (what Grok is and is not allowed to import)
- The voiceover block contract: the exact shape of a `with self.voiceover(...)` block the deterministic pipeline expects
- Anti-patterns: things Grok has gotten wrong before, captured in LESSONS_LEARNED
- Output structure requirements: how `construct()` methods should be organized, naming conventions, comment expectations

---

## What to Exclude

Since infrastructure is scripted and deterministic, do NOT upload:

- State machine logic, `project_state.json` schemas, or phase transition rules
- Build scripts (`build_video.sh`, `scaffold_scene.py`, `qc_final_video.sh`)
- Rendering configuration, file path conventions, or output directory structures
- TTS plugin internals (model loading, caching logic, audio format handling). Grok only needs the output contract: what a voiceover block looks like in scene code
- Third-party Manim TTS plugins (e.g., DurhamSmith's `manim-voiceover-qwen3-tts`). These would pollute results with patterns that do not match our custom implementation

The principle: Collections should make Grok a better writer of Manim scenes, not a better understander of the pipeline. The harness already ensures Grok never sees or touches infrastructure. The collection reinforces that boundary.

---

## Collection Configuration

Settings for the xAI Console create-collection form:

| Setting | Value | Rationale |
|---|---|---|
| Name | `flaming-horse` | Matches project namespace |
| Embedding model | `grok-embedding-small` | Default; no reason to change |
| Chunking | Token-based | Default mode |
| Max chunk size | `1536` | Keeps complete method definitions and example scenes intact (default 1024 splits mid-scene) |
| Chunk overlap | `256` | Ensures boundary context is not lost between adjacent chunks |
| Encoding name | `o200k_base` | Default |
| Inject name into chunks | Enabled | File names like `animate_transform.py` or `style_guide.md` provide immediate retrieval context |

### Metadata Fields

Add one metadata field:

| Key | Inject | Unique | Description |
|---|---|---|---|
| `category` | Yes | No | Document category. Values: `api_docs`, `examples`, `style_guide`, `code_rules` |

Injecting the category means every retrieved chunk self-identifies its type, so Grok knows whether it is looking at an API reference, a working example, a style constraint, or a code generation rule.

---

## Harness Integration

The integration point is the chat completions call. When the harness constructs an API request for a creative phase (scene writing, narrative production, repair reasoning), it includes `collections_search` as an available tool alongside the phase-specific system prompt.

```python
tools = [
    {
        "type": "collections_search",
        "collections_search": {
            "collection_ids": ["<flaming-horse-collection-id>"]
        }
    }
]
```

Grok autonomously decides what to search and when. During scene construction it might query "how to animate a Transform between VGroups" or "voiceover block structure." During repair it might search for known anti-patterns.

No changes to the harness phase architecture are required. Collections is just another tool passed in the API call. The harness still owns context assembly and phase transitions.

---

## Cost Estimate

At $2.50 per 1,000 searches, if the harness triggers roughly 20 collection searches per full video pipeline run (across plan, build, QC, and repair phases), the per-video retrieval cost is approximately $0.05. File indexing and storage are free after the initial upload.

---

## Expected Impact

- **Fewer repair cycles:** Grounding initial generation in real Manim docs reduces API hallucination failures (wrong method names, deprecated patterns, incorrect parameter types)
- **Style consistency:** The style guide and working examples teach Grok the project's visual and narrative language
- **Bounded creativity:** The collection contains only material relevant to Grok's authorized creative scope, reinforcing the architecture's separation of concerns
- **Low maintenance:** As new scenes pass QC or rules evolve, upload updated docs. Re-indexing is automatic and free
