import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "projects"


def migrate_scene(scene_path: Path) -> bool:
    text = scene_path.read_text(encoding="utf-8")
    original = text

    if "from flaming_horse_voice import get_speech_service" in text:
        lines = text.splitlines()
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from manim import") or line.startswith("import numpy"):
                insert_idx = i
                break
        if not any("sys.path.insert" in l for l in lines[:6]):
            prefix = [
                "import sys",
                "from pathlib import Path",
                "",
                "sys.path.insert(0, str(Path(__file__).resolve().parents[2]))",
                "",
            ]
            lines = lines[:insert_idx] + prefix + lines[insert_idx:]
            text = "\n".join(lines)

    # Replace ElevenLabs imports with cached Qwen service.
    text = text.replace(
        "from manim_voiceover_plus.services.elevenlabs import ElevenLabsService\n"
        "from elevenlabs import VoiceSettings\n",
        "from flaming_horse_voice import get_speech_service\n",
    )
    text = text.replace(
        "from manim_voiceover_plus.services.elevenlabs import ElevenLabsService\n",
        "from flaming_horse_voice import get_speech_service\n",
    )
    text = text.replace(
        "from scripts.voice_services import get_project_voice_service\n",
        "from flaming_horse_voice import get_speech_service\n",
    )
    text = text.replace(
        "from elevenlabs import VoiceSettings\n",
        "",
    )
    text = text.replace(
        "from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS\n",
        "",
    )

    # Replace ElevenLabsService block with cached service.
    text = re.sub(
        r"self\.set_speech_service\(\s*ElevenLabsService\([\s\S]*?\)\s*\)",
        "self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))",
        text,
        flags=re.MULTILINE,
    )
    text = text.replace(
        "self.set_speech_service(get_project_voice_service())",
        "self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))",
    )
    text = text.replace(
        "self.set_speech_service(get_speech_service())",
        "self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))",
    )

    # Update comment if present.
    text = text.replace(
        "# ELEVENLABS ONLY - NO FALLBACK - FAIL LOUD",
        "# Cached Qwen voiceover (precache required)",
    )

    if text != original:
        scene_path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    if not PROJECTS_DIR.exists():
        raise SystemExit(f"Projects directory not found: {PROJECTS_DIR}")

    updated = 0
    for scene_path in PROJECTS_DIR.glob("**/scene_*.py"):
        if migrate_scene(scene_path):
            updated += 1

    print(f"Updated {updated} scene files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
