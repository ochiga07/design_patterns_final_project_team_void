import sqlite3


def init_db() -> None:
    conn = sqlite3.connect("../bitcoin_wallet.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")
    create_tables(cursor)

    conn.commit()
    conn.close()


def create_tables(cursor: sqlite3.Cursor) -> None:
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Users (
         id INTEGER PRIMARY
         KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         api_key TEXT NOT NULL UNIQUE
    );
    """)

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        balance INTEGER NOT NULL DEFAULT 0,
        wallet_address TEXT NOT NULL UNIQUE,
        FOREIGN KEY (user_id) REFERENCES Users(id)
    );
    """)

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_wallet_id INTEGER NOT NULL,
        receiver_wallet_id INTEGER NOT NULL,
        transfer_amount INTEGER NOT NULL,
        transfer_fee INTEGER NOT NULL,
        FOREIGN KEY (sender_wallet_id) REFERENCES Wallets(id),
        FOREIGN KEY (receiver_wallet_id) REFERENCES Wallets(id)
    );
    """)

if __name__ == "__main__":
    init_db()


