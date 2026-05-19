#!/usr/bin/env python3
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
CREATE_VIDEO = REPO_ROOT / "scripts" / "create_video.sh"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    script = CREATE_VIDEO.read_text(encoding="utf-8")
    require(
        'PYTHON_BIN="${PYTHON:-python3.13}"' in script,
        "create_video.sh does not define the orchestration interpreter",
    )
    require(
        '"$PYTHON_BIN" -c' in script,
        "create_video.sh does not use PYTHON_BIN for Python one-liners",
    )
    require(
        '"$PYTHON_BIN" "${SCRIPT_DIR}/prepare_voice_service.py"' in script,
        "prepare_voice_service.py is not invoked with PYTHON_BIN",
    )
    require(
        'BUILD_ARGS_STR="${BUILD_ARGS_STR}" "$PYTHON_BIN" -' in script,
        "build-args parser is not invoked with PYTHON_BIN",
    )

    body_after_assignment = script.split('PYTHON_BIN="${PYTHON:-python3.13}"', 1)[1]
    bare_python = re.search(r"(?<![\w$])python3(?:\s|$)", body_after_assignment)
    require(bare_python is None, "create_video.sh still uses bare python3 after PYTHON_BIN selection")
    require(
        '${PYTHON:-python3.13}' not in body_after_assignment,
        "create_video.sh still re-resolves PYTHON after PYTHON_BIN selection",
    )
    print("OK")


if __name__ == "__main__":
    main()
