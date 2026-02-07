import sqlite3
import uuid

from entity.user import User


class UserRepository:
    def __init__(self, db_connection: sqlite3.Connection) -> None:
        self.db_connection = db_connection

    def find_user_by_api_key(self, api_key: str) -> User | None:
        cursor = self.db_connection.cursor()

        cursor.execute(
            "SELECT id, name, api_key from Users WHERE api_key = ?",
            (api_key, )
        )

        row = cursor.fetchone()

        if row:
            return User(id=row["id"], name=row["name"], api_key=row["api_key"])
        return None

    def create_user(self, name: str) -> User:
        api_key = str(uuid.uuid4())

        cursor = self.db_connection.cursor()
        cursor.execute(
            "INSERT INTO Users (name, api_key) VALUES (?, ?)",
            (name, api_key),
        )
        row = cursor.fetchone()
        return User(
            id=int(cursor.lastrowid),
            name=name,
            api_key=api_key
        )
