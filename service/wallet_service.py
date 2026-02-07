import uuid

from dto.wallet_response_dto import WalletResponseDto
from exception.exceptions import (
    UnauthorizedWalletAccessError,
    UserNotFoundError,
    WalletLimitExceededError,
    WalletNotFoundError,
)
from repository.user_repository import UserRepository
from repository.wallet_repository import WalletRepository
from service.btc_price_converter import BtcPriceConverter

INITIAL_BALANCE_SATOSHIS = 100_000_000
MAX_WALLETS_PER_USER = 3


class WalletService:
    def __init__(self, user_repo: UserRepository,
                 wallet_repo: WalletRepository,
                 btc_price_converter: BtcPriceConverter) -> None:
        self.user_repo = user_repo
        self.wallet_repo = wallet_repo
        self.btc_price_converter = btc_price_converter

    def create_wallet(self, api_key: str) -> WalletResponseDto:
        user = self.user_repo.find_user_by_api_key(api_key)
        if user is None:
            raise UserNotFoundError(
                f"User with api_key {api_key} not found"
            )

        wallet_count = self.wallet_repo.count_wallets_by_user_id(user.id)
        if wallet_count >= MAX_WALLETS_PER_USER:
            raise WalletLimitExceededError(
                f"User {user.name} already has {MAX_WALLETS_PER_USER} wallets"
            )

        wallet_address = str(uuid.uuid4())
        wallet = self.wallet_repo.insert_wallet(
            user.id, INITIAL_BALANCE_SATOSHIS, wallet_address
        )

        return self._build_wallet_response(wallet.wallet_address,
                                           wallet.balance)

    def get_wallet(self, wallet_address: str,
                   api_key: str) -> WalletResponseDto:
        user = self.user_repo.find_user_by_api_key(api_key)
        if user is None:
            raise UserNotFoundError(
                f"User with api_key {api_key} not found"
            )

        wallet = self.wallet_repo.get_wallet_by_address(wallet_address)
        if wallet is None:
            raise WalletNotFoundError(
                f"Wallet with address {wallet_address} not found."
            )

        if wallet.user_id != user.id:
            raise UnauthorizedWalletAccessError(
                f"Wallet with address {wallet_address} does not belong "
                f"to the user with the name of {user.name}"
            )

        return self._build_wallet_response(wallet.wallet_address,
                                           wallet.balance)

    def _build_wallet_response(self, wallet_address: str,
                               balance_satoshis: int) -> WalletResponseDto:
        balance_btc = self.btc_price_converter.satoshi_to_btc(
            balance_satoshis
        )
        balance_usd = self.btc_price_converter.satoshi_to_usd(
            balance_satoshis
        )
        return WalletResponseDto(
            wallet_address=wallet_address,
            balance_btc=balance_btc,
            balance_usd=balance_usd
        )
