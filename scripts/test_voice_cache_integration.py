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
        "ensure_voice_cache.py" in script,
        "build_video.sh does not call shared voice cache readiness owner",
    )
    require(
        "voice_cache_index_path()" not in script,
        "build_video.sh still has a local voice cache index path helper",
    )

    runtime_check = function_body(
        script,
        "ensure_qwen_cache_index",
        "runtime_validate_scene_with_preconditions",
    )
    require(
        'ensure_voice_cache.py" --project-dir "$PROJECT_DIR" --check' in runtime_check,
        "runtime cache precondition does not use ensure_voice_cache.py",
    )
    require(
        "precache_voiceovers_qwen.py" in runtime_check,
        "runtime cache precondition no longer preserves precache-on-missing behavior",
    )
    require(
        runtime_check.count("ensure_voice_cache.py") == 2,
        "runtime cache precondition should check before and after precache",
    )

    precache = function_body(script, "handle_precache_voiceovers", "handle_final_render")
    require(
        "ensure_voice_cache.py" in precache,
        "--skip-precache cache check does not use ensure_voice_cache.py",
    )

    final_render = function_body(script, "handle_final_render", "handle_assemble")
    require(
        "ensure_voice_cache.py" in final_render,
        "final_render cache precondition does not use ensure_voice_cache.py",
    )
    require(
        '[[ -n "${SKIP_PRECACHE}" ]]' in final_render,
        "final_render does not have an explicit --skip-precache validation branch",
    )
    require(
        "skip_precache_voice_cache_missing" in final_render,
        "final_render skip-precache failure is not recorded through update_project_state.py",
    )
    require(
        final_render.find('[[ -n "${SKIP_PRECACHE}" ]]') < final_render.find("handle_precache_voiceovers"),
        "final_render skip-precache branch should validate before any precache generation path",
    )
    require(
        "cache_index=" not in final_render,
        "final_render still computes cache_index locally",
    )

    print("OK")


if __name__ == "__main__":
    main()
