#!/usr/bin/env python3
"""
Facebook Browser Poster — No API tokens needed.
Uses browser automation with Hermes vault credentials (email + password).
Posts Reels directly to Pages.
"""
import json
import os
from pathlib import Path

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
PLAN_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue"

ACCOUNT_CONFIG = {
    "luxe": {
        "handle": "LuxeFashionFinds",
        "page_name": "Luxe Fashion Finds"
    },
    "smart": {
        "handle": "SmartBuyGuides",
        "page_name": "Smart Buy Guides"
    }
}


def generate_browser_instructions(account, item):
    """Generate browser automation instructions for Facebook Reel."""
    config = ACCOUNT_CONFIG[account]
    product = item["product"]
    serial = item["serial"]
    pillar = item["pillar"]
    caption = item["caption"]
    tracked_link = product.get("tracked_link", "")
    
    name = product.get("name", "Product")
    brand = product.get("brand", "Brand")
    price = product.get("price", "99")
    
    # Find video file
    video_dir = QUEUE_DIR / f"{account}_reels" / f"serial_{serial}"
    video_files = list(video_dir.glob("*.mp4"))
    
    if not video_files:
        return False, f"No video in {video_dir}"
    
    video_path = str(video_files[0])
    
    # Truncate caption for Facebook (limit ~2000 chars, but keep it reasonable)
    fb_caption = f"""{caption[:1500]}

🔗 Link #{serial}: {tracked_link}
📱 Follow {config['page_name']} for daily finds!

#ad #affiliate #{pillar.replace('_', '')}"""
    
    instructions = f"""
═══════════════════════════════════════════════════════
FACEBOOK REEL — {config['page_name']} — Serial #{serial}
═══════════════════════════════════════════════════════

VIDEO: {video_path}
PAGE: {config['page_name']} (@{config['handle']})
CAPTION: {fb_caption[:200]}...
LINK IN FIRST COMMENT: {tracked_link}

BROWSER AUTOMATION (Hermes):
```python
session="fb_{account}"
goto_url('https://www.facebook.com/{config["handle"]}/')
wait_for_load()
# vault_fill for {config["handle"]} login (email + password)
goto_url('https://www.facebook.com/reels/create/')
wait_for_load()
# Upload video: {os.path.basename(video_path)}
# Paste caption
# Location: Worldwide
# Audience: Public
# Advanced: "Label as branded content" (optional)
# Post
# After posting: Click Reel → Add comment with Link #{serial}: {tracked_link}
# Copy Reel URL for records
```

MANUAL STEPS:
1. Open facebook.com → Login as Page ({config['page_name']})
2. Click "Reels" → "Create Reel"
3. Upload: {os.path.basename(video_path)}
4. Caption: [See above]
5. Location: Worldwide
6. Audience: Public
7. Post
8. Go to Reel → Add first comment: "Link #{serial}: {tracked_link}"
9. Done
"""
    print(instructions)
    return True, "browser_instructions_generated"


def main():
    print("=" * 60)
    print("FACEBOOK BROWSER POSTER — No API Tokens Needed")
    print("=" * 60)
    
    if not PLAN_PATH.exists():
        print("  ✗ content_plan.json not found. Run copywriter.py first.")
        return
    
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    print(f"\nGenerating Luxe Reel instructions ({len(plan['luxe'])})...")
    for item in plan["luxe"]:
        generate_browser_instructions("luxe", item)
    
    print(f"\nGenerating Smart Reel instructions ({len(plan['smart'])})...")
    for item in plan["smart"]:
        generate_browser_instructions("smart", item)
    
    print("\n✓ Facebook browser instructions generated")
    print("  Uses your existing Page logins from Hermes vault")
    print("  No Page Access Tokens needed!")


if __name__ == "__main__":
    main()