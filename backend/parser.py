import sqlite3
import xml.etree.ElementTree as ET
import re
from datetime import datetime

DB = "sms.db"
XML = "modified_sms_v2.xml"
LOG = "unprocessed.txt"

conn = sqlite3.connect(DB)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

cur.execute("SELECT id, name FROM transaction_types")
types = {name: id for id, name in cur.fetchall()}

def get_type_id(name):
    if name in types:
        return types[name]
    cur.execute("INSERT INTO transaction_types (name) VALUES (?)", (name,))
    conn.commit()
    types[name] = cur.lastrowid
    return types[name]

def parse_amount(text):
    m = re.search(r"(\d[\d,]*)\s*RWF", text.replace(",", ""))
    return int(m.group(1)) if m else 0

def parse_date(ms):
    try:
        ts = int(ms) / 1000
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None

def categorize(text):
    t = text.lower()
    if "received" in t: return "Incoming Money"
    if "payment of" in t: return "Payment"
    if "transferred to" in t: return "Transfer to Mobile Numbers"
    if "bank deposit" in t: return "Bank Deposits"
    if "airtime" in t: return "Airtime Bill Payments"
    if "cash deposit" in t or "cash power" in t: return "Cash Power Bill Payments"
    if "withdrew" in t or "withdrawn" in t: return "Withdrawals from Agents"
    if "bank" in t and "transfer" in t: return "Bank Transfers"
    if "bundle" in t or "internet" in t or "voice" in t: return "Internet and Voice Bundle Purchases"
    return None

tree = ET.parse(XML)
root = tree.getroot()

with open(LOG, "w", encoding="utf-8") as lf:
    for sms in root.findall(".//sms"):
        body = sms.attrib.get("body", "")
        date = parse_date(sms.attrib.get("date", "0"))
        amount = parse_amount(body)
        category = categorize(body)

        if not date or amount <= 0 or not category:
            lf.write(body + "\n")
            continue

        tid = sms.attrib.get("date", "") + sms.attrib.get("address", "")
        type_id = get_type_id(category)
        cur.execute("""
            INSERT OR IGNORE INTO transactions (
                transaction_id, amount, currency, date, type_id, agent_id,
                sender_name, receiver_name, fee, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tid, amount, "RWF", date, type_id, None,
            sms.attrib.get("address", ""), None, None, "Mobile"
        ))

conn.commit()
conn.close()
print("done")
