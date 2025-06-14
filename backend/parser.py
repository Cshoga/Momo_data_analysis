import sqlite3
import xml.etree.ElementTree as ET
import re
from datetime import datetime

db = sqlite3.connect("sms.db")
db.execute("PRAGMA foreign_keys = ON")
cur = db.cursor()

tree = ET.parse("modified_sms_v2.xml")
root = tree.getroot()

cur.execute("SELECT id, name FROM transaction_types")
types = {name.lower(): id for id, name in cur.fetchall()}

def insert_type(name):
    lower = name.lower()
    if lower not in types:
        cur.execute("INSERT INTO transaction_types (name) VALUES (?)", (name,))
        db.commit()
        types[lower] = cur.lastrowid
    return types[lower]

def parse_amount(text):
    m = re.search(r'(\d[\d,]*)\s*RWF', text)
    if m:
        return int(m.group(1).replace(',', ''))
    return 0

def parse_date(timestamp):
    try:
        return datetime.fromtimestamp(int(timestamp) / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

def categorize(text):
    if "agaciro" in text.lower():
        return "Donation"
    if "received" in text.lower() and "from" in text.lower():
        return "Incoming Money"
    if "sent to" in text.lower():
        return "Transfer to Mobile"
    if "paid to" in text.lower():
        return "Payment"
    if "withdrew" in text.lower():
        return "Withdrawal"
    if "airtime" in text.lower():
        return "Airtime"
    if "bundle" in text.lower():
        return "Bundle"
    if "bank" in text.lower():
        return "Bank"
    return "Other"

for sms in root.findall("sms"):
    body = sms.attrib.get("body", "")
    date = parse_date(sms.attrib.get("date", "0"))
    amount = parse_amount(body)
    t_id = sms.attrib.get("date") + sms.attrib.get("address", "")
    category = categorize(body)
    type_id = insert_type(category)

    cur.execute("""
        INSERT OR IGNORE INTO transactions (
            transaction_id, amount, date, type_id
        ) VALUES (?, ?, ?, ?)
    """, (t_id, amount, date, type_id))

db.commit()
db.close()
