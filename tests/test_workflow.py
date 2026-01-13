"""Integration test for complete workflow."""
import tempfile
from pathlib import Path
from datetime import datetime

from instagram_audit.core import AccountIdentity, Snapshot
from instagram_audit.storage import initialize_database, get_connection, SnapshotDAO, VerificationDAO
from instagram_audit.diff import compute_diff, compute_views, find_missing_accounts
from instagram_audit.verify import VerificationQueue
from instagram_audit.core import VerificationStatus


def test_complete_workflow():
    """Test a complete audit workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        # Initialize database
        initialize_database(str(db_path))
        conn = get_connection(str(db_path))
        dao = SnapshotDAO(conn)

        # Week 1: Initial snapshot
        snapshot1 = Snapshot(
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

        snapshot1_id = dao.save_snapshot(snapshot1)
        assert snapshot1_id == 1

        # Verify we can load it back
        loaded1 = dao.get_latest_snapshot()
        assert loaded1 is not None
        assert loaded1.follower_count() == 3
        assert loaded1.following_count() == 2

        # Week 2: Second snapshot with changes
        snapshot2 = Snapshot(
            timestamp=datetime(2024, 1, 8),
            followers={
                AccountIdentity(pk="1", username="alice"),
                AccountIdentity(pk="2", username="bob_new"),  # Username change
                AccountIdentity(pk="5", username="eve"),  # New follower
            },
            following={
                AccountIdentity(pk="1", username="alice"),
                AccountIdentity(pk="5", username="eve"),  # New following
            },
        )

        snapshot2_id = dao.save_snapshot(snapshot2)
        assert snapshot2_id == 2

        # Compute diff
        diff = compute_diff(snapshot1, snapshot2)

        # Verify changes
        assert len(diff.new_followers) == 1
        assert any(acc.pk == "5" for acc in diff.new_followers)

        assert len(diff.unfollowers) == 1
        assert any(acc.pk == "3" for acc in diff.unfollowers)

        assert len(diff.new_following) == 1
        assert any(acc.pk == "5" for acc in diff.new_following)

        assert len(diff.unfollowing) == 1
        assert any(acc.pk == "4" for acc in diff.unfollowing)

        # Verify username change detection
        assert len(diff.username_changes) == 1
        assert "2" in diff.username_changes
        assert diff.username_changes["2"] == ("bob", "bob_new")

        # Verify username history was recorded
        username_history = dao.get_username_history("2")
        assert len(username_history) == 2
        assert username_history[0][0] == "bob"
        assert username_history[1][0] == "bob_new"

        # Find missing accounts
        missing = find_missing_accounts(snapshot1, snapshot2)
        assert len(missing) == 2  # charlie and dave

        # Add to verification queue
        verification_dao = VerificationDAO(conn)
        queue = VerificationQueue(verification_dao)

        for account in missing:
            queue.add_missing_account(
                account,
                snapshot1.timestamp,
                snapshot2.timestamp,
            )

        # Verify queue has pending items
        pending = queue.get_pending()
        assert len(pending) == 2

        # Mark one as blocked
        charlie_queue_item = next(
            (qid, acc) for qid, acc in pending if acc.account.username == "charlie"
        )
        queue.mark_blocked(charlie_queue_item[0], "They blocked me")

        # Mark one as unfollowed
        dave_queue_item = next(
            (qid, acc) for qid, acc in pending if acc.account.username == "dave"
        )
        queue.mark_unfollowed(dave_queue_item[0], "I unfollowed")

        # Verify queue is now empty
        pending_after = queue.get_pending()
        assert len(pending_after) == 0

        # Compute views for latest snapshot
        views = compute_views(snapshot2)

        # alice and eve are mutual (in both followers and following)
        assert len(views.mutuals) == 2
        assert any(acc.pk == "1" for acc in views.mutuals)
        assert any(acc.pk == "5" for acc in views.mutuals)

        # bob: follower but not following (changed username)
        assert len(views.not_following_back) == 1
        assert any(acc.pk == "2" for acc in views.not_following_back)

        # List all snapshots
        snapshots = dao.get_snapshots()
        assert len(snapshots) == 2
        assert snapshots[0][0] == 2  # Most recent first
        assert snapshots[1][0] == 1

        conn.close()


def test_empty_to_populated():
    """Test going from empty snapshot to populated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        initialize_database(str(db_path))
        conn = get_connection(str(db_path))
        dao = SnapshotDAO(conn)

        # Start with empty
        snapshot1 = Snapshot(
            timestamp=datetime(2024, 1, 1),
            followers=set(),
            following=set(),
        )

        dao.save_snapshot(snapshot1)

        # Add people
        snapshot2 = Snapshot(
            timestamp=datetime(2024, 1, 8),
            followers={
                AccountIdentity(pk="1", username="alice"),
                AccountIdentity(pk="2", username="bob"),
            },
            following={
                AccountIdentity(pk="1", username="alice"),
            },
        )

        dao.save_snapshot(snapshot2)

        diff = compute_diff(snapshot1, snapshot2)

        assert len(diff.new_followers) == 2
        assert len(diff.unfollowers) == 0
        assert len(diff.new_following) == 1
        assert len(diff.unfollowing) == 0

        conn.close()


def test_multiple_snapshots_timeline():
    """Test tracking changes across multiple snapshots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        initialize_database(str(db_path))
        conn = get_connection(str(db_path))
        dao = SnapshotDAO(conn)

        # Week 1
        snapshot1 = Snapshot(
            timestamp=datetime(2024, 1, 1),
            followers={AccountIdentity(pk="1", username="alice")},
            following=set(),
        )
        dao.save_snapshot(snapshot1)

        # Week 2
        snapshot2 = Snapshot(
            timestamp=datetime(2024, 1, 8),
            followers={
                AccountIdentity(pk="1", username="alice"),
                AccountIdentity(pk="2", username="bob"),
            },
            following=set(),
        )
        dao.save_snapshot(snapshot2)

        # Week 3
        snapshot3 = Snapshot(
            timestamp=datetime(2024, 1, 15),
            followers={
                AccountIdentity(pk="1", username="alice"),
                AccountIdentity(pk="2", username="bob"),
                AccountIdentity(pk="3", username="charlie"),
            },
            following={AccountIdentity(pk="2", username="bob")},
        )
        dao.save_snapshot(snapshot3)

        # Diff between week 1 and week 3
        diff_1_3 = compute_diff(snapshot1, snapshot3)
        assert len(diff_1_3.new_followers) == 2
        assert len(diff_1_3.new_following) == 1

        # Diff between week 2 and week 3
        diff_2_3 = compute_diff(snapshot2, snapshot3)
        assert len(diff_2_3.new_followers) == 1
        assert len(diff_2_3.new_following) == 1

        conn.close()
