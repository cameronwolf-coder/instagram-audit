"""Create a sample Instagram export for testing the tool."""
import json
from pathlib import Path
from datetime import datetime

def create_sample_export(output_dir: Path) -> None:
    """Create a sample Instagram export structure."""

    # Create directory structure
    connections_dir = output_dir / "connections" / "followers_and_following"
    connections_dir.mkdir(parents=True, exist_ok=True)

    # Sample followers data
    followers_data = [
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/alice_designs",
                    "value": "alice_designs",
                    "timestamp": int(datetime(2024, 1, 1).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/bob_photos",
                    "value": "bob_photos",
                    "timestamp": int(datetime(2024, 1, 1).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/charlie_travels",
                    "value": "charlie_travels",
                    "timestamp": int(datetime(2024, 1, 1).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/dave_fitness",
                    "value": "dave_fitness",
                    "timestamp": int(datetime(2024, 1, 1).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/eve_art",
                    "value": "eve_art",
                    "timestamp": int(datetime(2024, 1, 1).timestamp())
                }
            ]
        },
    ]

    # Sample following data
    following_data = [
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/alice_designs",
                    "value": "alice_designs",
                    "timestamp": int(datetime(2024, 1, 1).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/bob_photos",
                    "value": "bob_photos",
                    "timestamp": int(datetime(2024, 1, 1).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/frank_tech",
                    "value": "frank_tech",
                    "timestamp": int(datetime(2024, 1, 1).timestamp())
                }
            ]
        },
    ]

    # Write files
    followers_file = connections_dir / "followers_1.json"
    following_file = connections_dir / "following.json"

    with open(followers_file, "w") as f:
        json.dump(followers_data, f, indent=2)

    with open(following_file, "w") as f:
        json.dump(following_data, f, indent=2)

    print(f"✅ Created sample export in: {output_dir}")
    print(f"   - Followers: {len(followers_data)}")
    print(f"   - Following: {len(following_data)}")
    print(f"\nFiles created:")
    print(f"   - {followers_file}")
    print(f"   - {following_file}")


def create_sample_export_week2(output_dir: Path) -> None:
    """Create a second sample export with changes."""

    connections_dir = output_dir / "connections" / "followers_and_following"
    connections_dir.mkdir(parents=True, exist_ok=True)

    # Week 2: Some changes
    # - alice_designs and bob_photos still there
    # - charlie_travels unfollowed
    # - dave_fitness changed username to dave_fit_coach
    # - eve_art still there
    # - grace_music is a new follower
    followers_data = [
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/alice_designs",
                    "value": "alice_designs",
                    "timestamp": int(datetime(2024, 1, 8).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/bob_photos",
                    "value": "bob_photos",
                    "timestamp": int(datetime(2024, 1, 8).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/dave_fit_coach",
                    "value": "dave_fit_coach",
                    "timestamp": int(datetime(2024, 1, 8).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/eve_art",
                    "value": "eve_art",
                    "timestamp": int(datetime(2024, 1, 8).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/grace_music",
                    "value": "grace_music",
                    "timestamp": int(datetime(2024, 1, 8).timestamp())
                }
            ]
        },
    ]

    # Week 2 following: unfollowed frank_tech, followed grace_music
    following_data = [
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/alice_designs",
                    "value": "alice_designs",
                    "timestamp": int(datetime(2024, 1, 8).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/bob_photos",
                    "value": "bob_photos",
                    "timestamp": int(datetime(2024, 1, 8).timestamp())
                }
            ]
        },
        {
            "string_list_data": [
                {
                    "href": "https://www.instagram.com/grace_music",
                    "value": "grace_music",
                    "timestamp": int(datetime(2024, 1, 8).timestamp())
                }
            ]
        },
    ]

    followers_file = connections_dir / "followers_1.json"
    following_file = connections_dir / "following.json"

    with open(followers_file, "w") as f:
        json.dump(followers_data, f, indent=2)

    with open(following_file, "w") as f:
        json.dump(following_data, f, indent=2)

    print(f"✅ Created sample export (Week 2) in: {output_dir}")
    print(f"   - Followers: {len(followers_data)}")
    print(f"   - Following: {len(following_data)}")
    print(f"\nChanges from Week 1:")
    print(f"   - New follower: grace_music")
    print(f"   - Unfollower: charlie_travels")
    print(f"   - Username change: dave_fitness → dave_fit_coach")
    print(f"   - Unfollowed: frank_tech")
    print(f"   - Now following: grace_music")


if __name__ == "__main__":
    base_dir = Path(__file__).parent

    # Create Week 1 export
    week1_dir = base_dir / "sample-export-week1"
    create_sample_export(week1_dir)

    print("\n" + "=" * 60 + "\n")

    # Create Week 2 export
    week2_dir = base_dir / "sample-export-week2"
    create_sample_export_week2(week2_dir)

    print("\n" + "=" * 60)
    print("\n🎯 Sample exports created!")
    print("\nNow try the workflow:")
    print(f"\n1. Create first snapshot:")
    print(f"   audit run --input {week1_dir}")
    print(f"\n2. Create second snapshot:")
    print(f"   audit run --input {week2_dir}")
    print(f"\n3. View the diff:")
    print(f"   audit diff --latest")
    print(f"\n4. View relationships:")
    print(f"   audit views")
    print(f"\n5. Open HTML report:")
    print(f"   open reports/*.html")
