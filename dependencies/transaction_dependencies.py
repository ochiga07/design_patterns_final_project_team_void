import sqlite3
from typing import Annotated

from fastapi import Depends

from database.session import get_db
from repository.transaction_repository import TransactionRepository
from repository.user_repository import UserRepository
from repository.wallet_repository import WalletRepository
from service.transaction_service import TransactionService


def get_transaction_service(
        db_connection: Annotated[sqlite3.Connection, Depends(get_db)]
) -> TransactionService:
    transaction_repo = TransactionRepository(db_connection)
    wallet_repo = WalletRepository(db_connection)
    user_repo = UserRepository(db_connection)
    return TransactionService(user_repo, wallet_repo, transaction_repo)
