#!/usr/bin/env python3
import sys, urllib.parse
MID, OFFER = "52880", "1539873.528809996565778384071734"
BASE = "https://click.linksynergy.com/link"
if len(sys.argv)>1:
    print(f"{BASE}?id=Br7kCmfVLtE&offerid={OFFER}&type=2&murl={urllib.parse.quote(sys.argv[1], safe='')}")
