import sqlite3
import csv

DB_FILE = 'sms.db'

conn = sqlite3.connect(DB_FILE)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

def get_type_id(type_name):
    cursor.execute("SELECT id FROM transaction_types WHERE name = ?", (type_name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO transaction_types (name) VALUES (?)", (type_name,))
    conn.commit()
    return cursor.lastrowid

def get_agent_id(name, phone):
    if not name:
        return None
    cursor.execute("SELECT id FROM agents WHERE name = ? AND phone = ?", (name, phone))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO agents (name, phone) VALUES (?, ?)", (name, phone))
    conn.commit()
    return cursor.lastrowid

type_id = get_type_id("Incoming Money")
agent_id = get_agent_id("Jane Doe", "250123456789")

cursor.execute('''
    INSERT OR IGNORE INTO transactions (
        transaction_id, amount, currency, date, type_id, agent_id,
        sender_name, receiver_name, fee, source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    "TX900001", 10000, "RWF", "2025-06-13 09:00:00", type_id, agent_id,
    "Eric", None, None, "Mobile"
))

conn.commit()
conn.close()
print ("data inserted successfully")
