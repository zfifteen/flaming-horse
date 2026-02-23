"""Pydantic schema for build_scenes phase output."""

from pydantic import BaseModel, Field


class BuildScenesResponse(BaseModel):
    scene_body: str = Field(
        description="Python scene-body statements to inject into scaffold voiceover block.",
    )
