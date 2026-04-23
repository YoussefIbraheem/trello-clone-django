import pytest
import sqlite3

@pytest.fixture
def db_conn():
    # Setup: Create connection and table
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    yield conn
    # Teardown: Close connection after test
    conn.close()