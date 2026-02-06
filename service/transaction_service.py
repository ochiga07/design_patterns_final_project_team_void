from dto.statistics_response_dto import StatisticsResponseDto
from dto.transaction_create_dto import TransactionCreateDto
from dto.transaction_response_dto import TransactionResponseDto
from entity.transaction import Transaction
from entity.user import User
from entity.wallet import Wallet
from exception.exceptions import (
    NotEnoughBalanceError,
    UnauthorizedWalletAccessError,
    UserNotFoundError,
    WalletNotFoundError,
)
from repository.transaction_repository import TransactionRepository
from repository.user_repository import UserRepository
from repository.wallet_repository import WalletRepository


def construct_transaction_response_dtos_from_map(wallet_map: dict[int, str],
        transactions: list[Transaction]) -> list[TransactionResponseDto]:
    return [
        TransactionResponseDto(
            sender_wallet_address=wallet_map[tr.sender_wallet_id],
            receiver_wallet_address=wallet_map[tr.receiver_wallet_id],
            transfer_amount=tr.transfer_amount,
            transferred_amount=tr.transfer_amount - tr.transfer_fee,
            transfer_fee=tr.transfer_fee
        )
        for tr in transactions
    ]


class TransactionService:
    def __init__(self, user_repo: UserRepository,
                 wallet_repo: WalletRepository,
                 transaction_repo: TransactionRepository) -> None:
        self.user_repo = user_repo
        self.wallet_repo = wallet_repo
        self.transaction_repo = transaction_repo

    def check_user_existence(self, api_key: str) -> User:
        user = self.user_repo.find_user_by_api_key(api_key)
        if user is None:
            raise UserNotFoundError(
                f"User with api_key {api_key} not found"
            )

        return user

    def update_balances(self, sender_wallet: Wallet,
            receiver_wallet: Wallet, transfer_amount: int) -> tuple[int, int]:

        self.wallet_repo.update_balance(
            sender_wallet.wallet_address,
            sender_wallet.balance - transfer_amount
        )

        transfer_fee = 0.0
        transferred_amount = float(transfer_amount)
        if sender_wallet.user_id != receiver_wallet.user_id:
            transfer_fee = transfer_amount * 0.015
            transferred_amount = transfer_amount - transfer_fee

        self.wallet_repo.update_balance(
            receiver_wallet.wallet_address,
            int(receiver_wallet.balance + transferred_amount)
        )

        return int(transfer_fee), int(transferred_amount)

    def get_wallets(self, sender_wallet_address: str,
                    receiver_wallet_address: str) -> tuple[Wallet, Wallet]:

        sender_wallet = (
            self.wallet_repo.get_wallet_by_address(sender_wallet_address)
        )
        receiver_wallet = (
            self.wallet_repo.get_wallet_by_address(receiver_wallet_address)
        )

        if sender_wallet is None:
            raise WalletNotFoundError(
                f"Wallet with address {sender_wallet_address} not found."
            )

        if receiver_wallet is None:
            raise WalletNotFoundError(
                f"Wallet with address {receiver_wallet_address} not found."
            )

        return sender_wallet, receiver_wallet

    def construct_wallet_map(self, transactions: list[Transaction]) -> dict[int, str]:
        sender_ids = {tr.sender_wallet_id for tr in transactions}
        receiver_ids = {tr.receiver_wallet_id for tr in transactions}
        wallet_ids = list(sender_ids.union(receiver_ids))
        wallets = self.wallet_repo.get_wallets_by_ids(wallet_ids)
        return {wallet.id: wallet.wallet_address for wallet in wallets}


    #-------------------------------------------------------------------------------------------------------------------
    def get_wallet_related_transactions(self, wallet_address: str,
           api_key: str) -> list[TransactionResponseDto]:

        user = self.check_user_existence(api_key)
        wallet = self.wallet_repo.get_wallet_by_address(wallet_address)

        if wallet is None:
            raise WalletNotFoundError(
                f"Wallet with address {wallet_address} not found."
            )

        if user.id != wallet.user_id:
            raise UnauthorizedWalletAccessError(
                f"Wallet with address {wallet.wallet_address} does not belong "
                f"to the user with the name of {user.name}"
            )

        transactions = (self.
            transaction_repo.get_related_transactions_by_wallet_id(wallet.id))

        if not transactions:
            return []

        wallet_map = self.construct_wallet_map(transactions)

        return construct_transaction_response_dtos_from_map(
            wallet_map, transactions
        )

    def get_transactions(self, api_key: str) -> list[TransactionResponseDto]:
        user = self.check_user_existence(api_key)
        user_wallets = self.wallet_repo.get_wallets_by_user_id(user.id)

        transactions = self.transaction_repo.get_transactions_by_wallet_ids(
            [wallet.id for wallet in user_wallets]
        )

        if not transactions:
            return []

        wallet_map = self.construct_wallet_map(transactions)

        return construct_transaction_response_dtos_from_map(
            wallet_map, transactions
        )


    def make_transaction(self,
        transaction_create_dto: TransactionCreateDto, api_key:
            str) -> TransactionResponseDto:

        user = self.check_user_existence(api_key)
        sender_wallet, receiver_wallet = (self.get_wallets
            (transaction_create_dto.sender_wallet_address,
             transaction_create_dto.receiver_wallet_address))

        if sender_wallet.user_id != user.id:
            raise UnauthorizedWalletAccessError(
                f"Wallet with address {sender_wallet.wallet_address} does not belong "
                f"to the user with the name of {user.name}"
            )

        if sender_wallet.balance < transaction_create_dto.transfer_amount:
            raise NotEnoughBalanceError(
                f"Wallet with address {sender_wallet.wallet_address} "
                f"does not have enough balance to make this transaction. "
                f"Current balance: {sender_wallet.balance}, Transfer Amount: "
                f"{transaction_create_dto.transfer_amount}"
            )

        transfer_fee, transferred_amount = self.update_balances(
            sender_wallet, receiver_wallet,
            transaction_create_dto.transfer_amount
        )

        self.transaction_repo.insert_transaction(Transaction(
            sender_wallet_id=sender_wallet.id,
            receiver_wallet_id=receiver_wallet.id,
            transfer_amount=transaction_create_dto.transfer_amount,
            transfer_fee=transfer_fee
        ))

        return TransactionResponseDto(
            sender_wallet_address=sender_wallet.wallet_address,
            receiver_wallet_address=receiver_wallet.wallet_address,
            transfer_amount=transaction_create_dto.transfer_amount,
            transferred_amount=transferred_amount,
            transfer_fee=transfer_fee
        )

    def get_statistics(self) -> StatisticsResponseDto:
        total_transactions, platform_profit = (
            self.transaction_repo.get_transaction_count_and_profit())

        return StatisticsResponseDto(
            total_transactions=total_transactions,
            platform_profit=platform_profit
        )



