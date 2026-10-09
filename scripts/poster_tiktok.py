#!/usr/bin/env python3
"""
TikTok Poster — Browser automation using saved vault credentials.
Posts to TikTok via web interface.
"""
import json
from pathlib import Path

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue"

ACCOUNTS = {
    "luxe": {
        "username": "luxefashionfinds",
        "vault_label": "tiktok_luxe_login",
        "profile_url": "https://www.tiktok.com/@luxefashionfinds"
    },
    "smart": {
        "username": "smartbuyguides",
        "vault_label": "tiktok_smart_login",
        "profile_url": "https://www.tiktok.com/@smartbuyguides"
    }
}


def post_tiktok_browser(account, video_path, caption, serial):
    """Browser automation to post TikTok."""
    print(f"""
═══════════════════════════════════════════════════════
TIKTOK POST — Account: @{ACCOUNTS[account]['username']}
Serial: #{serial}
═══════════════════════════════════════════════════════

MANUAL STEPS:
1. Open browser → tiktok.com/upload
2. Login as {ACCOUNTS[account]['username']} (vault: {ACCOUNTS[account]['vault_label']})
3. Click "Upload" → Select video: {video_path.name}
4. Caption: [see caption_{serial}.txt] + hashtags
5. Add link in bio (Linktree): {ACCOUNTS[account]['profile_url']}
6. Settings: Allow comments, duet, stitch
7. Post
8. Copy video URL → update Linktree (serial #{serial})

AUTOMATION CODE (browser_exec):
```python
session="tiktok_{account}"
goto_url('https://www.tiktok.com/upload')
wait_for_load()
# vault_fill for login
# Upload video via file input
# Fill caption
# Post
```

Caption preview:
{caption[:200]}...
""")
    return True


def main():
    print("=" * 60)
    print("TIKTOK POSTER — Browser Automation")
    print("=" * 60)
    print("⚠️  TEMPLATE MODE - Manual posting instructions")
    
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
                        print(f"  @{ACCOUNTS[account]['username']} — Serial #{serial}: {meta.get('product', {}).get('name', 'Product')[:40]}")


if __name__ == "__main__":
    main()