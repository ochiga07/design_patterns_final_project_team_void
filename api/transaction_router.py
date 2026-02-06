from typing import Annotated

from fastapi import APIRouter, Header
from fastapi.params import Depends

from dependencies.transaction_dependencies import get_transaction_service
from dto.transaction_create_dto import TransactionCreateDto
from dto.transaction_response_dto import TransactionResponseDto
from service.transaction_service import TransactionService

transaction_router = APIRouter(prefix="/transactions", tags=["transactions"])

@transaction_router.get("")
def get_transactions(
    transaction_service: Annotated
        [TransactionService, Depends(get_transaction_service)],
    x_api_key: str = Header(...)
) -> list[TransactionResponseDto]:
    return transaction_service.get_transactions(x_api_key)

@transaction_router.post("")
def make_transaction(
    transaction_create_dto: TransactionCreateDto,
    transaction_service: Annotated
        [TransactionService, Depends(get_transaction_service)],
    x_api_key: str = Header(...)
) -> TransactionResponseDto:
    return transaction_service.make_transaction(transaction_create_dto, x_api_key)



