import sqlite3
from collections.abc import Generator


def get_db() -> Generator[sqlite3.Connection]:
    connection = sqlite3.connect("bitcoin_wallet.db", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
