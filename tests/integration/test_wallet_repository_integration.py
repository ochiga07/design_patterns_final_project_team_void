import sqlite3
from collections.abc import Generator

import pytest

from repository.wallet_repository import WalletRepository


@pytest.fixture
def db_connection() -> Generator[sqlite3.Connection]:
    """Create an in-memory database for testing."""
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Users (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         api_key TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        balance INTEGER NOT NULL DEFAULT 0,
        wallet_address TEXT NOT NULL UNIQUE,
        FOREIGN KEY (user_id) REFERENCES Users(id)
    );
    """)
    connection.commit()

    yield connection
    connection.close()


@pytest.fixture
def wallet_repository(db_connection: sqlite3.Connection) -> WalletRepository:
    """Create a wallet repository with test database."""
    return WalletRepository(db_connection)


@pytest.fixture
def create_test_users(db_connection: sqlite3.Connection) -> None:
    """Create test users in the database."""
    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT INTO Users (id, name, api_key) VALUES (?, ?, ?)",
        (1, "Test User 1", "test_api_key_123")
    )
    cursor.execute(
        "INSERT INTO Users (id, name, api_key) VALUES (?, ?, ?)",
        (2, "Test User 2", "test_api_key_456")
    )
    db_connection.commit()


class TestWalletRepositoryIntegration:
    """Integration tests for WalletRepository with real database."""

    def test_insert_wallet_success(
        self,
        wallet_repository: WalletRepository,
        db_connection: sqlite3.Connection,
        create_test_users: None,
    ) -> None:
        """Test inserting a wallet into the database."""
        # Arrange
        user_id = 1
        balance = 50000
        wallet_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

        # Act
        wallet = wallet_repository.insert_wallet(user_id, balance, wallet_address)

        # Assert
        assert wallet.id > 0
        assert wallet.user_id == user_id
        assert wallet.balance == balance
        assert wallet.wallet_address == wallet_address

        # Verify it's actually in the database
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM Wallets WHERE id = ?", (wallet.id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["wallet_address"] == wallet_address
        assert row["balance"] == balance

    def test_insert_wallet_with_default_balance(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test inserting a wallet with zero balance."""
        # Arrange
        user_id = 1
        balance = 0
        wallet_address = "test_address_1"

        # Act
        wallet = wallet_repository.insert_wallet(user_id, balance, wallet_address)

        # Assert
        assert wallet.balance == 0
        assert wallet.id > 0

    def test_count_wallets_by_user_id_no_wallets(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test counting wallets for user with no wallets."""
        # Act
        count = wallet_repository.count_wallets_by_user_id(999)

        # Assert
        assert count == 0

    def test_count_wallets_by_user_id_multiple_wallets(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test counting wallets for user with multiple wallets."""
        # Arrange
        user_id = 1
        wallet_repository.insert_wallet(user_id, 1000, "address1")
        wallet_repository.insert_wallet(user_id, 2000, "address2")
        wallet_repository.insert_wallet(user_id, 3000, "address3")

        # Act
        count = wallet_repository.count_wallets_by_user_id(user_id)

        # Assert
        assert count == 3

    def test_get_wallet_by_address_exists(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test getting a wallet by address when it exists."""
        # Arrange
        user_id = 1
        balance = 50000
        wallet_address = "test_address"
        inserted_wallet = wallet_repository.insert_wallet(
            user_id, balance, wallet_address
        )

        # Act
        wallet = wallet_repository.get_wallet_by_address(wallet_address)

        # Assert
        assert wallet is not None
        assert wallet.id == inserted_wallet.id
        assert wallet.user_id == user_id
        assert wallet.balance == balance
        assert wallet.wallet_address == wallet_address

    def test_get_wallet_by_address_not_exists(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test getting a wallet by address when it doesn't exist."""
        # Act
        wallet = wallet_repository.get_wallet_by_address("nonexistent_address")

        # Assert
        assert wallet is None

    def test_update_balance(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test updating wallet balance."""
        # Arrange
        user_id = 1
        initial_balance = 50000
        wallet_address = "test_address"
        wallet_repository.insert_wallet(user_id, initial_balance, wallet_address)
        new_balance = 75000

        # Act
        wallet_repository.update_balance(wallet_address, new_balance)

        # Assert
        updated_wallet = wallet_repository.get_wallet_by_address(wallet_address)
        assert updated_wallet is not None
        assert updated_wallet.balance == new_balance

    def test_get_wallets_by_user_id_no_wallets(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test getting wallets for user with no wallets."""
        # Act
        wallets = wallet_repository.get_wallets_by_user_id(999)

        # Assert
        assert wallets == []

    def test_get_wallets_by_user_id_multiple_wallets(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test getting multiple wallets for a user."""
        # Arrange
        user_id = 1
        wallet1 = wallet_repository.insert_wallet(user_id, 1000, "address1")
        wallet2 = wallet_repository.insert_wallet(user_id, 2000, "address2")
        wallet3 = wallet_repository.insert_wallet(user_id, 3000, "address3")

        # Act
        wallets = wallet_repository.get_wallets_by_user_id(user_id)

        # Assert
        assert len(wallets) == 3
        wallet_ids = {w.id for w in wallets}
        assert wallet1.id in wallet_ids
        assert wallet2.id in wallet_ids
        assert wallet3.id in wallet_ids

    def test_get_wallets_by_user_id_only_returns_users_wallets(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test that get_wallets_by_user_id only returns wallets for specified user."""
        # Arrange
        user1_id = 1
        user2_id = 2
        wallet_repository.insert_wallet(user1_id, 1000, "user1_address1")
        wallet_repository.insert_wallet(user1_id, 2000, "user1_address2")
        wallet_repository.insert_wallet(user2_id, 3000, "user2_address1")

        # Act
        user1_wallets = wallet_repository.get_wallets_by_user_id(user1_id)

        # Assert
        assert len(user1_wallets) == 2
        assert all(w.user_id == user1_id for w in user1_wallets)

    def test_get_wallets_by_ids_empty_list(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test getting wallets by empty ID list."""
        # Act
        wallets = wallet_repository.get_wallets_by_ids([])

        # Assert
        assert wallets == []

    def test_get_wallets_by_ids_single_wallet(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test getting a single wallet by ID."""
        # Arrange
        wallet = wallet_repository.insert_wallet(1, 5000, "test_address")

        # Act
        wallets = wallet_repository.get_wallets_by_ids([wallet.id])

        # Assert
        assert len(wallets) == 1
        assert wallets[0].id == wallet.id
        assert wallets[0].wallet_address == "test_address"

    def test_get_wallets_by_ids_multiple_wallets(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test getting multiple wallets by IDs."""
        # Arrange
        wallet1 = wallet_repository.insert_wallet(1, 1000, "address1")
        wallet2 = wallet_repository.insert_wallet(1, 2000, "address2")
        wallet3 = wallet_repository.insert_wallet(1, 3000, "address3")
        wallet_repository.insert_wallet(1, 4000, "address4")  # Not requested

        # Act
        wallets = wallet_repository.get_wallets_by_ids(
            [wallet1.id, wallet2.id, wallet3.id]
        )

        # Assert
        assert len(wallets) == 3
        wallet_ids = {w.id for w in wallets}
        assert wallet1.id in wallet_ids
        assert wallet2.id in wallet_ids
        assert wallet3.id in wallet_ids

    def test_get_wallets_by_ids_nonexistent_ids(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test getting wallets with IDs that don't exist."""
        # Act
        wallets = wallet_repository.get_wallets_by_ids([999, 1000, 1001])

        # Assert
        assert wallets == []

    def test_get_wallets_by_ids_mixed_existing_and_nonexistent(
        self, wallet_repository: WalletRepository, create_test_users: None
    ) -> None:
        """Test getting wallets with mix of existing and non-existing IDs."""
        # Arrange
        wallet = wallet_repository.insert_wallet(1, 5000, "test_address")

        # Act
        wallets = wallet_repository.get_wallets_by_ids([wallet.id, 999, 1000])

        # Assert
        assert len(wallets) == 1
        assert wallets[0].id == wallet.id
