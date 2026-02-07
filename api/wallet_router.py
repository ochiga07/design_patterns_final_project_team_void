from typing import Annotated

from fastapi import APIRouter, Depends, Header

from dependencies.wallet_dependencies import get_wallet_service
from dto.wallet_response_dto import WalletResponseDto
from service.wallet_service import WalletService

wallet_router = APIRouter(prefix="/wallets", tags=["wallets"])


@wallet_router.post("")
def create_wallet(
    wallet_service: Annotated[WalletService, Depends(get_wallet_service)],
    x_api_key: str = Header(...)
) -> WalletResponseDto:
    return wallet_service.create_wallet(x_api_key)


@wallet_router.get("/{address}")
def get_wallet(
    address: str,
    wallet_service: Annotated[WalletService, Depends(get_wallet_service)],
    x_api_key: str = Header(...)
) -> WalletResponseDto:
    return wallet_service.get_wallet(address, x_api_key)
