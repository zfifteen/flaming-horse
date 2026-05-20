#!/usr/bin/env python3
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_VIDEO = REPO_ROOT / "scripts" / "build_video.sh"
QC_FINAL_VIDEO = REPO_ROOT / "scripts" / "qc_final_video.sh"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def function_body(script: str, name: str, next_name: str) -> str:
    start = script.find(f"{name}() {{")
    require(start >= 0, f"{name} not found")
    end = script.find(f"\n{next_name}() {{", start)
    require(end >= 0, f"{next_name} not found after {name}")
    return script[start:end]


def main() -> None:
    build_script = BUILD_VIDEO.read_text(encoding="utf-8")
    assemble = function_body(build_script, "handle_assemble", "handle_complete")

    require(
        "INTER_SCENE_NARRATION_GAP_SECONDS=3" in build_script,
        "inter-scene gap constant is missing or not fixed at 3 seconds",
    )
    require(
        'if [[ "$i" -lt $((n - 1)) ]]; then' in assemble,
        "assemble does not distinguish non-final scenes from the final scene",
    )
    require(
        "tpad=stop_mode=clone:stop_duration=${INTER_SCENE_NARRATION_GAP_SECONDS}" in assemble,
        "assemble does not hold the final frame for non-final scenes",
    )
    require(
        "apad=pad_dur=${INTER_SCENE_NARRATION_GAP_SECONDS}" in assemble,
        "assemble does not add matching silent audio padding for non-final scenes",
    )
    require(
        "[${i}:v:0]setpts=PTS-STARTPTS[v${i}];" in assemble
        and "[${i}:a:0]asetpts=PTS-STARTPTS[a${i}];" in assemble,
        "assemble should leave the final scene unpadded",
    )
    require(
        "concat=n=${n}:v=1:a=1[v][a];[a]aresample=async=1:first_pts=0[aout]" in assemble,
        "assemble no longer preserves concat plus final audio timestamp normalization",
    )

    qc_script = QC_FINAL_VIDEO.read_text(encoding="utf-8")
    require(
        "EXPECTED_INTER_SCENE_SILENCE_SECONDS=3" in qc_script,
        "QC does not document the intentional inter-scene silence duration",
    )
    require(
        "SILENCE_WARNING_THRESHOLD_SECONDS=3.5" in qc_script,
        "QC silence warning threshold should tolerate the expected 3-second gap",
    )
    require(
        "duration > ${SILENCE_WARNING_THRESHOLD_SECONDS}" in qc_script,
        "QC silence detector does not use the explicit threshold",
    )

    print("OK")


if __name__ == "__main__":
    main()
