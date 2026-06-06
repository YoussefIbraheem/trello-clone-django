import re

from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field


@dataclass
class BaseEvent:
    user_id: str
    service: str = "users"
    actor_id: str = None
    action: str = field(init=False)
    timestamp: str = field(init=False)
    details: dict = None

    def __post_init__(self):
        name = self.__class__.__name__.replace("Event", "")
        self.action = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.details is None:
            self.details = {}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class UserRegisteredEvent(BaseEvent):
    def __init__(self, user_id: str, email: str, username: str, actor_id: str = None):
        self.details = {"email": email, "username": username}
        super().__init__(user_id=user_id, actor_id=actor_id, details=self.details)


@dataclass
class UserLoggedInEvent(BaseEvent):
    def __init__(self, user_id: str, email: str):
        super().__init__(
            user_id=user_id,
            details={"email": email}
        )
        
        
@dataclass
class UserDeletedEvent(BaseEvent):
    pass
