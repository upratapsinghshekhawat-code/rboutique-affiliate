#!/usr/bin/env python3
"""
Pinterest Auto Poster — Full browser automation with Hermes vault.
Actually posts pins, no manual steps.
"""
import json
import os
from pathlib import Path

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
PLAN_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue" / "pinterest_pins"

ACCOUNT_CONFIG = {
    "luxe": {
        "vault_user": "pinterest_luxe_login",
        "board_map": {
            "designer_for_less": "designer-for-less",
            "style_guide": "style-guide",
            "weekly_edit": "weekly-edit",
            "sale_alert": "sale-alert"
        }
    },
    "smart": {
        "vault_user": "pinterest_smart_login",
        "board_map": {
            "under_budget": "under-budget",
            "seasonal_must": "seasonal-must-haves",
            "problem_solved": "problem-solved",
            "best_of": "best-of"
        }
    }
}


def get_board_name(account, pillar):
    return ACCOUNT_CONFIG[account]["board_map"].get(pillar, list(ACCOUNT_CONFIG[account]["board_map"].values())[0])


def post_pin_browser(account, item):
    """Execute browser automation to post a Pinterest pin."""
    config = ACCOUNT_CONFIG[account]
    product = item["product"]
    serial = item["serial"]
    pillar = item["pillar"]
    caption = item["caption"]
    tracked_link = product.get("tracked_link", "")
    
    name = product.get("name", "Product")
    brand = product.get("brand", "Brand")
    price = product.get("price", "99")
    
    board_name = get_board_name(account, pillar)
    title = f"{name} - {brand} | ${price}"
    description = f"{caption[:400]}... Link #{serial} in bio"
    
    # Find media
    pin_dir = QUEUE_DIR / f"serial_{serial}"
    media_files = list(pin_dir.glob("*.mp4")) + list(pin_dir.glob("*.jpg")) + list(pin_dir.glob("*.png"))
    
    if not media_files:
        print(f"  Pinterest {account} #{serial}: No media in {pin_dir}")
        return None
    
    media_path = str(media_files[0])
    is_video = media_path.endswith(".mp4")
    media_type = "video/mp4" if is_video else "image/jpeg"
    media_basename = os.path.basename(media_path)
    
    print(f"  Pinterest {account} #{serial}: Preparing automation for '{name[:40]}'")
    
    # Return automation steps as dict for orchestrator
    return {
        "account": account,
        "serial": serial,
        "session": f"pinterest_{account}",
        "vault_handle": config['vault_user'],
        "steps": [
            {"action": "goto", "url": "https://www.pinterest.com/"},
            {"action": "wait"},
            {"action": "vault_fill", "handle": config['vault_user']},
            {"action": "goto", "url": "https://www.pinterest.com/pin-builder/"},
            {"action": "wait"},
            {"action": "upload_media", "media_path": media_path, "media_type": media_type},
            {"action": "fill_title", "title": title[:100]},
            {"action": "fill_description", "description": description[:500]},
            {"action": "select_board", "board_name": board_name},
            {"action": "fill_link", "link": tracked_link},
            {"action": "publish"}
        ]
    }


def main():
    print("=" * 60)
    print("PINTEREST AUTO POSTER - Browser Automation Steps Generator")
    print("=" * 60)
    
    if not PLAN_PATH.exists():
        print("  content_plan.json not found. Run copywriter.py first.")
        return
    
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    all_steps = []
    
    print(f"\nGenerating Luxe pin automation ({len(plan['luxe'])})...")
    for item in plan["luxe"]:
        steps = post_pin_browser("luxe", item)
        if steps:
            all_steps.append(steps)
    
    print(f"\nGenerating Smart pin automation ({len(plan['smart'])})...")
    for item in plan["smart"]:
        steps = post_pin_browser("smart", item)
        if steps:
            all_steps.append(steps)
    
    # Save automation steps for orchestrator
    auto_file = BASE / "rboutique-affiliate" / "scripts" / "pinterest_automation_steps.json"
    with open(auto_file, "w") as f:
        json.dump(all_steps, f, indent=2)
    
    print(f"\nAutomation steps saved: {auto_file}")
    print("  Orchestrator will execute via browser_exec")


if __name__ == "__main__":
    main()