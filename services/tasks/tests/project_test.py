# project_test.py
import os

os.environ["DB_URL"] = "sqlite:///:memory:"

import pytest
from flask_jwt_extended import JWTManager, create_access_token
from app import create_app
from . import DummyModel

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def app():
    os.environ["DB_URL"] = "sqlite:///:memory:"
    from app.db.database import create_tables

    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["JWT_SECRET_KEY"] = "test-secret-key"
    flask_app.config["JWT_ALGORITHM"] = "HS256"

    JWTManager(flask_app)
    create_tables()

    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Generate a valid JWT token and return it as Authorization headers."""
    with app.app_context():
        token = create_access_token(identity="10")  # default identity; override per test if needed
        return {"Authorization": f"Bearer {token}"}


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_projects_list_returns_projects(client, app, monkeypatch):
    expected = [
        {
            "id": 1,
            "name": "Test Project",
            "description": "Description",
            "owner_id": 10,
        }
    ]

    def fake_get_projects_by_owner(owner_id, limit, offset):
        assert owner_id == "10"
        assert limit == "5"
        assert offset == "0"
        return [DummyModel(expected[0])]

    monkeypatch.setattr("app.apis.project_api.get_projects_by_owner", fake_get_projects_by_owner)

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='10')}"}

    response = client.get("/api/v1/projects/?owner_id=10&limit=5&offset=0", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == expected


def test_project_details_returns_project(client, app, monkeypatch):
    expected = {
        "id": 2,
        "name": "Detail Project",
        "description": "Detail description",
        "owner_id": 20,
    }

    monkeypatch.setattr(
        "app.apis.project_api.get_project_by_id",
        lambda project_id: DummyModel(expected),
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='20')}"}

    response = client.get("/api/v1/projects/2", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == expected


def test_project_create_returns_201(client, app, monkeypatch):
    # owner_id will be overwritten by get_jwt_identity(), so it must match the token identity
    payload = {"name": "New Project", "description": "New description"}
    expected = {
        "id": 3,
        "name": "New Project",
        "description": "New description",
        "owner_id": "30",  # string because get_jwt_identity() returns the identity as-is
    }

    monkeypatch.setattr(
        "app.apis.project_api.create_project",
        lambda project_data: DummyModel(expected),
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='30')}"}

    response = client.post("/api/v1/projects/", json=payload, headers=headers)

    assert response.status_code == 201
    assert response.get_json() == expected


def test_project_update_returns_201(client, app, monkeypatch):
    expected = {
        "id": 4,
        "name": "Updated Project",
        "description": "Updated description",
        "owner_id": 40,
    }

    monkeypatch.setattr(
        "app.apis.project_api.update_project",
        lambda project_id, project_data: DummyModel(expected),
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='40')}"}

    response = client.put("/api/v1/projects/4", json={"name": "Updated Project"}, headers=headers)

    assert response.status_code == 201
    assert response.get_json() == expected


def test_project_delete_returns_200(client, auth_headers, monkeypatch):
    monkeypatch.setattr("app.apis.project_api.delete_project", lambda project_id: True)

    response = client.delete("/api/v1/projects/5", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {"message": "Project Deleted Successfully!"}


def test_project_delete_not_found_returns_404(client, auth_headers, monkeypatch):
    def fake_delete_project(project_id):
        raise ValueError("Project with id 5 does not exist")

    monkeypatch.setattr("app.apis.project_api.delete_project", fake_delete_project)

    response = client.delete("/api/v1/projects/5", headers=auth_headers)

    assert response.status_code == 404
    assert "error" in response.get_json()