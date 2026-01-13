"""Tests for export ingest collector."""
import json
from datetime import datetime
from pathlib import Path
import tempfile
import pytest

from instagram_audit.collectors import ExportIngestCollector


@pytest.fixture
def temp_export_dir():
    """Create a temporary directory for test exports."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_parse_followers_json(temp_export_dir):
    """Test parsing followers JSON file."""
    followers_data = [
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/alice",
                    "value": "alice",
                    "timestamp": 1704067200,
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/bob",
                    "value": "bob",
                    "timestamp": 1704067200,
                }
            ]
        },
    ]

    following_data = []

    followers_file = temp_export_dir / "followers_1.json"
    following_file = temp_export_dir / "following.json"

    followers_file.write_text(json.dumps(followers_data))
    following_file.write_text(json.dumps(following_data))

    collector = ExportIngestCollector(temp_export_dir)
    snapshot = collector.collect()

    assert snapshot.follower_count() == 2
    assert snapshot.following_count() == 0
    assert any(acc.username == "alice" for acc in snapshot.followers)
    assert any(acc.username == "bob" for acc in snapshot.followers)


def test_parse_following_json(temp_export_dir):
    """Test parsing following JSON file."""
    followers_data = []

    following_data = {
        "relationships_following": [
            {
                "string_list_data": [
                    {
                        "href": "https://www.instagram.com/charlie",
                        "value": "charlie",
                        "timestamp": 1704067200,
                    }
                ]
            }
        ]
    }

    followers_file = temp_export_dir / "followers.json"
    following_file = temp_export_dir / "following_1.json"

    followers_file.write_text(json.dumps(followers_data))
    following_file.write_text(json.dumps(following_data))

    collector = ExportIngestCollector(temp_export_dir)
    snapshot = collector.collect()

    assert snapshot.follower_count() == 0
    assert snapshot.following_count() == 1
    assert any(acc.username == "charlie" for acc in snapshot.following)


def test_timestamp_extraction(temp_export_dir):
    """Test that timestamp is extracted from data."""
    test_timestamp = 1704067200  # 2024-01-01 00:00:00 UTC

    followers_data = [
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/alice",
                    "value": "alice",
                    "timestamp": test_timestamp,
                }
            ]
        }
    ]

    following_data = []

    followers_file = temp_export_dir / "followers.json"
    following_file = temp_export_dir / "following.json"

    followers_file.write_text(json.dumps(followers_data))
    following_file.write_text(json.dumps(following_data))

    collector = ExportIngestCollector(temp_export_dir)
    snapshot = collector.collect()

    # Should use the timestamp from the data
    # Compare timestamps directly to avoid timezone issues
    from datetime import datetime
    expected_timestamp = datetime.fromtimestamp(test_timestamp)
    assert snapshot.timestamp == expected_timestamp


def test_pk_generation_from_username(temp_export_dir):
    """Test that pk is generated from username for exports."""
    followers_data = [
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/alice",
                    "value": "alice",
                    "timestamp": 1704067200,
                }
            ]
        }
    ]

    following_data = []

    followers_file = temp_export_dir / "followers.json"
    following_file = temp_export_dir / "following.json"

    followers_file.write_text(json.dumps(followers_data))
    following_file.write_text(json.dumps(following_data))

    collector = ExportIngestCollector(temp_export_dir)
    snapshot = collector.collect()

    # Since export doesn't have pk, it should use username as identifier
    alice = next(acc for acc in snapshot.followers if acc.username == "alice")
    assert alice.pk == "username:alice"


def test_file_not_found(temp_export_dir):
    """Test error handling when files are not found."""
    with pytest.raises(FileNotFoundError):
        ExportIngestCollector(temp_export_dir)


def test_empty_data(temp_export_dir):
    """Test handling of empty data."""
    followers_file = temp_export_dir / "followers.json"
    following_file = temp_export_dir / "following.json"

    followers_file.write_text(json.dumps([]))
    following_file.write_text(json.dumps([]))

    collector = ExportIngestCollector(temp_export_dir)
    snapshot = collector.collect()

    assert snapshot.follower_count() == 0
    assert snapshot.following_count() == 0


def test_missing_string_list_data(temp_export_dir):
    """Test handling when string_list_data is missing."""
    followers_data = [
        {
            "title": "Some title",
            "media_list_data": [],
        }
    ]

    following_data = []

    followers_file = temp_export_dir / "followers.json"
    following_file = temp_export_dir / "following.json"

    followers_file.write_text(json.dumps(followers_data))
    following_file.write_text(json.dumps(following_data))

    collector = ExportIngestCollector(temp_export_dir)
    snapshot = collector.collect()

    assert snapshot.follower_count() == 0


def test_subdirectory_search(temp_export_dir):
    """Test that collector can find files in subdirectories."""
    subdir = temp_export_dir / "followers_and_following"
    subdir.mkdir()

    followers_data = [
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/alice",
                    "value": "alice",
                    "timestamp": 1704067200,
                }
            ]
        }
    ]

    following_data = []

    followers_file = subdir / "followers.json"
    following_file = subdir / "following.json"

    followers_file.write_text(json.dumps(followers_data))
    following_file.write_text(json.dumps(following_data))

    collector = ExportIngestCollector(temp_export_dir)
    snapshot = collector.collect()

    assert snapshot.follower_count() == 1


def test_direct_file_path(temp_export_dir):
    """Test initialization with direct file path."""
    followers_data = [
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/alice",
                    "value": "alice",
                    "timestamp": 1704067200,
                }
            ]
        }
    ]

    following_data = []

    followers_file = temp_export_dir / "followers.json"
    following_file = temp_export_dir / "following.json"

    followers_file.write_text(json.dumps(followers_data))
    following_file.write_text(json.dumps(following_data))

    # Initialize with direct file path
    collector = ExportIngestCollector(followers_file)
    snapshot = collector.collect()

    assert snapshot.follower_count() == 1
    assert snapshot.following_count() == 0
