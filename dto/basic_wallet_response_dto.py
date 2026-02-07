from pydantic import BaseModel


class BasicWalletResponseDto(BaseModel):
    wallet_address: str
    balance_btc: float
    balance_satoshi: int
