# 🚨 VOICE SERVICE POLICY - MANDATORY READING

## THE RULE

**ELEVENLABS ONLY. NO EXCEPTIONS. NO FALLBACK. NO DEV MODE.**

## Voice Configuration

- **Service:** ElevenLabs Text-to-Speech
- **Voice ID:** `rBgRd5IfS6iqrGfuhlKR` (Big D's cloned voice)
- **Model:** `eleven_multilingual_v2`
- **API Key:** Must be set as `ELEVENLABS_API_KEY` environment variable

## What is PROHIBITED

❌ **NEVER** use gTTS (Google Text-to-Speech)  
❌ **NEVER** use Azure TTS  
❌ **NEVER** use OpenAI TTS  
❌ **NEVER** use pyttsx3  
❌ **NEVER** use any TTS service other than ElevenLabs  
❌ **NEVER** create fallback code (if/else for dev vs prod)  
❌ **NEVER** import GTTSService or any non-ElevenLabs service  
❌ **NEVER** create a "development mode" with different voice  

## What is REQUIRED

✅ **ALWAYS** use ElevenLabsService  
✅ **ALWAYS** use voice ID `rBgRd5IfS6iqrGfuhlKR`  
✅ **ALWAYS** use model `eleven_multilingual_v2`  
✅ **ALWAYS** fail the video if ElevenLabs is not available  
✅ **ALWAYS** import from `voice_config.py` (centralized configuration)  

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
        
        with self.voiceover(text=SCRIPT["my_narration"]) as tracker:
            # animations here
            pass
```

## Incorrect Code Pattern (DO NOT USE)

```python
# ❌ WRONG - NEVER DO THIS
import os
from manim_voiceover_plus.services.gtts import GTTSService  # ❌ PROHIBITED IMPORT

class MyScene(VoiceoverScene):
    def construct(self):
        # ❌ WRONG - NO FALLBACK ALLOWED
        if os.getenv("MANIM_VOICE_PROD"):
            self.set_speech_service(ElevenLabsService(...))
        else:
            self.set_speech_service(GTTSService(...))  # ❌ NEVER
```

## Why This Policy Exists

1. **Voice Consistency:** All videos must use Big D's cloned voice - no exceptions
2. **Quality Control:** gTTS is robotic and unacceptable for production
3. **No Confusion:** One voice service = simpler code, fewer bugs
4. **Fail Fast:** If ElevenLabs fails, we want to know immediately, not get a gTTS video

## What Happens if You Violate This Policy

If you generate code that uses gTTS or any non-ElevenLabs service:
- The video will be DELETED
- The code will be REJECTED
- You will need to START OVER

## Questions?

**Q: What if I want to save API credits during development?**  
A: No. Use ElevenLabs. There is no development mode.

**Q: What if ElevenLabs is down?**  
A: The video build MUST FAIL. Do not create fallback code.

**Q: What if I need to test without voice?**  
A: Don't. Test with ElevenLabs voice. That's what production will use.

**Q: But gTTS is faster...**  
A: NO. ElevenLabs only.

**Q: Can I use gTTS just for...**  
A: **NO. ELEVENLABS. ONLY.**

---

**Last Updated:** 2026-02-11  
**Enforcement:** Mandatory - violations will cause build failures
