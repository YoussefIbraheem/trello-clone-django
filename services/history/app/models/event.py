from beanie import Document
from typing import Dict, Any
from datetime import datetime , timezone
from typing import Optional
class Event(Document):
    
    service: str
    action: str
    user_id: str
    actor_id: Optional[str] = None
    details: Dict[str, Any]
    timestamp: datetime = datetime.now(timezone.utc)
    
    class Settings:
        name =  "events"
    
