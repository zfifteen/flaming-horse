# Prompt Infraction Report

**Branch:** `development`  
**Date:** 2026-02-18  
**Auditor:** Automated Analysis  

## Executive Summary

This report identifies all instances of LLM prompt content that are embedded in code, scripts, or documentation files outside the designated `harness/prompt_templates` directory. According to the repository's policy, **all prompts for the LLM backend should be in the `harness/prompt_templates` directory**.

**Findings:** 2 major infractions identified  
**Severity:** 🔴 Critical (blocks policy compliance)

---

## 🔴 CRITICAL INFRACTION #1: Embedded Prompts in `harness/prompts.py`

### Location
- **File:** `harness/prompts.py`
- **Lines:** Multiple sections throughout the file

### Description
The `harness/prompts.py` file contains extensive embedded prompt content directly in Python code. While this file correctly loads prompt templates from `harness/prompt_templates/`, it also contains additional user-facing prompt text that should be extracted into template files.

### Detailed Findings

#### 1. Plan Phase User Prompt (Lines 108-121)
```python
user_prompt = f"""You are creating a video plan for the following topic:

**Topic**: {topic}

Please create a detailed video plan following the JSON format specified in your instructions.

Think about:
1. What are the key concepts that need to be explained?
2. What is the logical sequence for explaining them?
3. What visual elements will make each concept clear?
4. How can we build understanding progressively?

Output ONLY the JSON plan. Begin your response with the opening brace.
"""
```

**Issue:** User-facing instructional prompt text is hardcoded in Python.  
**Expected Location:** Should be in `harness/prompt_templates/plan_user.md`

#### 2. Narration Phase User Prompt (Lines 160-178)
```python
user_prompt = f"""You are writing the voiceover script for this video:

**Title**: {plan_data.get("title", "Unknown")}

**Plan**:
```json
{json.dumps(plan_data, indent=2)}
```

Please write the complete narration script following the Python format specified in your instructions.

Create engaging, conversational narration for each scene that:
1. Matches the planned duration
2. Covers the key points
3. Flows naturally from scene to scene
4. Maintains audience engagement

Output ONLY the Python code (narration_script.py). Start with the comment line.
"""
```

**Issue:** User-facing instructional prompt text with numbered requirements is hardcoded.  
**Expected Location:** Should be in `harness/prompt_templates/narration_user.md`

#### 3. Build Scenes Phase User Prompt (Lines 301-338)
```python
user_prompt = f"""You are generating exactly ONE scene file for this run.

**Current Scene ID**: {scene_id}
**Expected File Name**: {scene_file_name}
**Expected Class Name**: {scene_class_name}
**Expected Narration Key**: {narration_key}
**Expected Title (Exact Match Required)**: {scene_title}

**Scene Details from Plan**:
```json
{scene_details}
```

**Current Scene Narration** (`SCRIPT["{narration_key}"]`):
```text
{scene_narration}
```

{reference_section}

{retry_section}

Generate ONLY the scene body code for `{scene_id}`.

Hard requirements:
1. Use the exact SCRIPT key: `SCRIPT["{narration_key}"]`.
2. The title text in code must exactly match: `{scene_title}` (no paraphrase).
3. Use subtitle and bullets grounded in this scene's plan details; do not use placeholders.
4. Keep semantics strictly scene-specific: use only this scene's plan details + narration text.
5. Do not introduce unrelated branding/topics/project names unless they appear in this scene's provided inputs.
6. Use class name `{scene_class_name}` and output code for file `{scene_file_name}` only.
7. Follow positioning rules (title at `UP * 3.8`, `safe_position` after `.next_to`, etc.).
8. Use standard `self.play()` for animations.
9. Forbidden placeholder strings/tokens: `{{{{TITLE}}}}`, `{{{{SUBTITLE}}}}`, `{{{{KEY_POINT_1}}}}`, `{{{{KEY_POINT_2}}}}`, `{{{{KEY_POINT_3}}}}` (and any `{{{{...}}}}` left in scaffold strings).
10. Do not reuse scaffold demo animations (default box/shape demo) unless explicitly required by this scene's plan.

Output ONLY the scene body code wrapped in <scene_body> XML tags as shown in your system instructions. Do NOT include imports, config, class definition, or helper functions - those are already in the scaffold.
"""
```

**Issue:** Extensive user-facing instructional prompt with 10 hard requirements is hardcoded.  
**Expected Location:** Should be in `harness/prompt_templates/build_scenes_user.md`

#### 4. Scene QC Phase User Prompt (Lines 390-402)
```python
user_prompt = f"""Please review all scene files for consistency and quality.

**Scene Files**:

{all_scenes}

Review each file against the QC checklist and:
1. Fix any issues found
2. Write corrected versions of modified files
3. Generate scene_qc_report.md

Output the modified scene files (with clear markers showing which file) and the QC report.
"""
```

**Issue:** User-facing instructional prompt text is hardcoded.  
**Expected Location:** Should be in `harness/prompt_templates/scene_qc_user.md`

#### 5. Scene Repair Phase User Prompt (Lines 473-511)
```python
user_prompt = f"""Please repair this scene file that failed to render.

**Current Scene ID**: {scene_id}
**Expected File Name**: {scene_file_name}
**Expected Class Name**: {scene_class_name}
**Expected Narration Key**: {narration_key}
**Expected Title (Exact Match Required)**: {scene_title}

**Scene Details from Plan**:
```json
{scene_details}
```

**Current Scene Narration** (`SCRIPT["{narration_key}"]`):
```text
{scene_narration}
```

**File**: {scene_file.name}

**Current Content**:
```python
{broken_file_content}
```

**Error**:
```
{retry_context or "Unknown error"}
```

Repair intent is strict:
1. Patch only what is needed to fix the reported failure.
2. Preserve this scene's topic and planned meaning.
3. Keep title text exactly `{scene_title}`.
4. Keep SCRIPT key exactly `SCRIPT["{narration_key}"]`.
5. Do not inject unrelated branding/topics/project names.

Output ONLY the corrected Python code. No explanations.
"""
```

**Issue:** User-facing instructional prompt with strict requirements is hardcoded.  
**Expected Location:** Should be in `harness/prompt_templates/scene_repair_user.md`

#### 6. Training Phase System Prompt (Lines 532-546)
```python
system_prompt = f"""# Flaming Horse Video Production Agent - Training Phase

You are about to generate Manim animations. Before you begin, study the official 
Manim Community Edition documentation below to ensure you use the correct APIs.

{manim_training}

---

## YOUR RESPONSE

Your response to this prompt is not important. You may simply reply with "Ready" 
when you have finished studying the documentation.

The actual scene generation will follow in the next phase.
"""
```

**Issue:** System prompt header and instructions are hardcoded in Python.  
**Expected Location:** Should be in `harness/prompt_templates/training_system.md` (or integrated with existing template)

#### 7. Training Phase User Prompt (Lines 549-550)
```python
user_prompt = """Please review the Manim documentation provided above. 
When you are ready to proceed with scene generation, reply with "Ready"."""
```

**Issue:** User-facing instructional prompt text is hardcoded.  
**Expected Location:** Should be in `harness/prompt_templates/training_user.md`

#### 8. System Prompt Headers (Multiple Locations)
```python
# Line 92
system_prompt = f"""# Flaming Horse Video Production Agent - Plan Phase
...
"""

# Line 140
system_prompt = f"""# Flaming Horse Video Production Agent - Narration Phase
...
"""

# Line 199
system_prompt = f"""# Video Production Agent - Build Scenes Phase
...
"""

# Line 357
system_prompt = f"""# Flaming Horse Video Production Agent - Scene QC Phase
...
"""

# Line 423
system_prompt = f"""# Video Production Agent - Scene Repair Phase
...
"""
```

**Issue:** System prompt headers and structural text are embedded in Python code. While these compose from templates, the wrapper text and formatting should also be templated.

### Impact
- **Maintainability:** Prompt changes require Python code modifications
- **Version Control:** Prompt evolution mixed with code changes
- **Collaboration:** Non-technical stakeholders cannot review/edit prompts
- **Testing:** Cannot easily A/B test prompt variations
- **Audit Trail:** Prompt changes not isolated in dedicated template files

### Recommendation
1. Create user prompt template files for each phase in `harness/prompt_templates/`:
   - `plan_user.md`
   - `narration_user.md`
   - `build_scenes_user.md`
   - `scene_qc_user.md`
   - `scene_repair_user.md`
   - `training_user.md`

2. Move all instructional text, numbered lists, and formatting directives into these templates

3. Update `harness/prompts.py` to load these templates using the existing `read_file()` pattern

4. Use template variables (e.g., `{{topic}}`, `{{scene_id}}`) for dynamic content insertion

---

## 🔴 CRITICAL INFRACTION #2: Embedded Prompt in Documentation

### Location
- **File:** `docs/SCENE_QC_AGENT_PROMPT.md`
- **Lines:** 15-93 (entire prompt section)

### Description
This documentation file contains a complete LLM prompt that should be in the templates directory. The file is titled "Scene QC Agent Prompt" and contains a full prompt under "## Prompt (Copy/Paste)" section.

### Detailed Content
```markdown
## Prompt (Copy/Paste)

You are the Scene QC agent for a Manim voiceover project.

Your job is to validate and repair scene code quality in-place, without changing the narrative intent.

Scope:
- Input: scene files listed in `project_state.json` under `scenes[].file`.
- Output: patched scene files + a concise QC report.

Hard requirements:
1. Fix timing safety issues.
   - No `self.wait(...)` with duration `<= 0`.
   - No animation `run_time < 0.3`.
   - Avoid expressions that can collapse to zero waits (example: `a - a`).
[... extensive requirements continue for ~80 lines ...]
```

### Issue Analysis
This file contains:
- Complete system/user prompt instructions
- Detailed requirements and constraints
- Validation checklists
- Output format specifications
- Operational notes

This is **duplicate content** that likely overlaps with or should be consolidated with `harness/prompt_templates/scene_qc_system.md`.

### Impact
- **Duplication:** Two sources of truth for Scene QC prompt content
- **Synchronization Risk:** Changes to one may not reflect in the other
- **Confusion:** Unclear which version is authoritative
- **Policy Violation:** Prompt content exists outside designated directory

### Recommendation
1. **Evaluate overlap:** Compare content with `harness/prompt_templates/scene_qc_system.md`
2. **Consolidate:** Merge unique content into the official template
3. **Convert to reference:** Transform `docs/SCENE_QC_AGENT_PROMPT.md` into a reference guide that points to the template
4. **Or Delete:** If content is already in templates, remove the documentation file entirely

---

## Summary of Infractions

| # | Location | Type | Severity | Lines of Prompt Content |
|---|----------|------|----------|------------------------|
| 1 | `harness/prompts.py` - Plan user prompt | Embedded code | 🔴 Critical | 14 |
| 2 | `harness/prompts.py` - Narration user prompt | Embedded code | 🔴 Critical | 19 |
| 3 | `harness/prompts.py` - Build scenes user prompt | Embedded code | 🔴 Critical | 38 |
| 4 | `harness/prompts.py` - Scene QC user prompt | Embedded code | 🔴 Critical | 13 |
| 5 | `harness/prompts.py` - Scene repair user prompt | Embedded code | 🔴 Critical | 39 |
| 6 | `harness/prompts.py` - Training system prompt | Embedded code | 🔴 Critical | 15 |
| 7 | `harness/prompts.py` - Training user prompt | Embedded code | 🔴 Critical | 2 |
| 8 | `harness/prompts.py` - System prompt headers | Embedded code | 🟠 High | ~30 |
| 9 | `docs/SCENE_QC_AGENT_PROMPT.md` | Documentation | 🔴 Critical | 80+ |

**Total Embedded Prompt Lines:** ~250+ lines

---

## Compliance Analysis

### Current State
- ✅ **System prompts partially compliant:** Core content loaded from `harness/prompt_templates/*.md`
- ❌ **User prompts non-compliant:** All user prompts are embedded in Python code
- ❌ **Documentation non-compliant:** One documentation file contains full prompt
- ⚠️  **Formatting non-compliant:** System prompt headers/wrappers are hardcoded

### Policy Requirements
According to the stated policy:
> All prompts for the LLM back end should be in the `harness/prompt_templates` directory.

**Interpretation:**
- "All prompts" = system prompts + user prompts + any instructional text sent to LLM
- "Should be in" = stored as template files, not embedded in code
- Current implementation only stores system prompt **content** in templates, but embeds:
  - User prompt instructions
  - System prompt wrappers/headers
  - Formatting directives

### Compliance Gap
- **Current Compliance:** ~50% (system prompt content only)
- **Target Compliance:** 100% (all prompt text in templates)
- **Gap:** ~250 lines of embedded prompt content

---

## Recommended Remediation Plan

### Phase 1: Extract User Prompts (High Priority)
1. Create new template files:
   ```
   harness/prompt_templates/
   ├── plan_user.md
   ├── narration_user.md
   ├── build_scenes_user.md
   ├── scene_qc_user.md
   ├── scene_repair_user.md
   └── training_user.md
   ```

2. Move all user prompt text from `harness/prompts.py` into these files

3. Use placeholder syntax for variable interpolation:
   ```markdown
   **Topic**: {{topic}}
   **Current Scene ID**: {{scene_id}}
   ```

4. Update `compose_*_prompt()` functions to load and interpolate templates

### Phase 2: Extract System Prompt Headers (Medium Priority)
1. Move system prompt wrapper text into existing template files
2. Remove hardcoded headers from Python code
3. Let templates control all formatting and structure

### Phase 3: Consolidate Documentation (Medium Priority)
1. Compare `docs/SCENE_QC_AGENT_PROMPT.md` with `harness/prompt_templates/scene_qc_system.md`
2. Merge any unique content into the official template
3. Convert documentation to a reference guide or remove if redundant

### Phase 4: Validation (High Priority)
1. Add unit tests to verify no prompt text exists in Python files
2. Add CI check to enforce policy compliance
3. Document template variable syntax and conventions

---

## Testing Strategy

To prevent future infractions:

1. **Static Analysis:**
   ```bash
   # Detect embedded prompt patterns in Python files
   grep -r "You are\|Please\|Generate\|Create a" \
     --include="*.py" \
     --exclude-dir="harness/prompt_templates" \
     harness/ scripts/
   ```

2. **Template Coverage Test:**
   - Verify all `compose_*_prompt()` functions load from templates
   - Ensure no f-string contains instructional text

3. **Content Audit:**
   - Regular review of `harness/prompt_templates/` completeness
   - Verify templates contain all prompt content

---

## Benefits of Full Compliance

### Maintainability
- ✅ Prompt engineers can edit templates without touching code
- ✅ Version control shows prompt evolution separately from code changes
- ✅ Easier to review and approve prompt changes

### Flexibility
- ✅ A/B test prompt variations by swapping template files
- ✅ Support multiple prompt strategies (e.g., locale-specific)
- ✅ Rapid iteration on prompt wording without code deployment

### Collaboration
- ✅ Non-technical stakeholders can contribute to prompts
- ✅ Clear separation of concerns (logic vs. content)
- ✅ Easier to maintain prompt quality standards

### Auditability
- ✅ Complete history of prompt changes in template files
- ✅ Clear accountability for prompt modifications
- ✅ Easier to identify which prompt version caused issues

---

## Note: Out-of-Scope Files

### AGENTS.md
- **File:** `AGENTS.md`
- **Content:** Contains system prompt instructions (e.g., "You are an incremental video production agent")
- **Status:** ⚠️ Out of scope for this audit
- **Reason:** This file appears to be a system prompt for **GitHub Copilot agents** (development tooling), not for the **Flaming Horse LLM backend** (video generation). The policy specifically states "prompts for the LLM back end", which refers to the video production pipeline.
- **References:** Mentioned in `.github/agents/flaming-horse-generator-auditor.md` as documentation for custom GitHub agents
- **Action:** No action required unless policy scope changes

---

## Conclusion

The repository has made good progress toward prompt policy compliance by storing system prompt **content** in `harness/prompt_templates/`. However, **significant embedded prompt content remains in code**, totaling approximately 250+ lines across:

1. **User prompts** (all phases) - embedded in Python
2. **System prompt headers/wrappers** - embedded in Python
3. **Documentation file** - contains full duplicate prompt

**Recommended Action:** Implement the remediation plan to achieve 100% compliance, starting with Phase 1 (user prompts) as the highest priority.

---

## Appendix: Template Extraction Examples

### Example 1: Plan User Prompt Template

**File:** `harness/prompt_templates/plan_user.md`
```markdown
You are creating a video plan for the following topic:

**Topic**: {{topic}}

Please create a detailed video plan following the JSON format specified in your instructions.

Think about:
1. What are the key concepts that need to be explained?
2. What is the logical sequence for explaining them?
3. What visual elements will make each concept clear?
4. How can we build understanding progressively?

Output ONLY the JSON plan. Begin your response with the opening brace.
```

**Updated Code:** `harness/prompts.py`
```python
def compose_plan_prompt(state: Dict[str, Any], topic: Optional[str]) -> Tuple[str, str]:
    # System prompt (already templated)
    core_rules = read_file(PROMPT_TEMPLATES_DIR / "core_rules.md")
    plan_system = read_file(PROMPT_TEMPLATES_DIR / "plan_system.md")
    # ... existing code ...
    
    # User prompt (now templated)
    user_template = read_file(PROMPT_TEMPLATES_DIR / "plan_user.md")
    user_prompt = user_template.replace("{{topic}}", topic)
    
    return system_prompt, user_prompt
```

### Example 2: Build Scenes User Prompt Template

**File:** `harness/prompt_templates/build_scenes_user.md`
```markdown
You are generating exactly ONE scene file for this run.

**Current Scene ID**: {{scene_id}}
**Expected File Name**: {{scene_file_name}}
**Expected Class Name**: {{scene_class_name}}
**Expected Narration Key**: {{narration_key}}
**Expected Title (Exact Match Required)**: {{scene_title}}

**Scene Details from Plan**:
```json
{{scene_details}}
```

**Current Scene Narration** (`SCRIPT["{{narration_key}}"]`):
```text
{{scene_narration}}
```

{{reference_section}}

{{retry_section}}

Generate ONLY the scene body code for `{{scene_id}}`.

Hard requirements:
1. Use the exact SCRIPT key: `SCRIPT["{{narration_key}}"]`.
2. The title text in code must exactly match: `{{scene_title}}` (no paraphrase).
[... etc ...]
```

---

**Report Generated:** 2026-02-18  
**Next Review:** After remediation implementation
