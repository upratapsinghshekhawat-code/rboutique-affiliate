#!/usr/bin/env python3
"""
Linktree Auto Updater — Full API v2 automation.
Manages serial-numbered links, archives old, updates titles.
"""
import json
import os
import sys
from pathlib import Path

# Add credentials loader
SCRIPTS_DIR = Path(r"C:\Users\HP\AppData\Local\hermes\rboutique-affiliate\scripts")
sys.path.insert(0, str(SCRIPTS_DIR))
from load_credentials import load_credentials

# Load credentials into environment
load_credentials()

import requests
from datetime import datetime, timedelta

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
FEED_PATH = BASE / "rboutique-affiliate" / "scripts" / "traffic_feed.json"
PLAN_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"

LINKTREE_API = "https://api.linktr.ee/v2"

ACCOUNTS = {
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


def get_headers(account):
    """Get API headers with auth."""
    token = ACCOUNTS[account]["api_token"]
    if not token:
        return None
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def fetch_existing_links(account):
    """Fetch all existing links from Linktree."""
    headers = get_headers(account)
    if not headers:
        return {}
    
    response = requests.get(f"{LINKTREE_API}/links", headers=headers)
    if response.status_code == 200:
        links = {}
        for link in response.json().get("links", []):
            links[link.get("id")] = {
                "title": link.get("title", ""),
                "url": link.get("url", ""),
                "enabled": link.get("enabled", True)
            }
        return links
    return {}


def create_link(account, title, url, position=0):
    """Create a new link at position (0 = top)."""
    headers = get_headers(account)
    if not headers:
        return False, "No token"
    
    data = {
        "title": title[:80],
        "url": url,
        "enabled": True
    }
    
    if position > 0:
        data["position"] = position
    
    response = requests.post(f"{LINKTREE_API}/links", headers=headers, json=data)
    return response.status_code == 201, response.json() if response.status_code == 201 else response.text


def update_link(account, link_id, title, url):
    """Update existing link."""
    headers = get_headers(account)
    if not headers:
        return False, "No token"
    
    data = {
        "title": title[:80],
        "url": url,
        "enabled": True
    }
    
    response = requests.patch(f"{LINKTREE_API}/links/{link_id}", headers=headers, json=data)
    return response.status_code == 200, response.json() if response.status_code == 200 else response.text


def archive_old_links(account, keep_days=30):
    """Disable links older than keep_days."""
    headers = get_headers(account)
    if not headers:
        return
    
    # Would need link creation dates - simplified: keep latest 50
    response = requests.get(f"{LINKTREE_API}/links", headers=headers)
    if response.status_code == 200:
        links = response.json().get("links", [])
        # Sort by position (assuming newer at top)
        for link in links[50:]:  # Archive beyond 50
            link_id = link.get("id")
            if link_id:
                requests.patch(f"{LINKTREE_API}/links/{link_id}", headers=headers, json={"enabled": False})
        print(f"  📦 Archived {max(0, len(links)-50)} old links for {account}")


def sync_account(account, products):
    """Sync Linktree with current run's products."""
    headers = get_headers(account)
    if not headers:
        print(f"  ✗ Linktree {account}: No API token in vault")
        return False
    
    # Fetch existing
    existing = fetch_existing_links(account)
    existing_by_title = {v["title"]: k for k, v in existing.items()}
    
    # Process each product (newest first)
    for i, p in enumerate(products):
        serial = p.get("serial")
        name = p.get("name", "Product")
        brand = p.get("brand", "")
        tracked = p.get("tracked_link", "")
        
        title = f"#{serial} {name}"
        if brand:
            title += f" — {brand}"
        title = title[:80]
        
        if title in existing_by_title:
            # Update existing
            link_id = existing_by_title[title]
            success, _ = update_link(account, link_id, title, tracked)
            if success:
                print(f"  ✓ Updated: {title}")
        else:
            # Create new at top
            success, result = create_link(account, title, tracked, position=i)
            if success:
                print(f"  ✓ Created: {title} (ID: {result.get('id')})")
            else:
                print(f"  ✗ Failed: {title} — {result}")
    
    # Archive old
    archive_old_links(account)
    
    return True


def main():
    print("=" * 60)
    print("LINKTREE AUTO UPDATER — API v2")
    print("=" * 60)
    
    if not FEED_PATH.exists():
        print("  ✗ traffic_feed.json not found. Run run_unified_automation.py first.")
        return
    
    with open(FEED_PATH, "r", encoding="utf-8") as f:
        feed = json.load(f)
    
    products = feed.get("products", [])
    
    # Split by account
    luxe_products = [p for p in products if p.get("account") == "luxe"]
    smart_products = [p for p in products if p.get("account") == "smart"]
    
    # Sort by serial descending (newest first)
    luxe_products.sort(key=lambda x: x.get("serial", 0), reverse=True)
    smart_products.sort(key=lambda x: x.get("serial", 0), reverse=True)
    
    print(f"\nSyncing Luxe ({len(luxe_products)} links)...")
    sync_account("luxe", luxe_products)
    
    print(f"\nSyncing Smart ({len(smart_products)} links)...")
    sync_account("smart", smart_products)
    
    print("\n✓ Linktree sync complete")


if __name__ == "__main__":
    main()