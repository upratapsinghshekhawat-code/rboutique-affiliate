#!/usr/bin/env python3
"""
Pinterest Poster — Uses Pinterest API v5 to create pins.
Reads assets from content/queue/pinterest_pins/
"""
import json
import os
import requests
from pathlib import Path

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue" / "pinterest_pins"

# Pinterest API config
PINTEREST_API = "https://api.pinterest.com/v5"

# Board IDs - UPDATE THESE WITH YOUR ACTUAL BOARD IDs
BOARD_IDS = {
    "luxe": {
        "Designer Clothing": "BOARD_ID_1",
        "Luxury Bags & Totes": "BOARD_ID_2", 
        "Designer Shoes": "BOARD_ID_3",
        "Fine Jewelry & Accessories": "BOARD_ID_4",
        "Beauty & Fragrance": "BOARD_ID_5",
        "Luxury Sale Alerts": "BOARD_ID_6"
    },
    "smart": {
        "Tech Under $200": "BOARD_ID_7",
        "Home & Kitchen Essentials": "BOARD_ID_8",
        "Fitness & Outdoors": "BOARD_ID_9",
        "Kitchen Gadgets Under $50": "BOARD_ID_10",
        "Seasonal Must-Haves": "BOARD_ID_11",
        "Problem Solvers": "BOARD_ID_12"
    }
}


def get_access_token(account):
    """Get valid access token from vault (would use refresh token in production)."""
    # In production, this would use the refresh token to get a new access token
    # For now, we expect access token to be in vault
    token_name = f"pinterest_{account}_access_token"
    # This would be retrieved from Hermes vault at runtime
    return os.environ.get(f"PINTEREST_{account.upper()}_ACCESS_TOKEN", "")


def create_pin(account, image_path, title, description, link, board_name, alt_text):
    """Create a pin via Pinterest API."""
    
    access_token = get_access_token(account)
    if not access_token:
        print(f"  ✗ No access token for {account}")
        return False
    
    board_id = BOARD_IDS.get(account, {}).get(board_name)
    if not board_id:
        print(f"  ✗ Board ID not found for {board_name}")
        return False
    
    url = f"{PINTEREST_API}/pins"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Upload image first (Pinterest requires media upload)
    # For simplicity, we assume image is hosted or use media upload endpoint
    # In production: upload to Pinterest media endpoint, get media_id
    
    data = {
        "board_id": board_id,
        "title": title[:100],  # Max 100 chars
        "description": description[:500],  # Max 500 chars
        "link": link,
        "alt_text": alt_text[:500],
        "media_source": {
            "source_type": "image_url",
            "content_type": "image/jpeg",
            "data": image_path  # This should be a hosted URL
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"  ✓ Pin created: {title[:50]}")
        return True
    else:
        print(f"  ✗ Pin failed: {response.status_code} - {response.text}")
        return False


def main():
    print("=" * 60)
    print("PINTEREST POSTER — API v5")
    print("=" * 60)
    
    if not QUEUE_DIR.exists():
        print("  ✗ Queue directory not found. Run asset_generator.py first.")
        return
    
    # This is a template - actual posting requires valid tokens and hosted images
    # The script shows the structure; real implementation needs:
    # 1. Valid access tokens from vault
    # 2. Images hosted on accessible URLs (or upload via Pinterest media API)
    # 3. Correct board IDs
    
    print("""
⚠️  TEMPLATE MODE - NOT POSTING FOR REAL

To enable real posting:
1. Replace BOARD_IDS with actual board IDs from Pinterest
2. Implement token refresh using refresh_token from vault
3. Host images on CDN or use Pinterest media upload API
4. Run with actual credentials

Current queue contents:""")
    
    for pin_dir in QUEUE_DIR.iterdir():
        if pin_dir.is_dir():
            meta_files = list(pin_dir.glob("*_meta.json"))
            for mf in meta_files:
                with open(mf, "r") as f:
                    meta = json.load(f)
                print(f"  • Serial #{meta.get('serial')}: {meta.get('product', {}).get('name', 'Unknown')}")
                print(f"    Board: {meta.get('board_suggestions')}")
                print(f"    Image: {meta.get('image_path')}")
                print(f"    Link: {meta.get('link')[:60]}...")
    
    print("\n✓ Ready for deployment when tokens arrive")


if __name__ == "__main__":
    main()