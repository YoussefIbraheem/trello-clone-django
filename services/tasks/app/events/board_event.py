from typing import Optional
from app.events.base_event import BaseEvent, dataclass


@dataclass
class BoardCreatedEvent(BaseEvent):
    def __init__(
        self,
        project_id: str,
        description: Optional[str] = None,
        columns: Optional[list] = [],
    ):
        self.details = {
            "project_id": project_id,
            "description": description,
            "columns": columns,
        }
        super().__init__(details=self.details)

