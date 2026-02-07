from pydantic import BaseModel


class WalletResponseDto(BaseModel):
    wallet_address: str
    balance_btc: float
    balance_usd: float
