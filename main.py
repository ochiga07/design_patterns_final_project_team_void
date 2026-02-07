from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from api.statistics_router import statistics_router
from api.transaction_router import transaction_router
from api.wallet_router import wallet_router
from api.wallet_transaction_router import wallet_transaction_router
from database.database_init import init_db
from exception.global_exception_handler import register_exception_handlers


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)
app.include_router(transaction_router)
app.include_router(wallet_transaction_router)
app.include_router(wallet_router)
app.include_router(statistics_router)
