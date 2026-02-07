from typing import Any
from unittest.mock import MagicMock

import pytest

from exception.exceptions import (
    UnauthorizedWalletAccessError,
    UserNotFoundError,
    WalletLimitExceededError,
    WalletNotFoundError,
)
from service.wallet_service import WalletService


class TestWalletService:

    @pytest.fixture
    def mock_deps(self) -> dict[str, Any]:
        converter = MagicMock()
        converter.satoshi_to_btc.return_value = 1.0
        converter.satoshi_to_usd.return_value = 100000.0
        return {
            "user": MagicMock(),
            "wallet": MagicMock(),
            "converter": converter,
        }

    @pytest.fixture
    def service(self, mock_deps: dict[str, Any]) -> WalletService:
        return WalletService(
            mock_deps["user"],
            mock_deps["wallet"],
            mock_deps["converter"],
        )

    def test_create_wallet_success(
            self, service: WalletService, mock_deps: dict[str, Any]
    ) -> None:
        mock_deps["user"].find_user_by_api_key.return_value = (
            MagicMock(id=1, name="Naruto"))
        mock_deps["wallet"].count_wallets_by_user_id.return_value = 0
        mock_deps["wallet"].insert_wallet.return_value = MagicMock(
            wallet_address="addr1", balance=100_000_000
        )

        result = service.create_wallet("key1")

        assert result.wallet_address == "addr1"
        assert result.balance_btc == 1.0
        mock_deps["wallet"].insert_wallet.assert_called_once()

    def test_create_wallet_user_not_found(
            self, service: WalletService, mock_deps: dict[str, Any]
    ) -> None:
        mock_deps["user"].find_user_by_api_key.return_value = None

        with pytest.raises(UserNotFoundError):
            service.create_wallet("bad_key")

    def test_create_wallet_limit_exceeded(
            self, service: WalletService, mock_deps: dict[str, Any]
    ) -> None:
        mock_deps["user"].find_user_by_api_key.return_value = (
            MagicMock(id=1, name="Naruto"))
        mock_deps["wallet"].count_wallets_by_user_id.return_value = 3

        with pytest.raises(WalletLimitExceededError):
            service.create_wallet("key1")

    def test_create_wallet_at_boundary(
            self, service: WalletService, mock_deps: dict[str, Any]
    ) -> None:
        mock_deps["user"].find_user_by_api_key.return_value = (
            MagicMock(id=1, name="Naruto"))
        mock_deps["wallet"].count_wallets_by_user_id.return_value = 2
        mock_deps["wallet"].insert_wallet.return_value = MagicMock(
            wallet_address="addr3", balance=100_000_000
        )

        result = service.create_wallet("key1")
        assert result.wallet_address == "addr3"

    def test_get_wallet_success(
            self, service: WalletService, mock_deps: dict[str, Any]
    ) -> None:
        mock_deps["user"].find_user_by_api_key.return_value = (
            MagicMock(id=1, name="Naruto"))
        mock_deps["wallet"].get_wallet_by_address.return_value = MagicMock(
            user_id=1, wallet_address="addr1", balance=50_000_000
        )

        result = service.get_wallet("addr1", "key1")
        assert result.wallet_address == "addr1"

    def test_get_wallet_user_not_found(
            self, service: WalletService, mock_deps: dict[str, Any]
    ) -> None:
        mock_deps["user"].find_user_by_api_key.return_value = None

        with pytest.raises(UserNotFoundError):
            service.get_wallet("addr1", "bad_key")

    def test_get_wallet_not_found(
            self, service: WalletService, mock_deps: dict[str, Any]
    ) -> None:
        mock_deps["user"].find_user_by_api_key.return_value = (
            MagicMock(id=1, name="Naruto"))
        mock_deps["wallet"].get_wallet_by_address.return_value = None

        with pytest.raises(WalletNotFoundError):
            service.get_wallet("bad_addr", "key1")

    def test_get_wallet_unauthorized(
            self, service: WalletService, mock_deps: dict[str, Any]
    ) -> None:
        mock_deps["user"].find_user_by_api_key.return_value = (
            MagicMock(id=1, name="Naruto"))
        mock_deps["wallet"].get_wallet_by_address.return_value = MagicMock(
            user_id=2, wallet_address="addr1"
        )

        with pytest.raises(UnauthorizedWalletAccessError):
            service.get_wallet("addr1", "key1")
