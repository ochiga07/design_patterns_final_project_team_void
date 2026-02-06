from typing import Any

import pytest

from entity.transaction import Transaction


class TestTransactionRepositoryIntegration:

    @pytest.mark.usefixtures("setup_test_data")
    def test_insert_transaction_saves_to_database(
            self, transaction_repo: Any, db_connection: Any
    ) -> None:

        transaction = Transaction(
            sender_wallet_id=1, receiver_wallet_id=2,
            transfer_amount=1000, transfer_fee=15
        )

        transaction_repo.insert_transaction(transaction)

        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM Transactions WHERE sender_wallet_id = 1 "
                       "AND receiver_wallet_id = 2")
        row = cursor.fetchone()

        assert row is not None
        assert row["sender_wallet_id"] == 1
        assert row["transfer_amount"] == 1000
        assert row["transfer_fee"] == 15

    @pytest.mark.usefixtures("setup_test_data")
    def test_insert_multiple_transactions(
            self, transaction_repo: Any, db_connection: Any
    ) -> None:
        transaction1 = Transaction(sender_wallet_id=1,
              receiver_wallet_id=2, transfer_amount=1000, transfer_fee=15)
        transaction2 = Transaction(sender_wallet_id=2,
              receiver_wallet_id=1, transfer_amount=2000, transfer_fee=30)

        transaction_repo.insert_transaction(transaction1)
        transaction_repo.insert_transaction(transaction2)

        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM Transactions")
        assert cursor.fetchone()["count"] == 2

    @pytest.mark.usefixtures("setup_test_data")
    def test_get_related_transactions_by_wallet_id_as_sender(
            self, transaction_repo: Any, db_connection: Any
    ) -> None:
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO Transactions (sender_wallet_id, receiver_wallet_id, "
            "transfer_amount, transfer_fee) VALUES (1, 2, 100, 2)")
        cursor.execute(
            "INSERT INTO Transactions (sender_wallet_id, receiver_wallet_id, "
            "transfer_amount, transfer_fee) VALUES (1, 3, 50, 1)")
        db_connection.commit()

        transactions = transaction_repo.get_related_transactions_by_wallet_id(1)

        assert len(transactions) == 2
        amounts = {transaction.transfer_amount for transaction in transactions}
        assert amounts == {100, 50}

    @pytest.mark.usefixtures("setup_test_data")
    def test_get_transactions_by_wallet_ids_multiple_wallets(
            self, transaction_repo: Any, db_connection: Any
    ) -> None:
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO Transactions (sender_wallet_id, receiver_wallet_id, "
            "transfer_amount, transfer_fee) VALUES (1, 2, 500, 7)")
        cursor.execute(
            "INSERT INTO Transactions (sender_wallet_id, receiver_wallet_id, "
            "transfer_amount, transfer_fee) VALUES (2, 3, 250, 3)")
        db_connection.commit()

        transactions = transaction_repo.get_transactions_by_wallet_ids([1, 2])
        assert len(transactions) == 2

    @pytest.mark.usefixtures("setup_test_data")
    def test_get_transaction_count_and_profit_with_transactions(
            self, transaction_repo: Any, db_connection: Any
    ) -> None:
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO Transactions (sender_wallet_id, receiver_wallet_id, "
            "transfer_amount, transfer_fee) VALUES (1, 2, 1000, 15)")
        cursor.execute(
            "INSERT INTO Transactions (sender_wallet_id, receiver_wallet_id, "
            "transfer_amount, transfer_fee) VALUES (2, 1, 2000, 30)")
        db_connection.commit()

        count, profit = transaction_repo.get_transaction_count_and_profit()

        assert count == 2
        assert profit == 45
