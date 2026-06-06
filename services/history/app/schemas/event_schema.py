from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId as _ObjectId
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from typing import Optional

ObjectId = Annotated[
    str, BeforeValidator(lambda v: str(v) if isinstance(v, _ObjectId) else v)
]


class EventCreate(BaseModel):
    service: str = Field(...)
    action: str = Field(...)
    user_id: str = Field(...)
    actor_id: Optional[str] = None
    details: dict = Field(...)


class EventResponse(BaseModel):
    id: ObjectId = Field(..., alias="_id")
    service: str = Field(...)
    action: str = Field(...)
    user_id: str = Field(...)
    details: dict = Field(...)
    timestamp: datetime = Field(...)


class EventsStats(BaseModel):
    pass
