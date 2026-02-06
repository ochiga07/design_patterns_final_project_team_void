from typing import Annotated

from fastapi import APIRouter, Depends, Header

from dependencies.transaction_dependencies import get_transaction_service
from dto.transaction_response_dto import TransactionResponseDto
from service.transaction_service import TransactionService

wallet_transaction_router = APIRouter(prefix="/wallets",tags=["wallet_transactions"])

@wallet_transaction_router.get("/{address}/transactions")
def get_wallet_transactions(
    address: str,
    transaction_service: Annotated
        [TransactionService, Depends(get_transaction_service)],
    x_api_key: str = Header(...)
) -> list[TransactionResponseDto]:
    return transaction_service.get_wallet_related_transactions(address, x_api_key)
