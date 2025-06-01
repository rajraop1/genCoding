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

Copy the Access Token and run the script I gave you earlier with:

export GPHOTOS_ACCESS_TOKEN="ya29.a0...your_access_token..."
python3 google_photos_mismatched_dates.py


"""

from __future__ import annotations

import csv as _csv
import os as _os
import re as _re
from datetime import datetime as _dt, date as _date
from typing import Dict, List, Optional

import requests as _requests
from dateutil import parser as _date_parser

_GOOGLE_PHOTOS_LIST_URL = "https://photoslibrary.googleapis.com/v1/mediaItems"

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
    token = access_token or _os.getenv("GPHOTOS_ACCESS_TOKEN")
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
    all_entries: list[tuple[str, str]] = []
    mismatches: list[tuple[str, str]] = []
    missing_dates: list[tuple[str, str]] = []

    for item in items:
        filename: str = item.get("filename", "")
        embedded_date = _extract_date_from_filename(filename)
        if not embedded_date:
            continue

        taken = _taken_date(item.get("mediaMetadata", {}))
        taken_str = taken.isoformat() if taken else "N/A"
        all_entries.append((filename, taken_str))

        if not taken:
            missing_dates.append((filename, taken_str))
        elif abs((embedded_date - taken).days) > 1:
            mismatches.append((filename, taken_str, embedded_date.isoformat()))

    with open("all_photos.csv", "w", newline="", encoding="utf-8") as all_csv:
        writer = _csv.writer(all_csv)
        writer.writerow(["filename", "taken_date"])
        writer.writerows(all_entries)

    with open("mismatched_photos.csv", "w", newline="", encoding="utf-8") as mismatch_csv:
        writer = _csv.writer(mismatch_csv)
        writer.writerow(["filename", "taken_date", "correct_date"])
        writer.writerows(mismatches)

    with open("missing.csv", "w", newline="", encoding="utf-8") as missing_csv:
        writer = _csv.writer(missing_csv)
        writer.writerow(["filename", "taken_date"])
        writer.writerows(missing_dates)

    if mismatches:
        print(f"Found {len(mismatches)} mismatched file(s). See mismatched_photos.csv.")
        for name, td, correct in mismatches:
            print(f"• {name} — taken {td} (correct: {correct})")
    else:
        print("No significant filename/metadata date mismatches detected.")

    if missing_dates:
        print(f"Found {len(missing_dates)} file(s) with missing taken date. See missing.csv.")

    print("Full list saved to all_photos.csv")


if __name__ == "__main__":
    _cli()
