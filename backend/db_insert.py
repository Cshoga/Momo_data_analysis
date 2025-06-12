# db_insert.py

import sqlite3
import csv

# Database file
DB_FILE = 'momo_sms.db'
CSV_FILE = 'cleaned_sms_data.csv'

# Connect to the database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Get or create transaction type
def get_type_id(type_name):
    cursor.execute("SELECT id FROM transaction_types WHERE name = ?", (type_name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO transaction_types (name) VALUES (?)", (type_name,))
    conn.commit()
    return cursor.lastrowid

# Get or create agent
def get_agent_id(name, phone):
    cursor.execute("SELECT id FROM agents WHERE name = ? AND phone = ?", (name, phone))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO agents (name, phone) VALUES (?, ?)", (name, phone))
    conn.commit()
    return cursor.lastrowid

# Read CSV and insert into database
with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        type_id = get_type_id(row['type'])
        agent_id = get_agent_id(row['agent_name'], row['agent_phone']) if row['agent_name'] else None

        cursor.execute('''
            INSERT OR IGNORE INTO transactions (
                transaction_id, amount, currency, date, type_id, agent_id,
                sender_name, receiver_name, fee, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['transaction_id'],
            int(row['amount']),
            row.get('currency', 'RWF'),
            row['date'],
            type_id,
            agent_id,
            row.get('sender_name'),
            row.get('receiver_name'),
            int(row['fee']) if row.get('fee') else None,
            row.get('source', 'Mobile')
        ))

conn.commit()
conn.close()
print("Data inserted successfully.")
