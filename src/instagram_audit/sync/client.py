"""API client for cloud sync."""
import json
from datetime import datetime
from typing import Any, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from .crypto import encrypt_payload, decrypt_payload, derive_key_hash

# Default API endpoint (can be overridden)
DEFAULT_API_URL = "https://dashboard-phi-three-98.vercel.app/api/sync"


class SyncClient:
    """Client for syncing data to cloud storage."""

    def __init__(self, api_url: str = DEFAULT_API_URL):
        """Initialize the sync client.

        Args:
            api_url: Base URL for the sync API
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "requests package required. Install with: pip install requests"
            )
        self.api_url = api_url

    def push(self, data: dict[str, Any], passphrase: str) -> dict[str, Any]:
        """Push encrypted data to the cloud.

        Args:
            data: The data to sync (will be encrypted)
            passphrase: Passphrase for encryption and lookup

        Returns:
            Response from the API
        """
        # Encrypt the payload
        encrypted = encrypt_payload(data, passphrase)

        # Add metadata
        payload = {
            **encrypted,
            "hash": derive_key_hash(passphrase),
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "version": 1,
        }

        # Send to API
        response = requests.post(
            self.api_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def pull(self, passphrase: str) -> Optional[dict[str, Any]]:
        """Pull and decrypt data from the cloud.

        Args:
            passphrase: Passphrase for lookup and decryption

        Returns:
            Decrypted data, or None if not found
        """
        key_hash = derive_key_hash(passphrase)

        response = requests.get(
            self.api_url,
            params={"hash": key_hash},
            timeout=30,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        encrypted = response.json()

        # Decrypt and return
        return decrypt_payload(encrypted, passphrase)

    def status(self, passphrase: str) -> Optional[dict[str, Any]]:
        """Check sync status without downloading full data.

        Args:
            passphrase: Passphrase for lookup

        Returns:
            Status info (updated_at, version) or None if not found
        """
        key_hash = derive_key_hash(passphrase)

        response = requests.get(
            self.api_url,
            params={"hash": key_hash, "metadata_only": "true"},
            timeout=30,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()
