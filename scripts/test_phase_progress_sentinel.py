#!/usr/bin/env python3
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_VIDEO = REPO_ROOT / "scripts" / "build_video.sh"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    script = BUILD_VIDEO.read_text(encoding="utf-8")

    for name in (
        "capture_phase_progress_state",
        "ensure_phase_made_progress",
        "mark_phase_no_progress",
    ):
        require(f"{name}() {{" in script, f"{name} helper missing")

    require(
        '[[ "$phase" == "plan" ]] || return 0' in script,
        "no-progress sentinel is not scoped to plan phase",
    )
    require(
        '"action": "phase_no_progress_detected"' in script,
        "no-progress marker does not write a history action",
    )

    capture_idx = script.find('phase_progress_before="$(capture_phase_progress_state)"')
    run_idx = script.find('if run_phase_once "$current_phase"; then')
    apply_idx = script.find('apply_state_phase "$current_phase" || true')
    ensure_idx = script.find('ensure_phase_made_progress "$current_phase" "$phase_progress_before"')
    increment_idx = script.find("increment_run_count", ensure_idx)

    require(capture_idx > 0, "main loop does not capture pre-phase progress state")
    require(run_idx > capture_idx, "pre-phase progress state must be captured before phase execution")
    require(apply_idx > run_idx, "state transition must still happen after phase execution")
    require(ensure_idx > apply_idx, "no-progress check must run after deterministic state apply")
    require(increment_idx > ensure_idx, "run count increments before no-progress check")
    require(
        'mark_phase_no_progress "$current_phase" "$progress_message"' in script,
        "no-progress failure does not persist a state error",
    )

    print("OK")


if __name__ == "__main__":
    main()
