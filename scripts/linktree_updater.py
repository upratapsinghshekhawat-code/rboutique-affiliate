#!/usr/bin/env python3
"""
Linktree Updater — Updates Linktree with serial-numbered affiliate links.
Uses Linktree API v2.
"""
import json
import os
import requests
from pathlib import Path

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
FEED_PATH = BASE / "rboutique-affiliate" / "scripts" / "traffic_feed.json"

LINKTREE_ACCOUNTS = {
    "luxe": {
        "username": "luxefashionfinds",
        "api_token": os.environ.get("LINKTREE_LUXE_TOKEN", ""),
        "base_url": "https://linktr.ee/luxefashionfinds"
    },
    "smart": {
        "username": "smartbuyguides",
        "api_token": os.environ.get("LINKTREE_SMART_TOKEN", ""),
        "base_url": "https://linktr.ee/smartbuyguides"
    }
}

LINKTREE_API = "https://api.linktr.ee/v2"


def update_linktree(account, products):
    """Add/update links for an account."""
    
    token = LINKTREE_ACCOUNTS[account]["api_token"]
    if not token:
        print(f"  ✗ No API token for {account}")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get existing links
    response = requests.get(f"{LINKTREE_API}/links", headers=headers)
    existing = {}
    if response.status_code == 200:
        for link in response.json().get("links", []):
            existing[link.get("title", "")] = link.get("id")
    
    # Add/update links for this run's products
    for p in products:
        if p.get("account") != account:
            continue
        
        serial = p.get("serial", 0)
        name = p.get("name", "Product")
        brand = p.get("brand", "")
        tracked = p.get("tracked_link", "")
        
        title = f"#{serial} {name}"
        if brand:
            title += f" — {brand}"
        
        # Truncate for Linktree
        title = title[:80]
        
        data = {
            "title": title,
            "url": tracked,
            "enabled": True
        }
        
        if title in existing:
            # Update existing
            link_id = existing[title]
            resp = requests.patch(f"{LINKTREE_API}/links/{link_id}", headers=headers, json=data)
            action = "Updated"
        else:
            # Create new
            resp = requests.post(f"{LINKTREE_API}/links", headers=headers, json=data)
            action = "Created"
        
        if resp.status_code in [200, 201]:
            print(f"  ✓ {action}: #{serial} {name[:40]}")
        else:
            print(f"  ✗ Failed: {resp.status_code} - {resp.text}")
    
    return True


def main():
    print("=" * 60)
    print("LINKTREE UPDATER — API v2")
    print("=" * 60)
    
    if not FEED_PATH.exists():
        print("  ✗ traffic_feed.json not found. Run run_unified_automation.py first.")
        return
    
    with open(FEED_PATH, "r", encoding="utf-8") as f:
        feed = json.load(f)
    
    products = feed.get("products", [])
    print(f"Loaded {len(products)} products")
    
    # Group by account
    luxe_products = [p for p in products if p.get("account") == "luxe"]
    smart_products = [p for p in products if p.get("account") == "smart"]
    
    print(f"  Luxe: {len(luxe_products)} links")
    print(f"  Smart: {len(smart_products)} links")
    
    print("""
⚠️  TEMPLATE MODE - Requires Linktree API tokens

To enable:
1. Get API tokens from Linktree developer settings
2. Save in vault/environment:
   LINKTREE_LUXE_TOKEN
   LINKTREE_SMART_TOKEN
3. Run this script after each automation cycle

Current plan:""")
    
    for p in luxe_products[:5]:
        print(f"  Luxe: #{p.get('serial')} {p.get('name', 'Product')[:40]} → {p.get('tracked_link', '')[:50]}...")
    for p in smart_products[:5]:
        print(f"  Smart: #{p.get('serial')} {p.get('name', 'Product')[:40]} → {p.get('tracked_link', '')[:50]}...")
    
    print(f"\n  ... and {len(luxe_products) + len(smart_products) - 10} more")
    print("\n✓ Ready when tokens available")


if __name__ == "__main__":
    main()