import sqlite3
from typing import Annotated

from fastapi import Depends

from database.session import get_db
from repository.user_repository import UserRepository
from service.user_service import UserService


def get_user_service(
    db: Annotated[sqlite3.Connection, Depends(get_db)]
) -> UserService:
    repo = UserRepository(db)
    return UserService(repo)
