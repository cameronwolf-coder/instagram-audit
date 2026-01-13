# Instagram Audit

A **local-first** Instagram relationship tracker that helps you understand your follower/following dynamics over time.

## Features

- 📊 **Track followers and following** - Snapshot your relationships over time
- 🔍 **Compute diffs** - See who followed/unfollowed you between snapshots
- 📈 **Derived views** - Mutuals, not-following-back, not-followed-back
- 🏷️ **Username tracking** - Detect when accounts change their username
- ✅ **Verification queue** - Classify missing accounts (blocked, deactivated, renamed, etc.)
- 📱 **Safe data collection** - Uses official Instagram data exports (lowest ban risk)
- 💾 **Local SQLite storage** - Your data stays on your machine
- 📄 **Beautiful HTML reports** - Professional-looking relationship reports

## Non-Goals

- ❌ No automation that could trigger rate limits
- ❌ No password storage or authentication
- ❌ No techniques to evade platform protections

## Installation

```bash
cd instagram-audit
pip install -e .
```

For development with tests:

```bash
pip install -e ".[dev]"
```

For Graph API support (Creator/Business accounts):

```bash
pip install -e ".[graph-api]"
```

## Quick Start

### 1. Download Your Instagram Data

1. Go to Instagram Settings → Security → Download Your Information
2. Select JSON format
3. Download the export
4. Unzip the export folder

### 2. Create Your First Snapshot

```bash
audit run --input /path/to/instagram-export
```

This will:
- Parse your followers and following from the export
- Save a snapshot to the local database
- Show you a summary of your relationships

### 3. Run Weekly to Track Changes

Wait a week, download a new export, then:

```bash
audit run --input /path/to/new-export
```

This will:
- Create a new snapshot
- Automatically compute the diff from your previous snapshot
- Show you who followed/unfollowed you
- Generate an HTML report in `./reports/`

## Usage

### Commands

#### `audit run`

Create a new snapshot from an Instagram export:

```bash
audit run --input /path/to/export
```

Options:
- `--input`, `-i`: Path to Instagram export directory or JSON file (required)
- `--html/--no-html`: Generate HTML report (default: true)
- `--db`: Path to SQLite database (default: `instagram_audit.db`)

#### `audit diff`

Compare two snapshots:

```bash
# Compare the two most recent snapshots
audit diff --latest

# Compare specific snapshots
audit diff --old-id 1 --new-id 2
```

Options:
- `--latest/--no-latest`: Compare two most recent snapshots (default: true)
- `--old-id`: ID of old snapshot (if not using --latest)
- `--new-id`: ID of new snapshot (if not using --latest)
- `--html/--no-html`: Generate HTML report (default: true)

#### `audit views`

Show relationship views for a snapshot:

```bash
# View latest snapshot
audit views

# View specific snapshot
audit views --snapshot-id 1
```

Options:
- `--snapshot-id`: ID of snapshot to view (default: latest)
- `--html/--no-html`: Generate HTML report (default: true)

#### `audit verify`

Interactively verify missing accounts:

```bash
audit verify
```

This helps you classify accounts that disappeared between snapshots:
- **Blocked** - Account blocked you
- **Deactivated** - Account was deleted or deactivated
- **Renamed** - Account changed username
- **Unfollowed** - You unfollowed them
- **Unknown** - Unclear what happened

#### `audit list`

List all snapshots:

```bash
audit list --limit 10
```

## Architecture

### Modules

```
instagram_audit/
├── core/           # Core data types (AccountIdentity, Snapshot, etc.)
├── collectors/     # Data collection interfaces
│   ├── base.py             # Collector interface
│   ├── export_ingest.py    # Instagram export parser
│   └── graph_api.py        # Graph API client (optional)
├── storage/        # SQLite storage layer
│   ├── schema.py   # Database schema
│   └── dao.py      # Data access objects
├── diff/           # Diff computation engine
├── verify/         # Verification queue
└── report/         # Report generation (CLI + HTML)
```

### Key Concepts

#### AccountIdentity

Accounts are identified by their `pk` (Instagram's internal user ID), which is stable even when usernames change. For export-based tracking, we use `username:` prefixed identifiers since numeric PKs aren't provided in exports.

#### Snapshot

A point-in-time capture of your followers and following lists.

#### Diff

Computed differences between two snapshots:
- New followers
- Unfollowers
- New following
- Unfollowing
- Username changes

#### Verification Queue

When accounts disappear between snapshots, they're added to a verification queue where you can classify them manually.

## Data Collection Methods

### 1. Export Ingest (Primary, Recommended)

**Pros:**
- ✅ Lowest ban risk (uses official export feature)
- ✅ Complete follower/following lists
- ✅ No authentication needed
- ✅ Works for all account types

**Cons:**
- ⚠️ Manual process (request → wait → download)
- ⚠️ Username changes can't be detected from exports alone
- ⚠️ Typically takes 24-48 hours to receive export

**Usage:**
```bash
audit run --input /path/to/instagram-export
```

### 2. Graph API (Optional, Limited)

**Pros:**
- ✅ Real-time data
- ✅ Access to insights and metrics
- ✅ Follower count tracking

**Cons:**
- ⚠️ Only for Creator/Business accounts
- ⚠️ Requires Facebook Page connection
- ⚠️ Does NOT provide individual follower lists (platform limitation)
- ⚠️ Requires API token management

**Usage:**
```python
from instagram_audit.collectors import GraphApiCollector

collector = GraphApiCollector(
    access_token="YOUR_ACCESS_TOKEN",
    instagram_business_account_id="YOUR_IG_BUSINESS_ID"
)

# Only gets follower count, not individual followers
count = collector.get_follower_count()
```

## Example Workflow

1. **Initial Setup** (Week 0):
   ```bash
   # Download Instagram export, then:
   audit run --input ~/Downloads/instagram-export
   ```

2. **Weekly Check** (Week 1):
   ```bash
   # Download new export, then:
   audit run --input ~/Downloads/new-instagram-export
   # Automatically shows diff from Week 0
   ```

3. **Review Missing Accounts**:
   ```bash
   audit verify
   # Interactively classify missing accounts
   ```

4. **Check Current State**:
   ```bash
   audit views
   # See mutuals, not-following-back, etc.
   ```

## HTML Reports

Reports are automatically generated in `./reports/YYYY-MM-DD.html` and include:

- Summary statistics (follower/following counts)
- New followers and unfollowers
- New following and unfollowing
- Username changes
- Current relationship views (mutuals, not-following-back, etc.)

Open the HTML file in any browser for a polished, Instagram-styled report.

## Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=instagram_audit
```

## Database Schema

The tool uses SQLite with the following key tables:

- `snapshots` - Point-in-time captures
- `accounts` - Deduplicated account records
- `snapshot_followers` - Follower relationships per snapshot
- `snapshot_following` - Following relationships per snapshot
- `username_history` - Track username changes
- `verification_queue` - Missing accounts pending verification

## Privacy & Security

- ✅ **All data stays local** - No cloud uploads
- ✅ **No password storage** - Uses export files only
- ✅ **No authentication** - No login credentials needed
- ✅ **SQLite database** - Fully portable, human-readable with tools

## Limitations

1. **Export-based username detection**: Since Instagram exports don't include numeric user IDs, we can't reliably detect username changes from exports alone. We use `username:` prefixed identifiers as a workaround.

2. **Manual export process**: You need to manually request and download exports. This is by design to minimize ban risk.

3. **Graph API limitations**: Individual follower lists are not available via Graph API (platform restriction). Only follower counts and insights are accessible.

## Contributing

Contributions welcome! Areas for improvement:

- [ ] Better username change detection for export-based tracking
- [ ] Export automation (if safe methods exist)
- [ ] Additional report formats (PDF, CSV)
- [ ] Trend analysis over multiple snapshots
- [ ] Data visualization charts

## License

MIT License - see LICENSE file for details.

## Disclaimer

This tool is for personal use only. Use responsibly and in accordance with Instagram's Terms of Service. The authors are not responsible for any account issues resulting from the use of this tool.

**Recommended usage**: Stick to the official export method and avoid excessive API calls.
