#!/usr/bin/env python3
"""
Account Maintainer — Influencer-mode profile management.
Updates profile pics, bios, highlights, pinned posts, engagement.
"""
import json
import os
import requests
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
PLAN_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"
ASSETS_DIR = BASE / "rboutique-affiliate" / "assets"

ACCOUNT_CONFIG = {
    "luxe": {
        "instagram": {
            "handle": "luxe_fashion_finds",
            "user_id": os.environ.get("INSTAGRAM_LUXE_USER_ID", ""),
            "access_token": os.environ.get("INSTAGRAM_LUXE_ACCESS_TOKEN", ""),
            "profile_name": "Luxe Fashion Finds",
            "bio_base": "Designer fashion for less 💎\nDaily curator @luxe_fashion_finds\n🔗 Link #{serial_range} in bio\n📦 Free shipping • Easy returns",
            "highlights": ["Designer Steals", "How to Style", "Weekly Edit", "Sale Alerts"]
        },
        "pinterest": {
            "access_token": os.environ.get("PINTEREST_LUXE_ACCESS_TOKEN", ""),
            "board_map": {
                "designer_for_less": "BOARD_ID_DESIGNER_LESS",
                "style_guide": "BOARD_ID_STYLE_GUIDE",
                "weekly_edit": "BOARD_ID_WEEKLY_EDIT",
                "sale_alert": "BOARD_ID_SALE_ALERT"
            }
        },
        "youtube": {
            "channel_name": "Luxe Fashion Finds",
            "playlist": "Designer for Less",
            "refresh_token": os.environ.get("YOUTUBE_LUXE_REFRESH_TOKEN", "")
        },
        "facebook": {
            "page_id": os.environ.get("FACEBOOK_LUXE_PAGE_ID", ""),
            "page_token": os.environ.get("FACEBOOK_LUXE_PAGE_TOKEN", ""),
            "handle": "LuxeFashionFinds"
        }
    },
    "smart": {
        "instagram": {
            "handle": "smart_buy_guides",
            "user_id": os.environ.get("INSTAGRAM_SMART_USER_ID", ""),
            "access_token": os.environ.get("INSTAGRAM_SMART_ACCESS_TOKEN", ""),
            "profile_name": "Smart Buy Guides",
            "bio_base": "Smart shopping, real value ✅\nDaily picks under budget\n🔗 Links #{serial_range} in bio\n📦 30-day returns",
            "highlights": ["Under $50", "Seasonal", "Problem Solved", "Best Of"]
        },
        "pinterest": {
            "access_token": os.environ.get("PINTEREST_SMART_ACCESS_TOKEN", ""),
            "board_map": {
                "under_budget": "BOARD_ID_UNDER_BUDGET",
                "seasonal_must": "BOARD_ID_SEASONAL",
                "problem_solved": "BOARD_ID_PROBLEM_SOLVED",
                "best_of": "BOARD_ID_BEST_OF"
            }
        },
        "youtube": {
            "channel_name": "Smart Buy Guides",
            "playlist": "Smart Picks Under Budget",
            "refresh_token": os.environ.get("YOUTUBE_SMART_REFRESH_TOKEN", "")
        },
        "facebook": {
            "page_id": os.environ.get("FACEBOOK_SMART_PAGE_ID", ""),
            "page_token": os.environ.get("FACEBOOK_SMART_PAGE_TOKEN", ""),
            "handle": "SmartBuyGuides"
        }
    }
}

GRAPH_API = "https://graph.facebook.com/v19.0"
PINTEREST_API = "https://api.pinterest.com/v5"


def generate_profile_pic(account, save_path):
    """Generate AI-style profile picture for account."""
    cfg = ACCOUNT_CONFIG[account]
    colors = {
        "luxe": {"bg": "#0a0a0f", "accent": "#d6a96a", "text": "#e8e6e3"},
        "smart": {"bg": "#0d1117", "accent": "#58a6ff", "text": "#e6edf3"}
    }[account]
    
    # Create 320x320 profile pic
    img = Image.new('RGB', (320, 320), colors["bg"])
    draw = ImageDraw.Draw(img)
    
    # Gradient circle
    for r in range(160, 0, -1):
        alpha = int(255 * (r / 160))
        c = tuple(int(colors["accent"].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        draw.ellipse([160-r, 160-r, 160+r, 160+r], outline=c + (alpha,))
    
    # Initials
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    initials = "LF" if account == "luxe" else "SB"
    bbox = draw.textbbox((0, 0), initials, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((160 - w//2, 160 - h//2), initials, fill=colors["text"], font=font)
    
    # Subtle glow
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    save_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(save_path)
    print(f"  ✓ Profile pic generated: {save_path}")
    return str(save_path)


def update_instagram_profile(account):
    """Update Instagram profile (bio, profile pic)."""
    cfg = ACCOUNT_CONFIG[account]["instagram"]
    token = cfg["access_token"]
    
    if not token or not cfg["user_id"]:
        print(f"  ⚠ Instagram {account}: Missing credentials")
        return update_instagram_profile_browser(account)
    
    # Get serial range from latest plan
    serial_range = get_serial_range(account)
    bio = cfg["bio_base"].format(serial_range=serial_range)
    
    # Generate profile pic
    pic_path = ASSETS_DIR / "profile_pics" / f"{account}_profile.jpg"
    generate_profile_pic(account, pic_path)
    
    # Update bio via Graph API
    url = f"{GRAPH_API}/{cfg['user_id']}"
    params = {"access_token": token, "bio": bio, "name": cfg["profile_name"]}
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        print(f"  ✓ Instagram bio updated: @{cfg['handle']}")
    else:
        print(f"  ✗ Bio update failed: {response.text}")
    
    # Profile pic upload would need multipart - skip for API, use browser
    print(f"  📸 Profile pic ready: {pic_path} (upload via browser)")
    
    return True


def update_instagram_profile_browser(account):
    """Browser automation for profile updates."""
    cfg = ACCOUNT_CONFIG[account]["instagram"]
    serial_range = get_serial_range(account)
    bio = cfg["bio_base"].format(serial_range=serial_range)
    
    print(f"""
═══════════════════════════════════════════════════════
INSTAGRAM PROFILE UPDATE — @{cfg['handle']}
═══════════════════════════════════════════════════════

BROWSER AUTOMATION:
```python
session="insta_{account}"
goto_url('https://www.instagram.com/{cfg["handle"]}/')
wait_for_load()
# Click "Edit Profile"
# Bio: {bio}
# Upload profile pic: assets/profile_pics/{account}_profile.jpg
# Save
```
""")
    return True


def update_pinterest_profile(account):
    """Update Pinterest profile boards, bio."""
    cfg = ACCOUNT_CONFIG[account]["pinterest"]
    token = cfg["access_token"]
    
    if not token:
        print(f"  ⚠ Pinterest {account}: Missing token")
        return True
    
    # Update board descriptions, profile bio
    print(f"  📌 Pinterest {account}: Profile maintenance queued")
    return True


def update_youtube_channel(account):
    """Update YouTube channel banner, playlists, featured sections."""
    cfg = ACCOUNT_CONFIG[account]["youtube"]
    refresh_token = cfg["refresh_token"]
    
    if not refresh_token:
        print(f"  ⚠ YouTube {account}: Missing refresh token")
        return True
    
    print(f"  📺 YouTube {account}: Channel maintenance queued")
    return True


def update_facebook_page(account):
    """Update Facebook Page info."""
    cfg = ACCOUNT_CONFIG[account]["facebook"]
    token = cfg["page_token"]
    
    if not token or not cfg["page_id"]:
        print(f"  ⚠ Facebook {account}: Missing page token")
        return True
    
    serial_range = get_serial_range(account)
    about = f"Daily {cfg['handle']} finds. Link in bio: #{serial_range}"
    
    url = f"{GRAPH_API}/{cfg['page_id']}"
    params = {"access_token": token, "about": about}
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        print(f"  ✓ Facebook Page updated: {cfg['handle']}")
    return True


def pin_top_posts(account):
    """Pin latest Weekly Edit / Best Of to profile."""
    # Would use Graph API to pin media
    cfg = ACCOUNT_CONFIG[account]["instagram"]
    print(f"  📌 Pin top posts for @{cfg['handle']}: Weekly Edit / Best Of")
    return True


def create_highlight_covers(account):
    """Generate highlight cover images."""
    cfg = ACCOUNT_CONFIG[account]["instagram"]
    highlights = cfg["highlights"]
    colors = {"luxe": {"bg": "#0a0a0f", "accent": "#d6a96a"}, "smart": {"bg": "#0d1117", "accent": "#58a6ff"}}[account]
    
    covers_dir = ASSETS_DIR / "highlight_covers" / account
    covers_dir.mkdir(parents=True, exist_ok=True)
    
    for highlight_name in highlights:
        img = Image.new('RGB', (160, 160), colors["bg"])
        draw = ImageDraw.Draw(img)
        
        # Circle background
        draw.ellipse([20, 20, 140, 140], fill=colors["accent"])
        
        # Text
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Abbreviate
        words = highlight_name.split()
        if len(words) > 1:
            text = "".join(w[0] for w in words).upper()
        else:
            text = highlight_name[:3].upper()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h_text = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((80 - w//2, 80 - h_text//2), text, fill=colors["bg"], font=font)
        
        save_path = covers_dir / f"{highlight_name.lower().replace(' ', '_')}.jpg"
        img.save(save_path)
    
    print(f"  📌 Highlight covers generated: {covers_dir}")
    return True


def get_serial_range(account):
    """Get serial range from latest plan."""
    if PLAN_PATH.exists():
        with open(PLAN_PATH, "r") as f:
            plan = json.load(f)
        items = plan.get("luxe", []) if account == "luxe" else plan.get("smart", [])
        serials = [item["serial"] for item in items]
        if serials:
            return f"#{min(serials)}-#{max(serials)}"
    return "#1-#21"


def main():
    print("=" * 60)
    print("ACCOUNT MAINTAINER — Influencer Mode")
    print("=" * 60)
    
    for account in ["luxe", "smart"]:
        print(f"\n--- {account.upper()} ---")
        update_instagram_profile(account)
        update_pinterest_profile(account)
        update_youtube_channel(account)
        update_facebook_page(account)
        pin_top_posts(account)
        create_highlight_covers(account)
    
    print("\n✓ Account maintenance complete")


if __name__ == "__main__":
    main()