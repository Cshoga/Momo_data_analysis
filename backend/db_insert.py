import sqlite3
import csv

DB_FILE = 'momo_sms.db'
CSV_FILE = 'cleaned_sms_data.csv'

conn = sqlite3.connect(DB_FILE)
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

with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            type_id = get_type_id(row['type'].strip())
            agent_id = get_agent_id(row['agent_name'].strip(), row['agent_phone'].strip()) if row.get('agent_name') else None

            cursor.execute('''
                INSERT OR IGNORE INTO transactions (
                    transaction_id, amount, currency, date, type_id, agent_id,
                    sender_name, receiver_name, fee, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['transaction_id'].strip(),
                int(row['amount']),
                row.get('currency', 'RWF').strip(),
                row['date'].strip(),
                type_id,
                agent_id,
                row.get('sender_name', '').strip() or None,
                row.get('receiver_name', '').strip() or None,
                int(row['fee']) if row.get('fee') else None,
                row.get('source', 'Mobile').strip()
            ))
        except Exception as e:
            print(f"Skipping row due to error: {e} - {row}")

conn.commit()
conn.close()
print("✅ Data inserted successfully.")
