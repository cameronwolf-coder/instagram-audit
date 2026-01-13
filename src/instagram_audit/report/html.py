"""HTML report generation."""
from datetime import datetime
from pathlib import Path
from typing import Optional

from instagram_audit.core import DiffResult, RelationshipViews, AccountIdentity

try:
    from jinja2 import Template
except ImportError:
    Template = None  # type: ignore


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Audit Report - {{ report_date }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        h1 {
            color: #262626;
            margin-bottom: 10px;
            font-size: 28px;
        }

        h2 {
            color: #262626;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 20px;
            border-bottom: 2px solid #dbdbdb;
            padding-bottom: 8px;
        }

        .meta {
            color: #8e8e8e;
            font-size: 14px;
            margin-bottom: 30px;
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: #fafafa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #dbdbdb;
        }

        .stat-label {
            color: #8e8e8e;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }

        .stat-value {
            font-size: 32px;
            font-weight: 600;
            color: #262626;
        }

        .stat-delta {
            font-size: 14px;
            margin-top: 5px;
        }

        .stat-delta.positive {
            color: #0095f6;
        }

        .stat-delta.negative {
            color: #ed4956;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        th {
            background: #fafafa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #262626;
            border-bottom: 2px solid #dbdbdb;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #efefef;
        }

        tr:last-child td {
            border-bottom: none;
        }

        .username {
            font-weight: 500;
            color: #262626;
        }

        .username::before {
            content: '@';
            color: #8e8e8e;
        }

        .full-name {
            color: #8e8e8e;
            font-size: 14px;
        }

        .empty-state {
            text-align: center;
            padding: 40px;
            color: #8e8e8e;
            font-style: italic;
        }

        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dbdbdb;
            text-align: center;
            color: #8e8e8e;
            font-size: 12px;
        }

        .username-change {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .arrow {
            color: #8e8e8e;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Relationship Audit</h1>
        <div class="meta">
            {% if is_diff %}
            Report generated on {{ report_date }}<br>
            Comparing snapshots from {{ old_date }} to {{ new_date }}
            {% else %}
            Report generated on {{ report_date }}<br>
            Snapshot from {{ snapshot_date }}
            {% endif %}
        </div>

        {% if is_diff %}
        <!-- Diff Report -->
        <div class="summary">
            <div class="stat-card">
                <div class="stat-label">Followers</div>
                <div class="stat-value">{{ new_follower_count }}</div>
                <div class="stat-delta {{ 'positive' if follower_delta > 0 else 'negative' if follower_delta < 0 else '' }}">
                    {{ follower_delta|format_delta }} from {{ old_follower_count }}
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Following</div>
                <div class="stat-value">{{ new_following_count }}</div>
                <div class="stat-delta {{ 'positive' if following_delta > 0 else 'negative' if following_delta < 0 else '' }}">
                    {{ following_delta|format_delta }} from {{ old_following_count }}
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">New Followers</div>
                <div class="stat-value">{{ new_followers|length }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Unfollowers</div>
                <div class="stat-value">{{ unfollowers|length }}</div>
            </div>
        </div>

        {% if new_followers %}
        <h2>New Followers</h2>
        <table>
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Full Name</th>
                </tr>
            </thead>
            <tbody>
                {% for account in new_followers|sort(attribute='username') %}
                <tr>
                    <td><span class="username">{{ account.username }}</span></td>
                    <td><span class="full-name">{{ account.full_name or '' }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}

        {% if unfollowers %}
        <h2>Unfollowers</h2>
        <table>
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Full Name</th>
                </tr>
            </thead>
            <tbody>
                {% for account in unfollowers|sort(attribute='username') %}
                <tr>
                    <td><span class="username">{{ account.username }}</span></td>
                    <td><span class="full-name">{{ account.full_name or '' }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}

        {% if new_following %}
        <h2>New Following</h2>
        <table>
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Full Name</th>
                </tr>
            </thead>
            <tbody>
                {% for account in new_following|sort(attribute='username') %}
                <tr>
                    <td><span class="username">{{ account.username }}</span></td>
                    <td><span class="full-name">{{ account.full_name or '' }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}

        {% if unfollowing %}
        <h2>Unfollowing</h2>
        <table>
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Full Name</th>
                </tr>
            </thead>
            <tbody>
                {% for account in unfollowing|sort(attribute='username') %}
                <tr>
                    <td><span class="username">{{ account.username }}</span></td>
                    <td><span class="full-name">{{ account.full_name or '' }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}

        {% if username_changes %}
        <h2>Username Changes</h2>
        <table>
            <thead>
                <tr>
                    <th>Previous Username</th>
                    <th></th>
                    <th>New Username</th>
                </tr>
            </thead>
            <tbody>
                {% for pk, (old_username, new_username) in username_changes.items()|sort(attribute='1.0') %}
                <tr>
                    <td><span class="username">{{ old_username }}</span></td>
                    <td class="arrow">→</td>
                    <td><span class="username">{{ new_username }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}

        {% else %}
        <!-- Views Report -->
        <div class="summary">
            <div class="stat-card">
                <div class="stat-label">Followers</div>
                <div class="stat-value">{{ follower_count }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Following</div>
                <div class="stat-value">{{ following_count }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Mutuals</div>
                <div class="stat-value">{{ mutuals|length }}</div>
            </div>
        </div>
        {% endif %}

        <h2>Current Relationships</h2>

        {% if mutuals %}
        <h3>Mutuals ({{ mutuals|length }})</h3>
        <table>
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Full Name</th>
                </tr>
            </thead>
            <tbody>
                {% for account in mutuals|sort(attribute='username') %}
                <tr>
                    <td><span class="username">{{ account.username }}</span></td>
                    <td><span class="full-name">{{ account.full_name or '' }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="empty-state">No mutuals</div>
        {% endif %}

        {% if not_following_back %}
        <h3>Not Following Back ({{ not_following_back|length }})</h3>
        <p style="color: #8e8e8e; font-size: 14px; margin-bottom: 10px;">These people follow you, but you don't follow them</p>
        <table>
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Full Name</th>
                </tr>
            </thead>
            <tbody>
                {% for account in not_following_back|sort(attribute='username') %}
                <tr>
                    <td><span class="username">{{ account.username }}</span></td>
                    <td><span class="full-name">{{ account.full_name or '' }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}

        {% if not_followed_back %}
        <h3>Not Followed Back ({{ not_followed_back|length }})</h3>
        <p style="color: #8e8e8e; font-size: 14px; margin-bottom: 10px;">You follow these people, but they don't follow you</p>
        <table>
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Full Name</th>
                </tr>
            </thead>
            <tbody>
                {% for account in not_followed_back|sort(attribute='username') %}
                <tr>
                    <td><span class="username">{{ account.username }}</span></td>
                    <td><span class="full-name">{{ account.full_name or '' }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}

        <div class="footer">
            Generated by Instagram Audit<br>
            Local-first relationship tracker
        </div>
    </div>
</body>
</html>
"""


def generate_diff_html(diff: DiffResult, output_path: Optional[Path] = None) -> Path:
    """Generate HTML report for a diff."""
    if Template is None:
        raise ImportError("jinja2 is required for HTML reports. Install with: pip install jinja2")

    # Custom filter for delta formatting
    def format_delta(value: int) -> str:
        if value > 0:
            return f"+{value}"
        elif value < 0:
            return str(value)
        else:
            return "0"

    from jinja2 import Environment

    # Create template with custom filter
    env = Environment()
    env.filters['format_delta'] = format_delta
    template = env.from_string(HTML_TEMPLATE)

    html = template.render(
        is_diff=True,
        report_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        old_date=diff.old_snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        new_date=diff.new_snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        old_follower_count=diff.old_snapshot.follower_count(),
        new_follower_count=diff.new_snapshot.follower_count(),
        follower_delta=diff.new_snapshot.follower_count() - diff.old_snapshot.follower_count(),
        old_following_count=diff.old_snapshot.following_count(),
        new_following_count=diff.new_snapshot.following_count(),
        following_delta=diff.new_snapshot.following_count() - diff.old_snapshot.following_count(),
        new_followers=diff.new_followers,
        unfollowers=diff.unfollowers,
        new_following=diff.new_following,
        unfollowing=diff.unfollowing,
        username_changes=diff.username_changes,
        mutuals=diff.mutuals,
        not_following_back=diff.not_following_back,
        not_followed_back=diff.not_followed_back,
    )

    if output_path is None:
        output_path = Path("reports") / f"{datetime.now().strftime('%Y-%m-%d')}.html"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    return output_path


def generate_views_html(views: RelationshipViews, output_path: Optional[Path] = None) -> Path:
    """Generate HTML report for relationship views."""
    if Template is None:
        raise ImportError("jinja2 is required for HTML reports. Install with: pip install jinja2")

    template = Template(HTML_TEMPLATE)

    html = template.render(
        is_diff=False,
        report_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        snapshot_date=views.snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        follower_count=views.snapshot.follower_count(),
        following_count=views.snapshot.following_count(),
        mutuals=views.mutuals,
        not_following_back=views.not_following_back,
        not_followed_back=views.not_followed_back,
    )

    if output_path is None:
        output_path = Path("reports") / f"{datetime.now().strftime('%Y-%m-%d')}.html"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    return output_path
