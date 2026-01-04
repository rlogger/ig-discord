import pandas as pd
import io
import re
from typing import Optional


def parse_filename(filename: str) -> dict:
    """
    Parse Instagram export filename to extract metadata.

    Supports formats like:
    - IGFollow_rajj__singhh_287_followers.csv
    - followers_1.csv
    - following.csv

    Returns:
        dict with 'ig_username', 'count', 'file_type'
    """
    result = {
        'ig_username': None,
        'count': None,
        'file_type': 'followers'  # default
    }

    filename_lower = filename.lower()

    # Detect file type
    if 'following' in filename_lower:
        result['file_type'] = 'following'
    elif 'follower' in filename_lower:
        result['file_type'] = 'followers'

    # Try to parse IGFollow format: IGFollow_username_count_type.csv
    igfollow_match = re.match(
        r'IGFollow_(.+?)_(\d+)_(followers|following)\.csv',
        filename,
        re.IGNORECASE
    )
    if igfollow_match:
        result['ig_username'] = igfollow_match.group(1)
        result['count'] = int(igfollow_match.group(2))
        result['file_type'] = igfollow_match.group(3).lower()

    return result


def parse_instagram_csv(content: bytes | str, filename: str = None) -> tuple[list[dict], dict]:
    """
    Parse Instagram follower/following CSV file.

    Returns:
        tuple: (list of records, metadata dict)
    """
    if isinstance(content, bytes):
        content = content.decode('utf-8-sig')  # Handle BOM

    df = pd.read_csv(io.StringIO(content))

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # Expected columns mapping
    column_map = {
        'user_id': ['user_id', 'userid', 'id'],
        'username': ['username', 'user_name', 'handle'],
        'fullname': ['fullname', 'full_name', 'name', 'display_name'],
        'followed_by_you': ['followed_by_you', 'following', 'you_follow'],
        'is_verified': ['is_verified', 'verified'],
        'profile_url': ['profile_url', 'url', 'profile'],
        'avatar_url': ['avatar_url', 'avatar', 'picture']
    }

    # Rename columns to standard names
    rename_map = {}
    for standard, variants in column_map.items():
        for variant in variants:
            if variant in df.columns:
                rename_map[variant] = standard
                break

    df = df.rename(columns=rename_map)

    # Fill NaN values
    df = df.fillna('')

    records = []
    for _, row in df.iterrows():
        record = {
            'user_id': str(row.get('user_id', '')),
            'username': str(row.get('username', '')),
            'fullname': str(row.get('fullname', '')),
            'followed_by_you': str(row.get('followed_by_you', '')).upper(),
            'is_verified': str(row.get('is_verified', '')).upper(),
            'profile_url': str(row.get('profile_url', '')),
        }
        records.append(record)

    # Calculate metadata
    total = len(records)
    following_count = sum(1 for r in records if r['followed_by_you'] == 'YES')
    not_following_count = sum(1 for r in records if r['followed_by_you'] == 'NO')
    verified_count = sum(1 for r in records if r['is_verified'] == 'YES')

    metadata = {
        'total': total,
        'following_back': following_count,
        'not_following_back': not_following_count,
        'verified': verified_count
    }

    # Add filename metadata if provided
    if filename:
        file_meta = parse_filename(filename)
        metadata['ig_username'] = file_meta['ig_username']
        metadata['detected_type'] = file_meta['file_type']

    return records, metadata


def analyze_follow_status(records: list[dict]) -> dict:
    """Analyze follow relationships from records."""
    following_you = [r for r in records]  # All records in followers list follow you
    you_follow = [r for r in records if r['followed_by_you'] == 'YES']
    you_dont_follow = [r for r in records if r['followed_by_you'] == 'NO']

    return {
        'followers': following_you,
        'you_follow_back': you_follow,
        'you_dont_follow_back': you_dont_follow,
        'mutual': you_follow,
        'fans': you_dont_follow  # People who follow you but you don't follow back
    }


def find_non_followers(
    followers_records: list[dict],
    following_records: list[dict]
) -> list[dict]:
    """
    Find people you follow who don't follow you back.

    Args:
        followers_records: List of people who follow you
        following_records: List of people you follow

    Returns:
        List of people you follow who don't follow back
    """
    follower_usernames = {r['username'].lower() for r in followers_records}

    non_followers = [
        r for r in following_records
        if r['username'].lower() not in follower_usernames
    ]

    return non_followers


def find_fans(
    followers_records: list[dict],
    following_records: list[dict]
) -> list[dict]:
    """
    Find people who follow you but you don't follow back (fans).

    Args:
        followers_records: List of people who follow you
        following_records: List of people you follow

    Returns:
        List of fans (followers you don't follow back)
    """
    following_usernames = {r['username'].lower() for r in following_records}

    fans = [
        r for r in followers_records
        if r['username'].lower() not in following_usernames
    ]

    return fans
