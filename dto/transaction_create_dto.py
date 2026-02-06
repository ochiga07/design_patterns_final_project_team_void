from pydantic import BaseModel


class TransactionCreateDto(BaseModel):
    sender_wallet_address: str
    receiver_wallet_address: str
    transfer_amount: int
