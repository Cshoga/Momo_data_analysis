mport sqlite3

conn = sqlite3.connect('sms.db')
cursor = conn.cursor()

try:
    cursor.execute('SELECT COUNT(*) FROM transactions')
    count = cursor.fetchone()[0]
    print(f'Total transactions: {count}')
except Exception as e:
    print('Error:', e)

conn.close()
