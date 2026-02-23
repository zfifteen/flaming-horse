"""Pydantic schema for narration phase output."""

from typing import Dict

from pydantic import BaseModel, Field


class NarrationResponse(BaseModel):
    script: Dict[str, str] = Field(
        description="Mapping from narration_key to narration text.",
    )
