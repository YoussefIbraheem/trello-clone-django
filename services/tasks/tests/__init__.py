import os
import sqlite3

import pytest
from flask_jwt_extended import JWTManager, create_access_token


class DummyModel:
    """Shared dummy model for monkeypatching service return values."""
    def __init__(self, data):
        self._data = data

    def model_dump(self):
        return self._data


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    yield conn
    conn.close()