import sqlite3

import pytest

from repository.wallet_repository import WalletRepository


class TestWalletRepositoryIntegration:

    @pytest.mark.usefixtures("setup_test_data")
    def test_insert_wallet_success(
        self,
        wallet_repo: WalletRepository,
        db_connection: sqlite3.Connection,
    ) -> None:
        user_id = 1
        balance = 50000
        wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

        wallet = wallet_repo.insert_wallet(user_id, balance, wallet_address)

        assert wallet.id > 0
        assert wallet.user_id == user_id
        assert wallet.balance == balance
        assert wallet.wallet_address == wallet_address

        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM Wallets WHERE id = ?", (wallet.id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["wallet_address"] == wallet_address
        assert row["balance"] == balance

    @pytest.mark.usefixtures("setup_test_data")
    def test_insert_wallet_with_default_balance(
        self, wallet_repo: WalletRepository
    ) -> None:
        user_id = 1
        balance = 0
        wallet_address = "test_address_1"

        wallet = wallet_repo.insert_wallet(user_id, balance, wallet_address)

        assert wallet.balance == 0
        assert wallet.id > 0

    @pytest.mark.usefixtures("setup_test_data")
    def test_count_wallets_by_user_id_no_wallets(
        self, wallet_repo: WalletRepository
    ) -> None:
        count = wallet_repo.count_wallets_by_user_id(999)
        assert count == 0

    @pytest.mark.usefixtures("setup_test_data")
    def test_count_wallets_by_user_id_multiple_wallets(
        self, wallet_repo: WalletRepository
    ) -> None:
        user_id = 1
        wallet_repo.insert_wallet(user_id, 1000, "addr_a")
        wallet_repo.insert_wallet(user_id, 2000, "addr_b")

        count = wallet_repo.count_wallets_by_user_id(user_id)
        assert count == 4

    @pytest.mark.usefixtures("setup_test_data")
    def test_get_wallet_by_address_exists(
        self, wallet_repo: WalletRepository
    ) -> None:
        wallet = wallet_repo.get_wallet_by_address("W1")

        assert wallet is not None
        assert wallet.wallet_address == "W1"
        assert wallet.user_id == 1

    @pytest.mark.usefixtures("setup_test_data")
    def test_get_wallet_by_address_not_exists(
        self, wallet_repo: WalletRepository
    ) -> None:
        wallet = wallet_repo.get_wallet_by_address("nonexistent_address")
        assert wallet is None

    @pytest.mark.usefixtures("setup_test_data")
    def test_update_balance(
        self, wallet_repo: WalletRepository
    ) -> None:
        wallet_address = "W1"
        new_balance = 75000

        wallet_repo.update_balance(wallet_address, new_balance)

        updated_wallet = wallet_repo.get_wallet_by_address(wallet_address)
        assert updated_wallet is not None
        assert updated_wallet.balance == new_balance

    @pytest.mark.usefixtures("setup_test_data")
    def test_get_wallets_by_user_id_no_wallets(
        self, wallet_repo: WalletRepository
    ) -> None:
        wallets = wallet_repo.get_wallets_by_user_id(999)
        assert wallets == []

    @pytest.mark.usefixtures("setup_test_data")
    def test_get_wallets_by_user_id_multiple_wallets(
        self, wallet_repo: WalletRepository
    ) -> None:
        wallets = wallet_repo.get_wallets_by_user_id(1)
        assert len(wallets) == 2
        wallet_addresses = {w.wallet_address for w in wallets}
        assert "W1" in wallet_addresses
        assert "W3" in wallet_addresses

    @pytest.mark.usefixtures("setup_test_data")
    def test_get_wallets_by_ids_empty_list(
        self, wallet_repo: WalletRepository
    ) -> None:
        wallets = wallet_repo.get_wallets_by_ids([])
        assert wallets == []

    @pytest.mark.usefixtures("setup_test_data")
    def test_get_wallets_by_ids_multiple_wallets(
        self, wallet_repo: WalletRepository
    ) -> None:
        wallets = wallet_repo.get_wallets_by_ids([1, 2])

        assert len(wallets) == 2
        ids = {w.id for w in wallets}
        assert 1 in ids
        assert 2 in ids

    @pytest.mark.usefixtures("setup_test_data")
    def test_get_wallets_by_ids_mixed_existing_and_nonexistent(
        self, wallet_repo: WalletRepository
    ) -> None:
        wallets = wallet_repo.get_wallets_by_ids([1, 999])

        assert len(wallets) == 1
        assert wallets[0].id == 1
