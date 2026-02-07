from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from dependencies.wallet_dependencies import get_wallet_service
from dto.wallet_response_dto import WalletResponseDto
from main import app


class TestWalletAPI:

    @pytest.fixture(autouse=True)
    def setup_mocks(self) -> Generator[None, Any]:
        self.mock_service = MagicMock()
        app.dependency_overrides[get_wallet_service] = (
            lambda: self.mock_service)
        yield
        app.dependency_overrides.clear()

    def test_create_wallet_success(self, client: TestClient) -> None:
        self.mock_service.create_wallet.return_value = WalletResponseDto(
            wallet_address="addr1", balance_btc=1.0, balance_usd=100000.0
        )

        headers = {"x-api-key": "key1"}
        response = client.post("/wallets", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["wallet_address"] == "addr1"
        assert data["balance_btc"] == 1.0
        self.mock_service.create_wallet.assert_called_once_with("key1")

    def test_create_wallet_missing_api_key(
            self, client: TestClient) -> None:
        response = client.post("/wallets")
        assert response.status_code == 422

    def test_get_wallet_success(self, client: TestClient) -> None:
        self.mock_service.get_wallet.return_value = WalletResponseDto(
            wallet_address="addr1", balance_btc=0.5, balance_usd=50000.0
        )

        headers = {"x-api-key": "key1"}
        response = client.get("/wallets/addr1", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["wallet_address"] == "addr1"
        assert data["balance_btc"] == 0.5
        self.mock_service.get_wallet.assert_called_once_with("addr1", "key1")

    def test_get_wallet_missing_api_key(self, client: TestClient) -> None:
        response = client.get("/wallets/addr1")
        assert response.status_code == 422

    def test_get_all_wallets(self, client: TestClient) -> None:
        self.mock_service.get_all_wallets.return_value = [
            WalletResponseDto(wallet_address="abc123",
                              balance_btc=0.5, balance_usd=25000.0),
            WalletResponseDto(wallet_address="def456",
                              balance_btc=1.2, balance_usd=60000.0),
        ]

        response = client.get("/wallets", headers={"x-api-key": "testkey"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["wallet_address"] == "abc123"
        assert data[0]["balance_btc"] == 0.5
        assert data[0]["balance_usd"] == 25000.0
        assert data[1]["wallet_address"] == "def456"
        assert data[1]["balance_btc"] == 1.2
        assert data[1]["balance_usd"] == 60000.0
        self.mock_service.get_all_wallets.assert_called_once()
