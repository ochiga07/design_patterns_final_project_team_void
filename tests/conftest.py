import sqlite3
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from main import app
from repository.transaction_repository import TransactionRepository
from repository.user_repository import UserRepository
from repository.wallet_repository import WalletRepository


@pytest.fixture
def client() -> Generator[TestClient]:
    with TestClient(app) as conn:
        yield conn

@pytest.fixture
def db_connection() -> Generator[sqlite3.Connection]:
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.executescript("""
    CREATE TABLE Users (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         api_key TEXT NOT NULL UNIQUE
    );

    CREATE TABLE Wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        balance INTEGER NOT NULL DEFAULT 0,
        wallet_address TEXT NOT NULL UNIQUE,
        FOREIGN KEY (user_id) REFERENCES Users(id)
    );

    CREATE TABLE Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_wallet_id INTEGER NOT NULL,
        receiver_wallet_id INTEGER NOT NULL,
        transfer_amount INTEGER NOT NULL,
        transfer_fee INTEGER NOT NULL,
        FOREIGN KEY (sender_wallet_id) REFERENCES Wallets(id),
        FOREIGN KEY (receiver_wallet_id) REFERENCES Wallets(id)
    );
    """)

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def user_repo(db_connection: sqlite3.Connection) -> UserRepository:
    return UserRepository(db_connection)


@pytest.fixture
def wallet_repo(db_connection: sqlite3.Connection) -> WalletRepository:
    return WalletRepository(db_connection)


@pytest.fixture
def transaction_repo(db_connection: sqlite3.Connection) -> TransactionRepository:
    return TransactionRepository(db_connection)


@pytest.fixture
def setup_test_data(db_connection: sqlite3.Connection) -> None:
    cursor = db_connection.cursor()

    cursor.execute("INSERT INTO Users (id, name, api_key) "
                   "VALUES (1, 'Naruto', 'key1')")
    cursor.execute("INSERT INTO Users (id, name, api_key)"
                   " VALUES (2, 'Hinata', 'key2')")

    cursor.execute("INSERT INTO Wallets (id, user_id, balance, "
                   "wallet_address) VALUES (1, 1, 10000, 'W1')")
    cursor.execute("INSERT INTO Wallets (id, user_id, balance, "
                   "wallet_address) VALUES (2, 2, 5000, 'W2')")
    cursor.execute("INSERT INTO Wallets (id, user_id, balance, "
                   "wallet_address) VALUES (3, 1, 3000, 'W3')")

    db_connection.commit()
