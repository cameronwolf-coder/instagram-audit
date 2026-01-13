"""Collector for Instagram data export files."""
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from instagram_audit.core import AccountIdentity, Snapshot
from .base import Collector


class ExportIngestCollector(Collector):
    """Collects data from Instagram "Download Your Information" exports.

    Instagram provides JSON files in the export:
    - followers_1.json (or followers.json)
    - following.json (or following_1.json)

    Each contains a list of relationship entries with:
    - string_list_data: list of dicts with href, value, timestamp
    """

    def __init__(self, export_path: Path):
        """Initialize with path to Instagram export directory or JSON file.

        Args:
            export_path: Path to either:
                - The root export directory (will search for followers/following files)
                - A specific followers JSON file (will infer following file location)
        """
        self.export_path = Path(export_path)

        if self.export_path.is_dir():
            self.followers_file = self._find_file(self.export_path, "followers")
            self.following_file = self._find_file(self.export_path, "following")
        elif self.export_path.is_file():
            # Assume it's a followers file, infer following
            if "followers" in self.export_path.name:
                self.followers_file = self.export_path
                parent = self.export_path.parent
                self.following_file = self._find_file(parent, "following")
            elif "following" in self.export_path.name:
                self.following_file = self.export_path
                parent = self.export_path.parent
                self.followers_file = self._find_file(parent, "followers")
            else:
                raise ValueError(f"Cannot determine file type from: {self.export_path}")
        else:
            raise ValueError(f"Invalid path: {self.export_path}")

        if not self.followers_file or not self.followers_file.exists():
            raise FileNotFoundError(f"Followers file not found in {self.export_path}")
        if not self.following_file or not self.following_file.exists():
            raise FileNotFoundError(f"Following file not found in {self.export_path}")

    def _find_file(self, directory: Path, file_type: str) -> Path | None:
        """Find followers or following JSON file in directory."""
        # Common patterns
        patterns = [
            f"{file_type}.json",
            f"{file_type}_1.json",
            f"*{file_type}*.json",
        ]

        for pattern in patterns:
            matches = list(directory.glob(pattern))
            if matches:
                return matches[0]

        # Search in common subdirectories (including nested paths)
        subdirs = [
            "followers_and_following",
            "connections",
            "connections/followers_and_following",
        ]

        for subdir in subdirs:
            subpath = directory / subdir
            if subpath.exists():
                for pattern in patterns:
                    matches = list(subpath.glob(pattern))
                    if matches:
                        return matches[0]

        return None

    def collect(self) -> Snapshot:
        """Collect snapshot from export files."""
        followers, followers_ts = self._parse_file(self.followers_file)
        following, following_ts = self._parse_file(self.following_file)

        # Use the most recent timestamp from either file
        all_timestamps = followers_ts + following_ts
        if all_timestamps:
            timestamp = datetime.fromtimestamp(max(all_timestamps))
        else:
            # Fallback to file modification time
            timestamp = datetime.fromtimestamp(self.followers_file.stat().st_mtime)

        return Snapshot(
            timestamp=timestamp,
            followers=followers,
            following=following,
            source="export",
        )

    def _load_raw_data(self, file_path: Path) -> list[dict[str, Any]]:
        """Load raw JSON data from file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle different export formats
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Sometimes wrapped in a key like "relationships_followers"
            for key in data:
                if isinstance(data[key], list):
                    return data[key]
            return [data]
        else:
            raise ValueError(f"Unexpected JSON format in {file_path}")

    def _parse_file(self, file_path: Path) -> tuple[set[AccountIdentity], list[int]]:
        """Parse Instagram export JSON file into AccountIdentity set and timestamps."""
        accounts = set()
        timestamps = []
        data = self._load_raw_data(file_path)

        for entry in data:
            # Instagram export format:
            # {
            #   "string_list_data": [
            #     {
            #       "href": "https://www.instagram.com/username",
            #       "value": "username",
            #       "timestamp": 1234567890
            #     }
            #   ]
            # }
            # OR (newer format):
            # {
            #   "title": "",
            #   "media_list_data": [],
            #   "string_list_data": [...]
            # }

            if "string_list_data" not in entry:
                continue

            for item in entry["string_list_data"]:
                username = item.get("value")
                href = item.get("href", "")
                ts = item.get("timestamp")

                if ts:
                    timestamps.append(ts)

                if not username:
                    continue

                # Extract pk from href if available
                # Format: https://www.instagram.com/username or https://instagram.com/username
                pk = self._extract_pk_from_href(href, username)

                accounts.add(
                    AccountIdentity(
                        pk=pk,
                        username=username,
                        full_name=None,  # Not available in export
                    )
                )

        return accounts, timestamps

    def _extract_pk_from_href(self, href: str, username: str) -> str:
        """Extract pk from href or use username as fallback.

        Note: Instagram export doesn't include numeric PKs in the standard format.
        We use username as the stable identifier for export-based tracking.
        This means username changes won't be detected from exports alone.
        """
        # For exports, we use username as pk since numeric pk isn't provided
        # This is a limitation of the export format
        return f"username:{username}"
