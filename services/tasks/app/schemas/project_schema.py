from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime



class ProjectBase(BaseModel):
    """Shared project fields used by project creation and response models."""

    name: str = Field(..., min_length=1, max_length=255, description="Project Name")
    description: Optional[str] = Field(None, description="Project Description")
    owner_id: int = Field(..., description="Owner ID")
    
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(ProjectBase):
    """Model for creating a new project."""

    pass


class ProjectUpdate(ProjectBase):
    """Model for updating an existing project.

    Only provides optional fields so partial updates are allowed.
    """

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Project Name"
    )
    description: Optional[str] = Field(None, description="Project Description")



class ProjectResponse(ProjectBase):
    """Response model containing project metadata returned to clients."""

    id: int = Field(..., description="Project ID")
    created_at: datetime = Field(..., description="Project Creation Date and Time")
    updated_at: Optional[datetime] = Field(
        ..., description="Project Updating Date and Time"
    )

