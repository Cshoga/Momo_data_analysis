-- Table for transaction types
CREATE TABLE transaction_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Table for agents (for withdrawals, etc.)
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT
);

-- Main transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE,
    amount INTEGER NOT NULL,
    currency TEXT DEFAULT 'RWF',
    date TEXT NOT NULL,
    type_id INTEGER,
    agent_id INTEGER,
    sender_name TEXT,
    receiver_name TEXT,
    fee INTEGER,
    source TEXT,
    FOREIGN KEY (type_id) REFERENCES transaction_types(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
