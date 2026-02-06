from dataclasses import dataclass


@dataclass
class Transaction:
    sender_wallet_id: int
    receiver_wallet_id: int
    transfer_amount: int
    transfer_fee: int
    id: int | None = None
