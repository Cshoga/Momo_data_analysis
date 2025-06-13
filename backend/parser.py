import xml.etree.ElementTree as ET
import re
from db import create_database, insert_transaction

XML_FILE = "modified_sms_v2.xml"
UNPROCESSED_FILE = "backend/unprocessed.txt"

CATEGORY_PATTERNS = [
    (r"you have received", "Incoming Money"),
    (r"sent to code \d+", "Payments to Code Holders"),
    (r"you have sent.*to.*\d{10}", "Transfers to Mobile Numbers"),
    (r"deposited to your bank", "Bank Deposits"),
    (r"airtime", "Airtime Bill Payments"),
    (r"cash power|electricity", "Cash Power Bill Payments"),
    (r"initiated by", "Transactions Initiated by Third Parties"),
    (r"withdrawn at agent", "Withdrawals from Agents"),
    (r"bank transfer", "Bank Transfers"),
    (r"bundle|internet|voice", "Internet and Voice Bundle Purchases"),
]

def categorize_message(text):
    text_lower = text.lower()
    for pattern, category in CATEGORY_PATTERNS:
        if re.search(pattern, text_lower):
            return category
    return "Uncategorized"

def extract_amount(text):
    match = re.search(r"(\d+[,\d]*)\s*RWF", text.replace(",", ""))
    return int(match.group(1)) if match else 0

def extract_date(sms_elem):
    return sms_elem.attrib.get("date", "")

def insert_transaction(transaction_id, amount, currency, date, type_name, sender, receiver, fee, source):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM transaction_types WHERE name = ?", (type_name,))
    row = cursor.fetchone()
    if row:
        type_id = row[0]
    else:
        cursor.execute("INSERT INTO transaction_types (name) VALUES (?)", (type_name,))
        conn.commit()
        type_id = cursor.lastrowid
    cursor.execute('''
        INSERT OR IGNORE INTO transactions (
            transaction_id, amount, currency, date, type_id, agent_id,
            sender_name, receiver_name, fee, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        transaction_id, amount, currency, date, type_id, None,
        sender, receiver, fee, source
    ))
    conn.commit()
    conn.close()

def parse_sms():
    tree = ET.parse(XML_FILE)
    root = tree.getroot()

    create_database()

    with open(UNPROCESSED_FILE, "w", encoding="utf-8") as log_file:
        for sms in root.findall(".//sms"):
            body = sms.attrib.get("body", "")
            date = extract_date(sms)
            amount = extract_amount(body)
            category = categorize_message(body)
            sender = sms.attrib.get("address", "")
            receiver = "" 

            if amount == 0 or category == "Uncategorized":
                log_file.write(body + "\n")
                continue

            insert_transaction(
                date=date,
                sender=sender,
                receiver=receiver,
                amount=amount,
                currency="RWF",
                message=body,
                category=category
            )

    print("Parsing complete. Check unprocessed.txt for skipped messages.")

if __name__ == "__main__":
    parse_sms()
