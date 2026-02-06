from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from dependencies.transaction_dependencies import get_transaction_service
from exception.exceptions import (
    NotEnoughBalanceError,
    UnauthorizedError,
    UnauthorizedWalletAccessError,
    UserNotFoundError,
    WalletNotFoundError,
)
from main import app


class TestTransactionAPIExceptions:

    @pytest.fixture(autouse=True)
    def setup_mocks(self) -> Generator[None]:
        self.mock_service = MagicMock()
        app.dependency_overrides[get_transaction_service] = lambda: self.mock_service
        yield
        app.dependency_overrides.clear()

    def test_handler_wallet_not_found_returns_404(self, client: TestClient) -> None:
        self.mock_service.make_transaction.side_effect = (
            WalletNotFoundError("Wallet 99 not found"))

        payload = {
            "sender_wallet_address": "1",
            "receiver_wallet_address": "99",
            "transfer_amount": 100
        }
        response = client.post("/transactions", json=payload,
                               headers={"x-api-key": "key1"})

        assert response.status_code == 404
        assert response.json() == {"error": "Wallet 99 not found"}

    def test_handler_not_enough_balance_returns_409(self, client: TestClient) -> None:
        self.mock_service.make_transaction.side_effect = (
            NotEnoughBalanceError("Insufficient balance"))

        payload = {
            "sender_wallet_address": "1",
            "receiver_wallet_address": "2",
            "transfer_amount": 1000000
        }
        response = client.post("/transactions",
                               json=payload, headers={"x-api-key": "key1"})

        assert response.status_code == 409
        assert response.json() == {"error": "Insufficient balance"}

    def test_handler_user_not_found_returns_404(self, client: TestClient) -> None:
        self.mock_service.get_transactions.side_effect = (
            UserNotFoundError("User not found"))

        response = client.get("/transactions", headers={"x-api-key": "key"})

        assert response.status_code == 404
        assert response.json() == {"error": "User not found"}

    def test_handler_unauthorized_wallet_access_returns_403(self,
            client: TestClient) -> None:

        self.mock_service.get_wallet_related_transactions.\
            side_effect = (UnauthorizedWalletAccessError
                                   ("Access denied to this wallet"))

        response = client.get("/wallets/2/transactions",
                              headers={"x-api-key": "user1_key"})

        assert response.status_code == 403
        assert response.json() == {"error": "Access denied to this wallet"}

    def test_handler_unauthorized_exception_returns_401(self,
              client: TestClient) -> None:
        self.mock_service.get_transactions.side_effect = (
            UnauthorizedError("Invalid API key"))

        response = client.get("/transactions", headers={"x-api-key": "invalid"})

        assert response.status_code == 401
        assert response.json() == {"error": "Invalid API key"}
