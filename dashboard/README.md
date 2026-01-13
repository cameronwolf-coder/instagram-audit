# Instagram Audit Dashboard

A web dashboard for visualizing Instagram relationship tracking data from the [Instagram Audit CLI tool](https://github.com/cameronwolf-coder/instagram-audit).

## Features

- 📊 **Visual Analytics** - Beautiful charts and stats for your Instagram relationships
- 🔒 **100% Private** - All processing happens in your browser, no data leaves your device
- 📱 **No Login Required** - Upload your local database file, no Instagram credentials needed
- 🎨 **Instagram-styled UI** - Familiar design language with responsive layout

## What You Can See

- **Overview**: Snapshot history and verification queue status
- **Followers**: Complete list with mutual indicators
- **Following**: Complete list with follow-back status
- **Relationships**:
  - Mutuals (accounts that follow you back)
  - Not following back (they follow you, you don't follow them)
  - Not followed back (you follow them, they don't follow you)

## How to Use

### 1. Generate Your Database

First, use the [CLI tool](https://github.com/cameronwolf-coder/instagram-audit) to create snapshots:

```bash
# Install CLI
pip install instagram-audit

# Create snapshot from Instagram export
audit run --input /path/to/instagram-export

# This creates instagram_audit.db
```

### 2. Upload to Dashboard

1. Visit the dashboard (hosted on Vercel)
2. Drag and drop your `instagram_audit.db` file
3. Explore your data!

## Local Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

## Deployment

This dashboard is designed to be deployed on Vercel:

```bash
vercel deploy
```

## Privacy & Security

- ✅ All data processing happens client-side in your browser
- ✅ No server-side storage or processing
- ✅ No Instagram login or credentials required
- ✅ Your database file never leaves your device
- ✅ No analytics or tracking

## Technology Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **sql.js** - Client-side SQLite parsing
- **Lucide React** - Icons

## License

MIT License - See [LICENSE](../LICENSE)

## Related

- [Instagram Audit CLI](https://github.com/cameronwolf-coder/instagram-audit) - The command-line tool for data collection
