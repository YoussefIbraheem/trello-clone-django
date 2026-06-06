from app.models.event import Event
from app.db.database import connect_db
from app.schemas.event_schema import EventCreate, EventsStats, EventResponse
from typing import Optional
from datetime import datetime, timezone

async def get_events(
    service: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    filters = []

    if service:
        filters.append(Event.service == service)
    if user_id:
        filters.append(Event.user_id == user_id)
        
    query = Event.find(*filters)

    events = await query.sort(-Event.timestamp).skip(offset).limit(limit).to_list()
    
    return [EventResponse(**event.model_dump(by_alias=True)) for event in events]


async def get_event_by_id(event_id: str):

    event = await Event.get(event_id)

    if not event:
        return None

    return EventResponse(**event.model_dump(by_alias=True))


async def create_event(event_data: dict):

    event_create = EventCreate(**event_data)
    event = Event(
        service=event_create.service,
        action=event_create.action,
        user_id=event_create.user_id,
        details=event_create.details,
        timestamp=datetime.now(timezone.utc),
    )

    await event.insert()
    return str(event.id)