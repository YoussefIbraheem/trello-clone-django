from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime



class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project Name")
    description: Optional[str] = Field(None, description="Project Description")
    owner_id: int = Field(..., description="Owner ID")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Project Name"
    )
    description: Optional[str] = Field(None, description="Project Description")

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(ProjectBase):
    id: int = Field(..., description="Project ID")
    created_at: datetime = Field(..., description="Project Creation Date and Time")
    updated_at: Optional[datetime] = Field(
        ..., description="Project Updating Date and Time"
    )

