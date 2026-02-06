import sqlite3
from sqlite3 import Row

from entity.transaction import Transaction


def construct_transactions(rows: list[Row]) -> list[Transaction]:
    return [
        Transaction(
            id=row["id"], sender_wallet_id=row["sender_wallet_id"],
            receiver_wallet_id=row["receiver_wallet_id"],
            transfer_amount=row["transfer_amount"],
            transfer_fee=row["transfer_fee"]
        )
        for row in rows
    ]

class TransactionRepository:

    def __init__(self, db_connection: sqlite3.Connection) -> None:
        self.db_connection = db_connection

    def insert_transaction(self, transaction: Transaction) -> None:
        cursor = self.db_connection.cursor()

        cursor.execute(
            """
            INSERT INTO transactions (
                sender_wallet_id, receiver_wallet_id, transfer_amount, transfer_fee)
            VALUES (?, ?, ?, ?)
            """,
            (
                transaction.sender_wallet_id,
                transaction.receiver_wallet_id,
                transaction.transfer_amount,
                transaction.transfer_fee
            )
        )

    def get_transactions_by_wallet_ids(self, wallet_ids:
        list[int]) -> list[Transaction]:

        if not wallet_ids:
            return []

        cursor = self.db_connection.cursor()

        wallet_ids_placeholder = ",".join(
            "?" for _ in wallet_ids
        )

        cursor.execute(
            f"""
            SELECT id, sender_wallet_id, receiver_wallet_id, transfer_amount,
            transfer_fee FROM Transactions WHERE sender_wallet_id in
            ({wallet_ids_placeholder}) OR receiver_wallet_id in
            ({wallet_ids_placeholder})""", tuple(wallet_ids) + tuple(wallet_ids)
        )

        rows = cursor.fetchall()

        return construct_transactions(rows)


    def get_related_transactions_by_wallet_id(self,
               wallet_id: int) -> list[Transaction]:

        cursor = self.db_connection.cursor()

        cursor.execute(
            """
            SELECT id, sender_wallet_id, receiver_wallet_id, transfer_amount,
            transfer_fee FROM Transactions WHERE sender_wallet_id = ?
            OR receiver_wallet_id = ? """, (wallet_id, wallet_id)
        )

        rows = cursor.fetchall()

        return construct_transactions(rows)


    def get_transaction_count_and_profit(self) -> tuple[int, int]:
        cursor = self.db_connection.cursor()
        cursor.execute(
           """
           SELECT COUNT(*) AS total_transactions,
           COALESCE(SUM(transfer_fee), 0) AS platform_profit
           FROM Transactions
           """
        )
        row = cursor.fetchone()

        return row["total_transactions"], row["platform_profit"]
