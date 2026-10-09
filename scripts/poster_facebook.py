#!/usr/bin/env python3
"""
Facebook Poster — Browser automation (shares from Instagram session).
Posts Reels to Facebook Pages via Instagram cross-posting or direct.
"""
import json
from pathlib import Path

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue"

# Facebook Pages linked to Instagram Business accounts
FB_PAGES = {
    "luxe": {
        "page_name": "Luxe Fashion Finds",
        "page_url": "https://www.facebook.com/LuxeFashionFinds",
        "insta_account": "luxe_fashion_finds"
    },
    "smart": {
        "page_name": "Smart Buy Guides",
        "page_url": "https://www.facebook.com/SmartBuyGuides",
        "insta_account": "smart_buy_guides"
    }
}


def post_reel_facebook(account, video_path, caption, serial):
    """
    Post Reel to Facebook Page.
    Best done via Instagram cross-posting (enable when posting to IG).
    Or direct via Facebook Pages API / browser automation.
    """
    print(f"""
═══════════════════════════════════════════════════════
FACEBOOK REEL POST — Page: {FB_PAGES[account]['page_name']}
Serial: #{serial}
═══════════════════════════════════════════════════════

OPTION 1: Cross-post from Instagram (RECOMMENDED)
- When posting Reel on Instagram, toggle "Share to Facebook"
- Select page: {FB_PAGES[account]['page_name']}
- Post goes live on both simultaneously

OPTION 2: Direct Facebook Browser Automation
1. Open browser → facebook.com
2. Login (same session as Instagram vault)
3. Go to Page: {FB_PAGES[account]['page_url']}
4. Click "Reel" → Upload video
5. Caption: [from caption_{serial}.txt]
6. Add link in first comment (FB allows links in comments)
7. Post

AUTOMATION CODE (browser_exec):
```python
session="fb_{account}"
goto_url('{FB_PAGES[account]['page_url']}')
wait_for_load()
# Navigate to Reels creation
# Upload, caption, post
```

Caption: {caption[:150]}...
Link in first comment: [tracked_link from meta]
""")
    return True


def main():
    print("=" * 60)
    print("FACEBOOK POSTER — Cross-post / Browser Automation")
    print("=" * 60)
    print("""
⚠️  TEMPLATE MODE

Best approach: Enable cross-posting when posting to Instagram.
Facebook Reels from Instagram get better reach anyway.

If direct posting needed, use browser automation with
same vault credentials as Instagram.

Queue contents:""")
    
    for account in ["luxe", "smart"]:
        account_dir = QUEUE_DIR / f"{account}_reels"
        if account_dir.exists():
            for serial_dir in account_dir.iterdir():
                if serial_dir.is_dir():
                    meta_files = list(serial_dir.glob("meta_*.json"))
                    for mf in meta_files:
                        with open(mf, "r") as f:
                            meta = json.load(f)
                        serial = meta.get("serial")
                        print(f"  {FB_PAGES[account]['page_name']} — Serial #{serial}: {meta.get('product', {}).get('name', 'Product')[:40]}")
    
    print("\n✓ Cross-post from Instagram Reels for best results.")


if __name__ == "__main__":
    main()