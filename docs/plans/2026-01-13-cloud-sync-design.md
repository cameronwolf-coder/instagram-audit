# Cloud Sync Design

## Overview

Add optional cloud sync to the Instagram Audit tool, allowing users to:
1. Push snapshots from CLI to cloud storage
2. View synced data in the web dashboard without uploading files

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   CLI (local)   │────▶│  Vercel API      │────▶│  Cloudflare KV  │
│  audit sync     │     │  /api/sync       │     │  (encrypted)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Dashboard UI    │
                        │  /sync page      │
                        └──────────────────┘
```

## Security Model

- **Passphrase-based access**: No accounts, users choose a passphrase
- **Client-side encryption**: All data encrypted before leaving client
- **Zero-knowledge server**: Server only stores encrypted blobs, cannot read data
- **Key derivation**: PBKDF2 with 100K iterations + random salt
- **Encryption**: AES-256-GCM (authenticated encryption)

## Data Model

### KV Storage Structure

```
Key: "sync:{sha256(passphrase)}"
Value: {
  encrypted_data: "base64...",
  salt: "base64...",
  iv: "base64...",
  updated_at: "ISO timestamp",
  version: 1
}
```

### Encrypted Payload

```json
{
  "snapshots": [
    {
      "id": 1,
      "timestamp": "2026-01-13T...",
      "source": "instaloader",
      "follower_count": 1234,
      "following_count": 567
    }
  ],
  "accounts": {
    "pk": { "username": "...", "full_name": "..." }
  },
  "latest_diff": {
    "new_followers": ["username1", "username2"],
    "unfollowers": ["username3"],
    "new_following": [],
    "unfollowing": []
  },
  "relationships": {
    "mutuals": ["username1"],
    "not_following_back": ["username2"],
    "not_followed_back": ["username3"]
  }
}
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sync` | POST | Upload encrypted snapshot |
| `/api/sync?hash=xxx` | GET | Download encrypted snapshot |

## CLI Commands

```bash
# Push data to cloud
audit sync push --passphrase "mysecret"

# Check sync status
audit sync status --passphrase "mysecret"
```

## Implementation Files

### CLI (Python)
- `src/instagram_audit/sync/__init__.py`
- `src/instagram_audit/sync/crypto.py` - Encryption utilities
- `src/instagram_audit/sync/client.py` - API client

### Dashboard (Next.js)
- `dashboard/app/sync/page.tsx` - Sync entry page
- `dashboard/app/api/sync/route.ts` - API route
- `dashboard/lib/crypto.ts` - Browser encryption (Web Crypto)

## Security Considerations

- Passphrase hash used for lookup (not stored)
- Rate limiting: 10 requests/min per IP
- No passphrase recovery (by design)
- HTTPS only for all API calls
