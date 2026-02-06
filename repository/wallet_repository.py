import sqlite3

from entity.wallet import Wallet


class WalletRepository:

    def __init__(self, db_connection: sqlite3.Connection) -> None:
        self.db_connection = db_connection

    def get_wallet_by_address(self, wallet_address: str) -> Wallet | None:
        cursor = self.db_connection.cursor()

        cursor.execute(
            "SELECT id, user_id, balance, wallet_address FROM Wallets"
            " WHERE wallet_address = ?", (wallet_address,)
        )

        row = cursor.fetchone()

        if row:
            return Wallet(
                id=row["id"], user_id=row["user_id"],
                balance=row["balance"],wallet_address=row["wallet_address"]
            )

        return None

    def update_balance(self, wallet_address: str, new_balance: int) -> None:
        cursor = self.db_connection.cursor()

        cursor.execute(
            "UPDATE Wallets SET balance = ? WHERE wallet_address = ?",
            (new_balance, wallet_address)
        )

    def get_wallets_by_user_id(self, user_id: int) -> list[Wallet]:
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT id, user_id, balance, wallet_address FROM Wallets "
            "WHERE user_id = ?", (user_id,)
        )

        rows = cursor.fetchall()
        return [
            Wallet(
                id=row["id"], user_id=row["user_id"],
                balance=row["balance"], wallet_address=row["wallet_address"]
            )
            for row in rows]

    def get_wallets_by_ids(self, wallet_ids: list[int]) -> list[Wallet]:
        if not wallet_ids:
            return []

        cursor = self.db_connection.cursor()

        wallet_ids_placeholder = ",".join(
            "?" for _ in wallet_ids
        )

        cursor.execute(
            f"""SELECT id, user_id, balance, wallet_address FROM Wallets
            WHERE id IN ({wallet_ids_placeholder})
            """, tuple(wallet_ids)
        )

        rows = cursor.fetchall()

        return [
            Wallet(
                id=row["id"], user_id=row["user_id"],
                balance=row["balance"], wallet_address=row["wallet_address"]
            )
            for row in rows
        ]
