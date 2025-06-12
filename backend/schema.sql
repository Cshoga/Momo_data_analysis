-- Table for transaction types
CREATE TABLE IF NOT EXISTS transaction_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Table for agents (for withdrawals, etc.)
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT
);

-- Main transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE NOT NULL,
    amount INTEGER NOT NULL,
    currency TEXT DEFAULT 'RWF',
    date TEXT NOT NULL,
    type_id INTEGER NOT NULL,
    agent_id INTEGER,
    sender_name TEXT,
    receiver_name TEXT,
    fee INTEGER,
    source TEXT DEFAULT 'Mobile',
    FOREIGN KEY (type_id) REFERENCES transaction_types(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
