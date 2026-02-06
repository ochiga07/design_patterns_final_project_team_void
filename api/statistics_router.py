from typing import Annotated

from fastapi import APIRouter, Depends, Header

from dependencies.transaction_dependencies import get_transaction_service
from dto.statistics_response_dto import StatisticsResponseDto
from exception.exceptions import UnauthorizedError
from service.transaction_service import TransactionService

statistics_router = APIRouter(prefix="/statistics", tags=["statistics"])
ADMIN_API_KEY = "secret_admin_api_key"

@statistics_router.get("")
def get_statistics(
    transaction_service: Annotated
        [TransactionService, Depends(get_transaction_service)],
    admin_api_key: str = Header(...)
) -> StatisticsResponseDto:
    if admin_api_key != ADMIN_API_KEY:
        raise UnauthorizedError("Invalid admin API key")

    return transaction_service.get_statistics()
