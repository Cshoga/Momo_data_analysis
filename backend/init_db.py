import sqlite3

def initialize_db():
    with open("schema.sql", "r", encoding="utf-8") as f:
        schema = f.read()

    conn = sqlite3.connect("sms.db")
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_db()

print("Database initialized successfully.")
