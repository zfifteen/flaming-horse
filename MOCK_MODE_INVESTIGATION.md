# Mock Mode Investigation

**Date:** 2026-02-16  
**Investigator:** GitHub Copilot Agent

---

## Issue Description Reference

The original issue (#audit-documentation-pipeline-qc) mentioned a `--mock` flag:

> If needed, the mock path remains valid for cloud/CI or constrained environments:
> ```bash
> ./scripts/create_video.sh copilot-test-video-1 --topic "Create a video explaining trial division." --mock
> ```

## Investigation Results

### Search Results

**Searched locations:**
- `scripts/create_video.sh` - No `--mock` flag in argument parser
- `scripts/build_video.sh` - No mock mode references
- `docs/*.md` - No mock mode documentation
- `reference_docs/*.md` - No mock mode documentation
- `AGENTS.md` - No mock mode guidance

**Command executed:**
```bash
grep -rn "mock\|MOCK\|--mock" scripts/ docs/ reference_docs/ AGENTS.md
# Result: No matches
```

### Conclusion

**Mock mode does NOT exist in the current codebase.**

The reference in the issue description was aspirational or from a different context. No implementation exists for:
- `--mock` command-line flag
- Mock TTS service fallback
- Placeholder audio generation

---

## Why Mock Mode Would Be Useful

### Use Cases
1. **CI/CD pipelines** - Test video generation without downloading Qwen model (3GB+)
2. **Quick validation** - Verify scene code and positioning without waiting for TTS
3. **Resource-constrained environments** - Run on machines without GPU or sufficient RAM
4. **Development iteration** - Faster feedback loops during scene development

### Implementation Considerations

If mock mode were to be implemented, it should:

1. **Use silent audio or beep placeholders** (not real TTS)
2. **Preserve timing** - Use estimated duration from word count (150 words/min)
3. **Clear labeling** - Add watermark or text overlay saying "MOCK MODE"
4. **Exit early** - Skip voice precache and synthesis steps
5. **Be opt-in only** - Never used for production builds

**Example flag design:**
```bash
./scripts/create_video.sh my_video --topic "..." --mock-audio
```

**Environment variable alternative:**
```bash
FLAMING_HORSE_MOCK_MODE=1 ./scripts/build_video.sh projects/my_video
```

---

## Current Voice Policy Alignment

The absence of mock mode aligns with the documented voice policy:

**From docs/VOICE_POLICY.md:**
> ❌ **NEVER** create fallback code (if/else for dev vs prod)
> ❌ **NEVER** create a "development mode" with different voice

**From AGENTS.md:**
> ❌ **NEVER** create conditional fallback patterns

**Conclusion:** Current implementation correctly enforces Qwen-only production path with no development shortcuts.

---

## Recommendation

**Do NOT implement mock mode** unless the voice policy is explicitly changed.

The current "Qwen-only, no fallback" policy is:
- ✅ Clearly documented
- ✅ Consistently enforced in code
- ✅ Prevents quality degradation
- ✅ Ensures production parity

If CI/development speed is a concern, better alternatives are:
1. **Use voice cache** - Cache hits skip TTS (2-5 min savings)
2. **Render only changed scenes** - Parallel rendering already implemented
3. **Test on reduced quality** - Use `-ql` flag for faster iteration
4. **Pre-download model** - Cache Qwen model in CI environment

---

## Documentation Update Needed

**Finding:** Issue description mentioned `--mock` but no implementation or documentation exists.

**Action taken:** Created this investigation document to clarify current state.

**Future action:** If mock mode is added, update:
- `scripts/create_video.sh` usage text
- `README.md` - Quick start section
- `docs/INSTALLATION.md` - Add mock mode section
- `AGENTS.md` - Clarify when agents can/cannot use mock mode
- Voice policy document - Reconcile "no fallback" rule with mock mode

---

**Status:** ✅ Investigation complete - Mock mode confirmed not implemented  
**Documentation:** ✅ Current docs correctly reflect Qwen-only policy  
**Recommendation:** ✅ Maintain current policy (no mock mode) for quality consistency
