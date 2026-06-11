from typing import Optional
from app.events.base_event import BaseEvent, dataclass


@dataclass
class BoardCreatedEvent(BaseEvent):
    def __init__(
        self,
        project_id: str,
        name:str,
        description: Optional[str] = None,
        columns: Optional[list] = [],
    ):
        self.details = {
            "name":name,
            "description": description,
            "project_id": project_id,
            "columns": columns,
        }
        super().__init__(details=self.details)

