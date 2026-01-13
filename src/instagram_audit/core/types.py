"""Core data types for Instagram audit."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


@dataclass(frozen=True)
class AccountIdentity:
    """Immutable identity of an Instagram account.

    Uses pk (primary key) as the stable identifier. Username can change.
    """
    pk: str  # Instagram's internal user ID (stable)
    username: str  # Current username (can change)
    full_name: Optional[str] = None

    def __hash__(self) -> int:
        return hash(self.pk)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccountIdentity):
            return NotImplemented
        return self.pk == other.pk


@dataclass
class Snapshot:
    """A point-in-time capture of followers and following."""
    timestamp: datetime
    followers: set[AccountIdentity] = field(default_factory=set)
    following: set[AccountIdentity] = field(default_factory=set)

    # Optional metadata
    snapshot_id: Optional[int] = None
    source: str = "export"  # "export" or "graph_api"

    def follower_count(self) -> int:
        return len(self.followers)

    def following_count(self) -> int:
        return len(self.following)


class VerificationStatus(Enum):
    """Status of a missing account verification."""
    PENDING = "pending"
    BLOCKED = "blocked"
    DEACTIVATED = "deactivated"
    RENAMED = "renamed"
    UNFOLLOWED = "unfollowed"
    UNKNOWN = "unknown"


@dataclass
class MissingAccount:
    """Represents an account that disappeared between snapshots."""
    account: AccountIdentity
    last_seen: datetime
    first_missing: datetime
    verification_status: VerificationStatus = VerificationStatus.PENDING
    new_username: Optional[str] = None  # If renamed
    notes: Optional[str] = None


@dataclass
class DiffEvent:
    """A single change between snapshots."""
    event_type: str  # "new_follower", "unfollower", "new_following", "unfollowing", "username_change"
    account: AccountIdentity
    timestamp: datetime
    old_value: Optional[str] = None  # For username changes
    new_value: Optional[str] = None


@dataclass
class DiffResult:
    """Complete diff between two snapshots."""
    old_snapshot: Snapshot
    new_snapshot: Snapshot

    # Follower changes
    new_followers: set[AccountIdentity] = field(default_factory=set)
    unfollowers: set[AccountIdentity] = field(default_factory=set)

    # Following changes
    new_following: set[AccountIdentity] = field(default_factory=set)
    unfollowing: set[AccountIdentity] = field(default_factory=set)

    # Username changes (same pk, different username)
    username_changes: dict[str, tuple[str, str]] = field(default_factory=dict)  # pk -> (old_username, new_username)

    # Derived views
    mutuals: set[AccountIdentity] = field(default_factory=set)
    not_following_back: set[AccountIdentity] = field(default_factory=set)  # They follow you, you don't follow them
    not_followed_back: set[AccountIdentity] = field(default_factory=set)  # You follow them, they don't follow you


@dataclass
class RelationshipViews:
    """Current relationship state views."""
    snapshot: Snapshot
    mutuals: set[AccountIdentity] = field(default_factory=set)
    not_following_back: set[AccountIdentity] = field(default_factory=set)
    not_followed_back: set[AccountIdentity] = field(default_factory=set)
