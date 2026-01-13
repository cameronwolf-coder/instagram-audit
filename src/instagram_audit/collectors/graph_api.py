"""Collector for Instagram Graph API (Creator/Business accounts only)."""
from datetime import datetime
from typing import Optional

from instagram_audit.core import AccountIdentity, Snapshot
from .base import Collector


class GraphApiCollector(Collector):
    """Collects data from Instagram Graph API.

    This requires:
    - A Creator or Business Instagram account
    - A Facebook Page connected to the Instagram account
    - An access token with appropriate permissions

    Note: The Graph API has limited follower data access.
    It provides follower_count but not individual follower lists.
    This collector is primarily useful for:
    - Getting accurate follower counts
    - Accessing insights/metrics
    - Tracking follower count over time

    For full follower/following lists, use ExportIngestCollector.
    """

    def __init__(self, access_token: str, instagram_business_account_id: str):
        """Initialize with Graph API credentials.

        Args:
            access_token: Facebook/Instagram Graph API access token
            instagram_business_account_id: The Instagram Business Account ID
        """
        self.access_token = access_token
        self.account_id = instagram_business_account_id

    def collect(self) -> Snapshot:
        """Collect snapshot from Graph API.

        Note: This returns an empty snapshot with metadata only.
        Individual follower/following lists are not available via Graph API.
        """
        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests library required for Graph API. "
                "Install with: pip install 'instagram-audit[graph-api]'"
            )

        # Get account info
        url = f"https://graph.facebook.com/v18.0/{self.account_id}"
        params = {
            "fields": "followers_count,follows_count,username",
            "access_token": self.access_token,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Graph API doesn't provide individual follower lists
        # Only follower counts are available
        # This is a platform limitation for privacy reasons

        return Snapshot(
            timestamp=datetime.now(),
            followers=set(),  # Not available
            following=set(),  # Not available
            source="graph_api",
        )

    def get_follower_count(self) -> int:
        """Get current follower count."""
        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests library required for Graph API. "
                "Install with: pip install 'instagram-audit[graph-api]'"
            )

        url = f"https://graph.facebook.com/v18.0/{self.account_id}"
        params = {
            "fields": "followers_count",
            "access_token": self.access_token,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return data.get("followers_count", 0)

    def get_insights(self, metric: str, period: str = "day") -> dict:
        """Get insights for a metric.

        Args:
            metric: Metric name (e.g., 'follower_count', 'impressions', 'reach')
            period: Time period ('day', 'week', 'days_28')

        Returns:
            Dict with insights data
        """
        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests library required for Graph API. "
                "Install with: pip install 'instagram-audit[graph-api]'"
            )

        url = f"https://graph.facebook.com/v18.0/{self.account_id}/insights"
        params = {
            "metric": metric,
            "period": period,
            "access_token": self.access_token,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
