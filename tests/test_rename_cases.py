"""Tests for rename edge cases."""
from datetime import datetime
import pytest

from instagram_audit.core import AccountIdentity, Snapshot
from instagram_audit.diff import compute_diff


def test_rename_only_in_followers():
    """Test username change for account only in followers."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="123", username="old_name"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="123", username="new_name"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.username_changes) == 1
    assert diff.username_changes["123"] == ("old_name", "new_name")
    assert len(diff.new_followers) == 0
    assert len(diff.unfollowers) == 0


def test_rename_only_in_following():
    """Test username change for account only in following."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers=set(),
        following={
            AccountIdentity(pk="456", username="old_name"),
        },
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers=set(),
        following={
            AccountIdentity(pk="456", username="new_name"),
        },
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.username_changes) == 1
    assert diff.username_changes["456"] == ("old_name", "new_name")
    assert len(diff.new_following) == 0
    assert len(diff.unfollowing) == 0


def test_rename_in_both_lists():
    """Test username change for mutual (in both followers and following)."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="789", username="old_name"),
        },
        following={
            AccountIdentity(pk="789", username="old_name"),
        },
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="789", username="new_name"),
        },
        following={
            AccountIdentity(pk="789", username="new_name"),
        },
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.username_changes) == 1
    assert diff.username_changes["789"] == ("old_name", "new_name")
    # Should still be mutual
    assert len(diff.mutuals) == 1
    assert any(acc.pk == "789" for acc in diff.mutuals)


def test_rename_from_follower_to_following():
    """Test username change when account moves from follower to following."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="111", username="old_name"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers=set(),
        following={
            AccountIdentity(pk="111", username="new_name"),
        },
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    # Should detect username change
    assert len(diff.username_changes) == 1
    assert diff.username_changes["111"] == ("old_name", "new_name")

    # Should also detect the relationship change
    assert len(diff.unfollowers) == 1
    assert len(diff.new_following) == 1


def test_rename_with_unfollow():
    """Test username change combined with unfollow action."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="222", username="old_name"),
        },
        following={
            AccountIdentity(pk="222", username="old_name"),
        },
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="222", username="new_name"),
        },
        following=set(),  # Unfollowed
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    # Should detect both username change and unfollow
    assert len(diff.username_changes) == 1
    assert diff.username_changes["222"] == ("old_name", "new_name")
    assert len(diff.unfollowing) == 1


def test_multiple_renames():
    """Test multiple username changes in one diff."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice_old"),
            AccountIdentity(pk="2", username="bob_old"),
            AccountIdentity(pk="3", username="charlie_old"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice_new"),
            AccountIdentity(pk="2", username="bob_new"),
            AccountIdentity(pk="3", username="charlie_new"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.username_changes) == 3
    assert diff.username_changes["1"] == ("alice_old", "alice_new")
    assert diff.username_changes["2"] == ("bob_old", "bob_new")
    assert diff.username_changes["3"] == ("charlie_old", "charlie_new")


def test_rename_mixed_with_new_followers():
    """Test username changes mixed with new followers."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice_old"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice_new"),
            AccountIdentity(pk="2", username="bob"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    # Should detect rename for pk=1
    assert len(diff.username_changes) == 1
    assert diff.username_changes["1"] == ("alice_old", "alice_new")

    # Should detect new follower for pk=2
    assert len(diff.new_followers) == 1
    assert any(acc.pk == "2" and acc.username == "bob" for acc in diff.new_followers)


def test_no_rename_when_username_unchanged():
    """Test that unchanged usernames are not reported as renames."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.username_changes) == 0


def test_rename_same_username_different_pk():
    """Test that same username with different pk is treated as different account."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="2", username="alice"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    # Should be treated as unfollower + new follower, not a rename
    assert len(diff.username_changes) == 0
    assert len(diff.unfollowers) == 1
    assert len(diff.new_followers) == 1


def test_case_sensitive_username():
    """Test that username changes are case-sensitive."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="Alice"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    # Should detect case change as username change
    assert len(diff.username_changes) == 1
    assert diff.username_changes["1"] == ("Alice", "alice")


def test_rename_with_full_name():
    """Test that full_name doesn't affect rename detection."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice_old", full_name="Alice Smith"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice_new", full_name="Alice Johnson"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    # Should only detect username change, not full_name change
    assert len(diff.username_changes) == 1
    assert diff.username_changes["1"] == ("alice_old", "alice_new")


def test_username_swap():
    """Test when two accounts swap usernames."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="2", username="bob"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="bob"),
            AccountIdentity(pk="2", username="alice"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    # Should detect both username changes
    assert len(diff.username_changes) == 2
    assert diff.username_changes["1"] == ("alice", "bob")
    assert diff.username_changes["2"] == ("bob", "alice")
