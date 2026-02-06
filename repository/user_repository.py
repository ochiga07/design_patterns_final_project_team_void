import sqlite3

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
