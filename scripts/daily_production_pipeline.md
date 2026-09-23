# Daily Product Reel Generation - Workflow Instructions

## System Overview
Creating Instagram Reels with 3 trending luxury products using ComfyUI and RBoutique affiliate program.

## Setup Requirements

### Hardware
- NVIDIA GPU with ≥8 GB VRAM (recommended for SDXL)
- Windows 10 (HP Victus)
- 16GB+ RAM (recommended)

### Software Dependencies
- Python 3.14+
- pipx/uvx for package management
- Internet connection for model downloads

### Environment Variables
```bash
export HF_API_TOKEN="your_huggingface_token"
export COMFY_CLOUD_API_KEY="your_cloud_api_key"
```

## ComfyUI Workflow Configuration

### Core Nodes Required
1. **CheckpointLoaderSimple** - SDXL base model (6.5GB)
2. **CLIPLoader** - Text encoding model
3. **VAELoader** - Image decoding
4. **EmptyLatentImage** - Canvas preparation
5. **CLIPTextEncode** - Product prompts
6. **KSampler** - Image generation
7. **VAEDecode** - Final image rendering
8. **SaveImage** - Output management

### Product Prompts (Generated)

#### Designer Silk Scarf
```
Elegant silk scarf draped on marble surface, soft natural lighting, 9:16 vertical, photorealistic, luxury fashion product photography, studio lighting, rich fabric texture, sophisticated aesthetic, warm tones
```

#### Sculptural Leather Mini Bag  
```
Sculptural leather mini bag on marble pedestal, dramatic studio lighting, 9:16 vertical, photorealistic, luxury fashion product photography, high detail, modern design, professional photography, clean background
```

#### Statement Oversized Sunglasses
```
Statement oversized sunglasses on model face, bold frame close-up, studio lighting, 9:16 vertical, photorealistic, luxury fashion product photography, high detail, modern design, professional photography, clean background
```

## Directory Structure
```
rboutique-affiliate/
├── scripts/
│   ├── workflow_v1_20260919.json
│   ├── reel_script.md
│   ├── deep_link_generated.txt
│   └── trend_analysis_20260919.json
├── site/
│   ├── index.html
│   └── assets/
├── assets/
│   ├── workflow/
│   ├── prompts/
│   └── product_shots/
├── links/
│   └── links_20260919.txt
└── references/
    ├── affiliate-video-pipeline.md
    └── session-notes.md
```

## Execution Pipeline

### Step 1: Local Setup
```bash
cd /c/Users/HP/Documents/comfy/ComfyUI
uvx --from comfy-cli comfy model download --set-hf-api-token $HF_API_TOKEN
uvx --from comfy-cli comfy launch --background
```

### Step 2: Image Generation (Batch Processing)
```bash
python3 scripts/run_workflow.py \
  --workflow assets/workflow/reel_20260919.json \
  --args '{"prompt": "Designer Silk Scarf product photography", "seed": -1, "steps": 30}' \
  --output-dir ./assets/product_shots/
```

### Step 3: Video Assembly
```bash
ffmpeg -framerate 2 -i assets/product_shots/led_strip_%04d.png \
       -i assets/product_shots/earbuds_%04d.png \
       -i assets/product_shots/garlic_chopper_%04d.png \
       -filter_complex "[0:v]setpts=PTS/STARTPTS[0];[1:v]setpts=PTS/STARTPTS[1];[2:v]setpts=PTS/STARTPTS[2];[0:v][1:v][2:v]concat=n=3:v=1[outv]" \
       -map "[outv]" -c:v libx264 -pix_fmt yuv420p -vf "scale=1080:1920" reel_raw.mp4
```

### Step 4: Audio Integration
```bash
ffmpeg -i reel_raw.mp4 -i trending_audio.mp3 \
       -filter_complex "[0:a]volume=0.5[a0];[1:a]volume=1.0[a1];[a0][a1]amix=inputs=2:duration=first[outa]" \
       -c:v copy -map 0:v -map "[outa]" reel_final.mp4
```

## Content Management

### Affiliate Link Generation
```bash
# Generate tracked links for all products
cd scripts
python3 deep_link_generator.py "https://www.rboutique.com/en-us/products/designer-silk-scarf"
python3 deep_link_generator.py "https://www.rboutique.com/en-us/products/sculptural-leather-mini-bag"  
python3 deep_link_generator.py "https://www.rboutique.com/en-us/products/statement-oversized-sunglasses"
```

### Daily Scheduling
- **Execution time**: 2-3 hours for full pipeline
- **Target posting**: 10 AM EST daily
- **Format**: 60-second vertical video
- **Hashtags**: #LuxuryFashion #Trending2026 #RBoutique #Reels

## Quality Assurance

### Pre-Production Checks
- [ ] ComfyUI server running and healthy
- [ ] All product models installed and verified
- [ ] Affiliate links generating correctly
- [ ] Trending audio selected and available

### Post-Production Validation
- [ ] All 3 product shots generated (1080x1920)
- [ ] Video compilation completed
- [ ] Audio integration seamless
- [ ] Text overlays readable and properly positioned

## Technical Specifications

### Image Generation Parameters
- **Resolution**: 1080x1920 (9:16 vertical)
- **Model**: SDXL Base 1.0
- **Steps**: 30 (quality vs. speed balance)
- **CFG Scale**: 7.5 (guidance strength)
- **Seed**: -1 (randomized each day)

### Video Output
- **Codec**: H.264 (MP4)
- **Bitrate**: 2.5 Mbps (optimized for mobile)
- **Frame Rate**: 24 fps
- **Duration**: 60 seconds
- **Aspect Ratio**: 9:16

## Monitoring and Analytics
- **Server health**: /system_stats endpoint
- **Queue status**: /queue endpoint
- **Job tracking**: prompt_id management
- **Output verification**: file checksums

## Troubleshooting

### Common Issues
1. **SQLAlchemy missing**: Install dependencies via uvx
2. **Model download failed**: Check HF API token
3. **Server not responding**: Restart with proper environment
4. **Video encoding errors**: Verify ffmpeg installation

### Fallback Options
- **Comfy Cloud**: For hardware limitations
- **Local CPU**: Slower but functional
- **Manual assets**: Pre-generated if AI pipeline fails

## Success Metrics
- **Daily generation**: 3 product shots per run
- **Video output**: 1 completed reel per day
- **Engagement target**: 1000+ views per reel
- **Conversion rate**: 2%+ affiliate click-through

This pipeline is designed for automated daily production with manual oversight for quality assurance.