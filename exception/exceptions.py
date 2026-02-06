class NotEnoughBalanceError(Exception):
    def __init__(self, message: str):
       super().__init__(message)

class UnauthorizedError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class UnauthorizedWalletAccessError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class UserNotFoundError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class WalletNotFoundError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
