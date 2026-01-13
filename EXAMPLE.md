# Example Usage

This guide walks through a complete example of using Instagram Audit.

## Step 1: Get Your Instagram Data Export

1. Open Instagram mobile app
2. Go to **Settings** → **Security** → **Download Your Information**
3. Select:
   - Format: **JSON**
   - Data: **Connections** (or select all)
4. Request the download
5. Wait for Instagram to email you (usually 24-48 hours)
6. Download and unzip the export

Your export will contain a structure like:

```
instagram-export/
├── connections/
│   └── followers_and_following/
│       ├── followers_1.json
│       └── following.json
└── ...
```

Or sometimes:

```
instagram-export/
├── followers.json
├── following_1.json
└── ...
```

## Step 2: Create Your First Snapshot

```bash
# Navigate to the project directory
cd instagram-audit

# Create a snapshot from your export
audit run --input ~/Downloads/instagram-export/
```

**Output:**
```
Loading Instagram export from: /Users/you/Downloads/instagram-export
Snapshot timestamp: 2024-01-01 12:00:00
Followers: 342
Following: 298

Snapshot saved with ID: 1

Done!
```

This creates:
- A snapshot in `instagram_audit.db`
- An HTML report in `./reports/2024-01-01.html`

## Step 3: View Your Current Relationships

```bash
audit views
```

**Output:**
```
============================================================
INSTAGRAM RELATIONSHIP AUDIT - VIEWS REPORT
============================================================
Snapshot: 2024-01-01 12:00:00

SUMMARY
------------------------------------------------------------
Followers:  342
Following:  298

RELATIONSHIPS
------------------------------------------------------------
Mutuals:             245
Not following back:  97
Not followed back:   53

MUTUALS (245):
  @alice
  @bob_the_builder
  @charlie_adventures
  ...

NOT FOLLOWING BACK (97):
  (These people follow you, but you don't follow them)
  @random_follower
  @another_user
  ...

NOT FOLLOWED BACK (53):
  (You follow these people, but they don't follow you)
  @celebrity_account
  @friend_who_unfollowed
  ...

HTML report: /path/to/reports/2024-01-01.html
```

## Step 4: Wait a Week and Create a Second Snapshot

A week later, request another Instagram export and download it.

```bash
audit run --input ~/Downloads/instagram-export-week2/
```

**Output:**
```
Loading Instagram export from: /Users/you/Downloads/instagram-export-week2
Snapshot timestamp: 2024-01-08 12:00:00
Followers: 345
Following: 295

Snapshot saved with ID: 2

============================================================
CHANGES SINCE LAST SNAPSHOT
============================================================
New followers:    5
Unfollowers:      2
New following:    1
Unfollowing:      4
Username changes: 1

3 accounts are missing (may be blocked, deactivated, or renamed)
Run 'audit verify' to classify them.

HTML report: /path/to/reports/2024-01-08.html

Done!
```

## Step 5: View Detailed Diff

```bash
audit diff --latest
```

**Output:**
```
============================================================
INSTAGRAM RELATIONSHIP AUDIT - DIFF REPORT
============================================================
Old snapshot: 2024-01-01 12:00:00
New snapshot: 2024-01-08 12:00:00

SUMMARY
------------------------------------------------------------
Followers:  342 -> 345 (+3)
Following:  298 -> 295 (-3)

CHANGES
------------------------------------------------------------
New followers:    5
Unfollowers:      2
New following:    1
Unfollowing:      4
Username changes: 1

NEW FOLLOWERS (5):
  @new_person1
  @new_person2
  @new_person3
  @new_person4
  @new_person5

UNFOLLOWERS (2):
  @person_who_unfollowed
  @another_unfollower

NEW FOLLOWING (1):
  @someone_i_followed

UNFOLLOWING (4):
  @account_i_unfollowed1
  @account_i_unfollowed2
  @account_i_unfollowed3
  @spam_account

USERNAME CHANGES (1):
  @old_username -> @new_username

CURRENT RELATIONSHIPS
------------------------------------------------------------
Mutuals:             247
Not following back:  98
Not followed back:   48
```

## Step 6: Verify Missing Accounts

Some accounts might have disappeared (blocked you, deactivated, etc.). Let's classify them:

```bash
audit verify
```

**Interactive Session:**
```
3 accounts need verification:

Account: @missing_person
  PK: username:missing_person
  Last seen: 2024-01-01
  First missing: 2024-01-08

What happened to this account?
  1) Blocked you
  2) Deactivated/deleted account
  3) Renamed (changed username)
  4) You unfollowed them
  5) Unknown
  s) Skip for now

Choice: 1
Notes (optional): They blocked me after our disagreement
Marked as blocked.

Account: @renamed_user
  PK: username:renamed_user
  Last seen: 2024-01-01
  First missing: 2024-01-08

What happened to this account?
  1) Blocked you
  2) Deactivated/deleted account
  3) Renamed (changed username)
  4) You unfollowed them
  5) Unknown
  s) Skip for now

Choice: 3
New username: their_new_username
Notes (optional): Found them with new name
Marked as renamed to @their_new_username.

...

Verification complete!
```

## Step 7: List All Snapshots

```bash
audit list
```

**Output:**
```
ID     Timestamp            Source       Followers  Following
----------------------------------------------------------------------
2      2024-01-08 12:00:00  export       345        295
1      2024-01-01 12:00:00  export       342        298
```

## Step 8: Compare Specific Snapshots

You can compare any two snapshots:

```bash
audit diff --old-id 1 --new-id 2
```

## HTML Reports

Open the generated HTML reports in your browser for a beautiful, Instagram-styled view:

```bash
open reports/2024-01-08.html
```

The HTML report includes:
- Summary cards with follower/following counts
- Color-coded deltas (green for gains, red for losses)
- Sortable tables of all changes
- Current relationship views
- Mobile-responsive design

## Automation (Weekly Workflow)

For regular tracking, set up a weekly routine:

1. **Sunday**: Request Instagram export
2. **Monday/Tuesday**: Download export when ready
3. **Tuesday**: Run `audit run --input <path>`
4. **Tuesday**: Review HTML report
5. **Tuesday**: Run `audit verify` if needed

## Tips

- **Keep exports organized**: Create dated folders for each export
  ```
  ~/instagram-exports/
  ├── 2024-01-01/
  ├── 2024-01-08/
  └── 2024-01-15/
  ```

- **Back up your database**: The SQLite database contains all your history
  ```bash
  cp instagram_audit.db instagram_audit_backup_$(date +%Y%m%d).db
  ```

- **Export the data**: SQLite data can be queried directly
  ```bash
  sqlite3 instagram_audit.db "SELECT * FROM snapshots;"
  ```

- **Check specific relationships**: Use SQL for custom queries
  ```bash
  sqlite3 instagram_audit.db "
    SELECT username
    FROM accounts
    WHERE pk IN (
      SELECT account_pk
      FROM snapshot_followers
      WHERE snapshot_id = 2
    )
    AND pk NOT IN (
      SELECT account_pk
      FROM snapshot_following
      WHERE snapshot_id = 2
    )
    ORDER BY username;
  "
  ```

## Troubleshooting

### "File not found" error

Make sure you're pointing to the correct directory. The tool searches for:
- `followers.json` or `followers_1.json`
- `following.json` or `following_1.json`

You can also point directly to a file:
```bash
audit run --input ~/Downloads/export/followers.json
```

### "No snapshots found"

Make sure you've run `audit run` at least once.

### Username changes not detected

Instagram exports don't include numeric user IDs, so we can't detect username changes from exports alone. Username changes will appear as an unfollower + new follower in export-based tracking.

### Different database

You can use multiple databases for different accounts:
```bash
audit --db my_business_account.db run --input ./export/
audit --db my_personal_account.db run --input ./export2/
```
