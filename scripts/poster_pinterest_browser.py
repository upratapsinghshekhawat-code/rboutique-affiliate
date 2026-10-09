#!/usr/bin/env python3
"""
Pinterest Browser Poster — No API approval needed.
Uses browser automation with Hermes vault credentials.
"""
import json
import os
from pathlib import Path

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
PLAN_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue" / "pinterest_pins"

ACCOUNT_CONFIG = {
    "luxe": {
        "handle": "luxe_fashion_finds",
        "board_map": {
            "designer_for_less": "designer-for-less",
            "style_guide": "style-guide",
            "weekly_edit": "weekly-edit",
            "sale_alert": "sale-alert"
        }
    },
    "smart": {
        "handle": "smart_buy_guides",
        "board_map": {
            "under_budget": "under-budget",
            "seasonal_must": "seasonal-must-haves",
            "problem_solved": "problem-solved",
            "best_of": "best-of"
        }
    }
}


def get_board_name(account, pillar):
    """Get board name for pillar."""
    return ACCOUNT_CONFIG[account]["board_map"].get(pillar, ACCOUNT_CONFIG[account]["board_map"][list(ACCOUNT_CONFIG[account]["board_map"].keys())[0]])


def generate_browser_instructions(account, item):
    """Generate browser automation instructions for Pinterest pin."""
    config = ACCOUNT_CONFIG[account]
    product = item["product"]
    serial = item["serial"]
    pillar = item["pillar"]
    caption = item["caption"]
    
    board_name = get_board_name(account, pillar)
    name = product.get("name", "Product")
    brand = product.get("brand", "Brand")
    price = product.get("price", "99")
    tracked_link = product.get("tracked_link", "")
    
    # Find media file
    pin_dir = QUEUE_DIR / f"serial_{serial}"
    media_files = list(pin_dir.glob("*.mp4")) + list(pin_dir.glob("*.jpg")) + list(pin_dir.glob("*.png"))
    
    if not media_files:
        return False, f"No media in {pin_dir}"
    
    media_path = str(media_files[0])
    is_video = media_path.endswith(".mp4")
    
    title = f"{name} — {brand} | ${price}"
    description = f"{caption[:400]}... Link #{serial} in bio → @{config['handle']}"
    
    instructions = f"""
═══════════════════════════════════════════════════════
PINTEREST PIN — @{config['handle']} — Serial #{serial}
═══════════════════════════════════════════════════════

MEDIA: {media_path} ({'Video' if is_video else 'Image'})
BOARD: {board_name}
TITLE: {title[:100]}
DESCRIPTION: {description[:500]}
LINK: {tracked_link}

BROWSER AUTOMATION (Hermes):
```python
session="pinterest_{account}"
goto_url('https://www.pinterest.com/')
wait_for_load()
# vault_fill for {config['handle']} login
goto_url('https://www.pinterest.com/pin-builder/')
wait_for_load()
# Upload media: {os.path.basename(media_path)}
# Title: {title[:100]}
# Description: {description[:500]}
# Board: {board_name}
# Link: {tracked_link}
# Tags: #ad #affiliate #{pillar}
# Publish
```

MANUAL STEPS:
1. Open pinterest.com → Login as @{config['handle']}
2. Click "+" → Create pin
3. Upload: {os.path.basename(media_path)}
4. Title: {title[:100]}
5. Description: [See description in caption_{serial}.txt]
6. Board: {board_name} (create if needed)
7. Destination link: {tracked_link}
8. Add tags: #ad #affiliate #{pillar}
9. Publish
10. Copy Pin URL → Update Linktree serial #{serial}
"""
    print(instructions)
    return True, "browser_instructions_generated"


def post_multi_pin_browser(account, multi_key, multi_data):
    """Browser instructions for multi-product pin."""
    config = ACCOUNT_CONFIG[account]
    first_product = multi_data["products"][0]
    serials = multi_data["serials"]
    
    board_name = config["board_map"].get("weekly_edit" if "luxe" in multi_key else "best_of", list(config["board_map"].values())[0])
    
    title = f"{multi_data['pillar_name']} — {len(multi_data['products'])} Curated Picks"
    description = f"{multi_data['caption'][:400]}..."
    
    # Use first product image
    first_serial = serials[0]
    pin_dir = QUEUE_DIR / f"serial_{first_serial}"
    media_files = list(pin_dir.glob("*.jpg")) + list(pin_dir.glob("*.png"))
    
    media_path = str(media_files[0]) if media_files else "MISSING"
    link = first_product.get("tracked_link", "")
    
    instructions = f"""
═══════════════════════════════════════════════════════
PINTEREST MULTI-PIN — @{config['handle']} — {multi_data['pillar_name']}
═══════════════════════════════════════════════════════

MEDIA: {media_path}
BOARD: {board_name}
TITLE: {title[:100]}
DESCRIPTION: {description[:500]}
LINK: {link}

BROWSER AUTOMATION:
```python
session="pinterest_{account}"
goto_url('https://www.pinterest.com/pin-builder/')
wait_for_load()
# Upload: {os.path.basename(media_path)}
# Title: {title[:100]}
# Description: {description[:500]}
# Board: {board_name}
# Link: {link}
# Publish
```
"""
    print(instructions)
    return True, "browser_instructions_generated"


def main():
    print("=" * 60)
    print("PINTEREST BROWSER POSTER — No API Approval Needed")
    print("=" * 60)
    
    if not PLAN_PATH.exists():
        print("  ✗ content_plan.json not found. Run copywriter.py first.")
        return
    
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    print(f"\nGenerating Luxe pin instructions ({len(plan['luxe'])})...")
    for item in plan["luxe"]:
        generate_browser_instructions("luxe", item)
    
    print(f"\nGenerating Smart pin instructions ({len(plan['smart'])})...")
    for item in plan["smart"]:
        generate_browser_instructions("smart", item)
    
    print("\nGenerating multi-pin instructions...")
    for key, multi in plan.get("multi_posts", {}).items():
        account = "luxe" if "luxe" in key else "smart"
        post_multi_pin_browser(account, key, multi)
    
    print("\n✓ Pinterest browser instructions generated")
    print("  Run browser automation or follow manual steps above")


if __name__ == "__main__":
    main()