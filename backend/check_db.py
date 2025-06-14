import sqlite3

conn = sqlite3.connect('sms.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM transactions")
count = cursor.fetchone()[0]

print(f"Total rows in 'transactions': {count}")

conn.close()
