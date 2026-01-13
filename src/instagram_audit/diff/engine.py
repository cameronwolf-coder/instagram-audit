"""Diff engine for computing changes between snapshots."""
from instagram_audit.core import Snapshot, DiffResult, RelationshipViews, AccountIdentity


def compute_diff(old_snapshot: Snapshot, new_snapshot: Snapshot) -> DiffResult:
    """Compute differences between two snapshots.

    This is deterministic and based purely on set operations.
    Username changes are detected by comparing accounts with same pk.
    """
    # Map accounts by pk for both snapshots
    old_followers_by_pk = {acc.pk: acc for acc in old_snapshot.followers}
    new_followers_by_pk = {acc.pk: acc for acc in new_snapshot.followers}
    old_following_by_pk = {acc.pk: acc for acc in old_snapshot.following}
    new_following_by_pk = {acc.pk: acc for acc in new_snapshot.following}

    # Compute follower changes
    old_follower_pks = set(old_followers_by_pk.keys())
    new_follower_pks = set(new_followers_by_pk.keys())

    new_follower_pks_set = new_follower_pks - old_follower_pks
    unfollower_pks_set = old_follower_pks - new_follower_pks

    new_followers = {new_followers_by_pk[pk] for pk in new_follower_pks_set}
    unfollowers = {old_followers_by_pk[pk] for pk in unfollower_pks_set}

    # Compute following changes
    old_following_pks = set(old_following_by_pk.keys())
    new_following_pks = set(new_following_by_pk.keys())

    new_following_pks_set = new_following_pks - old_following_pks
    unfollowing_pks_set = old_following_pks - new_following_pks

    new_following = {new_following_by_pk[pk] for pk in new_following_pks_set}
    unfollowing = {old_following_by_pk[pk] for pk in unfollowing_pks_set}

    # Detect username changes (same pk, different username)
    username_changes = {}
    all_pks = old_follower_pks | new_follower_pks | old_following_pks | new_following_pks

    for pk in all_pks:
        old_username = None
        new_username = None

        # Check followers
        if pk in old_followers_by_pk:
            old_username = old_followers_by_pk[pk].username
        if pk in new_followers_by_pk:
            new_username = new_followers_by_pk[pk].username

        # Check following if not found in followers
        if old_username is None and pk in old_following_by_pk:
            old_username = old_following_by_pk[pk].username
        if new_username is None and pk in new_following_by_pk:
            new_username = new_following_by_pk[pk].username

        # If both usernames exist and are different, record change
        if old_username and new_username and old_username != new_username:
            username_changes[pk] = (old_username, new_username)

    # Compute derived views (based on new snapshot)
    mutuals = new_snapshot.followers & new_snapshot.following
    not_following_back = new_snapshot.followers - new_snapshot.following
    not_followed_back = new_snapshot.following - new_snapshot.followers

    return DiffResult(
        old_snapshot=old_snapshot,
        new_snapshot=new_snapshot,
        new_followers=new_followers,
        unfollowers=unfollowers,
        new_following=new_following,
        unfollowing=unfollowing,
        username_changes=username_changes,
        mutuals=mutuals,
        not_following_back=not_following_back,
        not_followed_back=not_followed_back,
    )


def compute_views(snapshot: Snapshot) -> RelationshipViews:
    """Compute relationship views for a single snapshot."""
    mutuals = snapshot.followers & snapshot.following
    not_following_back = snapshot.followers - snapshot.following
    not_followed_back = snapshot.following - snapshot.followers

    return RelationshipViews(
        snapshot=snapshot,
        mutuals=mutuals,
        not_following_back=not_following_back,
        not_followed_back=not_followed_back,
    )


def find_missing_accounts(
    old_snapshot: Snapshot, new_snapshot: Snapshot
) -> set[AccountIdentity]:
    """Find accounts that existed in old snapshot but are missing in new.

    These accounts need verification (blocked, deactivated, renamed, etc.)
    """
    old_pks = {acc.pk for acc in old_snapshot.followers | old_snapshot.following}
    new_pks = {acc.pk for acc in new_snapshot.followers | new_snapshot.following}

    missing_pks = old_pks - new_pks

    # Get the account objects from old snapshot
    old_accounts_by_pk = {
        acc.pk: acc for acc in old_snapshot.followers | old_snapshot.following
    }

    return {old_accounts_by_pk[pk] for pk in missing_pks}


def format_diff_summary(diff: DiffResult) -> str:
    """Format diff result as a human-readable summary."""
    lines = []
    lines.append(f"Snapshot Comparison")
    lines.append(f"  Old: {diff.old_snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  New: {diff.new_snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("Follower Changes:")
    lines.append(f"  New followers: {len(diff.new_followers)}")
    lines.append(f"  Unfollowers: {len(diff.unfollowers)}")
    lines.append("")

    lines.append("Following Changes:")
    lines.append(f"  New following: {len(diff.new_following)}")
    lines.append(f"  Unfollowing: {len(diff.unfollowing)}")
    lines.append("")

    if diff.username_changes:
        lines.append(f"Username Changes: {len(diff.username_changes)}")
        for pk, (old_username, new_username) in diff.username_changes.items():
            lines.append(f"  {old_username} -> {new_username}")
        lines.append("")

    lines.append("Current Relationships:")
    lines.append(f"  Mutuals: {len(diff.mutuals)}")
    lines.append(f"  Not following back: {len(diff.not_following_back)}")
    lines.append(f"  Not followed back: {len(diff.not_followed_back)}")

    return "\n".join(lines)


def format_views_summary(views: RelationshipViews) -> str:
    """Format relationship views as a human-readable summary."""
    lines = []
    lines.append(f"Relationship Views")
    lines.append(f"  Snapshot: {views.snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append(f"Followers: {views.snapshot.follower_count()}")
    lines.append(f"Following: {views.snapshot.following_count()}")
    lines.append("")

    lines.append(f"Mutuals: {len(views.mutuals)}")
    lines.append(f"Not following back: {len(views.not_following_back)}")
    lines.append(f"Not followed back: {len(views.not_followed_back)}")

    return "\n".join(lines)
