from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from dependencies.user_dependencies import get_user_service
from dto.user_create_dto import UserCreateDto
from dto.user_response_dto import UserResponseDto
from main import app


class TestUserAPI:

    @pytest.fixture(autouse=True)
    def setup_mocks(self) -> Generator[None, Any]:
        self.mock_service = MagicMock()
        app.dependency_overrides[get_user_service] = lambda: self.mock_service
        yield
        app.dependency_overrides.clear()

    def test_create_user_success(self, client: TestClient) -> None:
        self.mock_service.create_user.return_value = UserResponseDto(
            id=1,
            name="Naruto",
            api_key="generated_key"
        )

        payload = {"name": "Naruto"}
        response = client.post("/users", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["api_key"] == "generated_key"

        self.mock_service.create_user.assert_called_once()
        called_arg = self.mock_service.create_user.call_args[0][0]
        assert isinstance(called_arg, UserCreateDto)
        assert called_arg.name == "Naruto"

    def test_create_user_missing_name(self, client: TestClient) -> None:
        response = client.post("/users", json={})

        assert response.status_code == 422

    def test_create_user_empty_name(self, client: TestClient) -> None:
        payload = {"name": ""}

        response = client.post("/users", json=payload)

        assert response.status_code == 422

    def test_create_multiple_users(self, client: TestClient) -> None:
        self.mock_service.create_user.side_effect = [
            UserResponseDto(id=1, name="yo", api_key="key1"),
            UserResponseDto(id=2, name="yo", api_key="key2"),
        ]

        r1 = client.post("/users", json={"name": "A"})
        r2 = client.post("/users", json={"name": "B"})

        assert r1.status_code == 200
        assert r2.status_code == 200

        assert r1.json()["api_key"] == "key1"
        assert r2.json()["api_key"] == "key2"

        assert self.mock_service.create_user.call_count == 2

    def test_get_all_users(self, client: TestClient) -> None:
        self.mock_service.get_all_users.return_value = [
            UserResponseDto(id=1,name="Naruto", api_key="key1"),
            UserResponseDto(id=2,name="Sasuke", api_key="key2"),
        ]

        response = client.get("/users")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["name"] == "Naruto"
        assert data[0]["api_key"] == "key1"
        assert data[1]["name"] == "Sasuke"
        assert data[1]["api_key"] == "key2"

        self.mock_service.get_all_users.assert_called_once()

    def test_get_user_by_id(self, client: TestClient) -> None:
        self.mock_service.get_user.return_value = UserResponseDto(
            id=1,
            name="Naruto",
            api_key="key1"
        )

        response = client.get("/users/123")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Naruto"
        assert data["api_key"] == "key1"

        self.mock_service.get_user.assert_called_once_with(123)
