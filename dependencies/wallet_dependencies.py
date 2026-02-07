import sqlite3
from typing import Annotated

from fastapi import Depends

from database.session import get_db
from repository.user_repository import UserRepository
from repository.wallet_repository import WalletRepository
from service.btc_price_converter import CoinGeckoBtcPriceConverter
from service.wallet_service import WalletService


def get_wallet_service(
        db_connection: Annotated[sqlite3.Connection, Depends(get_db)]
) -> WalletService:
    user_repo = UserRepository(db_connection)
    wallet_repo = WalletRepository(db_connection)
    btc_price_converter = CoinGeckoBtcPriceConverter()
    return WalletService(user_repo, wallet_repo, btc_price_converter)
