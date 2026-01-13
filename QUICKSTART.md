# Quick Start Guide

Get up and running with Instagram Audit in 5 minutes.

## Installation

```bash
cd instagram-audit
pip install -e .
```

## Get Your First Snapshot

### Step 1: Request Instagram Export

1. Open Instagram app on your phone
2. Tap **☰** → **Settings** → **Security**
3. Tap **Download Your Information**
4. Select **Some of your information** → **Connections**
5. Choose **JSON** format
6. Tap **Create files**
7. Wait for email (usually 24-48 hours)

### Step 2: Download and Extract

1. Check your email for the download link
2. Download the ZIP file
3. Extract it to a folder (e.g., `~/Downloads/instagram-export`)

### Step 3: Create Snapshot

```bash
audit run --input ~/Downloads/instagram-export
```

**Output:**
```
Loading Instagram export from: /Users/you/Downloads/instagram-export
Snapshot timestamp: 2024-01-15 12:00:00
Followers: 342
Following: 298

Snapshot saved with ID: 1

Done!
```

### Step 4: View Your Relationships

```bash
audit views
```

This shows you:
- **Mutuals**: People who follow you AND you follow back
- **Not following back**: People who follow you, but you don't follow
- **Not followed back**: People you follow, but they don't follow you

### Step 5: Check the HTML Report

```bash
open reports/2024-01-15.html
```

A beautiful, Instagram-styled report opens in your browser!

## Next Steps

### Track Changes Over Time

Wait a week, then:

1. Request another Instagram export
2. Download and extract it
3. Run: `audit run --input ~/Downloads/new-export`
4. Automatically see who followed/unfollowed you!

### Compare Snapshots

```bash
# Compare the two most recent snapshots
audit diff --latest
```

### Verify Missing Accounts

If accounts disappear (blocked you, deactivated, etc.):

```bash
audit verify
```

Interactively classify what happened to each account.

### List All Snapshots

```bash
audit list
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `audit run --input <path>` | Create new snapshot from export |
| `audit views` | Show current relationships |
| `audit diff --latest` | Compare two most recent snapshots |
| `audit verify` | Classify missing accounts |
| `audit list` | List all snapshots |

## Tips

### Use a Different Database

Track multiple Instagram accounts separately:

```bash
audit --db personal.db run --input ./export-personal/
audit --db business.db run --input ./export-business/
```

### Disable HTML Reports

If you only want CLI output:

```bash
audit run --input ./export --no-html
```

### Check Specific Snapshot

```bash
audit views --snapshot-id 1
```

## Troubleshooting

### "File not found"

Make sure you're pointing to the extracted export folder, not the ZIP file.

### "No snapshots found"

You need to run `audit run` first to create a snapshot.

### No changes shown

You need at least 2 snapshots to see changes. The first run only creates a baseline.

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Check out [EXAMPLE.md](EXAMPLE.md) for a complete walkthrough
- Explore the generated HTML reports for beautiful visualizations

## Safety Notes

✅ **Safe**: This tool only reads local export files
✅ **Private**: All data stays on your computer
✅ **No login**: Never asks for your Instagram password
✅ **Low risk**: Uses official Instagram export feature

---

Questions? Check the [README.md](README.md) or open an issue!
