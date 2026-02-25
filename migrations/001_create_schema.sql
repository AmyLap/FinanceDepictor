-- Migration: Create initial schema for FinanceDepictor
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Users: optional if you later add auth; keep simple for single couple use
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts (bank accounts)
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    bank_name TEXT,
    account_mask TEXT,
    account_type TEXT,
    currency TEXT DEFAULT 'GBP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Uploaded files metadata (pdf, ofx, csv)
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL,
    filename TEXT NOT NULL,
    original_name TEXT,
    file_type TEXT,
    checksum TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories (hierarchical)
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    is_system INTEGER DEFAULT 0
);

-- Rules for automatic categorization (simple patterns)
CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    pattern TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    priority INTEGER DEFAULT 100,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER REFERENCES files(id) ON DELETE SET NULL,
    account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL,
    external_id TEXT, -- bank-provided id or reference
    date DATE NOT NULL,
    posted_date DATE,
    amount NUMERIC NOT NULL,
    currency TEXT DEFAULT 'GBP',
    description TEXT,
    merchant TEXT,
    normalized_description TEXT,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    category_confidence REAL DEFAULT 0.0,
    categorized_by TEXT, -- 'rule','ai','manual'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_account_date ON transactions(account_id, date);
CREATE INDEX IF NOT EXISTS idx_transactions_external_id ON transactions(external_id);

-- Category audit/history for transactions (keeps change history)
CREATE TABLE IF NOT EXISTS transaction_category_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    previous_category_id INTEGER REFERENCES categories(id),
    new_category_id INTEGER REFERENCES categories(id),
    changed_by TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMIT;
