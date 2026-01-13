"""Command-line interface for Instagram audit."""
import sys
from pathlib import Path

try:
    import click
except ImportError:
    print("Error: click is required. Install with: pip install click")
    sys.exit(1)

from instagram_audit.collectors import ExportIngestCollector, INSTALOADER_AVAILABLE
from instagram_audit.storage import initialize_database, get_connection, SnapshotDAO, VerificationDAO
from instagram_audit.diff import compute_diff, compute_views, find_missing_accounts
from instagram_audit.report import (
    format_diff_detailed,
    format_views_detailed,
    generate_diff_html,
    generate_views_html,
)
from instagram_audit.verify import VerificationQueue


@click.group()
@click.option(
    "--db",
    default="instagram_audit.db",
    help="Path to SQLite database",
    show_default=True,
)
@click.pass_context
def cli(ctx: click.Context, db: str) -> None:
    """Instagram relationship tracker - local-first audit tool."""
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = db

    # Initialize database if needed
    initialize_database(db)


@cli.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to Instagram export directory or JSON file",
)
@click.option(
    "--html/--no-html",
    default=True,
    help="Generate HTML report",
    show_default=True,
)
@click.pass_context
def run(ctx: click.Context, input_path: Path, html: bool) -> None:
    """Create a new snapshot from Instagram export data."""
    db_path = ctx.obj["db_path"]

    click.echo(f"Loading Instagram export from: {input_path}")

    try:
        collector = ExportIngestCollector(input_path)
        snapshot = collector.collect()
    except Exception as e:
        click.echo(f"Error loading export: {e}", err=True)
        sys.exit(1)

    click.echo(f"Snapshot timestamp: {snapshot.timestamp}")
    click.echo(f"Followers: {snapshot.follower_count()}")
    click.echo(f"Following: {snapshot.following_count()}")
    click.echo()

    # Save snapshot
    conn = get_connection(db_path)
    dao = SnapshotDAO(conn)
    snapshot_id = dao.save_snapshot(snapshot)

    click.echo(f"Snapshot saved with ID: {snapshot_id}")

    # Check for previous snapshot and compute diff
    snapshots = dao.get_snapshots(limit=2)
    if len(snapshots) >= 2:
        click.echo("\nComputing diff from previous snapshot...")

        old_snapshot = dao.get_snapshot_by_id(snapshots[1][0])
        if old_snapshot:
            diff = compute_diff(old_snapshot, snapshot)

            click.echo("\n" + "=" * 60)
            click.echo("CHANGES SINCE LAST SNAPSHOT")
            click.echo("=" * 60)
            click.echo(f"New followers:    {len(diff.new_followers)}")
            click.echo(f"Unfollowers:      {len(diff.unfollowers)}")
            click.echo(f"New following:    {len(diff.new_following)}")
            click.echo(f"Unfollowing:      {len(diff.unfollowing)}")
            click.echo(f"Username changes: {len(diff.username_changes)}")

            # Check for missing accounts
            missing = find_missing_accounts(old_snapshot, snapshot)
            if missing:
                click.echo(f"\n{len(missing)} accounts are missing (may be blocked, deactivated, or renamed)")
                click.echo("Run 'audit verify' to classify them.")

                # Add to verification queue
                verification_dao = VerificationDAO(conn)
                queue = VerificationQueue(verification_dao)

                for account in missing:
                    queue.add_missing_account(
                        account,
                        old_snapshot.timestamp,
                        snapshot.timestamp,
                    )

            if html:
                report_path = generate_diff_html(diff)
                click.echo(f"\nHTML report: {report_path.absolute()}")

    conn.close()
    click.echo("\nDone!")


@cli.command()
@click.option(
    "--latest/--no-latest",
    default=True,
    help="Compare the two most recent snapshots",
    show_default=True,
)
@click.option(
    "--old-id",
    type=int,
    help="ID of old snapshot (if not using --latest)",
)
@click.option(
    "--new-id",
    type=int,
    help="ID of new snapshot (if not using --latest)",
)
@click.option(
    "--html/--no-html",
    default=True,
    help="Generate HTML report",
    show_default=True,
)
@click.pass_context
def diff(
    ctx: click.Context,
    latest: bool,
    old_id: int | None,
    new_id: int | None,
    html: bool,
) -> None:
    """Show differences between two snapshots."""
    db_path = ctx.obj["db_path"]
    conn = get_connection(db_path)
    dao = SnapshotDAO(conn)

    if latest:
        snapshots = dao.get_snapshots(limit=2)
        if len(snapshots) < 2:
            click.echo("Error: Need at least 2 snapshots to compute diff", err=True)
            sys.exit(1)

        new_snapshot = dao.get_snapshot_by_id(snapshots[0][0])
        old_snapshot = dao.get_snapshot_by_id(snapshots[1][0])
    else:
        if old_id is None or new_id is None:
            click.echo("Error: Must specify both --old-id and --new-id", err=True)
            sys.exit(1)

        old_snapshot = dao.get_snapshot_by_id(old_id)
        new_snapshot = dao.get_snapshot_by_id(new_id)

    if not old_snapshot or not new_snapshot:
        click.echo("Error: Could not load snapshots", err=True)
        sys.exit(1)

    diff_result = compute_diff(old_snapshot, new_snapshot)

    # Print detailed CLI report
    click.echo(format_diff_detailed(diff_result))

    if html:
        report_path = generate_diff_html(diff_result)
        click.echo(f"\nHTML report: {report_path.absolute()}")

    conn.close()


@cli.command()
@click.option(
    "--snapshot-id",
    type=int,
    help="ID of snapshot to view (default: latest)",
)
@click.option(
    "--html/--no-html",
    default=True,
    help="Generate HTML report",
    show_default=True,
)
@click.pass_context
def views(ctx: click.Context, snapshot_id: int | None, html: bool) -> None:
    """Show relationship views for a snapshot."""
    db_path = ctx.obj["db_path"]
    conn = get_connection(db_path)
    dao = SnapshotDAO(conn)

    if snapshot_id:
        snapshot = dao.get_snapshot_by_id(snapshot_id)
    else:
        snapshot = dao.get_latest_snapshot()

    if not snapshot:
        click.echo("Error: No snapshot found", err=True)
        sys.exit(1)

    relationship_views = compute_views(snapshot)

    # Print detailed CLI report
    click.echo(format_views_detailed(relationship_views))

    if html:
        report_path = generate_views_html(relationship_views)
        click.echo(f"\nHTML report: {report_path.absolute()}")

    conn.close()


@cli.command()
@click.pass_context
def verify(ctx: click.Context) -> None:
    """Interactively verify missing accounts."""
    db_path = ctx.obj["db_path"]
    conn = get_connection(db_path)
    verification_dao = VerificationDAO(conn)
    queue = VerificationQueue(verification_dao)

    queue.process_interactively()

    conn.close()


@cli.command()
@click.option(
    "--limit",
    default=10,
    help="Number of snapshots to show",
    show_default=True,
)
@click.pass_context
def list(ctx: click.Context, limit: int) -> None:
    """List all snapshots."""
    db_path = ctx.obj["db_path"]
    conn = get_connection(db_path)
    dao = SnapshotDAO(conn)

    snapshots = dao.get_snapshots(limit=limit)

    if not snapshots:
        click.echo("No snapshots found.")
        return

    click.echo(f"\n{'ID':<6} {'Timestamp':<20} {'Source':<12} {'Followers':<10} {'Following':<10}")
    click.echo("-" * 70)

    for snapshot_id, timestamp, source in snapshots:
        snapshot = dao.get_snapshot_by_id(snapshot_id)
        if snapshot:
            click.echo(
                f"{snapshot_id:<6} "
                f"{timestamp.strftime('%Y-%m-%d %H:%M:%S'):<20} "
                f"{source:<12} "
                f"{snapshot.follower_count():<10} "
                f"{snapshot.following_count():<10}"
            )

    conn.close()


# Instaloader-based commands (live data collection)
@cli.group()
def live() -> None:
    """Live data collection using Instaloader."""
    if not INSTALOADER_AVAILABLE:
        click.echo(
            "Error: Instaloader is not installed. Install with: pip install instagram-audit[instaloader]",
            err=True,
        )
        sys.exit(1)


@live.command(name="login")
@click.option(
    "--username",
    "-u",
    required=True,
    help="Instagram username to login with",
)
@click.option(
    "--session-file",
    "-s",
    type=click.Path(path_type=Path),
    default=Path.home() / ".instagram_audit_session",
    help="Path to save session file",
    show_default=True,
)
def live_login(username: str, session_file: Path) -> None:
    """Login to Instagram and save session for future use."""
    if not INSTALOADER_AVAILABLE:
        click.echo(
            "Error: Instaloader is not installed. Install with: pip install instagram-audit[instaloader]",
            err=True,
        )
        sys.exit(1)

    from instagram_audit.collectors import InstaLoaderCollector
    import getpass

    password = getpass.getpass(f"Password for {username}: ")

    click.echo(f"Logging in as {username}...")

    try:
        collector = InstaLoaderCollector(
            target_username=username,
            session_file=session_file,
            login_username=username,
            login_password=password,
        )
        collector._login()
        click.echo(f"Login successful! Session saved to: {session_file}")
    except Exception as e:
        click.echo(f"Login failed: {e}", err=True)
        sys.exit(1)


@live.command(name="profile")
@click.argument("username")
def live_profile(username: str) -> None:
    """Show profile information for a public Instagram account."""
    if not INSTALOADER_AVAILABLE:
        click.echo(
            "Error: Instaloader is not installed. Install with: pip install instagram-audit[instaloader]",
            err=True,
        )
        sys.exit(1)

    from instagram_audit.collectors import InstaLoaderCollector

    click.echo(f"Fetching profile info for @{username}...")

    try:
        collector = InstaLoaderCollector(target_username=username)
        info = collector.collect_profile_info()

        click.echo()
        click.echo(f"Username:   @{info['username']}")
        click.echo(f"User ID:    {info['user_id']}")
        click.echo(f"Full Name:  {info['full_name'] or '(not set)'}")
        click.echo(f"Bio:        {info['biography'][:100] + '...' if len(info['biography'] or '') > 100 else info['biography'] or '(not set)'}")
        click.echo(f"Followers:  {info['follower_count']:,}")
        click.echo(f"Following:  {info['following_count']:,}")
        click.echo(f"Posts:      {info['post_count']:,}")
        click.echo(f"Private:    {'Yes' if info['is_private'] else 'No'}")
        click.echo(f"Verified:   {'Yes' if info['is_verified'] else 'No'}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@live.command(name="collect")
@click.option(
    "--username",
    "-u",
    required=True,
    help="Your Instagram username",
)
@click.option(
    "--session-file",
    "-s",
    type=click.Path(path_type=Path),
    default=Path.home() / ".instagram_audit_session",
    help="Path to session file",
    show_default=True,
)
@click.option(
    "--html/--no-html",
    default=True,
    help="Generate HTML report",
    show_default=True,
)
@click.pass_context
def live_collect(ctx: click.Context, username: str, session_file: Path, html: bool) -> None:
    """Collect live followers/following data (requires login).

    This collects your current followers and following list directly from Instagram.
    You must be logged in first using 'audit live login'.
    """
    if not INSTALOADER_AVAILABLE:
        click.echo(
            "Error: Instaloader is not installed. Install with: pip install instagram-audit[instaloader]",
            err=True,
        )
        sys.exit(1)

    if not session_file.exists():
        click.echo(
            f"Error: No session file found at {session_file}. Please login first with: audit live login -u {username}",
            err=True,
        )
        sys.exit(1)

    from instagram_audit.collectors import InstaLoaderCollector

    db_path = ctx.obj["db_path"]

    click.echo(f"Collecting live data for @{username}...")
    click.echo("This may take a while depending on your follower/following count.")
    click.echo()

    try:
        collector = InstaLoaderCollector(
            target_username=username,
            session_file=session_file,
            login_username=username,
        )
        snapshot = collector.collect()
    except Exception as e:
        click.echo(f"Error collecting data: {e}", err=True)
        sys.exit(1)

    click.echo(f"Snapshot timestamp: {snapshot.timestamp}")
    click.echo(f"Followers: {snapshot.follower_count()}")
    click.echo(f"Following: {snapshot.following_count()}")
    click.echo()

    # Save snapshot
    conn = get_connection(db_path)
    dao = SnapshotDAO(conn)
    snapshot_id = dao.save_snapshot(snapshot)

    click.echo(f"Snapshot saved with ID: {snapshot_id}")

    # Check for previous snapshot and compute diff
    snapshots = dao.get_snapshots(limit=2)
    if len(snapshots) >= 2:
        click.echo("\nComputing diff from previous snapshot...")

        old_snapshot = dao.get_snapshot_by_id(snapshots[1][0])
        if old_snapshot:
            diff = compute_diff(old_snapshot, snapshot)

            click.echo("\n" + "=" * 60)
            click.echo("CHANGES SINCE LAST SNAPSHOT")
            click.echo("=" * 60)
            click.echo(f"New followers:    {len(diff.new_followers)}")
            click.echo(f"Unfollowers:      {len(diff.unfollowers)}")
            click.echo(f"New following:    {len(diff.new_following)}")
            click.echo(f"Unfollowing:      {len(diff.unfollowing)}")
            click.echo(f"Username changes: {len(diff.username_changes)}")

            # Check for missing accounts
            missing = find_missing_accounts(old_snapshot, snapshot)
            if missing:
                click.echo(f"\n{len(missing)} accounts are missing (may be blocked, deactivated, or renamed)")
                click.echo("Run 'audit verify' to classify them.")

                # Add to verification queue
                verification_dao = VerificationDAO(conn)
                queue = VerificationQueue(verification_dao)

                for account in missing:
                    queue.add_missing_account(
                        account,
                        old_snapshot.timestamp,
                        snapshot.timestamp,
                    )

            if html:
                report_path = generate_diff_html(diff)
                click.echo(f"\nHTML report: {report_path.absolute()}")

    conn.close()
    click.echo("\nDone!")


if __name__ == "__main__":
    cli(obj={})
