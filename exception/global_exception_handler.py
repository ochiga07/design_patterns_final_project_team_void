from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from exception.exceptions import (
    NotEnoughBalanceError,
    UnauthorizedError,
    UnauthorizedWalletAccessError,
    UserNotFoundError,
    WalletLimitExceededError,
    WalletNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(WalletNotFoundError)
    def handle_wallet_not_found(_: Request, exception:
        WalletNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error" : str(exception)}
        )

    @app.exception_handler(NotEnoughBalanceError)
    def handle_not_enough_balance(_: Request, exception:
        NotEnoughBalanceError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"error": str(exception)}
        )

    @app.exception_handler(UserNotFoundError)
    def handle_user_not_found(_: Request, exception:
        UserNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": str(exception)}
        )

    @app.exception_handler(UnauthorizedWalletAccessError)
    def handle_unauthorized_wallet_access_exception(
            _: Request, exception: UnauthorizedWalletAccessError) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"error": str(exception)}
        )

    @app.exception_handler(UnauthorizedError)
    def handle_unauthorized_exception(
            _: Request, exception: UnauthorizedError) -> JSONResponse:
        return JSONResponse(
            status_code=401 ,
            content={"error": str(exception)}
        )

    @app.exception_handler(WalletLimitExceededError)
    def handle_wallet_limit_exceeded(
            _: Request, exception: WalletLimitExceededError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"error": str(exception)}
        )
