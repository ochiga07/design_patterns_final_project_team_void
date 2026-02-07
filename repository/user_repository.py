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
        new_id = cursor.lastrowid
        assert new_id is not None
        return User(
            id=int(new_id),
            name=name,
            api_key=api_key
        )

    def get_user_by_id(self, user_id: int) -> User | None:
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT id, name, api_key FROM Users WHERE id = ?", (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return User(id=row["id"], name=row["name"], api_key=row["api_key"])
        return None

    def get_all_users(self) -> list[User]:
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT id, name, api_key FROM Users"
        )
        rows = cursor.fetchall()
        return [
            User(id=row["id"], name=row["name"], api_key=row["api_key"])
            for row in rows
        ]