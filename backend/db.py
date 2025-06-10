import sqlite3

DB_PATH = "sms.db"

# Create database and table if not exists
def create_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            sender TEXT,
            receiver TEXT,
            amount INTEGER,
            currency TEXT,
            message TEXT,
            category TEXT
        )
    """)
    conn.commit()
    conn.close()

# Insert one cleaned transaction into the database
def insert_transaction(date, sender, receiver, amount, currency, message, category):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions (date, sender, receiver, amount, currency, message, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (date, sender, receiver, amount, currency, message, category))
    conn.commit()
    conn.close()
