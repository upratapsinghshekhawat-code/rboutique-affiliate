#!/usr/bin/env python3
"""
Asset Generator — Creates CapCut projects, Pinterest pins, YouTube metadata.
Reads content_plan.json → outputs assets in /content/queue/
"""
import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import urllib.request

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
PLAN_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.py"
CONTENT_QUEUE = BASE / "rboutique-affiliate" / "content" / "queue"

# Ensure queue directories exist
for subdir in ["luxe_reels", "smart_reels", "pinterest_pins", "youtube_shorts", "facebook_reels", "tiktok_reels"]:
    (CONTENT_QUEUE / subdir).mkdir(parents=True, exist_ok=True)

# ─── TEMPLATE DIMENSIONS ────────────────────────────────────────────────
DIMENSIONS = {
    "reel": (1080, 1920),      # 9:16 for Reels/Shorts/TikTok
    "pin": (1000, 1500),       # 2:3 for Pinterest
    "story": (1080, 1920),     # 9:16 for Stories
}

# ─── BRAND COLORS ───────────────────────────────────────────────────────
LUXE_COLORS = {
    "bg": "#0a0a0f",
    "card_bg": "#111118",
    "accent": "#d6a96a",
    "text": "#e8e6e3",
    "muted": "#9a8f7a",
    "border": "#1e1e2e"
}

SMART_COLORS = {
    "bg": "#0d1117",
    "card_bg": "#161b22",
    "accent": "#58a6ff",
    "text": "#e6edf3",
    "muted": "#8b949e",
    "border": "#30363d"
}


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def download_image(url, save_path):
    """Download product image."""
    try:
        urllib.request.urlretrieve(url, save_path)
        return True
    except:
        return False


def create_placeholder_image(save_path, text, colors, size=(1080, 1920)):
    """Create a placeholder image with text."""
    img = Image.new('RGB', size, hex_to_rgb(colors["bg"]))
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default
    try:
        font_large = ImageFont.truetype("arial.ttf", 72)
        font_medium = ImageFont.truetype("arial.ttf", 48)
        font_small = ImageFont.truetype("arial.ttf", 36)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Center text
    bbox = draw.textbbox((0, 0), text, font=font_large)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (size[0] - text_w) // 2
    y = (size[1] - text_h) // 2
    
    draw.text((x, y), text, fill=hex_to_rgb(colors["accent"]), font=font_large)
    
    # Add subtitle
    subtitle = "Product Image"
    bbox = draw.textbbox((0, 0), subtitle, font=font_medium)
    text_w = bbox[2] - bbox[0]
    x = (size[0] - text_w) // 2
    y = y + text_h + 40
    draw.text((x, y), subtitle, fill=hex_to_rgb(colors["muted"]), font=font_medium)
    
    img.save(save_path)
    return True


def create_capcut_project(product, caption, serial, account, output_dir, video_type="reel"):
    """Create a CapCut project file (.cst) for a single product reel."""
    
    colors = LUXE_COLORS if account == "luxe" else SMART_COLORS
    w, h = DIMENSIONS["reel"]
    
    # Product image
    img_path = output_dir / f"product_{serial}.jpg"
    if product.get("image"):
        download_image(product["image"], img_path)
    else:
        create_placeholder_image(img_path, product.get("name", "Product"), colors, (w, h))
    
    # Background music placeholder (user adds in CapCut)
    music_path = output_dir / "background_music.mp3"
    
    # CapCut project structure (simplified XML)
    # Note: CapCut uses .cst files which are ZIP archives with specific structure
    # For hybrid workflow, we create the assets and a project template
    
    project_data = {
        "version": "3.0",
        "project_name": f"{account}_{serial}_{product.get('name', 'product')[:30]}",
        "canvas_size": {"width": w, "height": h},
        "duration": 15000000,  # 15 seconds in microseconds
        "tracks": [
            {
                "type": "video",
                "clips": [
                    {
                        "asset_path": f"product_{serial}.jpg",
                        "start": 0,
                        "duration": 5000000,
                        "transform": {"scale": 1.1, "position": [0, 0]},
                        "animation": "ken_burns_slow"
                    },
                    {
                        "asset_path": f"product_{serial}.jpg",
                        "start": 5000000,
                        "duration": 5000000,
                        "transform": {"scale": 1.05, "position": [0, 0]},
                        "animation": "zoom_in"
                    },
                    {
                        "asset_path": f"product_{serial}.jpg",
                        "start": 10000000,
                        "duration": 5000000,
                        "transform": {"scale": 1.0, "position": [0, 0]},
                        "animation": "fade_out"
                    }
                ]
            },
            {
                "type": "text",
                "clips": [
                    {
                        "text": product.get("name", "Product"),
                        "start": 1000000,
                        "duration": 4000000,
                        "style": {"font_size": 64, "color": colors["accent"], "font_weight": "bold"},
                        "position": "top_center",
                        "animation": "fade_in_up"
                    },
                    {
                        "text": f"${product.get('price', 'Check Price')}" if product.get('price') else "Tap for Price",
                        "start": 6000000,
                        "duration": 4000000,
                        "style": {"font_size": 48, "color": colors["text"]},
                        "position": "bottom_center",
                        "animation": "fade_in"
                    },
                    {
                        "text": f"Link #{serial} in bio",
                        "start": 12000000,
                        "duration": 3000000,
                        "style": {"font_size": 40, "color": colors["accent"], "font_weight": "bold"},
                        "position": "bottom_center",
                        "animation": "pulse"
                    }
                ]
            },
            {
                "type": "audio",
                "clips": [
                    {
                        "asset_path": "background_music.mp3",
                        "start": 0,
                        "duration": 15000000,
                        "volume": 0.3
                    }
                ]
            }
        ],
        "caption_file": f"caption_{serial}.txt",
        "metadata_file": f"meta_{serial}.json"
    }
    
    # Save project JSON (for reference)
    with open(output_dir / f"project_{serial}.json", "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2)
    
    # Save caption
    with open(output_dir / f"caption_{serial}.txt", "w", encoding="utf-8") as f:
        f.write(caption)
    
    # Save metadata
    meta = {
        "serial": serial,
        "account": account,
        "product": product,
        "caption": caption,
        "hashtags": " ".join([tag for tag in caption.split() if tag.startswith("#")]),
        "platform": video_type
    }
    with open(output_dir / f"meta_{serial}.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    
    # Create a simple CapCut-compatible project marker
    # Actual .cst creation requires CapCut app - we create the asset structure
    with open(output_dir / f"README_{serial}.txt", "w", encoding="utf-8") as f:
        f.write(f"""CAPCUT PROJECT SETUP FOR SERIAL #{serial}
==========================================
1. Open CapCut Desktop
2. Create new project: 9:16 (1080x1920)
3. Import: product_{serial}.jpg (3x for 3 segments)
4. Add text overlays per project_{serial}.json
5. Add background music
6. Export as MP4
7. Caption ready in caption_{serial}.txt
8. Metadata in meta_{serial}.json

Product: {product.get('name')}
Brand: {product.get('brand')}
Tracked Link: {product.get('tracked_link')}
Serial: #{serial}
Account: {account}
""")
    
    return True


def create_pinterest_pin(product, caption, serial, account, output_dir):
    """Create Pinterest pin image (1000x1500)."""
    
    colors = LUXE_COLORS if account == "luxe" else SMART_COLORS
    w, h = DIMENSIONS["pin"]
    
    img_path = output_dir / f"pin_{serial}.jpg"
    
    # Product image
    product_img_path = output_dir / f"product_{serial}_pin.jpg"
    if product.get("image"):
        download_image(product["image"], product_img_path)
        # Resize to fit pin
        img = Image.open(product_img_path)
        img = img.resize((w, int(w * img.height / img.width)), Image.Resampling.LANCZOS)
        if img.height > h:
            img = img.crop((0, 0, w, h))
        img.save(img_path)
    else:
        create_placeholder_image(img_path, product.get("name", "Product"), colors, (w, h))
    
    # Add text overlay version
    img_with_text = Image.new('RGB', (w, h), hex_to_rgb(colors["bg"]))
    
    # Place product image at top 70%
    prod_img = Image.open(product_img_path)
    img_with_text.paste(prod_img, (0, 0))
    
    # Add text at bottom 30%
    draw = ImageDraw.Draw(img_with_text)
    try:
        font_title = ImageFont.truetype("arial.ttf", 48)
        font_brand = ImageFont.truetype("arial.ttf", 36)
        font_price = ImageFont.truetype("arial.ttf", 42)
    except:
        font_title = ImageFont.load_default()
        font_brand = ImageFont.load_default()
        font_price = ImageFont.load_default()
    
    y_start = int(h * 0.75)
    padding = 40
    
    # Title
    name = product.get("name", "Product")
    # Wrap text
    words = name.split()
    lines = []
    current = ""
    for word in words:
        test = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test, font=font_title)
        if bbox[2] - bbox[0] < w - 2*padding:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    
    y = y_start
    for line in lines[:2]:  # Max 2 lines
        bbox = draw.textbbox((0, 0), line, font=font_title)
        x = (w - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, fill=hex_to_rgb(colors["text"]), font=font_title)
        y += bbox[3] - bbox[1] + 10
    
    # Brand
    if product.get("brand"):
        brand_text = product["brand"]
        bbox = draw.textbbox((0, 0), brand_text, font=font_brand)
        x = (w - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), brand_text, fill=hex_to_rgb(colors["accent"]), font=font_brand)
        y += bbox[3] - bbox[1] + 15
    
    # Price/CTA
    price_text = f"${product.get('price', 'Check Price')}" if product.get('price') else "Tap to Shop →"
    bbox = draw.textbbox((0, 0), price_text, font=font_price)
    x = (w - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), price_text, fill=hex_to_rgb(colors["accent"]), font=font_price)
    
    # Save
    final_path = output_dir / f"pin_{serial}_final.jpg"
    img_with_text.save(final_path)
    
    # Save metadata
    meta = {
        "serial": serial,
        "account": account,
        "product": product,
        "image_path": str(final_path),
        "board_suggestions": get_board_suggestions(product, account),
        "alt_text": f"{name} by {product.get('brand', 'Brand')} - {product.get('description', '')[:200]}",
        "link": product.get("tracked_link"),
        "hashtags": " ".join([tag for tag in caption.split() if tag.startswith("#")])
    }
    with open(output_dir / f"pin_{serial}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    
    return True


def get_board_suggestions(product, account):
    """Suggest Pinterest boards based on product."""
    category = product.get("category", "").lower()
    
    if account == "luxe":
        boards = {
            "bag": "Luxury Bags & Totes",
            "shoe": "Designer Shoes",
            "heel": "Designer Shoes",
            "boot": "Designer Shoes",
            "dress": "Designer Clothing",
            "top": "Designer Clothing",
            "shirt": "Designer Clothing",
            "jewel": "Fine Jewelry & Accessories",
            "accessory": "Fine Jewelry & Accessories",
            "beauty": "Beauty & Fragrance",
            "fragrance": "Beauty & Fragrance",
            "sale": "Luxury Sale Alerts"
        }
    else:
        boards = {
            "tech": "Tech Under $200",
            "electronic": "Tech Under $200",
            "home": "Home & Kitchen Essentials",
            "kitchen": "Kitchen Gadgets Under $50",
            "tool": "Home & Kitchen Essentials",
            "fitness": "Fitness & Outdoors",
            "health": "Fitness & Outdoors",
            "gadget": "Kitchen Gadgets Under $50",
            "seasonal": "Seasonal Must-Haves",
            "problem": "Problem Solvers"
        }
    
    for kw, board in boards.items():
        if kw in category or kw in product.get("name", "").lower():
            return board
    
    return "Designer Clothing" if account == "luxe" else "Tech Under $200"


def create_youtube_metadata(product, caption, serial, account, output_dir):
    """Create YouTube Shorts metadata."""
    
    meta = {
        "serial": serial,
        "account": account,
        "title": f"{product.get('name', 'Product')} — Link #{serial} in bio",
        "description": caption + f"\n\n#Shorts #Affiliate #Ad",
        "tags": [tag.replace("#", "") for tag in caption.split() if tag.startswith("#")][:15],
        "category": "22",  # People & Blogs
        "privacy": "public",
        "playlist": f"{account.capitalize()} - All Shorts",
        "thumbnail_time": "00:02",
        "product_link": product.get("tracked_link"),
        "serial_number": serial
    }
    
    with open(output_dir / f"youtube_{serial}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    
    return True


def create_instagram_meta(product, caption, serial, account, output_dir):
    """Create Instagram Reels metadata."""
    
    meta = {
        "serial": serial,
        "account": account,
        "caption": caption,
        "product_link": product.get("tracked_link"),
        "linktree_serial": serial,
        "cover_frame": "00:01",
        "location": "Worldwide",
        "alt_text": f"{product.get('name', 'Product')} by {product.get('brand', 'Brand')}"
    }
    
    with open(output_dir / f"insta_{serial}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    
    return True


def main():
    print("=" * 60)
    print("ASSET GENERATOR — CapCut Projects, Pins, YT Meta")
    print("=" * 60)
    
    # Load content plan
    plan_path = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"
    if not plan_path.exists():
        print("  ✗ content_plan.json not found. Run traffic_planner.py first.")
        return
    
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    # Clear queue
    if CONTENT_QUEUE.exists():
        shutil.rmtree(CONTENT_QUEUE)
    for subdir in ["luxe_reels", "smart_reels", "pinterest_pins", "youtube_shorts", "facebook_reels", "tiktok_reels"]:
        (CONTENT_QUEUE / subdir).mkdir(parents=True, exist_ok=True)
    
    # Generate assets for Luxe products
    print(f"\nGenerating Luxe assets ({len(plan['luxe'])} products)...")
    for item in plan["luxe"]:
        serial = item["serial"]
        product = item["product"]
        caption = item["caption"]
        out_dir = CONTENT_QUEUE / "luxe_reels" / f"serial_{serial}"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        create_capcut_project(product, caption, serial, "luxe", out_dir, "reel")
        create_pinterest_pin(product, caption, serial, "luxe", CONTENT_QUEUE / "pinterest_pins")
        create_youtube_metadata(product, caption, serial, "luxe", CONTENT_QUEUE / "youtube_shorts")
        create_instagram_meta(product, caption, serial, "luxe", CONTENT_QUEUE / "instagram_reels")
        
        print(f"  ✓ Serial #{serial}: {product.get('name', 'Product')[:40]}")
    
    # Generate assets for Smart products
    print(f"\nGenerating Smart assets ({len(plan['smart'])} products)...")
    for item in plan["smart"]:
        serial = item["serial"]
        product = item["product"]
        caption = item["caption"]
        out_dir = CONTENT_QUEUE / "smart_reels" / f"serial_{serial}"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        create_capcut_project(product, caption, serial, "smart", out_dir, "reel")
        create_pinterest_pin(product, caption, serial, "smart", CONTENT_QUEUE / "pinterest_pins")
        create_youtube_metadata(product, caption, serial, "smart", CONTENT_QUEUE / "youtube_shorts")
        create_instagram_meta(product, caption, serial, "smart", CONTENT_QUEUE / "instagram_reels")
        
        print(f"  ✓ Serial #{serial}: {product.get('name', 'Product')[:40]}")
    
    # Multi-post assets
    print("\nGenerating multi-post assets...")
    for key, multi in plan.get("multi_posts", {}).items():
        serials = multi["serials"]
        account = "luxe" if "luxe" in key else "smart"
        caption = multi["caption"]
        
        out_dir = CONTENT_QUEUE / f"pinterest_pins" / f"multi_{key}"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Create multi-image pin
        create_pinterest_pin(
            {"name": multi.get("product", {}).get("name", "Collection"), "brand": account.capitalize(), "price": ""},
            caption, f"multi_{key}", account, out_dir
        )
        
        print(f"  ✓ {key}: serials {min(serials)}-{max(serials)}")
    
    print(f"\n✓ All assets generated in: {CONTENT_QUEUE}")
    print(f"  Structure:")
    for subdir in CONTENT_QUEUE.iterdir():
        if subdir.is_dir():
            count = len([f for f in subdir.rglob("*") if f.is_file()])
            print(f"    {subdir.name}: {count} files")


if __name__ == "__main__":
    main()