# gTTS Removal Summary - 2026-02-11

## What Was Changed

### Files Updated

1. **system_prompt.md**
   - Added prominent warning at top about ElevenLabs-only policy
   - Removed gTTS imports from template code
   - Removed if/else dev/prod toggle pattern
   - Updated CRITICAL RULES to explicitly prohibit gTTS
   - Changed scene template to ElevenLabs-only

2. **reference_docs/manim_voiceover.md**
   - Added warning at top about ElevenLabs-only policy
   - Marked "dev/prod toggle" pattern as DEPRECATED
   - Replaced example with correct ElevenLabs-only pattern
   - Added warnings that other TTS backends are for reference only

3. **README.md**
   - Added prominent link to VOICE_POLICY.md at top
   - Added TL;DR warning about ElevenLabs-only requirement

4. **VOICE_POLICY.md** (NEW)
   - Created comprehensive policy document
   - Lists all prohibited TTS services
   - Shows correct vs incorrect code patterns
   - Explains consequences of violations
   - Answers common questions

## Changes Made

### Removed
- ❌ gTTS imports (`from manim_voiceover_plus.services.gtts import GTTSService`)
- ❌ Dev/prod toggle pattern (`if os.getenv("MANIM_VOICE_PROD"):`)
- ❌ Fallback code suggestions
- ❌ References to "development mode" with different voice

### Added
- ✅ ElevenLabs-only code pattern
- ✅ Voice ID specification (`rBgRd5IfS6iqrGfuhlKR`)
- ✅ Explicit warnings about prohibited services
- ✅ Policy enforcement documentation
- ✅ Clear "ELEVENLABS ONLY" messaging throughout

## Voice Configuration

**Required Configuration:**
- Service: ElevenLabs
- Voice ID: `rBgRd5IfS6iqrGfuhlKR` (Big D's cloned voice)
- Model: `eleven_multilingual_v2`
- API Key: Must be set in environment as `ELEVENLABS_API_KEY`

**Prohibited:**
- Any other TTS service (gTTS, Azure, OpenAI, pyttsx3, etc.)
- Fallback code (no if/else for dev vs prod)
- Development mode with different voice

## Correct Code Pattern

```python
from manim import *
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS
from narration_script import SCRIPT

class MyScene(VoiceoverScene):
    def construct(self):
        # ELEVENLABS ONLY - NO FALLBACK
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )
        
        with self.voiceover(text=SCRIPT["my_key"]) as tracker:
            # animations synchronized to voice
            pass
```

## Files Not Changed

The following files contain gTTS references but are **documentation of what happened** (post-mortems, lessons learned), not active templates:

- POST_MORTEM_simple_math.md
- LESSONS_LEARNED_COMPLETE.md
- LESSONS_LEARNED.md
- VALIDATION_COMPLETE.md
- VALIDATION_IMPROVEMENTS.md
- IMPLEMENTATION_SUMMARY.md
- TEST_READINESS.md
- PROJECT_UPDATE_PLAN.md

These files are historical records and should NOT be used as templates.

## Validation

All template code and active documentation now:
- ✅ Uses ElevenLabs only
- ✅ Has no gTTS imports
- ✅ Has no fallback patterns
- ✅ Clearly states ElevenLabs-only policy
- ✅ Shows correct voice ID (rBgRd5IfS6iqrGfuhlKR)

## Next Steps

1. ✅ system_prompt.md updated
2. ✅ reference_docs/manim_voiceover.md updated
3. ✅ README.md updated
4. ✅ VOICE_POLICY.md created
5. ✅ All active templates now ElevenLabs-only

**Status:** Complete. All gTTS references removed from active templates and documentation.

---

**Created:** 2026-02-11 03:52 UTC  
**Enforcement:** Immediate - all new projects must follow ElevenLabs-only policy
