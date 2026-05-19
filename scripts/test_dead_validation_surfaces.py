#!/usr/bin/env python3
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    removed_paths = [
        REPO_ROOT / "scripts" / "scene_validation.sh",
        REPO_ROOT / "scripts" / "build_video_validation_integration.patch",
    ]
    for path in removed_paths:
        require(not path.exists(), f"dead validation surface still exists: {path}")

    active_docs = [
        REPO_ROOT / "CURRENT_STATE.md",
        REPO_ROOT / "TECH_SPEC.md",
        REPO_ROOT / "docs" / "validation" / "VALIDATION.md",
        REPO_ROOT / "docs" / "framework-fixes" / "redundancy-and-complexity-audit.html",
        REPO_ROOT / "docs" / "framework-fixes" / "redundancy-reduction-fix-plan.html",
    ]
    forbidden = [
        "scripts/scene_validation.sh",
        "build_video_validation_integration.patch",
        "validate_scene_files_consistency",
    ]
    for path in active_docs:
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            require(token not in text, f"{path.relative_to(REPO_ROOT)} still describes {token} as active")
        require(
            "scene_validator.py" in text,
            f"{path.relative_to(REPO_ROOT)} does not name the live scene validator",
        )

    print("OK")


if __name__ == "__main__":
    main()
