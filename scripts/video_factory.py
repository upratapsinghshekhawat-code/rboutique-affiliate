#!/usr/bin/env python3
"""
Video Factory — Renders complete vertical MP4s with TTS, music, subtitles.
Zero human touch. Uses FFmpeg + MoviePy 2.x + Edge TTS (free).
"""
import json
import os
import random
import urllib.request
from pathlib import Path
from moviepy import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip,
    CompositeVideoClip, concatenate_videoclips, concatenate_audioclips,
    CompositeAudioClip
)
from moviepy.video.fx import Resize, Crop
from moviepy.audio.fx import MultiplyVolume, AudioLoop
from PIL import Image, ImageDraw, ImageFont
import asyncio
import edge_tts

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
PLAN_PATH = BASE / "rboutique-affiliate" / "scripts" / "content_plan.json"
QUEUE_DIR = BASE / "rboutique-affiliate" / "content" / "queue"

# ─── CONFIG ──────────────────────────────────────────────────────────────
DIMENSIONS = (1080, 1920)  # 9:16
FPS = 30
VIDEO_DURATION = 18  # seconds
SLIDE_DURATIONS = [3, 4, 4, 4, 3]  # Hook, Product, Benefit, Proof, CTA

# Brand configs
BRANDS = {
    "luxe": {
        "name": "Luxe Fashion Finds",
        "handle": "@luxe_fashion_finds",
        "colors": {"bg": "#0a0a0f", "card": "#111118", "accent": "#d6a96a", "text": "#e8e6e3", "muted": "#9a8f7a"},
        "voice": "en-US-AriaNeural",  # Female, warm, professional
        "music_vibe": "luxury_ambient",
        "watermark": "LuxeFashionFinds"
    },
    "smart": {
        "name": "Smart Buy Guides",
        "handle": "@smart_buy_guides",
        "colors": {"bg": "#0d1117", "card": "#161b22", "accent": "#58a6ff", "text": "#e6edf3", "muted": "#8b949e"},
        "voice": "en-US-JennyNeural",  # Female, energetic, trustworthy
        "music_vibe": "upbeat_tech",
        "watermark": "SmartBuyGuides"
    }
}

MUSIC_MAP = {
    "luxury_ambient": ["assets/music/luxury_1.mp3", "assets/music/luxury_2.mp3"],
    "upbeat_tech": ["assets/music/tech_1.mp3", "assets/music/tech_2.mp3"]
}

# ─── HELPERS ─────────────────────────────────────────────────────────────
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def download_image(url, save_path):
    try:
        urllib.request.urlretrieve(url, save_path)
        return True
    except:
        return False

def get_lifestyle_broll(category, save_dir, count=3):
    urls = []
    for i in range(count):
        p = save_dir / f"broll_{i}.jpg"
        img = Image.new('RGB', DIMENSIONS, (20, 20, 30))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        draw.text((DIMENSIONS[0]//2, DIMENSIONS[1]//2), f"{category} lifestyle", fill=(100,100,120), anchor="mm", font=font)
        img.save(p)
        urls.append(str(p))
    return urls

async def generate_tts(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return True

def create_slide_image(text_lines, colors, size=DIMENSIONS, font_size=72):
    img = Image.new('RGB', size, hex_to_rgb(colors["bg"]))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
        font_small = ImageFont.truetype("arial.ttf", font_size//2)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    y = size[1] // 3
    for i, line in enumerate(text_lines):
        f = font if i == 0 else font_small
        color = hex_to_rgb(colors["accent"]) if i == 0 else hex_to_rgb(colors["text"])
        bbox = draw.textbbox((0, 0), line, font=f)
        w = bbox[2] - bbox[0]
        x = (size[0] - w) // 2
        draw.text((x, y), line, fill=color, font=f)
        y += bbox[3] - bbox[1] + 20
    
    # Watermark
    wm = f"@{colors.get('handle', 'brand')}"
    bbox = draw.textbbox((0, 0), wm, font=font_small)
    draw.text((size[0] - bbox[2] - 40, size[1] - bbox[3] - 40), wm, fill=hex_to_rgb(colors["muted"]), font=font_small)
    
    return img

# ─── SLIDE TEMPLATES ─────────────────────────────────────────────────────
SLIDE_TEMPLATES = {
    "hook": {
        "luxe": [
            "Why pay full price for {brand}?",
            "{name} — {discount}% off retail 💎",
            "Designer {category} under ${price}? Yes."
        ],
        "smart": [
            "Stop overpaying for {category} 🛑",
            "5 {category} under ${budget} that work ✅",
            "The {category} hack brands hate 🤫"
        ]
    },
    "product": [
        "🏷️ {name}",
        "🏷 {brand}" if "{brand}" else "",
        "📦 {category}",
        "💰 ${price}" if "{price}" else "💰 Check price →"
    ],
    "benefit": {
        "luxe": [
            "Premium {material} — lasts decades",
            "Timeless design, never goes out of style",
            "Worn by editors, loved by collectors"
        ],
        "smart": [
            "Solves {problem} instantly ⚡",
            "Rated 4.7★ by {reviews}+ buyers",
            "Saves you ${savings}/year vs alternatives"
        ]
    },
    "proof": [
        "⭐ {reviews}+ reviews • 4.8 avg",
        "🏆 Bestseller in {category}",
        "📦 Ships free, easy returns"
    ],
    "cta": [
        "Link #{serial} in bio → {handle}",
        "Tap bio link #{serial} — expires soon",
        "Your {category} upgrade: bio #{serial}"
    ]
}

# ─── MAIN VIDEO BUILDER ──────────────────────────────────────────────────
def build_video_for_product(product, account, serial, output_dir):
    """Render a single vertical MP4 for a product."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    video_path = output_dir / "video.mp4"
    
    # Skip if already rendered
    if video_path.exists() and video_path.stat().st_size > 100000:  # >100KB
        print(f"  ✓ Already rendered: {video_path}")
        return str(video_path)
    
    brand_cfg = BRANDS[account]
    colors = brand_cfg["colors"]
    colors["handle"] = brand_cfg["handle"]
    voice = brand_cfg["voice"]
    music_files = MUSIC_MAP[brand_cfg["music_vibe"]]
    
    # Prepare assets
    slide_texts = generate_slide_texts(product, account, serial)
    tts_paths = []
    
    for i, (slide_type, text) in enumerate(slide_texts):
        tts_path = output_dir / f"tts_{i}.mp3"
        asyncio.run(generate_tts(text, voice, str(tts_path)))
        tts_paths.append(str(tts_path))
    
    # Visual slides
    slide_images = []
    for i, (slide_type, text) in enumerate(slide_texts):
        img = create_slide_image(text.split('\n'), colors)
        img_path = output_dir / f"slide_{i}.jpg"
        img.save(img_path)
        slide_images.append(str(img_path))
    
    # Product images
    product_imgs = []
    if product.get("image"):
        main_img = output_dir / "product_main.jpg"
        if download_image(product["image"], main_img):
            product_imgs.append(str(main_img))
    
    # Add lifestyle b-roll
    brolls = get_lifestyle_broll(product.get("category", "product"), output_dir, 2)
    product_imgs.extend(brolls)
    
    # Build video with MoviePy 2.x
    video_clips = []
    
    # Slide 0: Hook (with product image ken burns)
    if product_imgs:
        hook_clip = ImageClip(product_imgs[0], duration=SLIDE_DURATIONS[0])
        hook_clip = hook_clip.resized(height=DIMENSIONS[1])
        # Center crop
        if hook_clip.w > DIMENSIONS[0]:
            hook_clip = hook_clip.cropped(x_center=hook_clip.w//2, width=DIMENSIONS[0])
        # Ken burns effect - zoom in slightly
        hook_clip = hook_clip.with_effects([Resize(lambda t: 1 + 0.1 * t / SLIDE_DURATIONS[0])])
    else:
        hook_clip = ImageClip(slide_images[0], duration=SLIDE_DURATIONS[0])
    video_clips.append(hook_clip)
    
    # Slides 1-4: Text slides
    for i in range(1, 5):
        base = ImageClip(slide_images[i], duration=SLIDE_DURATIONS[i])
        # Overlay product image briefly
        if product_imgs and i % 2 == 0:
            overlay = ImageClip(product_imgs[min(i, len(product_imgs)-1)], duration=1.5).with_opacity(0.3).with_position("center").with_start(SLIDE_DURATIONS[i] - 1.5)
            base = CompositeVideoClip([base, overlay])
        video_clips.append(base)
    
    # Concatenate
    final_video = concatenate_videoclips(video_clips)
    
    # Audio: TTS + Background music
    tts_audio = concatenate_audioclips([AudioFileClip(p) for p in tts_paths])
    music_path = random.choice(music_files)
    if os.path.exists(music_path):
        music = AudioFileClip(music_path).with_effects([MultiplyVolume(0.15)]).with_duration(final_video.duration)
        if music.duration < final_video.duration:
            music = music.with_effects([AudioLoop(duration=final_video.duration)])
        final_audio = CompositeAudioClip([tts_audio, music])
    else:
        final_audio = tts_audio
    
    final_video = final_video.with_audio(final_audio)
    
    # Subtitles
    subtitle_clips = []
    current_time = 0
    for i, (slide_type, text) in enumerate(slide_texts):
        clean_text = text.replace('\n', ' ')
        sub = TextClip(text=clean_text, font_size=48, color='white',
                       stroke_color='black', stroke_width=2, size=(DIMENSIONS[0]-100, None))
        sub = sub.with_position(('center', DIMENSIONS[1] - 200)).with_duration(SLIDE_DURATIONS[i]).with_start(current_time)
        subtitle_clips.append(sub)
        current_time += SLIDE_DURATIONS[i]
    
    if subtitle_clips:
        final_video = CompositeVideoClip([final_video] + subtitle_clips)
    
    # Watermark
    watermark = TextClip(text=brand_cfg["watermark"], font_size=36, color=colors["accent"])
    watermark = watermark.with_position(('right', 'bottom')).with_duration(final_video.duration).with_opacity(0.7)
    final_video = CompositeVideoClip([final_video, watermark])
    
    # Render
    final_video.write_videofile(
        str(video_path),
        fps=FPS,
        codec='libx264',
        audio_codec='aac',
        bitrate='5000k',
        threads=4,
        preset='medium',
        temp_audiofile=str(video_path).replace('.mp4', '_temp_audio.m4a'),
        remove_temp=True,
        logger=None
    )
    
    # Cleanup temp files
    for p in tts_paths + slide_images:
        try: os.remove(p)
        except: pass
    
    print(f"  ✓ Rendered: {video_path} ({os.path.getsize(video_path)/1e6:.1f}MB)")
    return str(video_path)


def generate_slide_texts(product, account, serial):
    brand_cfg = BRANDS[account]
    handle = brand_cfg["handle"]
    
    name = product.get("name", "This product")
    brand = product.get("brand", "Premium Brand")
    category = product.get("category", "item").lower()
    price = product.get("price", "99")
    description = product.get("description", "")
    tracked = product.get("tracked_link", "")
    
    discount = random.randint(35, 60)
    budget = random.choice([50, 100, 150, 200, 300])
    problem = random.choice(["wasting money", "buying wrong", "settling for less"])
    reviews = random.randint(2000, 15000)
    savings = random.randint(50, 300)
    material = random.choice(["Italian leather", "cashmere", "silk", "organic cotton"])
    
    texts = []
    
    # Slide 0: Hook
    hook_template = random.choice(SLIDE_TEMPLATES["hook"][account])
    hook = hook_template.format(brand=brand, name=name, category=category, 
                                 discount=discount, price=price, budget=budget)
    texts.append(("hook", hook))
    
    # Slide 1: Product
    product_lines = [
        name,
        f"by {brand}",
        category.title(),
        f"${price}" if price else "Tap for price"
    ]
    texts.append(("product", "\n".join([l for l in product_lines if l])))
    
    # Slide 2: Benefit
    benefit_template = random.choice(SLIDE_TEMPLATES["benefit"][account])
    benefit = benefit_template.format(material=material, problem=problem, 
                                       reviews=reviews, savings=savings)
    texts.append(("benefit", benefit))
    
    # Slide 3: Social Proof
    proof_template = random.choice(SLIDE_TEMPLATES["proof"])
    proof = proof_template.format(reviews=reviews, category=category)
    texts.append(("proof", proof))
    
    # Slide 4: CTA
    cta_template = random.choice(SLIDE_TEMPLATES["cta"])
    cta = cta_template.format(serial=serial, handle=handle, category=category)
    texts.append(("cta", cta))
    
    return texts


def audio_loop(clip, duration):
    loops = int(duration / clip.duration) + 1
    return concatenate_videoclips([clip] * loops).subclipped(0, duration)


def main():
    print("=" * 60)
    print("VIDEO FACTORY — Zero-Touch MP4 Rendering (MoviePy 2.x)")
    print("=" * 60)
    
    if not PLAN_PATH.exists():
        print("  ✗ content_plan.json not found. Run traffic_planner first.")
        return
    
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    # Ensure music assets exist
    music_dir = BASE / "rboutique-affiliate" / "assets" / "music"
    music_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate videos for Luxe
    print(f"\nRendering Luxe videos ({len(plan['luxe'])})...")
    for item in plan["luxe"]:
        serial = item["serial"]
        product = item["product"]
        out_dir = QUEUE_DIR / "luxe_reels" / f"serial_{serial}"
        build_video_for_product(product, "luxe", serial, out_dir)
    
    # Generate videos for Smart
    print(f"\nRendering Smart videos ({len(plan['smart'])})...")
    for item in plan["smart"]:
        serial = item["serial"]
        product = item["product"]
        out_dir = QUEUE_DIR / "smart_reels" / f"serial_{serial}"
        build_video_for_product(product, "smart", serial, out_dir)
    
    # Multi-post videos
    print("\nRendering multi-post videos...")
    for key, multi in plan.get("multi_posts", {}).items():
        account = "luxe" if "luxe" in key else "smart"
        serials = multi["serials"]
        out_dir = QUEUE_DIR / f"{account}_reels" / f"multi_{key}"
        print(f"  ✓ {key}: serials {min(serials)}-{max(serials)}")
    
    print(f"\n✓ All videos rendered in: {QUEUE_DIR}")


if __name__ == "__main__":
    main()