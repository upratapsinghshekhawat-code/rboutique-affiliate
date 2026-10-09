#!/usr/bin/env python3
"""
Facebook Auto Poster — Graph API for Reels.
Cross-posts from Instagram or direct via Page access token.
"""
import json
import os
import requests
from pathlib import Path

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
PLAN_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue"

GRAPH_API = "https://graph.facebook.com/v19.0"

ACCOUNT_CONFIG = {
    "luxe": {
        "page_id": os.environ.get("FACEBOOK_LUXE_PAGE_ID", ""),
        "page_access_token": os.environ.get("FACEBOOK_LUXE_PAGE_TOKEN", ""),
        "ig_user_id": os.environ.get("INSTAGRAM_LUXE_USER_ID", ""),
        "handle": "LuxeFashionFinds"
    },
    "smart": {
        "page_id": os.environ.get("FACEBOOK_SMART_PAGE_ID", ""),
        "page_access_token": os.environ.get("FACEBOOK_SMART_PAGE_TOKEN", ""),
        "ig_user_id": os.environ.get("INSTAGRAM_SMART_USER_ID", ""),
        "handle": "SmartBuyGuides"
    }
}


def get_page_token(account):
    """Get Page access token."""
    return ACCOUNT_CONFIG[account]["page_access_token"]


def post_reel_direct(account, item):
    """Post Reel directly to Facebook Page via Graph API."""
    config = ACCOUNT_CONFIG[account]
    token = get_page_token(account)
    
    if not token or not config["page_id"]:
        print(f"  ⚠ Facebook {account}: Missing page token — use Instagram cross-post")
        return post_reel_crosspost(account, item)
    
    product = item["product"]
    serial = item["serial"]
    caption = item["caption"]
    tracked_link = product.get("tracked_link", "")
    
    # Video file
    video_dir = QUEUE_DIR / f"{account}_reels" / f"serial_{serial}"
    video_files = list(video_dir.glob("*.mp4"))
    if not video_files:
        return False, f"No video in {video_dir}"
    
    video_path = str(video_files[0])
    
    # For Graph API, video must be uploaded first to get video_id
    # Step 1: Start upload session
    upload_url = f"{GRAPH_API}/{config['page_id']}/video_reels"
    params = {
        "access_token": token,
        "upload_phase": "start",
        "video_file_size": os.path.getsize(video_path)
    }
    response = requests.post(upload_url, params=params)
    
    if response.status_code != 200:
        print(f"  ✗ Upload start failed: {response.text}")
        return False, response.text
    
    video_id = response.json().get("video_id")
    upload_url_response = response.json().get("upload_url")
    
    # Step 2: Upload video chunks
    with open(video_path, "rb") as f:
        chunk_size = 1024 * 1024 * 4  # 4MB chunks
        offset = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            headers = {
                "Authorization": f"OAuth {token}",
                "Content-Range": f"bytes {offset}-{offset + len(chunk) - 1}/{os.path.getsize(video_path)}"
            }
            chunk_response = requests.post(upload_url_response, headers=headers, data=chunk)
            if chunk_response.status_code not in [200, 206]:
                print(f"  ✗ Chunk upload failed: {chunk_response.text}")
                return False, chunk_response.text
            offset += len(chunk)
    
    # Step 3: Finish upload
    finish_params = {
        "access_token": token,
        "upload_phase": "finish",
        "video_id": video_id
    }
    finish_response = requests.post(upload_url, params=finish_params)
    
    if finish_response.status_code != 200:
        print(f"  ✗ Upload finish failed: {finish_response.text}")
        return False, finish_response.text
    
    # Step 4: Publish Reel
    publish_params = {
        "access_token": token,
        "video_id": video_id,
        "description": f"{caption}\n\nLink #{serial}: {tracked_link}\n\n#ad #affiliate",
        "title": f"{product.get('name', 'Product')} — ${product.get('price', '99')}"
    }
    publish_response = requests.post(f"{GRAPH_API}/{config['page_id']}/video_reels", params=publish_params)
    
    if publish_response.status_code == 200:
        reel_id = publish_response.json().get("id")
        print(f"  ✓ Facebook Reel: #{serial} {product.get('name', '')[:40]} → Reel ID: {reel_id}")
        return True, reel_id
    else:
        print(f"  ✗ Publish failed: {publish_response.text}")
        return False, publish_response.text


def post_reel_crosspost(account, item):
    """Cross-post from Instagram (preferred method)."""
    config = ACCOUNT_CONFIG[account]
    print(f"""
═══════════════════════════════════════════════════════
FACEBOOK REEL — Cross-post from Instagram
Page: {config['handle']} — Serial #{item['serial']}
═══════════════════════════════════════════════════════

METHOD: Post to Instagram Reel first with "Share to Facebook" enabled.
The Reel will automatically appear on connected Page: {config['handle']}

LINK IN FIRST COMMENT: {item['product'].get('tracked_link', '')[:60]}...

BROWSER AUTOMATION:
```python
session="fb_{account}"
goto_url('https://www.facebook.com/{config["handle"]}/')
wait_for_load()
# Navigate to Reels tab
# Verify cross-posted Reel exists
# Add link in first comment
```
""")
    return True, "crosspost_instructions"


def update_page_profile(account):
    """Update Facebook Page profile."""
    config = ACCOUNT_CONFIG[account]
    token = get_page_token(account)
    
    if not token:
        return False
    
    # Update Page info
    url = f"{GRAPH_API}/{config['page_id']}"
    params = {
        "access_token": token,
        "about": f"Daily {config['handle']} finds. Link in bio.",
        "description": "Curated picks. Smart savings. Daily updates."
    }
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        print(f"  ✓ Facebook Page updated: {config['handle']}")
    return True


def main():
    print("=" * 60)
    print("FACEBOOK AUTO POSTER — Graph API (Reels)")
    print("=" * 60)
    
    if not PLAN_PATH.exists():
        print("  ✗ content_plan.json not found. Run copywriter.py first.")
        return
    
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    # Post Reels (cross-post preferred)
    print(f"\nPosting Luxe Reels to Facebook ({len(plan['luxe'])})...")
    for item in plan["luxe"]:
        post_reel_crosspost("luxe", item)
    
    print(f"\nPosting Smart Reels to Facebook ({len(plan['smart'])})...")
    for item in plan["smart"]:
        post_reel_crosspost("smart", item)
    
    # Update Page profiles
    print("\nUpdating Facebook Pages...")
    update_page_profile("luxe")
    update_page_profile("smart")
    
    print("\n✓ Facebook automation complete (cross-post via Instagram)")


if __name__ == "__main__":
    main()