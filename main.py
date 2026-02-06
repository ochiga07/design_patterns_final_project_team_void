from fastapi import FastAPI

from api.statistics_router import statistics_router
from api.transaction_router import transaction_router
from api.wallet_transaction_router import wallet_transaction_router
from exception.global_exception_handler import register_exception_handlers

app = FastAPI()

register_exception_handlers(app)
app.include_router(transaction_router)
app.include_router(wallet_transaction_router)
app.include_router(statistics_router)
