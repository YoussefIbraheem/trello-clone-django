from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from services.users.accounts import events
from utils.publisher import publish_history_event

from app.events.project_event import ProjectCreatedEvent

from . import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    owner_id = Column(String(255), nullable=False, index=True)

    boards = relationship(
        "Board", back_populates="project", cascade="all, delete-orphan"
    )


@event.listens_for(Project, "after_insert")
def project_created(mapper, connection, target):

    event = ProjectCreatedEvent(
        project_name=target.name,
        owner_id=target.owner_id,
        description=target.description,
    )

    publish_history_event(event.to_dict())