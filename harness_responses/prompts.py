"""
Prompt composer for harness_responses.

Loads phase-specific prompts from harness_responses/prompts/<phase>/.
No dependencies on harness/.
"""

import re
from pathlib import Path
from typing import Any, Dict, Tuple

PROMPTS_DIR = Path(__file__).parent / "prompts"

PHASE_DIRS: Dict[str, str] = {
    "plan": "plan",
}

PLACEHOLDER_RE = re.compile(r"{{\s*([A-Za-z0-9_]+)\s*}}")


def _read_file(path: Path) -> str:
    """Read a file; fail fast if missing."""
    if not path.exists():
        raise FileNotFoundError(f"Required prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def _render(template_text: str, values: Dict[str, Any]) -> str:
    """Render {{placeholders}}; missing keys become empty strings."""
    left_esc = "__FHR_LBRACE__"
    right_esc = "__FHR_RBRACE__"
    working = template_text.replace("{{{{", left_esc).replace("}}}}", right_esc)

    def replace(match: re.Match) -> str:
        key = match.group(1)
        val = values.get(key, "")
        return "" if val is None else str(val)

    rendered = PLACEHOLDER_RE.sub(replace, working)
    return rendered.replace(left_esc, "{{").replace(right_esc, "}}")


def compose_prompt(
    phase: str,
    topic: str = "",
    retry_context: str = "",
) -> Tuple[str, str]:
    """
    Compose system and user prompts for the given phase.

    Args:
        phase: Phase name (must be in PHASE_DIRS)
        topic: Topic string (required for plan phase)
        retry_context: Optional error context from previous attempt

    Returns:
        (system_prompt, user_prompt) tuple
    """
    if phase not in PHASE_DIRS:
        raise ValueError(
            f"Phase '{phase}' is not implemented in harness_responses. "
            f"Implemented phases: {', '.join(PHASE_DIRS)}"
        )

    phase_dir = PROMPTS_DIR / PHASE_DIRS[phase]
    values: Dict[str, Any] = {"topic": topic, "retry_context": retry_context}

    system_prompt = _render(_read_file(phase_dir / "system.md"), values)
    user_prompt = _render(_read_file(phase_dir / "user.md"), values)

    if retry_context:
        user_prompt = (
            user_prompt.rstrip()
            + f"\n\nRetry context (previous attempt failed):\n{retry_context}\n"
        )

    return system_prompt, user_prompt
