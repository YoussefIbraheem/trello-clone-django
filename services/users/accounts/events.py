import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class BaseEvent:
    actor_id: str
    subject_id: str
    subject_type: str = "users"
    service: str = "users"
    action: str = field(init=False)
    timestamp: str = field(init=False)
    metadata: Optional[dict] = None

    def __post_init__(self):
        name = self.__class__.__name__.replace("Event", "")
        self.action = re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()
        self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class UserRegisteredEvent(BaseEvent):
    def __init__(self, subject_id: str, email: str, username: str, actor_id: str):
        self.metadata = {"email": email, "username": username}

        super().__init__(
            subject_id=subject_id, actor_id=actor_id, metadata=self.metadata
        )


@dataclass
class UserLoginEvent(BaseEvent):
    def __init__(self, subject_id: str, email: str, actor_id: str):
        super().__init__(
            subject_id=subject_id, actor_id=actor_id, metadata={"email": email}
        )


class UserLogoutEvent(BaseEvent):
    def __init__(self, subject_id: str, actor_id: str, email: str):
        super().__init__(
            subject_id=subject_id, actor_id=actor_id, metadata={"email": email}
        )


class UserUpdateEvent(BaseEvent):
    def __init__(
        self, subject_id: str, actor_id: str, email: str, updated_fields: Optional[list]
    ):
        super().__init__(
            subject_id=subject_id,
            actor_id=actor_id,
            metadata={"email": email, "updated_fields": updated_fields},
        )


@dataclass
class UserDeleteEvent(BaseEvent):
    def __init__(self, subject_id: str, email: str, actor_id: str):
        super().__init__(
            subject_id=subject_id, actor_id=actor_id, metadata={"email": email}
        )
