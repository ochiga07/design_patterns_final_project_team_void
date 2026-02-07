import sqlite3
from collections.abc import Generator
from sqlite3 import Connection
from typing import Any

import pytest
from starlette.testclient import TestClient

from main import app
from repository.user_repository import UserRepository
from service.user_service import UserService


@pytest.fixture
def db_connection() -> Generator[Connection, Any]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            api_key TEXT NOT NULL
        )
    """)
    yield conn
    conn.close()


@pytest.fixture
def user_service(db_connection: Connection) -> UserService:
    return UserService(UserRepository(db_connection))


@pytest.fixture
def client(user_service: UserService) -> Generator[TestClient, Any]:
    app.dependency_overrides = {"get_user_service": lambda: user_service} # type: ignore
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_user_and_get_user_by_id(client: TestClient) -> None:
    response = client.post("/users", json={"name": "Alice"})
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["name"] == "Alice"
    api_key = user_data["api_key"]
    user_id = user_data["id"]

    response2 = client.get(f"/users/{user_id}")
    assert response2.status_code == 200
    user2 = response2.json()
    assert user2["name"] == "Alice"
    assert user2["api_key"] == api_key


def test_create_multiple_users(client: TestClient) -> None:
    response1 = client.post("/users", json={"name": "Bob"})
    response2 = client.post("/users", json={"name": "Charlie"})

    assert response1.status_code == 200
    assert response2.status_code == 200

    users = [response1.json(), response2.json()]
    assert users[0]["name"] == "Bob"
    assert users[1]["name"] == "Charlie"
    assert users[0]["api_key"] != users[1]["api_key"]
