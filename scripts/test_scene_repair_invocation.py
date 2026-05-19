#!/usr/bin/env python3
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_VIDEO = REPO_ROOT / "scripts" / "build_video.sh"


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
    script = BUILD_VIDEO.read_text(encoding="utf-8")

    require(
        'REPAIR_DIAG_FILE="${LOG_DIR}/scene_repair_diagnostics.jsonl"' in script,
        "repair diagnostics JSONL path is missing",
    )
    for name in (
        "record_scene_repair_diagnostic",
        "repair_scene_until_valid",
        "invoke_scene_repair_for_gate",
    ):
        require(f"{name}() {{" in script, f"{name} function missing")

    wrapper = function_body(script, "invoke_scene_repair_for_gate", "repair_build_scene_first_pass_failure")
    require(
        'repair_scene_until_valid "$scene_id" "$scene_file" "$scene_class" "$reason"' in wrapper,
        "central repair wrapper does not call the underlying repair loop",
    )
    for outcome in ('"invoked"', '"resolved"', '"unresolved"'):
        require(outcome in wrapper, f"repair wrapper does not record {outcome}")
    for field in (
        '"scene_id": os.environ.get("SCENE_ID", "")',
        '"gate": os.environ.get("GATE", "")',
        '"reason": os.environ.get("REPAIR_REASON", "")[:2000]',
        '"attempt_count": attempt_count',
    ):
        require(field in script, f"repair diagnostic field missing: {field}")

    phase_region_start = script.find("repair_build_scene_first_pass_failure() {")
    phase_region = script[phase_region_start:]
    direct_call = 'repair_scene_until_valid "$scene_id" "$scene_file" "$scene_class"'
    require(direct_call not in phase_region, "phase code still calls repair_scene_until_valid directly")

    for gate in (
        '"$gate"',
        '"scene_qc_runtime"',
        '"final_render_syntax"',
        '"final_render_invalid_animation"',
        '"final_render_render_failure"',
    ):
        require(gate in phase_region, f"repair gate is not routed through wrapper: {gate}")

    print("OK")


if __name__ == "__main__":
    main()
