#!/usr/bin/env python3
"""
Copywriter — Sales-optimized captions using AIDA + psychology triggers.
Generates captions that sell, not just describe.
"""
import json
import random
from pathlib import Path

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
FEED_PATH = BASE / "rboutique-affiliate" / "scripts" / "traffic_feed.json"
OUTPUT_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"

# ─── PSYCHOLOGY FRAMEWORKS ───────────────────────────────────────────────

# AIDA: Attention → Interest → Desire → Action
# PAS: Problem → Agitation → Solution
# BAB: Before → After → Bridge

HOOKS_LUXE = {
    "aida": [
        "Why pay ${retail} for {brand} when you can get it for ${price}? 💎",
        "Same {category}, 40% less. The secret editors keep. 🤫",
        "Your {category} budget just doubled. Here's how. 📈"
    ],
    "pas": [
        "Tired of overpaying for designer {category}? 😤",
        "Settling for fast fashion because luxury is 'too expensive'? 🛑",
        "Watching others wear {brand} while you wait for sales? ⏳"
    ],
    "bab": [
        "Before: Paying retail for {brand}. After: ${price} delivered. Bridge: This link. 🌉",
        "Before: Guessing quality. After: Verified {brand} at wholesale. Bridge: Link in bio. 🔗"
    ]
}

HOOKS_SMART = {
    "aida": [
        "5 {category} under ${budget} that outperform $200 alternatives 🏆",
        "Stop wasting ${waste}/year on overpriced {category}. Here's the list. 📋",
        "The {category} hack that saves you ${savings} annually. 💡"
    ],
    "pas": [
        "Buying {category} blind and regretting it? 😞",
        "Overpaying for features you never use? 💸",
        "Returns, waste, disappointment — the {category} cycle. 🔄"
    ],
    "bab": [
        "Before: Random Amazon picks. After: Curated {category} that work. Bridge: This post. 🎯",
        "Before: ${waste} wasted. After: Smart picks under ${budget}. Bridge: Link #{serial}. 🔗"
    ]
}

BENEFIT_FRAMES_LUXE = [
    "Handcrafted in {origin} — {detail} that lasts decades",
    "Worn by {celebrity_type} — the quiet luxury signal",
    "Investment piece: cost-per-wear under ${cpw}/year",
    "Timeless silhouette — never goes out of style",
    "Exclusive access: not in department stores"
]

BENEFIT_FRAMES_SMART = [
    "Solves {problem} in {timeframe} — tested by {reviewers}+",
    "4.8★ avg from {reviews}+ verified buyers",
    "Saves ${savings}/year vs {competitor} — same specs",
    "Return-free guarantee: 30 days, no questions",
    "Featured in {publication} 'Best of {year}'"
]

URGENCY_TRIGGERS = [
    "Price expires {timeframe} ⏰",
    "Only {stock} left at this price 📦",
    "Flash sale ends {timeframe} — don't miss out 🔥",
    "Restock unlikely — this batch only 🎯",
    "Early access for followers — link in bio 🔐"
]

CTA_TEMPLATES = {
    "luxe": [
        "Your {category} upgrade: Link #{serial} in bio → @luxe_fashion_finds",
        "Tap bio #{serial} — {brand} delivered 📦",
        "Claim yours: bio link #{serial} (expires soon) ⏳"
    ],
    "smart": [
        "Smart buy #{serial}: Link in bio → @smart_buy_guides",
        "Grab the list: bio #{serial} — save ${savings} 💰",
        "Your {category} fix: bio #{serial} 🔗"
    ]
}

HASHTAG_POOLS = {
    "luxe": {
        "core": ["#luxuryfashion", "#designerforless", "#quietluxury", "#investmentpieces", "#costperwear"],
        "style": ["#minimaliststyle", "#capsulewardrobe", "#timelessfashion", "#elevatedbasics"],
        "deal": ["#designerdeal", "#luxurysale", "#sampleSale", "#wholesalefinds"],
        "compliance": ["#ad", "#affiliate", "#sponsored"]
    },
    "smart": {
        "core": ["#smartshopping", "#budgetfinds", "#valueformoney", "#smartbuyguides", "#underratedproducts"],
        "category": ["#techunder100", "#homeessentials", "#kitchengadgets", "#fitnessgear"],
        "deal": ["#amazonfinds", "#tiktokmademebuyit", "#budgetfriendly", "#moneysavingtips"],
        "compliance": ["#ad", "#affiliate", "#sponsored"]
    }
}

# ─── COPYWRITER ──────────────────────────────────────────────────────────

def generate_caption(product, account, serial, pillar):
    """Generate sales-optimized caption for one product."""
    
    name = product.get("name", "This product")
    brand = product.get("brand", "Premium Brand")
    category = product.get("category", "item").lower()
    price = product.get("price", "99")
    description = product.get("description", "")
    tracked = product.get("tracked_link", "")
    handle = "@luxe_fashion_finds" if account == "luxe" else "@smart_buy_guides"
    
    # Dynamic values
    retail = int(float(price) * random.uniform(2.5, 4))
    discount = int((1 - float(price)/retail) * 100)
    budget = random.choice([50, 100, 150, 200, 300])
    waste = random.randint(200, 800)
    savings = random.randint(50, 300)
    reviewers = random.randint(500, 5000)
    reviews = random.randint(2000, 15000)
    problem = random.choice(["wrong fit", "poor quality", "overpriced", "missing features"])
    timeframe = random.choice(["24h", "48h", "this weekend", "tonight"])
    stock = random.randint(3, 12)
    origin = random.choice(["Italy", "France", "Portugal", "Spain"])
    detail = random.choice(["hand-stitched", "vegetable-tanned", "seamless knit", "double-faced"])
    celebrity_type = random.choice(["stylists", "editors", "insiders", "creative directors"])
    cpw = random.randint(2, 8)
    publication = random.choice(["Wirecutter", "NYT", "Strategist", "CNN Underscored"])
    year = "2024"
    competitor = random.choice(["premium brands", "department stores", "big names"])
    
    hooks = HOOKS_LUXE if account == "luxe" else HOOKS_SMART
    frameworks = list(hooks.keys())
    framework = random.choice(frameworks)
    hook = random.choice(hooks[framework]).format(
        retail=retail, brand=brand, category=category, price=price,
        budget=budget, waste=waste, savings=savings, serial=serial
    )
    
    # Interest: Product specifics
    interest = f"🏷️ {name}\n🏷 {brand}\n📦 {category.title()}\n💰 ${price} (retail ~${retail})"
    
    # Desire: Benefits + Social Proof
    benefits = BENEFIT_FRAMES_LUXE if account == "luxe" else BENEFIT_FRAMES_SMART
    benefit = random.choice(benefits).format(
        origin=origin, detail=detail, celebrity_type=celebrity_type, cpw=cpw,
        problem=problem, timeframe="seconds", reviewers=reviewers,
        reviews=reviews, savings=savings, competitor=competitor,
        publication=publication, year=year
    )
    proof = f"⭐ {reviews}+ reviews • 4.8★ avg\n🏆 Bestseller in {category}\n📦 Free shipping • Easy returns"
    
    # Action: Urgency + CTA
    urgency = random.choice(URGENCY_TRIGGERS).format(timeframe=timeframe, stock=stock)
    cta = random.choice(CTA_TEMPLATES[account]).format(
        serial=serial, handle=handle, category=category, brand=brand, savings=savings
    )
    
    # Hashtags
    pools = HASHTAG_POOLS[account]
    tags = (random.sample(pools["core"], 3) + 
            random.sample(pools.get("style", pools.get("category", [])), 2) +
            random.sample(pools["deal"], 2) +
            pools["compliance"])
    
    # Assemble
    caption = f"""{hook}

{interest}

✨ {benefit}

{proof}

⚡ {urgency}

{cta}

{' '.join(tags)}"""
    
    return caption.strip()


def generate_multi_post_caption(account, serials, pillar_name, products):
    """Generate caption for multi-product posts (Weekly Edit, Best Of)."""
    
    handle = "@luxe_fashion_finds" if account == "luxe" else "@smart_buy_guides"
    pillar_label = pillar_name.replace("_", " ").title()
    
    if account == "luxe":
        intro = f"This week's {pillar_label} — {len(products)} designer pieces, all under retail 💎"
        items = "\n".join([f"#{s} {p.get('name', 'Item')[:30]} — ${p.get('price', '?')}" for s, p in zip(serials, products)])
        cta = f"All links in bio: #{min(serials)}-#{max(serials)} → {handle}"
    else:
        intro = f"{pillar_label}: {len(products)} smart picks under budget ✅"
        items = "\n".join([f"#{s} {p.get('name', 'Item')[:30]} — ${p.get('price', '?')}" for s, p in zip(serials, products)])
        cta = f"Every link: bio #{min(serials)}-#{max(serials)} → {handle}"
    
    tags = " ".join(random.sample(HASHTAG_POOLS[account]["core"], 3) + HASHTAG_POOLS[account]["compliance"])
    
    return f"""{intro}

{items}

{cta}

{tags}"""


def assign_pillar(product, account, index):
    """Assign content pillar based on product and rotation."""
    
    if account == "luxe":
        pillars = [
            ("designer_for_less", "Designer for Less", "carousel_reel"),
            ("style_guide", "How to Style", "reel"),
            ("weekly_edit", "Weekly Luxe Edit", "carousel_reel"),
            ("sale_alert", "Sale Alert", "story_reel")
        ]
    else:
        pillars = [
            ("under_budget", "5 Under $X", "carousel_reel"),
            ("seasonal_must", "Seasonal Must-Haves", "reel"),
            ("problem_solved", "Problem → Solved", "short_reel"),
            ("best_of", "Best of Category", "carousel_reel")
        ]
    
    return pillars[index % len(pillars)]


def main():
    print("=" * 60)
    print("COPYWRITER — Sales-Optimized Captions (AIDA/PAS/BAB)")
    print("=" * 60)
    
    if not FEED_PATH.exists():
        print("  ✗ traffic_feed.json not found. Run run_unified_automation.py first.")
        return
    
    with open(FEED_PATH, "r", encoding="utf-8") as f:
        feed = json.load(f)
    
    products = feed.get("products", [])
    serial_start = feed.get("serial_range", "#1").split("-")[0].replace("#", "")
    serial = int(serial_start) if serial_start.isdigit() else 1
    
    # Split by account
    luxe_products = [p for p in products if p.get("account") == "luxe"]
    smart_products = [p for p in products if p.get("account") == "smart"]
    
    plan = {
        "generated_at": feed.get("generated_at"),
        "season": "autumn",
        "luxe": [],
        "smart": [],
        "multi_posts": {}
    }
    
    # Generate Luxe captions
    for i, p in enumerate(luxe_products):
        p["serial"] = serial
        pillar_id, pillar_name, fmt = assign_pillar(p, "luxe", i)
        caption = generate_caption(p, "luxe", serial, pillar_id)
        plan["luxe"].append({
            "serial": serial,
            "pillar": pillar_id,
            "pillar_name": pillar_name,
            "format": fmt,
            "product": p,
            "caption": caption,
            "hashtags": [t for t in caption.split() if t.startswith("#")]
        })
        serial += 1
    
    # Generate Smart captions
    for i, p in enumerate(smart_products):
        p["serial"] = serial
        pillar_id, pillar_name, fmt = assign_pillar(p, "smart", i)
        caption = generate_caption(p, "smart", serial, pillar_id)
        plan["smart"].append({
            "serial": serial,
            "pillar": pillar_id,
            "pillar_name": pillar_name,
            "format": fmt,
            "product": p,
            "caption": caption,
            "hashtags": [t for t in caption.split() if t.startswith("#")]
        })
        serial += 1
    
    # Multi-posts
    if luxe_products:
        plan["multi_posts"]["luxe_weekly_edit"] = {
            "pillar": "weekly_edit",
            "pillar_name": "Weekly Luxe Edit",
            "format": "carousel_reel",
            "serials": [item["serial"] for item in plan["luxe"]],
            "caption": generate_multi_post_caption("luxe", [item["serial"] for item in plan["luxe"]], "Weekly Luxe Edit", luxe_products),
            "products": luxe_products
        }
    
    if smart_products:
        plan["multi_posts"]["smart_best_of"] = {
            "pillar": "best_of",
            "pillar_name": "Best of Category",
            "format": "carousel_reel",
            "serials": [item["serial"] for item in plan["smart"]],
            "caption": generate_multi_post_caption("smart", [item["serial"] for item in plan["smart"]], "Best of Category", smart_products),
            "products": smart_products
        }
    
    # Save
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Generated {len(plan['luxe'])} Luxe captions")
    print(f"✓ Generated {len(plan['smart'])} Smart captions")
    print(f"✓ Generated {len(plan['multi_posts'])} multi-post captions")
    print(f"✓ Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()