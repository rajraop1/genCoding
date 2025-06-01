#!/usr/bin/env python3
"""google_photos_mismatched_dates.py


Get Auth token
1. Go to:

👉 https://developers.google.com/oauthplayground
2. Open the OAuth 2.0 configuration (gear icon at top right):

    ✅ Check “Use your own OAuth credentials” — leave the fields blank (for now).

    Click Close.

3. In the Step 1 box (left pane):

    Scroll to the top.

    Paste this manually into the "Input your own scopes" box:

https://www.googleapis.com/auth/photoslibrary.readonly

    Then click Authorize APIs.

4. Sign in and allow access to your Google Photos account.
5. Click “Exchange authorization code for tokens”.

You will now see:

    ✅ Access Token (valid for ~1 hour)

    🔁 Refresh Token (you can store this to renew your token later)



-----
Run:

Copy the Access Token and run the script 

Save it to a file named `token.txt`.

python3 google_photos_mismatched_dates.py


"""

from __future__ import annotations

import csv as _csv
import os as _os
import re as _re
from datetime import datetime as _dt, date as _date
from typing import Dict, List, Optional

TOKEN_FILE = "token.txt"

import requests as _requests
from dateutil import parser as _date_parser

_GOOGLE_PHOTOS_LIST_URL = "https://photoslibrary.googleapis.com/v1/mediaItems"

def load_access_token(filepath=TOKEN_FILE):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            token = f.read().strip()
            if not token:
                raise ValueError("Token file is empty.")
            return token
    except FileNotFoundError:
        print(f"❌ Token file '{filepath}' not found.")
        exit(1)
    except Exception as e:
        print(f"❌ Error reading token: {e}")
        exit(1)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

_DATE_PATTERNS: list[tuple[_re.Pattern[str], int]] = [
    (_re.compile(r"^(\d{8})"), 1),
    (_re.compile(r"^PXL_(\d{8})_", _re.IGNORECASE), 1),
]


def _extract_date_from_filename(filename: str) -> Optional[_date]:
    for pattern, grp in _DATE_PATTERNS:
        m = pattern.match(filename)
        if m:
            datestr = m.group(grp)
            try:
                return _dt.strptime(datestr, "%Y%m%d").date()
            except ValueError:
                return None
    return None


def _taken_date(metadata: Dict) -> Optional[_date]:
    ct = metadata.get("creationTime")
    if not ct:
        return None
    try:
        return _date_parser.isoparse(ct).date()
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Google Photos access
# ---------------------------------------------------------------------------

def list_all_media_items(
    access_token: str | None = None,
    *,
    page_size: int = 100,
) -> List[Dict]:
    token = load_access_token()
    if not token:
        raise ValueError(
            "Provide an OAuth token via the 'access_token' argument or set the "
            "GPHOTOS_ACCESS_TOKEN environment variable."
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    items: List[Dict] = []
    next_page_token: str | None = None

    while True:
        params = {"pageSize": page_size}
        if next_page_token:
            params["pageToken"] = next_page_token

        resp = _requests.get(
            _GOOGLE_PHOTOS_LIST_URL, headers=headers, params=params, timeout=20
        )
        resp.raise_for_status()
        data = resp.json()

        items.extend(data.get("mediaItems", []))
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return items


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def _cli() -> None:
    items = list_all_media_items()
    all_entries: list[Dict] = []
    mismatches: list[Dict] = []
    missing_dates: list[Dict] = []

    for item in items:
        filename: str = item.get("filename", "")
        embedded_date = _extract_date_from_filename(filename)
        taken = _taken_date(item.get("mediaMetadata", {}))

        item_copy = {
            "mediaItemId": item.get("id"),
            "filename": filename,
            "creationTime": item.get("mediaMetadata", {}).get("creationTime"),
            "taken_date": taken.isoformat() if taken else None,
            "embedded_date": embedded_date.isoformat() if embedded_date else None,
            "baseUrl": item.get("baseUrl"),
        }

        all_entries.append(item_copy)

        if not taken:
            missing_dates.append(item_copy)
        elif embedded_date and abs((embedded_date - taken).days) > 1:
            mismatches.append(item_copy)

    with open("all_photos.csv", "w", newline="", encoding="utf-8") as all_csv:
        writer = _csv.writer(all_csv)
        writer.writerow(['mediaItemId', 'filename', 'creationTime', 'baseUrl'])
        for item in all_entries:
            writer.writerow([
                item['mediaItemId'],
                item['filename'],
                item['creationTime'],
                item['baseUrl']
            ])

    with open("mismatched_photos.csv", "w", newline="", encoding="utf-8") as mismatch_csv:
        writer = _csv.writer(mismatch_csv)
        writer.writerow(['mediaItemId', 'filename', 'taken_date', 'correct_date', 'baseUrl'])
        for item in mismatches:
            writer.writerow([
                item['mediaItemId'],
                item['filename'],
                item['taken_date'],
                item['embedded_date'],
                item['baseUrl']
            ])

    with open("missing.csv", "w", newline="", encoding="utf-8") as missing_csv:
        writer = _csv.writer(missing_csv)
        writer.writerow(['mediaItemId', 'filename', 'creationTime', 'baseUrl'])
        for item in missing_dates:
            writer.writerow([
                item['mediaItemId'],
                item['filename'],
                item['creationTime'],
                item['baseUrl']
            ])

    if mismatches:
        print(f"Found {len(mismatches)} mismatched file(s). See mismatched_photos.csv.")
        for item in mismatches:
            print(f"• {item['filename']} — taken {item['taken_date']} (correct: {item['embedded_date']})")
    else:
        print("No significant filename/metadata date mismatches detected.")

    if missing_dates:
        print(f"Found {len(missing_dates)} file(s) with missing taken date. See missing.csv.")

    print("Full list saved to all_photos.csv")


if __name__ == "__main__":
    _cli()
