#!/usr/bin/env python3
"""
Credential Loader — Loads credentials from local file into environment.
Run this once to set up, or import in scripts.
"""
import json
import os
from pathlib import Path

CRED_FILE = Path(__file__).parent / "credentials.json"

DEFAULT_CREDS = {
    # YouTube
    "YOUTUBE_CLIENT_ID": "",
    "YOUTUBE_CLIENT_SECRET": "",
    "YOUTUBE_LUXE_REFRESH_TOKEN": "",
    "YOUTUBE_SMART_REFRESH_TOKEN": "",
    
    # Instagram
    "INSTAGRAM_LUXE_LOGIN": "",
    "INSTAGRAM_SMART_LOGIN": "",
    "INSTAGRAM_LUXE_USER_ID": "",
    "INSTAGRAM_SMART_USER_ID": "",
    "INSTAGRAM_LUXE_ACCESS_TOKEN": "",
    "INSTAGRAM_SMART_ACCESS_TOKEN": "",
    
    # Facebook
    "FACEBOOK_LUXE_PAGE_LOGIN": "",
    "FACEBOOK_SMART_PAGE_LOGIN": "",
    "FACEBOOK_LUXE_PAGE_ID": "",
    "FACEBOOK_SMART_PAGE_ID": "",
    "FACEBOOK_LUXE_ACCESS_TOKEN": "",
    "FACEBOOK_SMART_ACCESS_TOKEN": "",
    
    # Pinterest
    "PINTEREST_LUXE_CLIENT_ID": "",
    "PINTEREST_LUXE_CLIENT_SECRET": "",
    "PINTEREST_LUXE_ACCESS_TOKEN": "",
    "PINTEREST_LUXE_REFRESH_TOKEN": "",
    "PINTEREST_SMART_CLIENT_ID": "",
    "PINTEREST_SMART_CLIENT_SECRET": "",
    "PINTEREST_SMART_ACCESS_TOKEN": "",
    "PINTEREST_SMART_REFRESH_TOKEN": "",
    
    # Linktree
    "LINKTREE_LUXE_TOKEN": "",
    "LINKTREE_SMART_TOKEN": "",
    
    # Telegram
    "TELEGRAM_BOT_TOKEN": "",
    "TELEGRAM_CHAT_ID": "",
    
    # Rakuten
    "RAKUTEN_EMAIL": "",
    "RAKUTEN_PASSWORD": "",
}


def load_credentials():
    """Load credentials from file into os.environ."""
    if CRED_FILE.exists():
        with open(CRED_FILE, "r") as f:
            creds = json.load(f)
    else:
        creds = DEFAULT_CREDS.copy()
        save_credentials(creds)
        print(f"Created template: {CRED_FILE}")
        print("Fill in your credentials and re-run.")
        return False
    
    loaded = 0
    for key, value in creds.items():
        if value and not os.environ.get(key):
            os.environ[key] = value
            loaded += 1
    
    print(f"Loaded {loaded} credentials into environment")
    return loaded > 0


def save_credentials(creds):
    """Save credentials to file."""
    with open(CRED_FILE, "w") as f:
        json.dump(creds, f, indent=2)


def get_credential(key):
    """Get a credential value from environment or file."""
    if key in os.environ:
        return os.environ[key]
    
    if CRED_FILE.exists():
        with open(CRED_FILE, "r") as f:
            creds = json.load(f)
        return creds.get(key, "")
    
    return ""


if __name__ == "__main__":
    load_credentials()
    print("\nTemplate created at:", CRED_FILE)
    print("Edit credentials.json with your actual values.")