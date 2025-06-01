#!/usr/bin/env python3

"""
Token setup: --did not work
1. Go to https://developers.google.com/oauthplayground
2. Use your own OAuth credentials.
3. Use the scope: https://www.googleapis.com/auth/photoslibrary
4. Exchange for tokens, and copy the access token.
5. Save it to a file named `token.txt`.


---trying google cloud steps


Run the script with:
    python3 fix_photo_dates_token.py
"""

import csv
import requests
import os
import piexif
from datetime import datetime
from io import BytesIO

TOKEN_FILE = "token.txt"
CSV_PATH = "mismatched_photos.csv"
API_URL = "https://photoslibrary.googleapis.com/v1/mediaItems"
UPLOAD_URL = "https://photoslibrary.googleapis.com/v1/uploads"
CREATE_MEDIA_ITEM_URL = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"

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

def download_photo(media_item_id, access_token):
    url = f"{API_URL}/{media_item_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"❌ Failed to get media item metadata: {resp.status_code} - {resp.text}")
        return None

    base_url = resp.json().get('baseUrl')
    if not base_url:
        print(f"❌ No baseUrl found for media item {media_item_id}")
        return None

    # Download original photo (full resolution)
    download_url = base_url + "=d"  # =d to get download-quality image
    resp = requests.get(download_url, headers=headers)
    if resp.status_code != 200:
        print(f"❌ Failed to download media item: {resp.status_code} - {resp.text}")
        return None

    return resp.content

def update_exif_creation_date(image_bytes, creation_datetime_str):
    # Parse datetime string to EXIF format: "YYYY:MM:DD HH:MM:SS"
    try:
        dt = datetime.fromisoformat(creation_datetime_str.rstrip("Z"))
        exif_dt = dt.strftime("%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"❌ Invalid datetime format: {creation_datetime_str} - {e}")
        return None

    # Load EXIF data
    try:
        exif_dict = piexif.load(image_bytes)
    except Exception:
        # If image has no EXIF, create empty EXIF dict
        exif_dict = {"0th":{}, "Exif":{}, "GPS":{}, "1st":{}, "thumbnail":None}

    # Set DateTimeOriginal and DateTime in EXIF
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = exif_dt.encode()
    exif_dict["0th"][piexif.ImageIFD.DateTime] = exif_dt.encode()

    exif_bytes = piexif.dump(exif_dict)
    # Insert updated EXIF back into the JPEG
    try:
        from PIL import Image
        img = Image.open(BytesIO(image_bytes))
        output = BytesIO()
        img.save(output, "jpeg", exif=exif_bytes)
        return output.getvalue()
    except ImportError:
        print("❌ Pillow is required to update EXIF metadata. Please install it with `pip install Pillow`.")
        return None
    except Exception as e:
        print(f"❌ Failed to save image with updated EXIF: {e}")
        return None

def upload_photo(photo_bytes, access_token, filename="upload.jpg"):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/octet-stream",
        "X-Goog-Upload-File-Name": filename,
        "X-Goog-Upload-Protocol": "raw",
    }
    resp = requests.post(UPLOAD_URL, headers=headers, data=photo_bytes)
    if resp.status_code != 200:
        print(f"❌ Upload failed: {resp.status_code} - {resp.text}")
        return None
    return resp.text  # This is the upload token

def create_media_item(upload_token, access_token, description=""):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/json",
    }
    body = {
        "newMediaItems": [
            {
                "description": description,
                "simpleMediaItem": {
                    "uploadToken": upload_token
                }
            }
        ]
    }
    resp = requests.post(CREATE_MEDIA_ITEM_URL, headers=headers, json=body)
    if resp.status_code != 200:
        print(f"❌ Create media item failed: {resp.status_code} - {resp.text}")
        return None
    return resp.json()

def delete_media_item(media_item_id, access_token):
    url = f"{API_URL}/{media_item_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    resp = requests.delete(url, headers=headers)
    if resp.status_code == 204:
        return True
    else:
        print(f"❌ Failed to delete media item {media_item_id}: {resp.status_code} - {resp.text}")
        return False

def main():
    access_token = load_access_token()

    success = 0
    fail = 0

    with open(CSV_PATH, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            media_id = row.get('mediaItemId')
            correct_date = row.get('correct_date')
            filename = row.get('filename', 'unknown.jpg')

            if not media_id or not correct_date:
                print(f"⚠️ Skipping row with missing data: {row}")
                continue

            print(f"\n➡️ Processing {filename} ({media_id}) with date {correct_date}")

            # 1. Download original photo
            photo_bytes = download_photo(media_id, access_token)
            if not photo_bytes:
                fail += 1
                continue

            # 2. Update EXIF creation date
            updated_photo = update_exif_creation_date(photo_bytes, correct_date)
            if not updated_photo:
                fail += 1
                continue

            # 3. Upload updated photo
            upload_token = upload_photo(updated_photo, access_token, filename=filename)
            if not upload_token:
                fail += 1
                continue

            # 4. Create media item in library
            result = create_media_item(upload_token, access_token, description=f"Fixed creation date to {correct_date}")
            if not result:
                fail += 1
                continue

            # 5. Delete original photo
            deleted = delete_media_item(media_id, access_token)
            if not deleted:
                print(f"⚠️ Warning: failed to delete original media item {media_id}")
                # Continue anyway

            print(f"[✓] Fixed {filename}")
            success += 1

    print(f"\n✅ Finished: {success} processed, {fail} failed.")

if __name__ == "__main__":
    main()

