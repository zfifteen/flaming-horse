"""
Pydantic schema for the plan phase output.

Constraints:
  - durations must be positive integers
"""

from typing import List

from pydantic import BaseModel, Field


class SceneItem(BaseModel):
    title: str = Field(description="Scene title")
    description: str = Field(description="Scene description")
    estimated_duration_seconds: int = Field(
        gt=0,
        description="Estimated scene duration in seconds (positive integer)"
    )
    visual_ideas: List[str] = Field(
        description="Concrete visual ideas for the scene",
    )


class PlanResponse(BaseModel):
    title: str = Field(description="Video title")
    description: str = Field(description="Video description")
    target_duration_seconds: int = Field(
        gt=0,
        description="Total target duration in seconds (positive integer)"
    )
    scenes: List[SceneItem] = Field(
        description="Ordered list of scenes",
    )
