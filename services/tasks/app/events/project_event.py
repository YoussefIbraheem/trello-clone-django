from typing import Optional

from app.events.base_event import BaseEvent, dataclass


@dataclass
class ProjectCreatedEvent(BaseEvent):
    def __init__(
        self,
        project_name: str,
        owner_id: str,
        description: Optional[dict] = None,
    ):
        self.details = {"project_name": project_name, "description": description}
        super().__init__(user_id=owner_id, actor_id=owner_id, details=self.details)


class ProjectUpdatedEvent(BaseEvent):
    def __init__(self, owner_id: str, updated_fields: Optional[list] = None):
        self.details = {"updated_fields": updated_fields}
        super().__init__(user_id=owner_id, actor_id=owner_id, details=self.details)


class ProjectDeletedEvent(BaseEvent):
    def __init__(
        self,
        project_name: str,
        owner_id: str,
        description: Optional[dict] = None,
    ):
        self.details = {"project_name": project_name, "description": description}
        super().__init__(user_id=owner_id, actor_id=owner_id, details=self.details)
