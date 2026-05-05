import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from pydantic import ValidationError

from app.services.event_service import create_event, get_event_by_id, get_events


@pytest.mark.asyncio
async def test_get_events_returns_event_responses():
    mock_event = MagicMock()
    mock_event.model_dump.return_value = {
        "_id": "event-1",
        "service": "test-service",
        "action": "created",
        "user_id": "user-123",
        "details": {"key": "value"},
        "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }

    with patch("app.services.event_service.Event") as MockEvent:
        mock_query = MagicMock()
        mock_query.sort.return_value.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=[mock_event])
        MockEvent.find.return_value = mock_query

        events = await get_events(service="test-service")

    assert len(events) == 1
    assert events[0].service == "test-service"
    assert events[0].action == "created"


@pytest.mark.asyncio
async def test_get_event_by_id_returns_response():
    mock_event = MagicMock()
    mock_event.model_dump.return_value = {
        "_id": "event-1",
        "service": "test-service",
        "action": "created",
        "user_id": "user-123",
        "details": {"key": "value"},
        "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }

    with patch("app.services.event_service.Event") as MockEvent:
        MockEvent.get = AsyncMock(return_value=mock_event)
        event = await get_event_by_id("event-1")

    assert event is not None
    assert event.service == "test-service"


@pytest.mark.asyncio
async def test_get_event_by_id_returns_none_for_missing():
    with patch("app.services.event_service.Event") as MockEvent:
        MockEvent.get = AsyncMock(return_value=None)
        event = await get_event_by_id("missing-id")

    assert event is None


@pytest.mark.asyncio
async def test_create_event_inserts_and_returns_id():
    with patch("app.services.event_service.Event") as MockEvent:
        mock_instance = MagicMock()
        mock_instance.insert = AsyncMock()
        mock_instance.id = "new-event-id"
        MockEvent.return_value = mock_instance

        result = await create_event({
            "service": "history",
            "action": "create",
            "user_id": "user-321",
            "details": {"resource": "board"},
        })

    assert result == "new-event-id"


@pytest.mark.asyncio
async def test_create_event_requires_user_id():
    with pytest.raises(ValidationError):
        await create_event({
            "service": "history",
            "action": "create",
            "details": {"resource": "board"},
        })