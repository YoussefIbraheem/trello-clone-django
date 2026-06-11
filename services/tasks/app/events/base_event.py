import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class BaseEvent:
    user_id:str = "tmp"
    service: str = "tasks"
    actor_id: Optional[str] = None
    action: str = field(init=False)
    timestamp: str = field(init=False)
    details: Optional[dict] = None

    def __post_init__(self):
        name = self.__class__.__name__.replace("Event", "")
        self.action = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.details is None:
            self.details = {}

    def to_dict(self) -> dict:
        return asdict(self)