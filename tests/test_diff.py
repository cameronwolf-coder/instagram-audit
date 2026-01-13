"""Tests for diff engine."""
from datetime import datetime
import pytest

from instagram_audit.core import AccountIdentity, Snapshot
from instagram_audit.diff import compute_diff, compute_views, find_missing_accounts


def test_compute_diff_new_followers():
    """Test detecting new followers."""
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
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="2", username="bob"),
            AccountIdentity(pk="3", username="charlie"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.new_followers) == 1
    assert any(acc.pk == "3" and acc.username == "charlie" for acc in diff.new_followers)
    assert len(diff.unfollowers) == 0


def test_compute_diff_unfollowers():
    """Test detecting unfollowers."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="2", username="bob"),
            AccountIdentity(pk="3", username="charlie"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="3", username="charlie"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.unfollowers) == 1
    assert any(acc.pk == "2" and acc.username == "bob" for acc in diff.unfollowers)
    assert len(diff.new_followers) == 0


def test_compute_diff_username_change():
    """Test detecting username changes."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="2", username="bob_old"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="2", username="bob_new"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.username_changes) == 1
    assert "2" in diff.username_changes
    assert diff.username_changes["2"] == ("bob_old", "bob_new")
    assert len(diff.new_followers) == 0
    assert len(diff.unfollowers) == 0


def test_compute_diff_username_change_in_following():
    """Test detecting username changes in following list."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers=set(),
        following={
            AccountIdentity(pk="1", username="alice_old"),
        },
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers=set(),
        following={
            AccountIdentity(pk="1", username="alice_new"),
        },
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.username_changes) == 1
    assert "1" in diff.username_changes
    assert diff.username_changes["1"] == ("alice_old", "alice_new")


def test_compute_diff_username_change_across_lists():
    """Test detecting username changes when account appears in both followers and following."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice_old"),
        },
        following={
            AccountIdentity(pk="1", username="alice_old"),
        },
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice_new"),
        },
        following={
            AccountIdentity(pk="1", username="alice_new"),
        },
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.username_changes) == 1
    assert "1" in diff.username_changes
    assert diff.username_changes["1"] == ("alice_old", "alice_new")


def test_compute_diff_mutual_to_not_mutual():
    """Test when mutual becomes non-mutual."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice"),
        },
        following={
            AccountIdentity(pk="1", username="alice"),
        },
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.unfollowing) == 1
    assert len(diff.mutuals) == 0
    assert len(diff.not_following_back) == 1


def test_compute_diff_following_changes():
    """Test detecting new following and unfollowing."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers=set(),
        following={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="2", username="bob"),
        },
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers=set(),
        following={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="3", username="charlie"),
        },
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.new_following) == 1
    assert any(acc.pk == "3" for acc in diff.new_following)
    assert len(diff.unfollowing) == 1
    assert any(acc.pk == "2" for acc in diff.unfollowing)


def test_compute_views():
    """Test computing relationship views."""
    snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="2", username="bob"),
            AccountIdentity(pk="3", username="charlie"),
        },
        following={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="4", username="dave"),
        },
    )

    views = compute_views(snapshot)

    # alice is mutual
    assert len(views.mutuals) == 1
    assert any(acc.pk == "1" for acc in views.mutuals)

    # bob and charlie follow you but you don't follow them
    assert len(views.not_following_back) == 2
    assert any(acc.pk == "2" for acc in views.not_following_back)
    assert any(acc.pk == "3" for acc in views.not_following_back)

    # dave is followed but doesn't follow you
    assert len(views.not_followed_back) == 1
    assert any(acc.pk == "4" for acc in views.not_followed_back)


def test_find_missing_accounts():
    """Test finding missing accounts."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="2", username="bob"),
        },
        following={
            AccountIdentity(pk="3", username="charlie"),
        },
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice"),
        },
        following=set(),
    )

    missing = find_missing_accounts(old_snapshot, new_snapshot)

    assert len(missing) == 2
    assert any(acc.pk == "2" for acc in missing)
    assert any(acc.pk == "3" for acc in missing)


def test_deterministic_diff():
    """Test that diff results are deterministic."""
    snapshot1 = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="2", username="bob"),
        },
        following={
            AccountIdentity(pk="3", username="charlie"),
        },
    )

    snapshot2 = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice"),
            AccountIdentity(pk="4", username="dave"),
        },
        following={
            AccountIdentity(pk="2", username="bob"),
        },
    )

    # Compute diff multiple times
    diff1 = compute_diff(snapshot1, snapshot2)
    diff2 = compute_diff(snapshot1, snapshot2)

    # Results should be identical
    assert diff1.new_followers == diff2.new_followers
    assert diff1.unfollowers == diff2.unfollowers
    assert diff1.new_following == diff2.new_following
    assert diff1.unfollowing == diff2.unfollowing
    assert diff1.username_changes == diff2.username_changes


def test_empty_snapshots():
    """Test diff with empty snapshots."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers=set(),
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="alice"),
        },
        following={
            AccountIdentity(pk="2", username="bob"),
        },
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    assert len(diff.new_followers) == 1
    assert len(diff.new_following) == 1
    assert len(diff.unfollowers) == 0
    assert len(diff.unfollowing) == 0


def test_renamed_account_not_counted_as_new():
    """Test that a renamed account is not counted as a new follower."""
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        followers={
            AccountIdentity(pk="1", username="old_username"),
        },
        following=set(),
    )

    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 8),
        followers={
            AccountIdentity(pk="1", username="new_username"),
        },
        following=set(),
    )

    diff = compute_diff(old_snapshot, new_snapshot)

    # Should be detected as username change, not new follower
    assert len(diff.new_followers) == 0
    assert len(diff.unfollowers) == 0
    assert len(diff.username_changes) == 1
    assert diff.username_changes["1"] == ("old_username", "new_username")


def test_account_identity_equality():
    """Test that AccountIdentity equality is based on pk."""
    acc1 = AccountIdentity(pk="123", username="alice")
    acc2 = AccountIdentity(pk="123", username="alice_new")
    acc3 = AccountIdentity(pk="456", username="alice")

    assert acc1 == acc2  # Same pk
    assert acc1 != acc3  # Different pk
    assert hash(acc1) == hash(acc2)
    assert hash(acc1) != hash(acc3)
