# Prompt Improvements

Date: 2026-02-22  
Scope: `harness/prompts/` and `harness/templates/`

---

## Summary of Structural Changes

### 1. `harness/prompts/00_plan/manifest.yaml`

**Change:** Corrected `scene_count` and `total_duration_seconds` constraints from `8-12 / 240-480` to `12-24 / 480-960`.

**Rationale:** The previous values conflicted with `docs/reference_docs/phase_plan.md`, which defines the authoritative scene count as 12–24 and total duration as 480–960 seconds. The user prompt (`user.md`) already used the correct values, creating a misleading inconsistency in the manifest. Aligning them removes a potential confusion source for tooling or audit checks.

---

### 2. `harness/prompts/02_narration/manifest.yaml`

**Change:** Replaced `exclude: voice_runtime_policy` with an explicit constraint: `qwen_tts_safe_text` and a note that narration text feeds cached Qwen TTS synthesis.

**Rationale:** `VOICE_POLICY.md` requires unconditional Qwen-only TTS. The previous `exclude` entry silently suppressed any voice policy awareness from the narration manifest. Since narration text is the direct input to Qwen TTS, the agent must know not to produce markup, brackets, or special characters that could break synthesis. This aligns with the "Rule Enforcement" criterion.

---

### 3. `harness/prompts/02_narration/system.md`

**Change:** Renamed "voiceover writer" to "voiceover writer for cached Qwen TTS voice synthesis" and added one explicit constraint: write plain spoken prose only — no special markup or formatting characters.

**Rationale:** Per `VOICE_POLICY.md`, all narration is synthesized through cached Qwen TTS. The prior system prompt had no voice-pipeline awareness. This minimal addition enforces the policy without adding bulk, directly addressing the "Rule Enforcement" criterion. The rest of the creative guidance is preserved unchanged.

---

### 4. `harness/prompts/_shared/core_rules.md`

**Change:** Merged the duplicate voice configuration rule. The file previously declared voice requirements in two separate sections: "VOICE POLICY - READ THIS FIRST" (lines 7–21) and "Voice Configuration" under "CRITICAL RULES" (lines 38–43). These were collapsed into a single authoritative section ("Voice Configuration — Cached Qwen Only — No Exceptions") that covers all required points from both.

**Rationale:** `DEVELOPMENT_GUIDELINES.md` stresses reliability and reproducibility. Maintaining two nearly-identical voice policy blocks introduces inconsistency risk (one block could drift). The merged section preserves all technical requirements while removing ~14 lines of redundant text, improving token efficiency by approximately 9%.

---

### 5. `harness/prompts/04_build_scenes/system.md`

**Change:** Added a "Voice policy" paragraph at the end of the system role preamble, explicitly stating that the scaffold uses cached Qwen TTS and that agents must not modify voice setup or add alternative TTS imports.

**Rationale:** The build_scenes agent generates scene body code that runs inside a scaffold which already calls `get_speech_service`. Without an explicit constraint, the agent could inject TTS imports or alternative voice calls into the scene body. This addition enforces `VOICE_POLICY.md` at the code-generation boundary.

---

### 6. `harness/prompts/04_build_scenes/user.md`

Three changes:

**6a. Removed duplicate "Self-Check Before Output" mini-checklist.**  
The 4-item mini-checklist (pacing, black tail, visual cluster, MObjects reference) appeared before the output format block. A more comprehensive 8-item "Mandatory Readability Self-Check" appeared later in the same prompt. The mini-checklist was redundant and split attention. It was condensed to a focused "Pacing Self-Check Before Output" covering timing items only (not layout, which belongs to the full checklist).

**6b. Merged "Layout and Overlap Examples" with "Known Failure Patterns" into one section.**  
Both sections contained Wrong/Right code pairs demonstrating layout collisions. They were presented under separate headings 60 lines apart, causing redundant framing and extra LLM context overhead. The merged section uses numbered examples (1–5) with inline diffs, preserving all five concrete wrong/right pairs while eliminating ~25 lines of duplicate setup text.

**6c. Removed duplicate Color Rule and fixed `+` diff markers.**  
The Color Rule (`color=BLUE` → hex) appeared verbatim in both `system.md` and `user.md`. Since `system.md` is the authoritative context for this rule, it was removed from `user.md` to avoid sending it twice per API call. Also fixed four trailing lines that used `+` git-diff notation (`+ HARD CONSTRAINT: ...`) — converted to a clean `⚠️` marker with inline text.

**Token impact:** Combined, these changes reduce `user.md` from 257 to ~185 lines (~28% reduction), directly lowering per-call token cost for the most frequently invoked phase.

---

### 7. `harness/prompts/06_scene_repair/system.md`

**Change:** Collapsed redundant headers ("# Video Production Agent - Scene Repair Phase" + "# Scene Repair Phase System Prompt" → single heading), merged the "Source of Truth" section into the opening role line, consolidated the "no loops" note into the NameError example header, and added a voice policy constraint matching the build_scenes treatment.

**Rationale:** The file had two H1 headers for the same phase, creating misleading structural weight. The "Source of Truth" section restated the URL already on line 8. Merging these removes ~10 lines without losing any policy content. Voice policy addition prevents the repair agent from accidentally re-introducing alternative TTS calls when fixing scene code.

---

### 8. `harness/templates/manim_content_pipeline.md`

**Change:** Replaced the 372-line file with a focused 90-line reference covering: locked config values, VoiceoverScene + Qwen cached voice pattern, SCRIPT dict narration pattern, tracker.duration timing contract, and the layout checklist.

**Sections removed:**
- Section 1 (Overview/Z-mapping conceptual model) — not needed in production prompts
- Section 2 (Subject Material Understanding) — agent-agnostic conceptual guidance
- Section 3 (Z-Mapping Insight Analysis) — ad hoc; described as "user specifies each time"
- Section 4 (Narration Script Generation) — covered by `02_narration` phase prompts
- Section 6 (Bash Rendering on macOS) — deterministic orchestrator-owned; conflicts with `DEVELOPMENT_GUIDELINES.md` which says rendering/assembly are script-owned
- Section 7 (How Assistants Should Use This Pipeline) — meta-guidance redundant with `AGENTS.md`

**Rationale:** `DEVELOPMENT_GUIDELINES.md` mandates that rendering, assembly, and pipeline orchestration are script-owned. Including macOS bash rendering guidance in agent-facing templates blurs the determinism/creativity boundary. The Z-mapping sections described a framework the user provides ad hoc, making them zero-value permanent context tokens. The retained sections (config lock, voice pattern, SCRIPT dict, timing contract, layout checklist) are the only parts with direct impact on agent-generated scene code quality.

**Token impact:** Reduces this template from 372 to ~90 lines (~76% reduction). Since this template is injected into multiple agent prompts, the per-call savings are significant.

---

## Rationale Linked to Repository Guidelines

| Change | Guideline |
|--------|-----------|
| scene_count manifest fix | `phase_plan.md` (authoritative scene count: 12–24) |
| Narration Qwen TTS constraint | `VOICE_POLICY.md` ("CACHED QWEN ONLY. NO EXCEPTIONS.") |
| Voice policy in build_scenes/scene_repair system | `VOICE_POLICY.md`, `DEVELOPMENT_GUIDELINES.md` §Non-Negotiable |
| Merged voice config in core_rules | `VOICE_POLICY.md`, DRY reliability principle |
| Removed orchestrator-owned bash sections | `DEVELOPMENT_GUIDELINES.md` §Ownership Split (rendering = script-owned) |
| Merged layout checklists | `DEVELOPMENT_GUIDELINES.md` §Implementation Guidance ("Keep agent prompts focused") |
| Fixed `+` diff markers | Clean authoring standard; prevents model from interpreting `+` as diff syntax |

---

## Token Efficiency Analysis

| File | Before (lines) | After (lines) | Δ Lines | % Reduction |
|------|---------------|---------------|---------|-------------|
| `_shared/core_rules.md` | 109 | 95 | −14 | ~13% |
| `04_build_scenes/user.md` | 257 | ~185 | −72 | ~28% |
| `06_scene_repair/system.md` | 98 | ~78 | −20 | ~20% |
| `templates/manim_content_pipeline.md` | 372 | ~90 | −282 | ~76% |
| **Total savings** | **836** | **~448** | **−388** | **~46%** |

### Agent Reliability Improvements

1. **Phase alignment**: The manifest fix eliminates silent schema drift between the prompt constraints and the reference docs. Any tooling that reads the manifest now agrees with what the LLM is asked to produce.

2. **Voice policy enforcement**: By adding Qwen TTS constraints to both the narration and build_scenes system prompts, the policy boundary is explicit at every code-generating and text-generating phase. Previously, an agent could produce a scene body with `from manim_voiceover_plus.services.gtts import GTTSService` without violating any explicit prompt rule.

3. **Reduced checklist duplication**: Duplicate checklists in `04_build_scenes/user.md` created competing self-evaluation loops. A single authoritative checklist with a clear rejection rule reduces the chance of the model satisfying one checklist while violating the other.

4. **Determinism boundary clarity**: Removing macOS bash sections from `manim_content_pipeline.md` eliminates template content that contradicts `DEVELOPMENT_GUIDELINES.md`. An agent that read the old template might attempt to generate bash render scripts — a script-owned responsibility. The cleaned template only provides content directly relevant to agent-generated scene bodies.
