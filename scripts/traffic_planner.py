#!/usr/bin/env python3
"""
Traffic Planner — Assigns products to content pillars, generates captions, hashtags.
Reads traffic_feed.json → outputs content_plan.json
"""
import json
import random
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
FEED_PATH = BASE / "rboutique-affiliate" / "scripts" / "traffic_feed.json"
PLAN_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"

# ─── CONTENT PILLARS ────────────────────────────────────────────────────
PILLARS_LUXE = {
    "designer_for_less": {
        "name": "Designer for Less",
        "format": "carousel_reel",
        "max_items": 5,
        "hook_templates": [
            "Same {brand} {category}, {discount}% off retail 💎",
            "Why pay full price? {brand} {name} for ${price} 💸",
            "Designer {category} under ${price} — {brand} edition ✨"
        ],
        "hashtags": ["#designerforless", "#luxuryfashion", "#designerdupe", "#smartshopping", "#fashionhacks"],
        "cta": "Link #{serial} in bio → @luxe_fashion_finds"
    },
    "style_guide": {
        "name": "How to Style",
        "format": "reel",
        "max_items": 3,
        "hook_templates": [
            "3 ways to wear {name} 👗",
            "Style {brand} {category} like a pro ✨",
            "{brand} {category}: day to night looks 🌅🌙"
        ],
        "hashtags": ["#styletips", "#howtostyle", "#outfitinspo", "#fashionreels", "#ootd"],
        "cta": "Full look links in bio → #{serial}"
    },
    "weekly_edit": {
        "name": "Weekly Luxe Edit",
        "format": "carousel_pin",
        "max_items": 7,
        "hook_templates": [
            "This week's 7 must-see luxury drops 💎",
            "Weekly Luxe Edit: {count} pieces you'll love ✨",
            "Fresh from the runway to your closet 👗"
        ],
        "hashtags": ["#weeklyedit", "#luxefashion", "#newarrivals", "#designerfashion", "#fashionweekly"],
        "cta": "All #{start_serial}-#{end_serial} in bio → @luxe_fashion_finds"
    },
    "sale_alert": {
        "name": "Sale Alert",
        "format": "story_reel",
        "max_items": 2,
        "hook_templates": [
            "FLASH: {brand} {name} {discount}% off — ends tonight ⚡",
            "Sale alert: {brand} {category} under ${price} 🔥"
        ],
        "hashtags": ["#salealert", "#fashionsale", "#luxurysale", "#limitedtime", "#shopnow"],
        "cta": "Link #{serial} in bio → expires soon"
    }
}

PILLARS_SMART = {
    "five_under": {
        "name": "5 Under ${budget}",
        "format": "carousel_reel",
        "max_items": 5,
        "hook_templates": [
            "5 {category} under ${budget} that actually work 🛠️",
            "Best {category} under ${budget} — tested ✅",
            "Budget {category}: 5 picks under ${budget} 💰"
        ],
        "hashtags": ["#budgetfinds", "#under50", "#smartshopping", "#amazonfinds", "#musthaves"],
        "cta": "Links #{start_serial}-#{end_serial} in bio → @smart_buy_guides"
    },
    "seasonal_musts": {
        "name": "Seasonal Must-Haves",
        "format": "reel",
        "max_items": 7,
        "hook_templates": [
            "{season} essentials you'll use daily 🍂❄️☀️",
            "Don't start {season} without these {count} things 📋",
            "{season} prep: {count} items that save you money 💡"
        ],
        "hashtags": ["#seasonalmusthaves", "#homeessentials", "#kitchengadgets", "#prepper", "#smartbuy"],
        "cta": "All links in bio → #{start_serial}-#{end_serial}"
    },
    "problem_solved": {
        "name": "Problem → Solved",
        "format": "short_reel",
        "max_items": 3,
        "hook_templates": [
            "Stop {problem} — these {count} fixes work 🛑",
            "{problem}? Try this {category} instead 💡",
            "Finally solved: {problem} with {name} ✨"
        ],
        "hashtags": ["#problemsolved", "#lifehack", "#smartbuy", "#productreview", "#worthit"],
        "cta": "Link #{serial} in bio → @smart_buy_guides"
    },
    "best_of": {
        "name": "Best of {category} 2026",
        "format": "carousel_pin",
        "max_items": 10,
        "hook_templates": [
            "Best {category} under ${budget} — 2026 edition 🏆",
            "Top {count} {category} tested & ranked 📊",
            "Which {category} wins? Our picks 🥇"
        ],
        "hashtags": ["#bestoftheyear", "#toprated", "#productreview", "#buyingguide", "#smartshopping"],
        "cta": "Full list #{start_serial}-#{end_serial} in bio → @smart_buy_guides"
    }
}

# ─── SEASONAL CONTEXT ───────────────────────────────────────────────────
def get_season():
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "fall"

SEASON = get_season()


def categorize_product(product):
    """Determine which pillar fits best."""
    name = product.get("name", "").lower()
    category = product.get("category", "").lower()
    brand = product.get("brand", "").lower()
    network = product.get("network", "")
    account = product.get("account", "")
    
    # Luxe account (A) - Fashion/Luxury
    if account == "luxe":
        if any(kw in name for kw in ["sale", "off", "discount", "%"]):
            return "sale_alert"
        elif "bag" in category or "bag" in name:
            return "designer_for_less"
        elif "shoe" in category or "shoe" in name or "heel" in name or "boot" in name:
            return "designer_for_less"
        elif "dress" in category or "dress" in name:
            return "style_guide"
        elif "top" in category or "shirt" in category or "blouse" in name:
            return "style_guide"
        else:
            return random.choice(["designer_for_less", "style_guide", "weekly_edit"])
    
    # Smart account (B) - Tech/Home/Value
    else:
        budget_keywords = ["under", "budget", "cheap", "affordable", "deal"]
        if any(kw in name for kw in budget_keywords):
            return "five_under"
        elif any(kw in category for kw in ["home", "kitchen", "tool", "gadget", "tech", "electronic"]):
            return random.choice(["five_under", "seasonal_musts", "best_of"])
        elif any(kw in category for kw in ["health", "fitness", "wellness", "supplement"]):
            return "problem_solved"
        else:
            return random.choice(["five_under", "seasonal_musts", "problem_solved"])


def generate_caption(product, pillar_key, account, serial, all_serials=None):
    """Generate platform-ready caption."""
    pillars = PILLARS_LUXE if account == "luxe" else PILLARS_SMART
    pillar = pillars.get(pillar_key, list(pillars.values())[0])
    
    name = product.get("name", "Product")
    brand = product.get("brand", "")
    category = product.get("category", "")
    price = product.get("price", "")
    tracked = product.get("tracked_link", "")
    
    # Pick hook template
    hook = random.choice(pillar["hook_templates"])
    hook = hook.format(
        name=name,
        brand=brand or "this brand",
        category=category or "item",
        discount=random.randint(30, 60),
        price=price or random.randint(50, 200),
        budget=random.choice([50, 100, 200, 500]),
        season=SEASON.capitalize(),
        count=len(all_serials) if all_serials else pillar["max_items"],
        problem="wasting money"  # fallback
    )
    
    # Build caption
    caption = f"{hook}\n\n"
    
    # Product details
    caption += f"🏷️ {name}\n"
    if brand:
        caption += f"🏷 {brand}\n"
    if category:
        caption += f"📦 {category}\n"
    if price:
        caption += f"💰 ${price}\n"
    
    # Description snippet
    desc = product.get("description", "")
    if desc:
        short = desc[:200].rstrip()
        if len(desc) > 200:
            short = short.rsplit('.', 1)[0] + "."
        caption += f"\n💡 {short}\n"
    
    # CTA
    if all_serials and len(all_serials) > 1:
        caption += f"\n{pillar['cta'].format(start_serial=all_serials[0], end_serial=all_serials[-1])}\n"
    else:
        caption += f"\n{pillar['cta'].format(serial=serial)}\n"
    
    # Hashtags
    tags = " ".join(pillar["hashtags"][:5])
    if account == "luxe":
        tags += " #luxe_fashion_finds #ad #affiliate"
    else:
        tags += " #smart_buy_guides #ad #affiliate"
    
    caption += f"\n\n{tags}"
    
    return caption


def main():
    print("=" * 60)
    print("TRAFFIC PLANNER — Content Assignment & Caption Generation")
    print("=" * 60)
    
    # Load traffic feed
    with open(FEED_PATH, "r", encoding="utf-8") as f:
        feed_data = json.load(f)
    
    products = feed_data.get("products", [])
    print(f"Loaded {len(products)} products from feed")
    
    # Group by account
    luxe_products = [p for p in products if p.get("account") == "luxe"]
    smart_products = [p for p in products if p.get("account") == "smart"]
    
    print(f"  Luxe (Account A): {len(luxe_products)} products")
    print(f"  Smart (Account B): {len(smart_products)} products")
    
    # Assign pillars and generate captions
    plan = {
        "generated_at": datetime.now().isoformat(),
        "season": SEASON,
        "luxe": [],
        "smart": []
    }
    
    # Process Luxe products
    for p in luxe_products:
        pillar = categorize_product(p)
        serial = p.get("serial", 0)
        caption = generate_caption(p, pillar, "luxe", serial)
        
        plan["luxe"].append({
            "serial": serial,
            "pillar": pillar,
            "pillar_name": PILLARS_LUXE[pillar]["name"],
            "format": PILLARS_LUXE[pillar]["format"],
            "product": p,
            "caption": caption,
            "hashtags": PILLARS_LUXE[pillar]["hashtags"]
        })
    
    # Process Smart products
    for p in smart_products:
        pillar = categorize_product(p)
        serial = p.get("serial", 0)
        caption = generate_caption(p, pillar, "smart", serial)
        
        plan["smart"].append({
            "serial": serial,
            "pillar": pillar,
            "pillar_name": PILLARS_SMART[pillar]["name"],
            "format": PILLARS_SMART[pillar]["format"],
            "product": p,
            "caption": caption,
            "hashtags": PILLARS_SMART[pillar]["hashtags"]
        })
    
    # Create weekly edit / best_of groups (multi-product posts)
    luxe_serials = [p["serial"] for p in plan["luxe"]]
    smart_serials = [p["serial"] for p in plan["smart"]]
    
    plan["multi_posts"] = {
        "luxe_weekly_edit": {
            "serials": luxe_serials,
            "caption": generate_caption(
                {"name": "Weekly Luxe Edit", "description": "This week's curated luxury picks"},
                "weekly_edit", "luxe", min(luxe_serials), luxe_serials
            ),
            "format": "carousel_pin"
        },
        "smart_best_of": {
            "serials": smart_serials,
            "caption": generate_caption(
                {"name": f"Best {SEASON.capitalize()} Finds", "description": f"Top {len(smart_serials)} smart buys this {SEASON}"},
                "best_of", "smart", min(smart_serials), smart_serials
            ),
            "format": "carousel_pin"
        }
    }
    
    # Save plan
    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Content plan saved: {PLAN_PATH}")
    print(f"  Luxe posts: {len(plan['luxe'])}")
    print(f"  Smart posts: {len(plan['smart'])}")
    print(f"  Multi-posts: 2 (weekly edit + best of)")
    
    return plan


if __name__ == "__main__":
    main()