"""CLI report formatting."""
from instagram_audit.core import DiffResult, RelationshipViews, AccountIdentity


def format_account_list(
    accounts: set[AccountIdentity], title: str, show_full_name: bool = True
) -> str:
    """Format a list of accounts for CLI output."""
    lines = [f"\n{title} ({len(accounts)}):"]

    if not accounts:
        lines.append("  (none)")
        return "\n".join(lines)

    # Sort by username for consistent output
    sorted_accounts = sorted(accounts, key=lambda a: a.username.lower())

    for account in sorted_accounts:
        if show_full_name and account.full_name:
            lines.append(f"  @{account.username} ({account.full_name})")
        else:
            lines.append(f"  @{account.username}")

    return "\n".join(lines)


def format_diff_detailed(diff: DiffResult) -> str:
    """Format detailed diff report for CLI."""
    lines = []

    # Header
    lines.append("=" * 60)
    lines.append("INSTAGRAM RELATIONSHIP AUDIT - DIFF REPORT")
    lines.append("=" * 60)
    lines.append(f"Old snapshot: {diff.old_snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"New snapshot: {diff.new_snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 60)
    lines.append(f"Followers:  {diff.old_snapshot.follower_count()} -> {diff.new_snapshot.follower_count()} "
                 f"({_format_delta(diff.new_snapshot.follower_count() - diff.old_snapshot.follower_count())})")
    lines.append(f"Following:  {diff.old_snapshot.following_count()} -> {diff.new_snapshot.following_count()} "
                 f"({_format_delta(diff.new_snapshot.following_count() - diff.old_snapshot.following_count())})")
    lines.append("")

    # Changes
    lines.append("CHANGES")
    lines.append("-" * 60)
    lines.append(f"New followers:    {len(diff.new_followers)}")
    lines.append(f"Unfollowers:      {len(diff.unfollowers)}")
    lines.append(f"New following:    {len(diff.new_following)}")
    lines.append(f"Unfollowing:      {len(diff.unfollowing)}")
    lines.append(f"Username changes: {len(diff.username_changes)}")
    lines.append("")

    # Detailed lists
    if diff.new_followers:
        lines.append(format_account_list(diff.new_followers, "NEW FOLLOWERS"))
        lines.append("")

    if diff.unfollowers:
        lines.append(format_account_list(diff.unfollowers, "UNFOLLOWERS"))
        lines.append("")

    if diff.new_following:
        lines.append(format_account_list(diff.new_following, "NEW FOLLOWING"))
        lines.append("")

    if diff.unfollowing:
        lines.append(format_account_list(diff.unfollowing, "UNFOLLOWING"))
        lines.append("")

    if diff.username_changes:
        lines.append(f"\nUSERNAME CHANGES ({len(diff.username_changes)}):")
        for pk, (old_username, new_username) in sorted(
            diff.username_changes.items(), key=lambda x: x[1][0].lower()
        ):
            lines.append(f"  @{old_username} -> @{new_username}")
        lines.append("")

    # Current state
    lines.append("CURRENT RELATIONSHIPS")
    lines.append("-" * 60)
    lines.append(f"Mutuals:             {len(diff.mutuals)}")
    lines.append(f"Not following back:  {len(diff.not_following_back)}")
    lines.append(f"Not followed back:   {len(diff.not_followed_back)}")

    return "\n".join(lines)


def format_views_detailed(views: RelationshipViews) -> str:
    """Format detailed relationship views for CLI."""
    lines = []

    # Header
    lines.append("=" * 60)
    lines.append("INSTAGRAM RELATIONSHIP AUDIT - VIEWS REPORT")
    lines.append("=" * 60)
    lines.append(f"Snapshot: {views.snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 60)
    lines.append(f"Followers:  {views.snapshot.follower_count()}")
    lines.append(f"Following:  {views.snapshot.following_count()}")
    lines.append("")

    # Relationships
    lines.append("RELATIONSHIPS")
    lines.append("-" * 60)
    lines.append(f"Mutuals:             {len(views.mutuals)}")
    lines.append(f"Not following back:  {len(views.not_following_back)}")
    lines.append(f"Not followed back:   {len(views.not_followed_back)}")
    lines.append("")

    # Detailed lists
    lines.append(format_account_list(views.mutuals, "MUTUALS"))
    lines.append("")
    lines.append(format_account_list(views.not_following_back, "NOT FOLLOWING BACK"))
    lines.append("  (These people follow you, but you don't follow them)")
    lines.append("")
    lines.append(format_account_list(views.not_followed_back, "NOT FOLLOWED BACK"))
    lines.append("  (You follow these people, but they don't follow you)")

    return "\n".join(lines)


def _format_delta(value: int) -> str:
    """Format a delta value with sign."""
    if value > 0:
        return f"+{value}"
    elif value < 0:
        return str(value)
    else:
        return "0"
