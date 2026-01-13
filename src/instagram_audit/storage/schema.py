"""SQLite schema for Instagram audit data."""
import sqlite3
from typing import Optional


SCHEMA_VERSION = 1

SCHEMA_SQL = """
-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);

-- Snapshots
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'export',
    follower_count INTEGER NOT NULL DEFAULT 0,
    following_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON snapshots(timestamp);

-- Accounts (deduplicated by pk)
CREATE TABLE IF NOT EXISTS accounts (
    pk TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    full_name TEXT,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_accounts_username ON accounts(username);

-- Snapshot followers
CREATE TABLE IF NOT EXISTS snapshot_followers (
    snapshot_id INTEGER NOT NULL,
    account_pk TEXT NOT NULL,
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE,
    FOREIGN KEY (account_pk) REFERENCES accounts(pk),
    PRIMARY KEY (snapshot_id, account_pk)
);

-- Snapshot following
CREATE TABLE IF NOT EXISTS snapshot_following (
    snapshot_id INTEGER NOT NULL,
    account_pk TEXT NOT NULL,
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE,
    FOREIGN KEY (account_pk) REFERENCES accounts(pk),
    PRIMARY KEY (snapshot_id, account_pk)
);

-- Username history (for tracking renames)
CREATE TABLE IF NOT EXISTS username_history (
    account_pk TEXT NOT NULL,
    username TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    FOREIGN KEY (account_pk) REFERENCES accounts(pk) ON DELETE CASCADE,
    PRIMARY KEY (account_pk, username)
);

-- Verification queue for missing accounts
CREATE TABLE IF NOT EXISTS verification_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_pk TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    first_missing TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    new_username TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_pk) REFERENCES accounts(pk)
);

CREATE INDEX IF NOT EXISTS idx_verification_queue_status ON verification_queue(status);
CREATE INDEX IF NOT EXISTS idx_verification_queue_account ON verification_queue(account_pk);
"""


def initialize_database(db_path: str) -> sqlite3.Connection:
    """Initialize the database with schema."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # Check schema version
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
    )
    if not cursor.fetchone():
        # Fresh database
        conn.executescript(SCHEMA_SQL)
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
        conn.commit()
    else:
        # Existing database - check version
        cursor.execute("SELECT version FROM schema_version")
        current_version = cursor.fetchone()[0]
        if current_version != SCHEMA_VERSION:
            raise RuntimeError(
                f"Database schema version mismatch: expected {SCHEMA_VERSION}, got {current_version}"
            )

    return conn


def get_connection(db_path: str = "instagram_audit.db") -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
