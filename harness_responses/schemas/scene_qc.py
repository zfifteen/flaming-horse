"""Pydantic schema for scene_qc phase output."""

from pydantic import BaseModel, Field


class SceneQcResponse(BaseModel):
    report_markdown: str = Field(
        description="Markdown content for scene_qc_report.md",
    )
