#!/usr/bin/env python3
"""
YouTube Auto Poster — Full Data API v3 automation.
Uploads Shorts with thumbnails, playlists, tags, descriptions.
"""
import json
import os
import sys
from pathlib import Path

# Add credentials loader
SCRIPTS_DIR = Path(r"C:\Users\HP\AppData\Local\hermes\rboutique-affiliate\scripts")
sys.path.insert(0, str(SCRIPTS_DIR))
from load_credentials import load_credentials

# Load credentials into environment
load_credentials()

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
PLAN_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue"
TOKEN_DIR = BASE / "rboutique-affiliate" / "scripts" / "tokens"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

CLIENT_SECRETS = BASE / "rboutique-affiliate" / "scripts" / "client_secret.json"

CHANNEL_CONFIG = {
    "luxe": {
        "channel_name": "Luxe Fashion Finds",
        "playlist": "Designer for Less",
        "description_suffix": "Luxury fashion for less. New finds daily."
    },
    "smart": {
        "channel_name": "Smart Buy Guides", 
        "playlist": "Smart Picks Under Budget",
        "description_suffix": "Smart shopping guides. Value finds daily."
    }
}


def get_youtube_service(account):
    """Get authenticated YouTube service using refresh token from vault."""
    refresh_token = os.environ.get(f"YOUTUBE_{account.upper()}_REFRESH_TOKEN", "")
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
    
    if not all([refresh_token, client_id, client_secret]):
        print(f"  ✗ Missing credentials for {account}")
        return None
    
    from google.oauth2.credentials import Credentials
    
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )
    
    if not creds.valid:
        creds.refresh(Request())
    
    return build("youtube", "v3", credentials=creds)


def get_or_create_playlist(service, playlist_title):
    """Get existing playlist ID or create new one."""
    # Search existing playlists
    response = service.playlists().list(part="snippet", mine=True, maxResults=50).execute()
    for pl in response.get("items", []):
        if pl["snippet"]["title"] == playlist_title:
            return pl["id"]
    
    # Create new playlist
    body = {
        "snippet": {"title": playlist_title, "description": f"Auto-generated: {playlist_title}"},
        "status": {"privacyStatus": "public"}
    }
    response = service.playlists().insert(part="snippet,status", body=body).execute()
    return response["id"]


def upload_short(account, item):
    """Upload a Short to YouTube."""
    service = get_youtube_service(account)
    if not service:
        return False, "No service"
    
    product = item["product"]
    serial = item["serial"]
    caption = item["caption"]
    
    config = CHANNEL_CONFIG[account]
    playlist_title = config["playlist"]
    
    # Video file
    video_dir = QUEUE_DIR / f"{account}_reels" / f"serial_{serial}"
    video_files = list(video_dir.glob("*.mp4"))
    if not video_files:
        return False, f"No video in {video_dir}"
    
    video_path = str(video_files[0])
    
    # Get/create playlist
    playlist_id = get_or_create_playlist(service, playlist_title)
    
    # Build metadata
    name = product.get("name", "Product")
    brand = product.get("brand", "Brand")
    category = product.get("category", "item")
    price = product.get("price", "99")
    tracked_link = product.get("tracked_link", "")
    
    title = f"{name} — {brand} | ${price} | Link #{serial} in bio"
    if len(title) > 100:
        title = title[:97] + "..."
    
    description = f"""{caption}

🔗 Link #{serial}: {tracked_link}
📱 Follow {config['channel_name']} for daily finds!

{config['description_suffix']}

#Shorts #Affiliate #Ad"""
    
    if len(description) > 5000:
        description = description[:4997] + "..."
    
    tags = [tag.replace("#", "") for tag in item.get("hashtags", []) if tag.startswith("#")]
    tags = tags[:15]  # YouTube limit
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    
    # Upload
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    
    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Upload {account} #{serial}: {int(status.progress() * 100)}%")
    
    video_id = response["id"]
    print(f"  ✓ YouTube: #{serial} {name[:40]} → Video ID: {video_id}")
    
    # Add to playlist
    service.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id}
            }
        }
    ).execute()
    
    return True, video_id


def main():
    print("=" * 60)
    print("YOUTUBE AUTO POSTER — Data API v3")
    print("=" * 60)
    
    if not PLAN_PATH.exists():
        print("  ✗ content_plan.json not found. Run copywriter.py first.")
        return
    
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    print(f"\nUploading Luxe Shorts ({len(plan['luxe'])})...")
    for item in plan["luxe"]:
        upload_short("luxe", item)
    
    print(f"\nUploading Smart Shorts ({len(plan['smart'])})...")
    for item in plan["smart"]:
        upload_short("smart", item)
    
    print("\n✓ YouTube uploads complete")


if __name__ == "__main__":
    main()