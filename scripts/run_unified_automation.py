#!/usr/bin/env python3
"""
Unified Affiliate Automation Runner — Phase 1 + Traffic Feed Output
Outputs traffic_feed.json for Phase 2 content pipeline.
"""
import json
import os
import random
import urllib.parse
from datetime import datetime
from pathlib import Path

# ─── CONFIG ──────────────────────────────────────────────────────────────
BASE = Path(r"C:\Users\HP\AppData\Local\hermes")

NETWORKS = {
    "rboutique": {
        "dir": BASE / "rboutique-affiliate",
        "products_file": "scripts/products_rboutique.json",
        "site_file": "docs/index.html",
        "tg_file": "telegram_message.txt",
        "tracker": lambda url: f"https://click.linksynergy.com/link?id=Br7kCmfVLtE&offerid=1539873.528809996565778384071734&type=2&murl={urllib.parse.quote(url)}",
        "commission": "6%",
        "tags": "#rboutique #luxuryfashion",
        "title": "Rboutique Luxury Fashion",
        "account": "luxe",  # maps to Account A
    },
    "amazon": {
        "dir": BASE / "amazon-affiliate",
        "products_file": "scripts/products_amazon.json",
        "site_file": "index.html",
        "tg_file": "telegram_message.txt",
        "tracker": lambda url: f"https://www.amazon.com/dp/{url.split('/dp/')[-1].split('/')[0]}?tag=udaybannastor-21-20" if '/dp/' in url else url,
        "commission": "4-10%",
        "tags": "#amazon #deals",
        "title": "Amazon Curated Deals",
        "account": "luxe",  # Amazon fashion goes to Account A
    },
    "clickbank": {
        "dir": BASE / "clickbank-affiliate",
        "products_file": "scripts/products_clickbank.json",
        "site_file": "index.html",
        "tg_file": "telegram_message.txt",
        "tracker": lambda url: url,
        "commission": "50-75%",
        "tags": "#clickbank #digital",
        "title": "ClickBank Top Offers",
        "account": "smart",  # maps to Account B
    },
}

LINKS_PER_NETWORK = 7
SERIAL_FILE = BASE / "rboutique-affiliate" / "scripts" / "serial_counter.json"
# ─────────────────────────────────────────────────────────────────────────


def load_products(network_key):
    cfg = NETWORKS[network_key]
    path = cfg["dir"] / cfg["products_file"]
    if not path.exists():
        print(f"  ✗ {network_key}: products file not found at {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_products(products, count):
    return random.sample(products, min(count, len(products)))


def make_tracked_link(network_key, product):
    cfg = NETWORKS[network_key]
    url = product.get("url") or product.get("hoplink") or f"https://www.amazon.com/dp/{product.get('asin', '')}"
    return cfg["tracker"](url)


def load_serial():
    if SERIAL_FILE.exists():
        with open(SERIAL_FILE, "r") as f:
            return json.load(f).get("last_serial", 0)
    return 0


def save_serial(serial):
    SERIAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SERIAL_FILE, "w") as f:
        json.dump({"last_serial": serial}, f)


def build_site_html(network_key, products):
    cfg = NETWORKS[network_key]
    title = cfg["title"]

    cards = []
    for i, p in enumerate(products):
        tracked = make_tracked_link(network_key, p)
        name = p.get("name", "Product")
        brand = p.get("brand", p.get("vendor", ""))
        category = p.get("category", "")
        image = p.get("image", "")
        desc = p.get("description", "")

        tag_line = ""
        if brand:
            tag_line += f'<span class="tag">{brand}</span>'
        if category:
            tag_line += f'<span class="tag">{category}</span>'

        img_html = f'<img src="{image}" alt="{name}" loading="lazy">' if image else ""

        cards.append(f'''
<div class="card" id="product-{i+1}">
{img_html}
<h2>{name}</h2>
<p class="tags">{tag_line}</p>
<p class="desc">{desc}</p>
<a href="{tracked}" class="btn" target="_blank" rel="noopener">Check Price →</a>
</div>''')

    cards_html = "\n".join(cards)

    subtitles = {
        "rboutique": "Curated luxury fashion from 200+ designers. Independent selection, updated daily.",
        "amazon": "Hand-picked tech, gear & deals. Updated daily with fresh picks.",
        "clickbank": "Top-converting digital offers across health, wealth & skills. Updated daily."
    }
    subtitle = subtitles.get(network_key, "Curated picks updated daily.")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Curated Picks 2026</title>
<meta name="description" content="{subtitle} {len(products)} tracked affiliate links. Updated daily at 09:00 UTC.">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#0a0a0f;color:#e8e6e3;max-width:1000px;margin:0 auto;padding:2rem 1rem;line-height:1.6}}header{{text-align:center;margin-bottom:3rem;padding-bottom:2rem;border-bottom:1px solid #1a1a2e}}h1{{font-size:clamp(1.8rem,4vw,2.5rem);font-weight:700;background:linear-gradient(135deg,#d6a96a 0%,#f4e4bc 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.5rem}}p.lead{{color:#9a8f7a;font-size:1.1rem;max-width:600px;margin:0 auto}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.5rem}}.card{{background:#111118;border:1px solid #1e1e2e;border-radius:16px;overflow:hidden;transition:transform .2s,box-shadow .2s,border-color .2s}}.card:hover{{transform:translateY(-4px);box-shadow:0 20px 40px -15px rgba(214,169,106,.15);border-color:#2a2a3e}}.card img{{width:100%;height:280px;object-fit:cover}}.card h2{{font-size:1.05rem;font-weight:600;padding:1rem 1.25rem .5rem;color:#f4e4bc}}.tags{{display:flex;flex-wrap:wrap;gap:.4rem;padding:0 1.25rem;margin-bottom:.5rem}}.tag{{font-size:.7rem;background:#1a1a2e;color:#d6a96a;padding:.2rem .55rem;border-radius:999px;font-weight:500;text-transform:uppercase;letter-spacing:.02em}}.desc{{font-size:.85rem;color:#a8a296;padding:0 1.25rem 1rem;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}.btn{{display:block;width:calc(100% - 2.5rem);margin:0 1.25rem 1.25rem;padding:.85rem;background:linear-gradient(135deg,#d6a96a 0%,#c49a5a 100%);color:#0a0a0f;font-weight:600;font-size:.9rem;text-align:center;text-decoration:none;border-radius:10px;transition:opacity .2s,transform .1s}}.btn:hover{{opacity:.9;transform:scale(1.01)}}footer{{text-align:center;padding:3rem 1rem 1rem;color:#555;font-size:.8rem;border-top:1px solid #1a1a2e;margin-top:3rem}}@media (max-width:600px){{.card img{{height:220px}}}}
</style>
</head>
<body>
<header>
<h1>{title}</h1>
<p class="lead">{subtitle}</p>
</header>
<main>
<div class="grid">
{cards_html}
</div>
</main>
<footer>
<p>Product data sourced from official catalogs. Affiliate links used — no extra cost to you.</p>
<p>Updated daily • Built with automation</p>
</footer>
</body>
</html>'''


def build_telegram_message(network_key, products):
    cfg = NETWORKS[network_key]
    tags = cfg["tags"]
    title = cfg["title"]

    emojis = {"rboutique": "💎", "amazon": "🛍️", "clickbank": "📚"}
    emoji = emojis.get(network_key, "✨")

    msg = f"{emoji} *{title} — Today's Curated Picks* {emoji}\n\n"
    msg += f"Hand-picked for you. Tap any link to see the deal →\n\n---\n\n"

    for p in products:
        tracked = make_tracked_link(network_key, p)
        name = p.get("name", "Product")
        brand = p.get("brand", p.get("vendor", ""))
        desc = p.get("description", "")

        short_desc = desc[:160].rstrip()
        if len(desc) > 160:
            short_desc = short_desc.rsplit('.', 1)[0] + "."

        msg += f"*🏷️ {name}*\n"
        if brand:
            msg += f"🏷 {brand}\n"
        msg += f"💡 {short_desc}\n\n"
        msg += f"🔗 [View Deal →]({tracked})\n\n---\n\n"

    msg += f"_{title} — fresh picks daily._\n\n@t.me/hermeeagent05bot | {tags}"
    return msg


def build_traffic_feed(network_key, products, serial_start):
    """Build structured feed for traffic pipeline."""
    cfg = NETWORKS[network_key]
    feed = []
    serial = serial_start
    
    for p in products:
        serial += 1
        tracked = make_tracked_link(network_key, p)
        feed.append({
            "serial": serial,
            "network": network_key,
            "account": cfg["account"],
            "name": p.get("name", "Product"),
            "brand": p.get("brand", p.get("vendor", "")),
            "category": p.get("category", ""),
            "image": p.get("image", ""),
            "description": p.get("description", ""),
            "original_url": p.get("url") or p.get("hoplink") or f"https://www.amazon.com/dp/{p.get('asin', '')}",
            "tracked_link": tracked,
            "commission": cfg["commission"],
            "tags": cfg["tags"],
            "title": cfg["title"],
            "timestamp": datetime.now().isoformat()
        })
    
    return feed, serial


def update_network(network_key):
    cfg = NETWORKS[network_key]
    print(f"\n{'='*60}")
    print(f"Processing {network_key.upper()}...")
    print(f"{'='*60}")

    products = load_products(network_key)
    if not products:
        return {"network": network_key, "status": "no_products", "count": 0, "feed": []}

    picked = pick_products(products, LINKS_PER_NETWORK)
    print(f"  [OK] Picked {len(picked)} products from {len(products)} catalog")

    for p in picked:
        p["tracked_link"] = make_tracked_link(network_key, p)
        name = p.get("name", "Product")[:50]
        print(f"  [OK] {name}: {p['tracked_link'][:70]}...")

    # Update site
    html = build_site_html(network_key, picked)
    site_path = cfg["dir"] / cfg["site_file"]
    site_path.parent.mkdir(parents=True, exist_ok=True)
    with open(site_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [OK] Updated {site_path} ({len(html)} bytes)")

    # Save Telegram message
    tg_msg = build_telegram_message(network_key, picked)
    tg_path = cfg["dir"] / cfg["tg_file"]
    with open(tg_path, "w", encoding="utf-8") as f:
        f.write(tg_msg)
    print(f"  [OK] Saved Telegram message to {tg_path} ({len(tg_msg)} bytes)")

    return {"network": network_key, "status": "success", "count": len(picked), "products": picked}


def main():
    print("=" * 60)
    print("UNIFIED AFFILIATE AUTOMATION — 20+ LINKS/DAY + TRAFFIC FEED")
    print("=" * 60)
    print(f"Networks: {', '.join(NETWORKS.keys())}")
    print(f"Links per network: {LINKS_PER_NETWORK}")
    print(f"Target total: {LINKS_PER_NETWORK * len(NETWORKS)} links/day")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load serial counter
    serial = load_serial()
    print(f"  Starting serial: #{serial + 1}")

    results = []
    all_feed = []

    for net in NETWORKS:
        try:
            res = update_network(net)
            results.append(res)
            
            if res["status"] == "success":
                feed, serial = build_traffic_feed(net, res["products"], serial)
                all_feed.extend(feed)
                res["feed"] = feed
            else:
                res["feed"] = []
                
        except Exception as e:
            print(f"  [FAIL] {net} FAILED: {e}")
            results.append({"network": net, "status": "error", "error": str(e), "feed": []})

    # Save serial counter
    save_serial(serial)
    print(f"  Ending serial: #{serial}")

    # Save traffic feed
    feed_path = BASE / "rboutique-affiliate" / "scripts" / "traffic_feed.json"
    with open(feed_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_products": len(all_feed),
            "serial_range": f"#{serial - len(all_feed) + 1} - #{serial}",
            "products": all_feed
        }, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved traffic feed: {feed_path} ({len(all_feed)} products)")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = 0
    for r in results:
        status = r.get("status", "unknown")
        count = r.get("count", 0)
        total += count
        print(f"  {r['network']:12} | {status:8} | {count} links")
    print(f"\n  TOTAL LINKS GENERATED: {total}")
    print(f"  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Save combined telegram message
    emojis = {"rboutique": "💎", "amazon": "🛍️", "clickbank": "📚"}
    combined = "✨ *YOUR DAILY AFFILIATE PICKS — All Networks* ✨\n\n"
    combined += "Curated deals across luxury fashion, tech & digital products. Tap to explore →\n\n---\n\n"
    for r in results:
        if r["status"] == "success":
            net = r["network"]
            cfg = NETWORKS[net]
            emoji = emojis.get(net, "✨")
            combined += f"{emoji} *{cfg['title']}*\n\n"
            for p in r["products"]:
                tracked = p["tracked_link"]
                name = p.get("name", "Product")[:50]
                brand = p.get("brand", p.get("vendor", ""))
                desc = p.get("description", "")[:120].rstrip()
                if len(p.get("description", "")) > 120:
                    desc = desc.rsplit('.', 1)[0] + "."
                combined += f"🏷️ *{name}*\n"
                if brand:
                    combined += f"🏷 {brand}\n"
                combined += f"💡 {desc}\n"
                combined += f"🔗 [View Deal →]({tracked})\n\n"
            combined += "---\n\n"
    combined += "_Fresh picks every morning. You save time researching; I earn from confirmed sales._\n\n@t.me/hermeeagent05bot | #affiliate #deals #automation"

    combined_path = BASE / "rboutique-affiliate" / "telegram_combined.txt"
    with open(combined_path, "w", encoding="utf-8") as f:
        f.write(combined)
    print(f"\n  Combined Telegram message: {combined_path}")

    return {"total_links": total, "results": results, "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    result = main()
    print("\n" + json.dumps(result, indent=2))