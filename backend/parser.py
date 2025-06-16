import sqlite3
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from collections import defaultdict
import os

class EfficientSMSParser:
    def __init__(self, db_path="momo.db", xml_path="modified_sms_v2.xml", log_path="unprocessed.txt"):
        self.db_path = db_path
        self.xml_path = xml_path
        self.log_path = log_path
        self.conn = None
        self.cur = None
        self.types = {}
        
        # Regex patterns for categorizing messages
        self.patterns = {
            'Incoming Money': [
                r'You have received (\d+(?:,\d{3})*) RWF from ([^(]+)',
                r'received.*?(\d+(?:,\d{3})*)\s*RWF'
            ],
            'Payments to Code Holders': [
                r'Your payment of (\d+(?:,\d{3})*) RWF to ([^0-9\n]+)',
                r'TxId: \d+\. Your payment of ([\d,]+) RWF to ([^0-9]+)',
                r'payment of.*?(\d+(?:,\d{3})*)\s*RWF to ([^0-9\n]+)'
            ],
            'Transfers to Mobile Numbers': [
                r'\*165\*S\*(\d+(?:,\d{3})*) RWF transferred to ([^(]+)',
                r'transferred.*?(\d+(?:,\d{3})*)\s*RWF to ([^(]+)',
                r'transferred.*?(\d+(?:,\d{3})*)\s*RWF to (\d+)'
            ],
            'Bank Deposits': [
                r'bank deposit of (\d+(?:,\d{3})*) RWF',
                r'bank.*?deposit.*?(\d+(?:,\d{3})*)\s*RWF',
                r'DEPOSIT RWF (\d+(?:,\d{3})*)'
            ],
            'Airtime Bill Payments': [
                r'payment of (\d+(?:,\d{3})*) RWF to Airtime',
                r'airtime.*?(\d+(?:,\d{3})*)\s*RWF'
            ],
            'Cash Power Bill Payments': [
                r'cash deposit.*?(\d+(?:,\d{3})*)\s*RWF',
                r'cash power.*?(\d+(?:,\d{3})*)\s*RWF'
            ],
            'Transactions Initiated by Third Parties': [
                r'transaction of (\d+(?:,\d{3})*) RWF by ([^(]+)',
                r'payment to ([^(]+).*?(\d+(?:,\d{3})*)\s*RWF',
                r'by ([^(]+).*?(\d+(?:,\d{3})*)\s*RWF'
            ],
            'Withdrawals from Agents': [
                r'withdrew.*?(\d+(?:,\d{3})*)\s*RWF',
                r'withdrawn.*?(\d+(?:,\d{3})*)\s*RWF'
            ],
            'Bank Transfers': [
                r'bank.*?transfer.*?(\d+(?:,\d{3})*)\s*RWF'
            ],
            'Internet and Voice Bundle Purchases': [
                r'kugura.*?(\d+(?:,\d{3})*)Rwf\((\d+(?:\.\d+)?GB)',
                r'kugura.*?(\d+(?:,\d{3})*)FRW\((\d+(?:\.\d+)?GB)',
                r'kugura.*?(\d+(?:,\d{3})*)Rwf\((\d+(?:\.\d+)?MB)',
                r'kugura.*?(\d+(?:,\d{3})*)Frw=(\d+)Mins\+(\d+)SMS',
                r'kugura.*?(\d+(?:,\d{3})*)Rwf=(\d+)Mins\+(\d+)SMS',
                r'bundle.*?(\d+(?:,\d{3})*)\s*RWF',
                r'internet.*?(\d+(?:,\d{3})*)\s*RWF',
                r'voice.*?(\d+(?:,\d{3})*)\s*RWF'
            ]
        }
    
    def connect_db(self):
        """Initialize database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cur = self.conn.cursor()
        
        self.cur.execute("SELECT id, name FROM transaction_types")
        self.types = {name: id for id, name in self.cur.fetchall()}
    
    def get_type_id(self, name):
        """Get or create transaction type ID"""
        if name in self.types:
            return self.types[name]
        
        self.cur.execute("INSERT INTO transaction_types (name) VALUES (?)", (name,))
        self.conn.commit()
        self.types[name] = self.cur.lastrowid
        return self.types[name]
    
    def extract_amount(self, text):
        """Extract amount with better accuracy"""
        clean_text = text.replace(',', '')
        match = re.search(r'(\d+)\s*RWF', clean_text, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def parse_date(self, ms_timestamp):
        """Convert millisecond timestamp to datetime"""
        try:
            timestamp = int(ms_timestamp) / 1000
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return None
    
    def categorize_message(self, text):
        """Categorize message using enhanced patterns"""
        text_lower = text.lower()
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return category
        
        return None
    
    def extract_recipient_sender(self, text, category):
        """Extract recipient/sender information based on category, only accept valid names for code holders and mobile numbers"""
        if category == 'Incoming Money':
            match = re.search(r'from ([^(]+)', text, re.IGNORECASE)
            return match.group(1).strip() if match else None
        elif category == 'Payments to Code Holders':
            match = re.search(r'to ([^0-9\n]+)', text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if (re.match(r'^[A-Za-z]+( [A-Za-z]+)+$', name) and
                    not re.search(r'token|bundle|completed|pack|has been|at$', name, re.IGNORECASE)):
                    return name
            return None
        elif category == 'Transfers to Mobile Numbers':
            match = re.search(r'transferred to ([^(]+)', text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if re.match(r'^[A-Za-z]+( [A-Za-z]+)+$', name):
                    return name
            return None
        else:
            return None
    
    def parse_xml(self):
        """Parse XML file and extract SMS messages"""
        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            return root.findall(".//sms")
        except Exception as e:
            print(f"Error parsing XML: {e}")
            return []
    
    def process_messages(self):
        """Process all SMS messages and insert into database"""
        sms_messages = self.parse_xml()
        processed_count = 0
        unprocessed_count = 0
        
        with open(self.log_path, "w", encoding="utf-8") as log_file:
            for sms in sms_messages:
                body = sms.attrib.get("body", "")
                date_ms = sms.attrib.get("date", "0")
                address = sms.attrib.get("address", "")
                
                if address != "M-Money":
                    continue
                
                # Parse message details
                date = self.parse_date(date_ms)
                amount = self.extract_amount(body)
                category = self.categorize_message(body)
                
                # Log unprocessed messages
                if not date or amount <= 0 or not category:
                    log_file.write(f"UNPROCESSED: {body}\n")
                    unprocessed_count += 1
                    continue
                
                recipient_sender = self.extract_recipient_sender(body, category)
                
                # Create unique transaction ID
                transaction_id = f"{date_ms}_{address}_{hash(body) % 100000}"
                
                # Get transaction type ID
                type_id = self.get_type_id(category)
                
                # Insert into db
                try:
                    self.cur.execute("""
                        INSERT OR IGNORE INTO transactions (
                            transaction_id, amount, currency, date, type_id, agent_id,
                            sender_name, receiver_name, fee, source
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        transaction_id, amount, "RWF", date, type_id, None,
                        recipient_sender if category == 'Incoming Money' else None,
                        None if category == 'Incoming Money' else recipient_sender,
                        None, "Mobile"
                    ))
                    processed_count += 1
                except Exception as e:
                    log_file.write(f"DB ERROR: {body} - {str(e)}\n")
                    unprocessed_count += 1
        
        self.conn.commit()
        return processed_count, unprocessed_count
    
    def get_statistics(self):
        """Get processing statistics"""
        self.cur.execute("""
            SELECT tt.name, COUNT(*) as count, SUM(amount) as total_amount
            FROM transactions t
            JOIN transaction_types tt ON t.type_id = tt.id
            WHERE t.source = 'Mobile'
            GROUP BY tt.name
            ORDER BY total_amount DESC
        """)
        
        stats = self.cur.fetchall()
        return stats
    
    def print_summary(self, processed, unprocessed):
        """Print processing summary"""
        print("=" * 60)
        print("SMS TRANSACTION PROCESSING COMPLETE")
        print("=" * 60)
        print(f"Processed: {processed} transactions")
        self.cur.execute("SELECT DISTINCT name FROM transaction_types")
        categories = [c[0] for c in self.cur.fetchall()]
        with open('category_types.txt', 'w') as f:
            f.write(str(categories))

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    DB_PATH = os.path.join(root_dir, "momo.db")  # Always use root directory
    XML_PATH = os.path.join(script_dir, "modified_sms_v2.xml") 
    LOG_PATH = os.path.join(script_dir, "unprocessed.txt") 
    
    print("Starting SMS transaction processing...")
    parser = EfficientSMSParser(DB_PATH, XML_PATH, LOG_PATH)
    parser.connect_db()
    processed, unprocessed = parser.process_messages()
    parser.print_summary(processed, unprocessed)
    print("Processing completed!")

if __name__ == '__main__':
    main()