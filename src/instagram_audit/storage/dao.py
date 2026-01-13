"""Data Access Object for Instagram audit storage."""
import sqlite3
from datetime import datetime
from typing import Optional

from instagram_audit.core import AccountIdentity, Snapshot, MissingAccount, VerificationStatus


class SnapshotDAO:
    """Data access for snapshots and related data."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save_snapshot(self, snapshot: Snapshot) -> int:
        """Save a snapshot and return its ID."""
        cursor = self.conn.cursor()

        # Insert snapshot
        cursor.execute(
            """
            INSERT INTO snapshots (timestamp, source, follower_count, following_count)
            VALUES (?, ?, ?, ?)
            """,
            (
                snapshot.timestamp.isoformat(),
                snapshot.source,
                snapshot.follower_count(),
                snapshot.following_count(),
            ),
        )
        snapshot_id = cursor.lastrowid

        # Save accounts and relationships
        self._save_accounts(snapshot.followers | snapshot.following, snapshot.timestamp)
        self._save_followers(snapshot_id, snapshot.followers)
        self._save_following(snapshot_id, snapshot.following)

        self.conn.commit()
        return snapshot_id

    def _save_accounts(self, accounts: set[AccountIdentity], timestamp: datetime) -> None:
        """Save or update accounts."""
        timestamp_str = timestamp.isoformat()

        for account in accounts:
            # Check if account exists
            cursor = self.conn.cursor()
            cursor.execute("SELECT username, first_seen FROM accounts WHERE pk = ?", (account.pk,))
            row = cursor.fetchone()

            if row:
                old_username = row["username"]
                first_seen = row["first_seen"]

                # Update last_seen and username
                cursor.execute(
                    """
                    UPDATE accounts
                    SET username = ?, full_name = ?, last_seen = ?
                    WHERE pk = ?
                    """,
                    (account.username, account.full_name, timestamp_str, account.pk),
                )

                # Track username change
                if old_username != account.username:
                    self._save_username_history(account.pk, old_username, first_seen, timestamp_str)
                    self._save_username_history(account.pk, account.username, timestamp_str, timestamp_str)
            else:
                # New account
                cursor.execute(
                    """
                    INSERT INTO accounts (pk, username, full_name, first_seen, last_seen)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (account.pk, account.username, account.full_name, timestamp_str, timestamp_str),
                )
                self._save_username_history(account.pk, account.username, timestamp_str, timestamp_str)

    def _save_username_history(
        self, account_pk: str, username: str, first_seen: str, last_seen: str
    ) -> None:
        """Save or update username history."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO username_history (account_pk, username, first_seen, last_seen)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(account_pk, username) DO UPDATE SET last_seen = ?
            """,
            (account_pk, username, first_seen, last_seen, last_seen),
        )

    def _save_followers(self, snapshot_id: int, followers: set[AccountIdentity]) -> None:
        """Save snapshot followers."""
        cursor = self.conn.cursor()
        cursor.executemany(
            "INSERT INTO snapshot_followers (snapshot_id, account_pk) VALUES (?, ?)",
            [(snapshot_id, account.pk) for account in followers],
        )

    def _save_following(self, snapshot_id: int, following: set[AccountIdentity]) -> None:
        """Save snapshot following."""
        cursor = self.conn.cursor()
        cursor.executemany(
            "INSERT INTO snapshot_following (snapshot_id, account_pk) VALUES (?, ?)",
            [(snapshot_id, account.pk) for account in following],
        )

    def get_latest_snapshot(self) -> Optional[Snapshot]:
        """Get the most recent snapshot."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, timestamp, source FROM snapshots ORDER BY timestamp DESC LIMIT 1"
        )
        row = cursor.fetchone()

        if not row:
            return None

        return self._load_snapshot(row["id"], row["timestamp"], row["source"])

    def get_snapshot_by_id(self, snapshot_id: int) -> Optional[Snapshot]:
        """Get a snapshot by ID."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, timestamp, source FROM snapshots WHERE id = ?", (snapshot_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return self._load_snapshot(row["id"], row["timestamp"], row["source"])

    def get_snapshots(self, limit: int = 10) -> list[tuple[int, datetime, str]]:
        """Get list of snapshots (id, timestamp, source)."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, timestamp, source FROM snapshots ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        return [
            (row["id"], datetime.fromisoformat(row["timestamp"]), row["source"])
            for row in cursor.fetchall()
        ]

    def _load_snapshot(self, snapshot_id: int, timestamp_str: str, source: str) -> Snapshot:
        """Load a complete snapshot."""
        timestamp = datetime.fromisoformat(timestamp_str)

        # Load followers
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT a.pk, a.username, a.full_name
            FROM snapshot_followers sf
            JOIN accounts a ON sf.account_pk = a.pk
            WHERE sf.snapshot_id = ?
            """,
            (snapshot_id,),
        )
        followers = {
            AccountIdentity(pk=row["pk"], username=row["username"], full_name=row["full_name"])
            for row in cursor.fetchall()
        }

        # Load following
        cursor.execute(
            """
            SELECT a.pk, a.username, a.full_name
            FROM snapshot_following sf
            JOIN accounts a ON sf.account_pk = a.pk
            WHERE sf.snapshot_id = ?
            """,
            (snapshot_id,),
        )
        following = {
            AccountIdentity(pk=row["pk"], username=row["username"], full_name=row["full_name"])
            for row in cursor.fetchall()
        }

        return Snapshot(
            timestamp=timestamp,
            followers=followers,
            following=following,
            snapshot_id=snapshot_id,
            source=source,
        )

    def get_username_history(self, account_pk: str) -> list[tuple[str, datetime, datetime]]:
        """Get username history for an account."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT username, first_seen, last_seen
            FROM username_history
            WHERE account_pk = ?
            ORDER BY first_seen
            """,
            (account_pk,),
        )
        return [
            (row["username"], datetime.fromisoformat(row["first_seen"]), datetime.fromisoformat(row["last_seen"]))
            for row in cursor.fetchall()
        ]


class VerificationDAO:
    """Data access for verification queue."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add_to_queue(self, missing: MissingAccount) -> int:
        """Add a missing account to verification queue."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO verification_queue
            (account_pk, last_seen, first_missing, status, new_username, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                missing.account.pk,
                missing.last_seen.isoformat(),
                missing.first_missing.isoformat(),
                missing.verification_status.value,
                missing.new_username,
                missing.notes,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_status(
        self,
        queue_id: int,
        status: VerificationStatus,
        new_username: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Update verification status."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE verification_queue
            SET status = ?, new_username = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status.value, new_username, notes, queue_id),
        )
        self.conn.commit()

    def get_pending(self) -> list[tuple[int, MissingAccount]]:
        """Get all pending verifications."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT vq.id, a.pk, a.username, a.full_name,
                   vq.last_seen, vq.first_missing, vq.status, vq.new_username, vq.notes
            FROM verification_queue vq
            JOIN accounts a ON vq.account_pk = a.pk
            WHERE vq.status = 'pending'
            ORDER BY vq.first_missing
            """
        )

        results = []
        for row in cursor.fetchall():
            account = AccountIdentity(pk=row["pk"], username=row["username"], full_name=row["full_name"])
            missing = MissingAccount(
                account=account,
                last_seen=datetime.fromisoformat(row["last_seen"]),
                first_missing=datetime.fromisoformat(row["first_missing"]),
                verification_status=VerificationStatus(row["status"]),
                new_username=row["new_username"],
                notes=row["notes"],
            )
            results.append((row["id"], missing))

        return results
