
-- Schema
CREATE TABLE IF NOT EXISTS transaction_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE,
    amount INTEGER,
    currency TEXT,
    date TEXT,
    type_id INTEGER,
    agent_id INTEGER,
    sender_name TEXT,
    receiver_name TEXT,
    fee INTEGER,
    source TEXT,
    FOREIGN KEY (type_id) REFERENCES transaction_types(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Sample Data
INSERT INTO transaction_types (id, name) VALUES (1, 'Incoming Money');
INSERT INTO transaction_types (id, name) VALUES (2, 'Payment to Code Holder');
INSERT INTO transaction_types (id, name) VALUES (3, 'Airtime Purchase');

INSERT INTO agents (id, name, phone) VALUES (1, 'Jane Doe', '250123456789');
INSERT INTO agents (id, name, phone) VALUES (2, 'John Agent', '250987654321');

INSERT INTO transactions (
    transaction_id, amount, currency, date, type_id, agent_id, sender_name, receiver_name, fee, source
) VALUES (
    '123456', 5000, 'RWF', '2024-01-01 10:00:00', 1, NULL, 'John Doe', NULL, NULL, 'Mobile'
);

INSERT INTO transactions (
    transaction_id, amount, currency, date, type_id, agent_id, sender_name, receiver_name, fee, source
) VALUES (
    '789012', 1500, 'RWF', '2024-01-02 14:30:00', 2, NULL, NULL, 'Jane Smith', NULL, 'Mobile'
);

INSERT INTO transactions (
    transaction_id, amount, currency, date, type_id, agent_id, sender_name, receiver_name, fee, source
) VALUES (
    '345678', 3000, 'RWF', '2024-01-03 16:00:00', 3, NULL, NULL, 'Airtime', 50, 'Mobile'
);

INSERT INTO transactions (
    transaction_id, amount, currency, date, type_id, agent_id, sender_name, receiver_name, fee, source
) VALUES (
    '567890', 20000, 'RWF', '2024-01-04 12:00:00', 1, 1, 'Wakuma Tekalign DEBELA', NULL, NULL, 'Agent'
);
