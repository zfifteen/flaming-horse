"""Pydantic schema for build_scenes phase output."""

from pydantic import BaseModel, Field


class BuildScenesResponse(BaseModel):
    scene_body: str = Field(
        min_length=1,
        description="Python scene-body statements to inject into scaffold voiceover block.",
    )
