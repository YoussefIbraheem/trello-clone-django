from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from app.models.task import TaskPriority, TaskStatus



class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM, description="Task priority"
    )
    user_id: str = Field(..., description="ID of the task owner")
    assigned_to: str = Field(..., description="ID of the task assingee")
    board_id: int = Field(..., description="ID of the parent board")
    due_date: Optional[datetime] = Field(None, description="Due date of the task")


class TaskResponse(TaskBase):
    id: int = Field(..., description="ID of the task")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Task update timestamp")

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Task title"
    )
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    priority: Optional[TaskPriority] = Field(None, description="Task priority")
    user_id: Optional[str] = Field(None, description="ID of the task owner")
    assigned_to: Optional[str] = Field(None, description="ID of the task assingee")
    board_id: Optional[int] = Field(None, description="ID of the parent board")
    due_date: Optional[datetime] = Field(None, description="Due date of the task")


class TaskStats(BaseModel):
    total_tasks: int = Field(..., description="Total number of tasks")
    tasks_by_status: dict = Field(..., description="Number of tasks by status")
    tasks_by_priority: dict = Field(..., description="Number of tasks by priority")
