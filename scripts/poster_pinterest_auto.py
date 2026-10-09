#!/usr/bin/env python3
"""
Pinterest Auto Poster — Full API v5 automation.
Posts pins with video/images, board selection, hashtags, linktree serials.
"""
import json
import os
import requests
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
PLAN_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue" / "pinterest_pins"

PINTEREST_API = "https://api.pinterest.com/v5"

# Board IDs - UPDATE WITH YOUR ACTUAL BOARD IDs FROM PINTEREST
BOARD_IDS = {
    "luxe": {
        "designer_for_less": "BOARD_ID_DESIGNER_LESS",
        "style_guide": "BOARD_ID_STYLE_GUIDE", 
        "weekly_edit": "BOARD_ID_WEEKLY_EDIT",
        "sale_alert": "BOARD_ID_SALE_ALERT"
    },
    "smart": {
        "under_budget": "BOARD_ID_UNDER_BUDGET",
        "seasonal_must": "BOARD_ID_SEASONAL",
        "problem_solved": "BOARD_ID_PROBLEM_SOLVED",
        "best_of": "BOARD_ID_BEST_OF"
    }
}

# Default board fallback
DEFAULT_BOARDS = {
    "luxe": "BOARD_ID_DESIGNER_LESS",
    "smart": "BOARD_ID_UNDER_BUDGET"
}


def get_access_token(account):
    """Get valid access token from vault via environment."""
    # In production: use refresh token to get new access token
    # For now, expect access token in environment
    return os.environ.get(f"PINTEREST_{account.upper()}_ACCESS_TOKEN", "")


def refresh_access_token(account):
    """Refresh access token using refresh token from vault."""
    refresh_token = os.environ.get(f"PINTEREST_{account.upper()}_REFRESH_TOKEN", "")
    client_id = os.environ.get(f"PINTEREST_{account.upper()}_CLIENT_ID", "")
    client_secret = os.environ.get(f"PINTEREST_{account.upper()}_CLIENT_SECRET", "")
    
    if not all([refresh_token, client_id, client_secret]):
        return None
    
    url = "https://api.pinterest.com/v5/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get("access_token")
        new_refresh = tokens.get("refresh_token", refresh_token)
        # Save new tokens (would update vault/env)
        os.environ[f"PINTEREST_{account.upper()}_ACCESS_TOKEN"] = access_token
        return access_token
    return None


def upload_media(access_token, media_path):
    """Upload media to Pinterest and return media_id."""
    url = f"{PINTEREST_API}/media"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    with open(media_path, "rb") as f:
        files = {"media": (os.path.basename(media_path), f, "image/jpeg" if media_path.endswith(".jpg") else "video/mp4")}
        data = {"media_type": "image" if media_path.endswith(".jpg") else "video"}
        response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 201:
        return response.json().get("media_id")
    return None


def create_pin(access_token, board_id, title, description, link, media_id, alt_text):
    """Create a pin with uploaded media."""
    url = f"{PINTEREST_API}/pins"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "board_id": board_id,
        "title": title[:100],
        "description": description[:500],
        "link": link,
        "alt_text": alt_text[:500],
        "media_source": {
            "source_type": "media_id",
            "media_id": media_id
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 201, response.json() if response.status_code == 201 else response.text


def post_product_pin(account, item, plan_item):
    """Post a single product pin."""
    access_token = get_access_token(account)
    if not access_token:
        # Try refresh
        access_token = refresh_access_token(account)
        if not access_token:
            return False, "No valid access token"
    
    product = item["product"]
    serial = item["serial"]
    pillar = item["pillar"]
    caption = item["caption"]
    
    # Board selection
    board_id = BOARD_IDS.get(account, {}).get(pillar, DEFAULT_BOARDS[account])
    
    # Prepare pin content
    name = product.get("name", "Product")
    brand = product.get("brand", "Brand")
    price = product.get("price", "99")
    tracked_link = product.get("tracked_link", "")
    
    title = f"{name} — {brand} | ${price}"
    description = f"{caption[:400]}... Link #{serial} in bio"
    alt_text = f"{name} by {brand}, {product.get('category', 'item')}, ${price}"
    
    # Find media file (prefer video, fallback to image)
    pin_dir = QUEUE_DIR / f"serial_{serial}"
    media_files = list(pin_dir.glob("*.mp4")) + list(pin_dir.glob("*.jpg")) + list(pin_dir.glob("*.png"))
    
    if not media_files:
        return False, f"No media found in {pin_dir}"
    
    media_path = str(media_files[0])
    
    # Upload media
    media_id = upload_media(access_token, media_path)
    if not media_id:
        return False, "Media upload failed"
    
    # Create pin
    success, result = create_pin(access_token, board_id, title, description, tracked_link, media_id, alt_text)
    
    if success:
        print(f"  ✓ Pinterest: #{serial} {name[:40]} → Pin ID: {result.get('id')}")
        return True, result.get("id")
    else:
        print(f"  ✗ Pinterest: #{serial} failed — {result}")
        return False, result


def post_multi_pin(account, multi_key, multi_data):
    """Post multi-product carousel pin."""
    access_token = get_access_token(account)
    if not access_token:
        access_token = refresh_access_token(account)
        if not access_token:
            return False, "No valid access token"
    
    # For carousel, we'd need multiple media IDs
    # Simplified: post as single pin with first product image
    first_product = multi_data["products"][0]
    serials = multi_data["serials"]
    
    board_id = DEFAULT_BOARDS[account]
    
    title = f"{multi_data['pillar_name']} — {len(multi_data['products'])} Picks"
    description = f"{multi_data['caption'][:400]}..."
    alt_text = f"{len(multi_data['products'])} curated {first_product.get('category', 'items')}"
    
    pin_dir = QUEUE_DIR / f"multi_{multi_key}"
    media_files = list(pin_dir.glob("*.jpg")) + list(pin_dir.glob("*.png"))
    
    if not media_files:
        # Use first product's image
        first_serial = serials[0]
        pin_dir = QUEUE_DIR / f"serial_{first_serial}"
        media_files = list(pin_dir.glob("*.jpg")) + list(pin_dir.glob("*.png"))
    
    if not media_files:
        return False, "No media for multi-pin"
    
    media_path = str(media_files[0])
    media_id = upload_media(access_token, media_path)
    if not media_id:
        return False, "Media upload failed"
    
    # Use first product link as primary
    link = first_product.get("tracked_link", "")
    
    success, result = create_pin(access_token, board_id, title, description, link, media_id, alt_text)
    
    if success:
        print(f"  ✓ Pinterest Multi: {multi_data['pillar_name']} → Pin ID: {result.get('id')}")
        return True, result.get("id")
    return False, result


def main():
    print("=" * 60)
    print("PINTEREST AUTO POSTER — API v5")
    print("=" * 60)
    
    if not PLAN_PATH.exists():
        print("  ✗ content_plan.json not found. Run copywriter.py first.")
        return
    
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    print(f"\nPosting Luxe pins ({len(plan['luxe'])})...")
    for item in plan["luxe"]:
        post_product_pin("luxe", item, plan)
    
    print(f"\nPosting Smart pins ({len(plan['smart'])})...")
    for item in plan["smart"]:
        post_product_pin("smart", item, plan)
    
    print("\nPosting multi-pins...")
    for key, multi in plan.get("multi_posts", {}).items():
        account = "luxe" if "luxe" in key else "smart"
        post_multi_pin(account, key, multi)
    
    print("\n✓ Pinterest posting complete")


if __name__ == "__main__":
    main()