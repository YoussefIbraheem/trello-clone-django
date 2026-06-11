from beanie import Document
from typing import Dict, Any
from datetime import datetime , timezone
from pydantic import Field

def utc_now():
    return datetime.now(timezone.utc)

class Event(Document):
    
    actor_id: str
    service: str
    action: str
    subject_id: str
    subject_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    timestamp: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name =  "events"
    
