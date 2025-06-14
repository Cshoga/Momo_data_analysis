import sqlite3

db = sqlite3.connect("sms.db")
db.execute("PRAGMA foreign_keys = ON")
cur = db.cursor()

transactions = [
    {
        "transaction_id": "tx001",
        "amount": 5000,
        "currency": "RWF",
        "date": "2024-06-01 08:00:00",
        "type": "Incoming Money",
        "agent": "Agent A",
        "phone": "0788000000",
        "sender": "John Doe",
        "receiver": "Me",
        "fee": 100,
        "source": "Mobile"
    },
    {
        "transaction_id": "tx002",
        "amount": 2500,
        "currency": "RWF",
        "date": "2024-06-02 10:00:00",
        "type": "Withdrawal",
        "agent": "Agent B",
        "phone": "0788111111",
        "sender": "",
        "receiver": "",
        "fee": 300,
        "source": "Mobile"
    }
]

def get_type_id(name):
    cur.execute("SELECT id FROM transaction_types WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO transaction_types (name) VALUES (?)", (name,))
    db.commit()
    return cur.lastrowid

def get_agent_id(name, phone):
    cur.execute("SELECT id FROM agents WHERE name = ? AND phone = ?", (name, phone))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO agents (name, phone) VALUES (?, ?)", (name, phone))
    db.commit()
    return cur.lastrowid

for t in transactions:
    type_id = get_type_id(t["type"])
    agent_id = get_agent_id(t["agent"], t["phone"])
    cur.execute("""
        INSERT OR IGNORE INTO transactions (
            transaction_id, amount, currency, date,
            type_id, agent_id, sender_name, receiver_name,
            fee, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        t["transaction_id"], t["amount"], t["currency"], t["date"],
        type_id, agent_id, t["sender"], t["receiver"],
        t["fee"], t["source"]
    ))

db.commit()
db.close()
