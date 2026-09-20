#!/usr/bin/env python3
"""
Unified Affiliate Automation Runner
Scales to 20+ links/day across 3 networks: Rboutique, Amazon, ClickBank
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
        "site_file": "site/index.html",
        "tg_file": "telegram_message.txt",
        "tracker": lambda url: f"https://click.linksynergy.com/link?id=Br7kCmfVLtE&offerid=1539873.528809996565778384071734&type=2&murl={urllib.parse.quote(url)}",
        "commission": "6%",
        "tags": "#rboutique #luxuryfashion",
        "title": "Rboutique Luxury Fashion",
    },
    "amazon": {
        "dir": BASE / "amazon-affiliate",
        "products_file": "scripts/products_amazon.json",
        "site_file": "index.html",  # at root for GitHub Pages
        "tg_file": "telegram_message.txt",
        "tracker": lambda url: f"https://www.amazon.com/dp/{url.split('/dp/')[-1].split('/')[0]}?tag=udaybannastor-21-20" if '/dp/' in url else url,
        "commission": "4-10%",
        "tags": "#amazon #deals",
        "title": "Amazon Curated Deals",
    },
    "clickbank": {
        "dir": BASE / "clickbank-affiliate",
        "products_file": "scripts/products_clickbank.json",
        "site_file": "index.html",
        "tg_file": "telegram_message.txt",
        "tracker": lambda url: url,  # hoplink already has affiliate ID
        "commission": "50-75%",
        "tags": "#clickbank #digital",
        "title": "ClickBank Top Offers",
    },
}

LINKS_PER_NETWORK = 7  # 7 × 3 = 21 links/day
# ─────────────────────────────────────────────────────────────────────────


def load_products(network_key):
    """Load product catalog for a network."""
    cfg = NETWORKS[network_key]
    path = cfg["dir"] / cfg["products_file"]
    if not path.exists():
        print(f"  ✗ {network_key}: products file not found at {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_products(products, count):
    """Randomly pick `count` products."""
    return random.sample(products, min(count, len(products)))


def make_tracked_link(network_key, product):
    """Generate tracked affiliate link."""
    cfg = NETWORKS[network_key]
    url = product.get("url") or product.get("hoplink") or f"https://www.amazon.com/dp/{product.get('asin', '')}"
    return cfg["tracker"](url)


def build_site_html(network_key, products):
    """Generate complete site HTML with tracked links."""
    cfg = NETWORKS[network_key]
    commission = cfg["commission"]
    title = cfg["title"]
    
    # Network-specific card rendering
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
        tag_line += f'<span class="tag">{commission} Commission</span>'
        
        img_html = f'<img src="{image}" alt="{name}">' if image else ""
        
        cards.append(f'''
<div class="card" id="product-{i+1}">
<h2>{name}</h2>
{img_html}
<p>{tag_line}</p>
<p>{desc}</p>
<p><a href="{tracked}">Check Price & Availability — Tracked Link ({commission} Commission)</a></p>
</div>''')
    
    cards_html = "\n".join(cards)
    
    # Add opt-in form only for rboutique
    optin_html = ""
    if network_key == "rboutique":
        optin_html = '''
<h2>Get the Free Guide: Top 10 Luxury Knitwear Under $300</h2>
<div class="card" style="text-align:center;background:#1a1a2e;border-color:#d6a96a">
<p style="font-size:1.1rem;margin-bottom:1rem">Curated list of premium cashmere, merino & wool blends from John Smedley, Loro Piana, Alanui & more — all under $300.</p>
<form action="http://localhost:5678/webhook/optin" method="POST" style="display:inline-flex;gap:.5rem;max-width:400px;margin:0 auto">
<input type="email" name="email" placeholder="your@email.com" required style="flex:1;padding:.75rem;border-radius:6px;border:1px solid #2a2a2e;background:#0f0f12;color:#eae6df">
<button type="submit" style="background:#d6a96a;color:#0f0f12;border:none;padding:.75rem 1.5rem;border-radius:6px;font-weight:600;cursor:pointer">Get Free Guide →</button>
</form>
<p style="font-size:.75rem;color:#777;margin-top:.5rem">No spam. Unsubscribe anytime. Daily curated picks via email.</p>
</div>
'''
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Curated Reviews & Best Deals 2026</title>
<meta name="description" content="Independent {title.lower()} reviews. {len(products)} tracked affiliate links. Updated daily at 09:00 UTC.">
<style>
body{{font-family:system-ui,sans-serif;background:#0f0f12;color:#eae6df;max-width:960px;margin:0 auto;padding:2rem;line-height:1.6}}
h1{{color:#d6a96a;font-size:2.2rem;margin-bottom:.5rem}} h2{{color:#d6a96a;border-bottom:1px solid #2a2a2e;padding-bottom:.5rem;margin-top:2.5rem}}
.card{{background:#18181c;border:1px solid #2a2a2e;border-radius:12px;padding:1.25rem;margin:1rem 0}}
.card img{{max-width:100%;border-radius:8px;margin-bottom:.75rem}}
.card a{{color:#d6a96a;text-decoration:underline;font-weight:600}}
.footer{{margin-top:4rem;padding-top:1rem;border-top:1px solid #2a2a2e;color:#777;font-size:.85rem}}
.tag{{display:inline-block;background:#2a2a2e;color:#d6a96a;padding:.15rem .5rem;border-radius:4px;font-size:.75rem;margin-right:.25rem}}
</style>
</head>
<body>
<h1>{title} — Independent Reviews 2026</h1>
<p><strong>Curated {title.lower()} products. No identity shown. Only products that matter.</strong></p>
<p>{len(products)} tracked affiliate links updated daily. You save time researching; I earn from confirmed sales — that's the deal.</p>

{cards_html}

{optin_html}

<h2>How This Works</h2>
<p>Every product link above is tracked through our affiliate partnerships. When you purchase through any of these links, we receive a commission ({commission}). There is no additional cost to you.</p>
<p>This site grows daily with new product reviews targeting specific search queries. More content = more traffic = more commissions.</p>

<h2>Automation Status</h2>
<p><strong>Daily Cron (09:00 UTC):</strong> Refreshes {LINKS_PER_NETWORK} products per network → generates tracked links → updates site.</p>
<p><strong>Telegram (@hermeeagent05bot):</strong> Pushes new deals to subscribers automatically.</p>
<p><strong>Networks:</strong> Rboutique (6%), Amazon (4-10%), ClickBank (50-75%).</p>

<div class="footer">
<p>Commission structure varies by network. Product data sourced from official catalogs. No personal identity shown — content is product-focused and automated.</p>
<p>Built with Hermes Agent automation. Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}</p>
</div>
</body>
</html>'''


def build_telegram_message(network_key, products):
    """Generate Telegram message for a network."""
    cfg = NETWORKS[network_key]
    tags = cfg["tags"]
    title = cfg["title"]
    
    emojis = {
        "rboutique": "💎",
        "amazon": "🛍️",
        "clickbank": "📚"
    }
    emoji = emojis.get(network_key, "✨")
    
    msg = f"{emoji} *{title} — Today's Curated Picks* {emoji}\n\n"
    msg += f"Hand-picked for you. Tap any link to see the deal →\n\n---\n\n"
    
    for p in products:
        tracked = make_tracked_link(network_key, p)
        name = p.get("name", "Product")
        brand = p.get("brand", p.get("vendor", ""))
        desc = p.get("description", "")
        
        # Short, punchy 1-2 line description
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


def update_network(network_key):
    """Process one network: pick products, update site, save telegram message."""
    cfg = NETWORKS[network_key]
    print(f"\n{'='*60}")
    print(f"Processing {network_key.upper()}...")
    print(f"{'='*60}")
    
    products = load_products(network_key)
    if not products:
        return {"network": network_key, "status": "no_products", "count": 0}
    
    picked = pick_products(products, LINKS_PER_NETWORK)
    print(f"  ✓ Picked {len(picked)} products from {len(products)} catalog")
    
    # Generate tracked links
    for p in picked:
        p["tracked_link"] = make_tracked_link(network_key, p)
        name = p.get("name", "Product")[:50]
        print(f"  ✓ {name}: {p['tracked_link'][:70]}...")
    
    # Update site
    html = build_site_html(network_key, picked)
    site_path = cfg["dir"] / cfg["site_file"]
    site_path.parent.mkdir(parents=True, exist_ok=True)
    with open(site_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ Updated {site_path} ({len(html)} bytes)")
    
    # Save Telegram message
    tg_msg = build_telegram_message(network_key, picked)
    tg_path = cfg["dir"] / cfg["tg_file"]
    with open(tg_path, "w", encoding="utf-8") as f:
        f.write(tg_msg)
    print(f"  ✓ Saved Telegram message to {tg_path} ({len(tg_msg)} bytes)")
    
    return {"network": network_key, "status": "success", "count": len(picked)}


def main():
    print("=" * 60)
    print("UNIFIED AFFILIATE AUTOMATION — 20+ LINKS/DAY")
    print("=" * 60)
    print(f"Networks: {', '.join(NETWORKS.keys())}")
    print(f"Links per network: {LINKS_PER_NETWORK}")
    print(f"Target total: {LINKS_PER_NETWORK * len(NETWORKS)} links/day")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    for net in NETWORKS:
        try:
            res = update_network(net)
            results.append(res)
        except Exception as e:
            print(f"  ✗ {net} FAILED: {e}")
            results.append({"network": net, "status": "error", "error": str(e)})
    
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
            products = load_products(net)
            picked = pick_products(products, LINKS_PER_NETWORK)
            emoji = emojis.get(net, "✨")
            combined += f"{emoji} *{cfg['title']}*\n\n"
            for p in picked:
                tracked = make_tracked_link(net, p)
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