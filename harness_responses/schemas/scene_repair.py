"""Pydantic schema for scene_repair phase output."""

from pydantic import BaseModel, Field


class SceneRepairResponse(BaseModel):
    scene_body: str = Field(
        description="Repaired Python scene-body statements to inject into scaffold voiceover block.",
    )
