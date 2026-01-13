"""Collector using Instaloader for live Instagram data."""
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import instaloader
    INSTALOADER_AVAILABLE = True
except ImportError:
    INSTALOADER_AVAILABLE = False

from instagram_audit.core import AccountIdentity, Snapshot
from .base import Collector


class InstaLoaderCollector(Collector):
    """Collects live follower/following data using Instaloader.

    Instaloader is an open-source tool that can:
    - Download public profile data without login
    - Download private profile data when logged in (your own account)
    - Fetch followers/following lists

    Note: For followers/following lists, you must be logged in
    and can only access your own account's data.
    """

    def __init__(
        self,
        target_username: str,
        session_file: Optional[Path] = None,
        login_username: Optional[str] = None,
        login_password: Optional[str] = None,
    ):
        """Initialize the Instaloader collector.

        Args:
            target_username: Instagram username to collect data for
            session_file: Path to saved session file for login persistence
            login_username: Username for login (required for followers/following)
            login_password: Password for login (if not using session file)
        """
        if not INSTALOADER_AVAILABLE:
            raise ImportError(
                "Instaloader is not installed. Install with: pip install instagram-audit[instaloader]"
            )

        self.target_username = target_username
        self.session_file = session_file
        self.login_username = login_username
        self.login_password = login_password

        # Initialize Instaloader instance
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            quiet=True,
        )

    def _login(self) -> bool:
        """Attempt to login using session file or credentials.

        Returns:
            True if login successful, False otherwise
        """
        # Try loading from session file first
        if self.session_file and self.session_file.exists() and self.login_username:
            try:
                self.loader.load_session_from_file(self.login_username, str(self.session_file))
                return True
            except Exception:
                pass

        # Try login with credentials
        if self.login_username and self.login_password:
            try:
                self.loader.login(self.login_username, self.login_password)
                # Save session for future use
                if self.session_file:
                    self.loader.save_session_to_file(str(self.session_file))
                return True
            except Exception as e:
                raise RuntimeError(f"Login failed: {e}")

        return False

    def collect(self) -> Snapshot:
        """Collect followers and following data.

        Note: This requires being logged in and can only fetch data
        for the logged-in user's account.

        Returns:
            Snapshot with current followers and following
        """
        # Login is required for followers/following
        if not self._login():
            raise RuntimeError(
                "Login required to fetch followers/following. "
                "Provide session_file with login_username, or login_username with login_password."
            )

        try:
            profile = instaloader.Profile.from_username(
                self.loader.context, self.target_username
            )
        except Exception as e:
            raise RuntimeError(f"Could not load profile '{self.target_username}': {e}")

        # Collect followers
        followers = set()
        try:
            for follower in profile.get_followers():
                followers.add(
                    AccountIdentity(
                        pk=str(follower.userid),
                        username=follower.username,
                        full_name=follower.full_name,
                    )
                )
        except Exception as e:
            raise RuntimeError(f"Could not fetch followers: {e}")

        # Collect following
        following = set()
        try:
            for followee in profile.get_followees():
                following.add(
                    AccountIdentity(
                        pk=str(followee.userid),
                        username=followee.username,
                        full_name=followee.full_name,
                    )
                )
        except Exception as e:
            raise RuntimeError(f"Could not fetch following: {e}")

        return Snapshot(
            timestamp=datetime.now(),
            followers=followers,
            following=following,
            source="instaloader",
        )

    def collect_profile_info(self) -> dict:
        """Collect basic profile information (works without login for public profiles).

        Returns:
            Dictionary with profile information
        """
        try:
            profile = instaloader.Profile.from_username(
                self.loader.context, self.target_username
            )
            return {
                "username": profile.username,
                "user_id": profile.userid,
                "full_name": profile.full_name,
                "biography": profile.biography,
                "follower_count": profile.followers,
                "following_count": profile.followees,
                "post_count": profile.mediacount,
                "is_private": profile.is_private,
                "is_verified": profile.is_verified,
                "profile_pic_url": profile.profile_pic_url,
            }
        except Exception as e:
            raise RuntimeError(f"Could not load profile: {e}")
