# 🚨 VOICE SERVICE POLICY - MANDATORY READING

## THE RULE

**CACHED QWEN ONLY. NO EXCEPTIONS. NO FALLBACK. NO DEV MODE.**

## Voice Configuration

- **Service:** Cached Qwen voice clone
- **Model:** `Qwen/Qwen3-TTS-12Hz-1.7B-Base`
- **Config:** `voice_clone_config.json` in project root

## What is PROHIBITED

❌ **NEVER** use gTTS (Google Text-to-Speech)  
❌ **NEVER** use Azure TTS  
❌ **NEVER** use OpenAI TTS  
❌ **NEVER** use pyttsx3  
❌ **NEVER** use any network TTS service  
❌ **NEVER** create fallback code (if/else for dev vs prod)  
❌ **NEVER** import GTTSService or any non-Qwen service  
❌ **NEVER** create a "development mode" with different voice  

## What is REQUIRED

✅ **ALWAYS** use cached Qwen via `flaming_horse_voice.get_speech_service`  
✅ **ALWAYS** use model `Qwen/Qwen3-TTS-12Hz-1.7B-Base` unless overridden in `voice_clone_config.json`  
✅ **ALWAYS** fail the video if cached audio is missing  

## Correct Code Pattern

```python
from manim import *
from pathlib import Path
from pathlib import Path
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

class MyScene(VoiceoverScene):
    def construct(self):
        # CACHED QWEN ONLY - NO FALLBACK
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        
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
            self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        else:
            self.set_speech_service(GTTSService(...))  # ❌ NEVER
```

## Why This Policy Exists

1. **Voice Consistency:** All videos must use Big D's cloned voice - no exceptions
2. **Quality Control:** gTTS is robotic and unacceptable for production
3. **No Confusion:** One voice service = simpler code, fewer bugs
4. **Fail Fast:** If ElevenLabs fails, we want to know immediately, not get a gTTS video

## What Happens if You Violate This Policy

If you generate code that uses gTTS or any non-Qwen service:
- The video will be DELETED
- The code will be REJECTED
- You will need to START OVER

## Questions?

**Q: What if I want to save API credits during development?**  
A: No. Use cached Qwen. There is no development mode.

**Q: What if cached audio is missing?**  
A: The video build MUST FAIL. Run the precache step.

**Q: What if I need to test without voice?**  
A: Don't. Test with ElevenLabs voice. That's what production will use.

**Q: But gTTS is faster...**  
A: NO. Cached Qwen only.

**Q: Can I use gTTS just for...**  
A: **NO. CACHED QWEN. ONLY.**

---

**Last Updated:** 2026-02-11  
**Enforcement:** Mandatory - violations will cause build failures
