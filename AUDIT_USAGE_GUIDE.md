# Prompt Compliance Audit - Usage Guide

This directory contains the results of the prompt compliance audit for the `development` branch.

## Quick Start

```bash
# View executive summary (60 lines)
cat PROMPT_AUDIT_SUMMARY.txt

# Read full report (554 lines)
less PROMPT_INFRACTION_REPORT.md

# Run compliance checker
./scripts/check_prompt_compliance.sh
```

## Files

### PROMPT_AUDIT_SUMMARY.txt
- **Purpose:** Quick reference for stakeholders
- **Contents:** Key findings, impact assessment, priority recommendations
- **Read time:** 2-3 minutes

### PROMPT_INFRACTION_REPORT.md
- **Purpose:** Comprehensive documentation of all infractions
- **Contents:** 
  - Line-by-line analysis of embedded prompts
  - Detailed remediation plan with code examples
  - Testing strategy and compliance roadmap
  - Template extraction examples
- **Read time:** 15-20 minutes

### scripts/check_prompt_compliance.sh
- **Purpose:** Automated validation script
- **Usage:** `./scripts/check_prompt_compliance.sh`
- **Exit codes:**
  - `0` = Fully compliant
  - `1` = Infractions found
- **Integration:** Can be added to CI/CD pipeline

## Audit Summary

**Branch:** `development`  
**Date:** 2026-02-18  
**Status:** 🔴 Non-compliant

### Findings
- 2 critical infractions identified
- ~250 lines of embedded prompt content
- Current compliance: ~50% (system prompts only)
- Target compliance: 100%

### Top Infractions

1. **harness/prompts.py** - Contains 7+ embedded user prompts
2. **docs/SCENE_QC_AGENT_PROMPT.md** - Contains duplicate prompt content

### Policy

> All prompts for the LLM backend should be in the `harness/prompt_templates` directory.

## Remediation Plan

### Phase 1: Extract User Prompts (HIGH PRIORITY)
Create template files for all user prompts:
- `harness/prompt_templates/plan_user.md`
- `harness/prompt_templates/narration_user.md`
- `harness/prompt_templates/build_scenes_user.md`
- `harness/prompt_templates/scene_qc_user.md`
- `harness/prompt_templates/scene_repair_user.md`
- `harness/prompt_templates/training_user.md`

### Phase 2: Extract System Prompt Headers (MEDIUM PRIORITY)
Move system prompt wrapper text into templates

### Phase 3: Consolidate Documentation (MEDIUM PRIORITY)
Remove duplicate prompt from `docs/SCENE_QC_AGENT_PROMPT.md`

### Phase 4: Validation (HIGH PRIORITY)
- Add unit tests for template coverage
- Integrate `check_prompt_compliance.sh` into CI

## Validation

After implementing remediation:

```bash
# Should pass all checks
./scripts/check_prompt_compliance.sh
# Expected output: ✓ COMPLIANT: No infractions found
```

## Next Steps

1. Review the full report: `PROMPT_INFRACTION_REPORT.md`
2. Prioritize Phase 1 (user prompt extraction)
3. Implement remediation incrementally
4. Validate with compliance checker
5. Add CI integration to prevent future infractions

## Questions?

See the full report for:
- Detailed examples of each infraction
- Step-by-step remediation instructions
- Template extraction code examples
- Benefits of full compliance

---

**Generated:** 2026-02-18  
**Auditor:** Automated Analysis  
**Scope:** `development` branch
