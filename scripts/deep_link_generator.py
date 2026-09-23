#!/usr/bin/env python3
"""Manual deep-link replication — Kong API broken. Input Rboutique URL → tracked link."""
import sys, urllib.parse
MID, OFFER = "52880", "1539873.528809996565778384071734"
BASE = "https://click.linksynergy.com/link"

def make(url: str) -> str:
    return f"{BASE}?id=Br7kCmfVLtE&offerid={OFFER}&type=2&murl={urllib.parse.quote(url, safe='')}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(make(sys.argv[1]))
    else:
        print("Usage: python deep_link_generator.py <RBOUTIQUE_URL>")
