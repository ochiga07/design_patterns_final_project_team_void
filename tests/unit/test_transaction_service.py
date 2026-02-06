from typing import Any
from unittest.mock import MagicMock

import pytest

from dto.transaction_create_dto import TransactionCreateDto
from exception.exceptions import (
    NotEnoughBalanceError,
    UnauthorizedWalletAccessError,
    UserNotFoundError,
    WalletNotFoundError,
)
from service.transaction_service import TransactionService


class TestTransactionService:

    @pytest.fixture
    def mock_repos(self) -> dict[str, Any]:
        return {
            "user" : MagicMock(), "wallet" : MagicMock(), "transaction" : MagicMock()
        }

    @pytest.fixture
    def mock_service(self, mock_repos: dict[str, Any]) -> TransactionService:
        return TransactionService(
            mock_repos["user"],
            mock_repos["wallet"],
            mock_repos["transaction"]
        )

    def test_check_user_existence_success(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_user = MagicMock(id=1, name="Naruto")
        mock_repos["user"].find_user_by_api_key.return_value = mock_user

        result = mock_service.check_user_existence("key")
        assert result == mock_user

    def test_check_user_existence_raises_error(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_repos["user"].find_user_by_api_key.return_value = None
        with pytest.raises(UserNotFoundError):
            mock_service.check_user_existence("key")

    def test_make_transaction_success_with_fee(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_repos["user"].find_user_by_api_key.return_value = (
            MagicMock(id=1, name="Kakashi"))

        sender = MagicMock(id=10, user_id=1, balance=10000, wallet_address="1")
        receiver = MagicMock(id=20, user_id=2, balance=5000, wallet_address="2")
        mock_repos["wallet"].get_wallet_by_address.side_effect = [sender, receiver]

        dto = TransactionCreateDto(sender_wallet_address="1",
                                   receiver_wallet_address="2",transfer_amount=1000)
        result = mock_service.make_transaction(dto, "key")

        assert result.transfer_fee == 15
        assert result.transferred_amount == 985
        mock_repos["wallet"].update_balance.assert_any_call("1", 9000)
        mock_repos["wallet"].update_balance.assert_any_call("2", 5985)

    def test_make_transaction_success_no_fee(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_repos["user"].find_user_by_api_key.return_value = MagicMock(id=1)
        sender = MagicMock(user_id=1, balance=100, wallet_address="1")
        receiver = MagicMock(user_id=1, balance=100, wallet_address="2")
        mock_repos["wallet"].get_wallet_by_address.side_effect = [sender, receiver]

        dto = TransactionCreateDto(sender_wallet_address="1",
                                   receiver_wallet_address="2", transfer_amount=50)
        result = mock_service.make_transaction(dto, "key")

        assert result.transfer_fee == 0
        assert result.transferred_amount == 50

    def test_make_transaction_insufficient_balance(
        self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_repos["user"].find_user_by_api_key.return_value = MagicMock(id=1)
        sender = MagicMock(user_id=1, balance=10, wallet_address="1")
        receiver = MagicMock(user_id=2, balance=10, wallet_address="2")
        mock_repos["wallet"].get_wallet_by_address.side_effect = [sender, receiver]

        dto = TransactionCreateDto(sender_wallet_address="1",
                                   receiver_wallet_address="2", transfer_amount=50)

        with pytest.raises(NotEnoughBalanceError):
            mock_service.make_transaction(dto, "key")

    def test_make_transaction_sender_wallet_not_found(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_repos["user"].find_user_by_api_key.return_value = MagicMock(id=1)
        mock_repos["wallet"].get_wallet_by_address.return_value = None

        dto = TransactionCreateDto(sender_wallet_address="1",
                                   receiver_wallet_address="2", transfer_amount=50)

        with pytest.raises(WalletNotFoundError):
            mock_service.make_transaction(dto, "key")

    def test_make_transaction_receiver_wallet_not_found(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_repos["user"].find_user_by_api_key.return_value = MagicMock(id=1)
        sender = MagicMock(user_id=1, balance=1000, wallet_address="1")
        mock_repos["wallet"].get_wallet_by_address.side_effect = [sender, None]

        dto = TransactionCreateDto(sender_wallet_address="1",
                                   receiver_wallet_address="2", transfer_amount=50)

        with pytest.raises(WalletNotFoundError):
            mock_service.make_transaction(dto, "key")

    def test_make_transaction_unauthorized_sender(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_repos["user"].find_user_by_api_key.return_value = (
            MagicMock(id=1, name="Obito"))
        sender = MagicMock(user_id=2, balance=1000, wallet_address="1")
        receiver = MagicMock(user_id=3, balance=500, wallet_address="2")
        mock_repos["wallet"].get_wallet_by_address.side_effect = [sender, receiver]

        dto = TransactionCreateDto(sender_wallet_address="1",
                                   receiver_wallet_address="2", transfer_amount=50)

        with pytest.raises(UnauthorizedWalletAccessError):
            mock_service.make_transaction(dto, "key")

    def test_get_wallet_related_transactions_success(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_repos["user"].find_user_by_api_key.return_value = (
            MagicMock(id=1, name="Hinata"))

        wallet = MagicMock(id=10, user_id=1, wallet_address="1")
        mock_repos["wallet"].get_wallet_by_address.return_value = wallet

        transaction = MagicMock(sender_wallet_id=10,
            receiver_wallet_id=20, transfer_amount=1000, transfer_fee=15)
        (mock_repos["transaction"].get_related_transactions_by_wallet_id.
         return_value) = [transaction]

        mock_repos["wallet"].get_wallets_by_ids.return_value = [
            MagicMock(id=10, wallet_address="1"),
            MagicMock(id=20, wallet_address="2")
        ]

        result = mock_service.get_wallet_related_transactions("1", "key")

        assert len(result) == 1
        assert result[0].sender_wallet_address == "1"

    def test_get_wallet_related_transactions_unauthorized(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:

        mock_repos["user"].find_user_by_api_key.return_value = (
            MagicMock(id=1, name="Minato"))
        mock_repos["wallet"].get_wallet_by_address.return_value = (
            MagicMock(user_id=2, wallet_address="2"))

        with pytest.raises(UnauthorizedWalletAccessError):
            mock_service.get_wallet_related_transactions("2", "minato_key")

    def test_get_wallet_related_transactions_wallet_not_found(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_repos["user"].find_user_by_api_key.return_value = MagicMock(id=1)
        mock_repos["wallet"].get_wallet_by_address.return_value = None

        with pytest.raises(WalletNotFoundError):
            mock_service.get_wallet_related_transactions("1", "key")

    def test_get_wallet_related_transactions_empty(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        user = MagicMock(id=1)
        wallet = MagicMock(id=10, user_id=1, wallet_address="1")

        mock_repos["user"].find_user_by_api_key.return_value = user
        mock_repos["wallet"].get_wallet_by_address.return_value = wallet
        (mock_repos["transaction"].get_related_transactions_by_wallet_id.
         return_value) = []

        result = mock_service.get_wallet_related_transactions("1", "key")

        assert result == []

    def test_get_transactions_success(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_repos["user"].find_user_by_api_key.return_value = MagicMock(id=1)

        wallet1 = MagicMock(id=10, wallet_address="1")
        wallet2 = MagicMock(id=20, wallet_address="2")
        mock_repos["wallet"].get_wallets_by_user_id.return_value = [wallet1, wallet2]

        transaction = MagicMock(sender_wallet_id=10, receiver_wallet_id=30,
                                transfer_amount=1000, transfer_fee=15)
        (mock_repos["transaction"].get_transactions_by_wallet_ids.
         return_value) = [transaction]

        mock_repos["wallet"].get_wallets_by_ids.return_value = [
            MagicMock(id=10, wallet_address="1"),
            MagicMock(id=30, wallet_address="3")
        ]

        result = mock_service.get_transactions("key")

        assert len(result) == 1
        assert result[0].transferred_amount == 985

    def test_get_transactions_empty_list(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        mock_repos["user"].find_user_by_api_key.return_value = MagicMock(id=1)
        mock_repos["wallet"].get_wallets_by_user_id.return_value = [MagicMock(id=10)]
        mock_repos["transaction"].get_transactions_by_wallet_ids.return_value = []

        result = mock_service.get_transactions("key")

        assert result == []

    def test_get_statistics(
            self, mock_service: TransactionService, mock_repos: dict[str, Any]
    ) -> None:
        (mock_repos["transaction"].get_transaction_count_and_profit.
         return_value) = (150, 225)

        result = mock_service.get_statistics()

        assert result.total_transactions == 150
        assert result.platform_profit == 225
