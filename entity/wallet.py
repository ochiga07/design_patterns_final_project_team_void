from dataclasses import dataclass


@dataclass
class Wallet:
    id: int
    user_id: int
    balance: int
    wallet_address: str
