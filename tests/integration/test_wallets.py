import sqlite3
from collections.abc import Generator
from sqlite3 import Connection
from typing import Any

import pytest
from fastapi.testclient import TestClient

from dependencies.wallet_dependencies import get_wallet_service
from main import app  # assuming your FastAPI app is here
from repository.user_repository import UserRepository
from repository.wallet_repository import WalletRepository
from service.btc_price_converter import BtcPriceConverter
from service.wallet_service import WalletService


@pytest.fixture
def db_connection() -> Generator[Connection, Any]:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            api_key TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE Wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            balance INTEGER,
            wallet_address TEXT,
            FOREIGN KEY(user_id) REFERENCES Users(id)
        )
    """)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def client(db_connection: Connection) -> TestClient:
    def _get_wallet_service() -> WalletService:
        return WalletService(
            UserRepository(db_connection),
            WalletRepository(db_connection),
            FakeBtcPriceConverter(),
        )

    app.dependency_overrides[get_wallet_service] = _get_wallet_service
    return TestClient(app)



class FakeBtcPriceConverter(BtcPriceConverter):
    def satoshi_to_btc(self, satoshis: int) -> float:
        return satoshis / 100_000_000

    def get_btc_to_usd_rate(self) -> float:
        return 50_000



def test_create_wallet_and_get_wallet_by_address(client: TestClient,
                                                 db_connection: Connection) -> None:
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Users (name, api_key) VALUES (?, ?)",
                   ("Alice", "alice-key"))
    db_connection.commit()

    wallet_response = client.post(
        "/wallets",
        headers={"x-api-key": "alice-key"}
    )
    assert wallet_response.status_code == 200
    wallet_data = wallet_response.json()
    assert "wallet_address" in wallet_data
    assert wallet_data["wallet_address"] is not None

    address = wallet_data["wallet_address"]
    response = client.get(f"/wallets/{address}", headers={"x-api-key": "alice-key"})
    assert response.status_code == 200
    wallet = response.json()
    assert wallet["wallet_address"] == address


def test_get_all_wallets_for_user(client: TestClient,
                                  db_connection: Connection) -> None:
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO Users (name, api_key) VALUES (?, ?)",
                   ("Bob", "bob-key"))
    db_connection.commit()

    wallet1 = client.post("/wallets", headers={"x-api-key": "bob-key"})
    wallet2 = client.post("/wallets", headers={"x-api-key": "bob-key"})
    assert wallet1.status_code == 200
    assert wallet2.status_code == 200

    response = client.get("/wallets", headers={"x-api-key": "bob-key"})
    assert response.status_code == 200
    wallets = response.json()
    assert isinstance(wallets, list)
    assert len(wallets) == 2
    for w in wallets:
        assert "wallet_address" in w
        assert w["wallet_address"] is not None
