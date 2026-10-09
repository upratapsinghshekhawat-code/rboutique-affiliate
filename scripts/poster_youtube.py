#!/usr/bin/env python3
"""
YouTube Poster — Uses YouTube Data API v3 to upload Shorts.
Reads assets from content/queue/youtube_shorts/
"""
import json
import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue" / "youtube_shorts"
TOKEN_DIR = BASE / "rboutique-affiliate" / "scripts" / "tokens"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

CLIENT_SECRETS = BASE / "rboutique-affiliate" / "scripts" / "client_secret.json"


def get_youtube_service(account):
    """Get authenticated YouTube service for an account."""
    token_file = TOKEN_DIR / f"youtube_{account}_token.pickle"
    
    creds = None
    if token_file.exists():
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
            # Note: This would need to be run interactively per account
            # In production, use refresh tokens from vault
            creds = flow.run_local_server(port=8080, prompt="consent")
        
        token_file.parent.mkdir(parents=True, exist_ok=True)
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)
    
    return build("youtube", "v3", credentials=creds)


def upload_short(account, video_path, meta_path):
    """Upload a Short to YouTube."""
    
    service = get_youtube_service(account)
    if not service:
        print(f"  ✗ Could not authenticate {account}")
        return False
    
    with open(meta_path, "r") as f:
        meta = json.load(f)
    
    title = meta.get("title", "Short")[:100]
    description = meta.get("description", "")[:5000]
    tags = meta.get("tags", [])[:15]
    playlist = meta.get("playlist", "")
    
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
    
    # Upload video
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    
    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Upload progress: {int(status.progress() * 100)}%")
    
    video_id = response["id"]
    print(f"  ✓ Uploaded: {title[:50]} (ID: {video_id})")
    
    # Add to playlist
    if playlist:
        try:
            playlists = service.playlists().list(part="id", mine=True, maxResults=50).execute()
            playlist_id = None
            for pl in playlists.get("items", []):
                if pl["snippet"]["title"] == playlist:
                    playlist_id = pl["id"]
                    break
            
            if not playlist_id:
                # Create playlist
                pl_body = {
                    "snippet": {"title": playlist},
                    "status": {"privacyStatus": "public"}
                }
                pl_response = service.playlists().insert(part="snippet,status", body=pl_body).execute()
                playlist_id = pl_response["id"]
            
            # Add video to playlist
            service.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id}
                    }
                }
            ).execute()
            print(f"  ✓ Added to playlist: {playlist}")
        except Exception as e:
            print(f"  ⚠ Playlist add failed: {e}")
    
    return True


def main():
    print("=" * 60)
    print("YOUTUBE POSTER — Data API v3")
    print("=" * 60)
    
    if not QUEUE_DIR.exists():
        print("  ✗ Queue directory not found. Run asset_generator.py first.")
        return
    
    print("""
⚠️  TEMPLATE MODE - NOT POSTING FOR REAL

To enable real posting:
1. Run authentication for each account once:
   python -c "
   from google_auth_oauthlib.flow import InstalledAppFlow
   flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', 
       ['https://www.googleapis.com/auth/youtube.upload'])
   creds = flow.run_local_server(port=8080)
   import pickle
   with open('youtube_luxe_token.pickle', 'wb') as f: pickle.dump(creds, f)
   "
   (repeat for smart account)

2. Save tokens in tokens/ directory
3. Have MP4 videos ready in queue (from CapCut export)

Current queue contents:""")
    
    for short_dir in QUEUE_DIR.iterdir():
        if short_dir.is_dir():
            meta_files = list(short_dir.glob("*_meta.json"))
            for mf in meta_files:
                with open(mf, "r") as f:
                    meta = json.load(f)
                print(f"  • Serial #{meta.get('serial')}: {meta.get('title', 'Unknown')}")
                print(f"    Video needed: {short_dir}/*.mp4")
                print(f"    Playlist: {meta.get('playlist')}")
    
    print("\n✓ Ready for deployment when tokens and videos ready")


if __name__ == "__main__":
    main()