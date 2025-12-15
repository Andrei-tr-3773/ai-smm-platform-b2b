# Image Inventory

## Overview

This document tracks all stock images used in the AI SMM Platform. All images are from free stock photo sources (Unsplash, Pexels) with appropriate licenses for commercial use.

---

## Directory Structure

```
static/images/
├── logos/              # Brand logos (3 SVG files)
│   ├── fitzone_logo.svg
│   ├── cloudflow_logo.svg
│   └── shopstyle_logo.svg
├── fitness/            # Fitness & wellness images (10 images)
├── ecommerce/          # E-commerce & shopping images (10 images)
├── saas/               # SaaS & tech images (10 images)
├── generic/            # Generic business images (10 images)
└── platforms/          # Social media platform mockups (5 images)
```

---

## Logos (✅ Complete)

| File | Type | Brand Colors | Usage |
|------|------|--------------|-------|
| fitzone_logo.svg | SVG | Orange (#FF6B35), Black (#2D3142) | FitZone Fitness branding |
| cloudflow_logo.svg | SVG | Blue (#0066CC), Cyan (#00D9FF) | CloudFlow SaaS branding |
| shopstyle_logo.svg | SVG | Pink (#FF69B4), Gold (#FFD700) | ShopStyle E-commerce branding |

---

## Images to Download (TODO)

### Fitness & Wellness (10 images)

Download from **Unsplash** (https://unsplash.com):

1. **fitness-gym-01.jpg** - Search: "gym equipment" - Modern gym with weights
2. **fitness-workout-01.jpg** - Search: "person working out" - Person exercising
3. **fitness-class-01.jpg** - Search: "fitness class" - Group fitness class
4. **fitness-trainer-01.jpg** - Search: "personal trainer" - Trainer with client
5. **fitness-yoga-01.jpg** - Search: "yoga class" - Yoga studio scene
6. **fitness-running-01.jpg** - Search: "running outdoor" - Person running
7. **fitness-weights-01.jpg** - Search: "dumbbell workout" - Weight training
8. **fitness-cardio-01.jpg** - Search: "cardio exercise" - Cardio equipment
9. **fitness-success-01.jpg** - Search: "fitness transformation" - Success story concept
10. **fitness-nutrition-01.jpg** - Search: "healthy food fitness" - Nutrition/meal prep

**Download Instructions:**
```bash
# Navigate to static/images/fitness/
cd static/images/fitness/

# Download from Unsplash (replace PHOTO_ID with actual ID)
curl -o fitness-gym-01.jpg "https://unsplash.com/photos/PHOTO_ID/download?force=true"
```

---

### E-commerce & Shopping (10 images)

Download from **Pexels** (https://www.pexels.com):

1. **ecommerce-fashion-01.jpg** - Search: "fashion clothing" - Clothing display
2. **ecommerce-shopping-01.jpg** - Search: "shopping bags" - Shopping bags
3. **ecommerce-online-01.jpg** - Search: "online shopping laptop" - Person shopping online
4. **ecommerce-product-01.jpg** - Search: "product photography" - Product showcase
5. **ecommerce-dress-01.jpg** - Search: "dress fashion" - Fashion dress
6. **ecommerce-accessories-01.jpg** - Search: "fashion accessories" - Accessories display
7. **ecommerce-customer-01.jpg** - Search: "happy shopper" - Happy customer
8. **ecommerce-package-01.jpg** - Search: "package delivery" - Delivery package
9. **ecommerce-store-01.jpg** - Search: "boutique store" - Store interior
10. **ecommerce-mobile-01.jpg** - Search: "mobile shopping" - Phone with shopping app

---

### SaaS & Tech (10 images)

Download from **Unsplash**:

1. **saas-laptop-01.jpg** - Search: "laptop code" - Developer working
2. **saas-team-01.jpg** - Search: "team collaboration" - Team meeting
3. **saas-dashboard-01.jpg** - Search: "dashboard analytics" - Analytics dashboard
4. **saas-office-01.jpg** - Search: "modern office" - Office workspace
5. **saas-remote-01.jpg** - Search: "remote work" - Remote worker
6. **saas-meeting-01.jpg** - Search: "video conference" - Online meeting
7. **saas-code-01.jpg** - Search: "programming code" - Code on screen
8. **saas-startup-01.jpg** - Search: "startup office" - Startup environment
9. **saas-cloud-01.jpg** - Search: "cloud computing concept" - Cloud tech concept
10. **saas-api-01.jpg** - Search: "api development" - API/integration concept

---

### Generic Business (10 images)

Download from **Pexels**:

1. **business-meeting-01.jpg** - Search: "business meeting" - Professional meeting
2. **business-handshake-01.jpg** - Search: "business handshake" - Partnership
3. **business-success-01.jpg** - Search: "business success" - Success celebration
4. **business-office-01.jpg** - Search: "office building" - Office exterior
5. **business-phone-01.jpg** - Search: "smartphone business" - Phone with apps
6. **business-team-01.jpg** - Search: "diverse team" - Diverse team
7. **business-presentation-01.jpg** - Search: "presentation business" - Presentation scene
8. **business-coworking-01.jpg** - Search: "coworking space" - Coworking environment
9. **business-coffee-01.jpg** - Search: "business coffee" - Business casual
10. **business-growth-01.jpg** - Search: "business growth chart" - Growth concept

---

### Social Media Platforms (5 images)

Download from **Unsplash**:

1. **platform-instagram-01.jpg** - Search: "instagram mobile" - Instagram app mockup
2. **platform-facebook-01.jpg** - Search: "facebook social" - Facebook interface
3. **platform-telegram-01.jpg** - Search: "telegram messaging" - Telegram app
4. **platform-linkedin-01.jpg** - Search: "linkedin professional" - LinkedIn interface
5. **platform-social-01.jpg** - Search: "social media icons" - Social media concept

---

## Download Script

Create a bash script to download all images:

```bash
#!/bin/bash
# download_images.sh

# Unsplash API key (get from https://unsplash.com/developers)
UNSPLASH_ACCESS_KEY="your_access_key_here"

# Function to download from Unsplash
download_unsplash() {
    local query=$1
    local filename=$2
    local directory=$3

    # Search for photo
    photo_url=$(curl -s "https://api.unsplash.com/search/photos?query=${query}&client_id=${UNSPLASH_ACCESS_KEY}" | jq -r '.results[0].urls.regular')

    # Download
    curl -o "${directory}/${filename}" "${photo_url}"
    echo "Downloaded: ${filename}"
}

# Create directories
mkdir -p static/images/{fitness,ecommerce,saas,generic,platforms}

# Download fitness images
download_unsplash "gym equipment" "fitness-gym-01.jpg" "static/images/fitness"
download_unsplash "person working out" "fitness-workout-01.jpg" "static/images/fitness"
# ... (add all 45 images)

echo "✅ All images downloaded!"
```

---

## Attribution & Credits

### Unsplash License
- **License**: Unsplash License (https://unsplash.com/license)
- **Usage**: Free to use for commercial and non-commercial purposes
- **Attribution**: Optional but appreciated

### Pexels License
- **License**: Pexels License (https://www.pexels.com/license/)
- **Usage**: Free to use for commercial and non-commercial purposes
- **Attribution**: Not required but appreciated

---

## Credits (To be filled after download)

### Fitness Images
- fitness-gym-01.jpg: Photo by [Photographer Name](link) on Unsplash
- (Add after download)

### E-commerce Images
- ecommerce-fashion-01.jpg: Photo by [Photographer Name](link) on Pexels
- (Add after download)

### SaaS Images
- saas-laptop-01.jpg: Photo by [Photographer Name](link) on Unsplash
- (Add after download)

### Generic Business Images
- business-meeting-01.jpg: Photo by [Photographer Name](link) on Pexels
- (Add after download)

### Platform Images
- platform-instagram-01.jpg: Photo by [Photographer Name](link) on Unsplash
- (Add after download)

---

## Usage Guidelines

1. **Image Selection**: Choose high-quality, professional images that represent target businesses
2. **Diversity**: Ensure diverse representation in people-focused images
3. **Resolution**: Minimum 1920x1080px for web use
4. **File Format**: JPG for photos, SVG for logos
5. **File Naming**: descriptive-name-##.jpg (lowercase, dash-separated)
6. **Attribution**: Track photographer credits for proper attribution

---

## Status

- ✅ Logos: 3/3 complete (SVG created)
- ⏳ Fitness Images: 0/10 (to download)
- ⏳ E-commerce Images: 0/10 (to download)
- ⏳ SaaS Images: 0/10 (to download)
- ⏳ Generic Images: 0/10 (to download)
- ⏳ Platform Images: 0/5 (to download)

**Total Progress**: 3/48 (6%)

---

## Next Steps

1. Get Unsplash API key (free): https://unsplash.com/developers
2. Run download script or manually download images
3. Update credits section with photographer attributions
4. Create CREDITS.md with full attribution list
5. Test images in templates to ensure quality

---

## Alternative: Use Placeholder Images

For development/testing, use placeholder services:

- **Lorem Picsum**: https://picsum.photos/1920/1080 (random images)
- **Unsplash Source**: https://source.unsplash.com/1920x1080/?fitness (keyword-based)
- **Placeholder.com**: https://via.placeholder.com/1920x1080/FF6B35/FFFFFF?text=FitZone

Example:
```html
<img src="https://source.unsplash.com/1920x1080/?gym" alt="Gym">
```
