"""
Pydantic schema for the plan phase output.

Constraints (from harness/prompts/00_plan/manifest.yaml):
  - 8-12 scenes
  - 20-45 seconds per scene
  - total target duration 240-480 seconds
"""

from typing import List

from pydantic import BaseModel, Field


class SceneItem(BaseModel):
    title: str = Field(description="Scene title")
    description: str = Field(description="Scene description")
    estimated_duration_seconds: int = Field(
        ge=20,
        le=45,
        description="Estimated scene duration in seconds (20-45)"
    )
    visual_ideas: List[str] = Field(
        description="Concrete visual ideas for the scene",
    )


class PlanResponse(BaseModel):
    title: str = Field(description="Video title")
    description: str = Field(description="Video description")
    target_duration_seconds: int = Field(
        ge=240,
        le=480,
        description="Total target duration in seconds (240-480)"
    )
    scenes: List[SceneItem] = Field(
        description="Ordered list of scenes (8-12 items)",
    )
