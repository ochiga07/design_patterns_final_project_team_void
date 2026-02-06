from pydantic import BaseModel


class TransactionResponseDto(BaseModel):
    sender_wallet_address: str
    receiver_wallet_address: str
    transfer_amount: int
    transferred_amount: int
    transfer_fee: int
