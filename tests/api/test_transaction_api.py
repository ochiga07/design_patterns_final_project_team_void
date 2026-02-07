from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from dependencies.transaction_dependencies import get_transaction_service
from dto.statistics_response_dto import StatisticsResponseDto
from dto.transaction_response_dto import TransactionResponseDto
from main import app


class TestTransactionAPI:

    @pytest.fixture(autouse=True)
    def setup_mocks(self) -> Generator[None, Any]:
        self.mock_service = MagicMock()
        app.dependency_overrides[get_transaction_service] = lambda: self.mock_service
        yield
        app.dependency_overrides.clear()

    def test_get_statistics_success(self, client: TestClient) -> None:
        self.mock_service.get_statistics.return_value = StatisticsResponseDto(
            total_transactions=10, platform_profit=500
        )

        headers = {"admin-api-key": "secret_admin_api_key"}
        response = client.get("/statistics", headers=headers)

        assert response.status_code == 200
        assert response.json() == {"total_transactions": 10, "platform_profit": 500}

    def test_get_statistics_forbidden(self, client: TestClient) -> None:
        headers = {"admin-api-key": "wrong_key"}
        response = client.get("/statistics", headers=headers)

        assert response.status_code == 401

    def test_get_transactions_success(self, client: TestClient) -> None:
        self.mock_service.get_transactions.return_value = [
            TransactionResponseDto(
                sender_wallet_address="addr1",
                receiver_wallet_address="addr2",
                transfer_amount=100,
                transferred_amount=100,
                transfer_fee=0
            )
        ]

        headers = {"x-api-key": "key1"}
        response = client.get("/transactions", headers=headers)

        assert response.status_code == 200
        self.mock_service.get_transactions.assert_called_once_with("key1")

    def test_make_transaction_success(self, client: TestClient) -> None:
        self.mock_service.make_transaction.return_value = TransactionResponseDto(
            sender_wallet_address="W1",
            receiver_wallet_address="W2",
            transfer_amount=500,
            transferred_amount=500,
            transfer_fee=0
        )

        payload = {
            "sender_wallet_address": "W1",
            "receiver_wallet_address": "W2",
            "transfer_amount": 500
        }
        headers = {"x-api-key": "key1"}
        response = client.post("/transactions", json=payload, headers=headers)

        assert response.status_code == 200

    def test_get_wallet_transactions_success(self, client: TestClient) -> None:
        self.mock_service.get_wallet_related_transactions.return_value = []

        headers = {"x-api-key": "key1"}
        response = client.get("/wallets/W1/transactions", headers=headers)

        assert response.status_code == 200
        (self.mock_service.get_wallet_related_transactions.
         assert_called_once_with("W1", "key1"))
