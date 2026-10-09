#!/usr/bin/env python3
"""
Instagram Poster — Browser automation using saved vault credentials.
Posts Reels via Instagram web interface.
"""
import json
import time
from pathlib import Path

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue"

# Account mappings
ACCOUNTS = {
    "luxe": {
        "username": "luxefashionf",
        "vault_label": "luxe insta",
        "profile_url": "https://www.instagram.com/luxe_fashion_finds/"
    },
    "smart": {
        "username": "smart_buy_guides",
        "vault_label": "smartbuy insta",
        "profile_url": "https://www.instagram.com/smart_buy_guides/"
    }
}

LINKTREE_URLS = {
    "luxe": "https://linktr.ee/luxefashionfinds",
    "smart": "https://linktr.ee/smartbuyguides"
}


def post_reel_browser(account, video_path, caption, serial):
    """
    Browser automation to post Instagram Reel.
    Requires Hermes browser automation with vault credentials.
    """
    print(f"""
═══════════════════════════════════════════════════════
INSTAGRAM REEL POST — Account: @{ACCOUNTS[account]['username']}
Serial: #{serial}
═══════════════════════════════════════════════════════

MANUAL STEPS (until browser automation is wired):
1. Open browser → instagram.com
2. Login as {ACCOUNTS[account]['username']} (vault: {ACCOUNTS[account]['vault_label']})
3. Click "+" → Reel → Upload video: {video_path.name}
4. Caption: [see caption_{serial}.txt in same folder]
5. Add location: Worldwide
6. Turn ON "Share to Facebook" (if FB page connected)
7. Post
8. Copy Reel URL → update Linktree (serial #{serial})

AUTOMATION CODE (for browser_exec):
```python
# In Hermes browser_exec with session="insta_{account}"
goto_url('https://www.instagram.com/')
wait_for_load()
# Login handled by vault_fill
# Navigate to Reels creation
# Upload video, paste caption, post
```

Caption preview:
{caption[:200]}...

Linktree entry: #{serial} → {video_path.stem}
Linktree URL: {LINKTREE_URLS[account]}
""")
    return True


def update_linktree(account, serial, product_name, tracked_link):
    """
    Update Linktree via API or browser.
    Linktree API: https://linktr.ee/api-docs
    """
    print(f"""
LINKTREE UPDATE — {LINKTREE_URLS[account]}
Add entry: #{serial} {product_name} → {tracked_link[:60]}...

API endpoint: PATCH https://api.linktr.ee/v2/links
Auth: Bearer {LINKTREE_URLS[account]}_token (from vault)
""")
    return True


def main():
    print("=" * 60)
    print("INSTAGRAM POSTER — Browser Automation")
    print("=" * 60)
    
    reels_dir = QUEUE_DIR / "luxe_reels"
    if not reels_dir.exists():
        print("  ✗ No reels queue found. Run asset_generator.py first.")
        return
    
    print("""
⚠️  BROWSER AUTOMATION TEMPLATE

This script generates the step-by-step instructions for manual posting.
Full browser automation requires wiring to Hermes browser_exec with vault credentials.

Current queue:""")
    
    for account in ["luxe", "smart"]:
        account_dir = QUEUE_DIR / f"{account}_reels"
        if account_dir.exists():
            for serial_dir in account_dir.iterdir():
                if serial_dir.is_dir():
                    meta_files = list(serial_dir.glob("meta_*.json"))
                    caption_files = list(serial_dir.glob("caption_*.txt"))
                    video_files = list(serial_dir.glob("*.mp4"))
                    
                    for mf in meta_files:
                        with open(mf, "r") as f:
                            meta = json.load(f)
                        serial = meta.get("serial")
                        product_name = meta.get("product", {}).get("name", "Product")
                        tracked_link = meta.get("product", {}).get("tracked_link", "")
                        
                        caption = ""
                        if caption_files:
                            with open(caption_files[0], "r") as f:
                                caption = f.read()
                        
                        print(f"\n  @{ACCOUNTS[account]['username']} — Serial #{serial}")
                        print(f"    Product: {product_name}")
                        print(f"    Video: {'✓ Ready' if video_files else '✗ MISSING — export from CapCut'}")
                        print(f"    Caption: {'✓' if caption_files else '✗'}")
                        print(f"    Tracked link: {tracked_link[:60]}...")
                        
                        # Show the posting instructions
                        if video_files:
                            post_reel_browser(account, video_files[0], caption, serial)
                            update_linktree(account, serial, product_name, tracked_link)
    
    print("\n✓ Instructions generated. Execute manually or wire browser automation.")


if __name__ == "__main__":
    main()