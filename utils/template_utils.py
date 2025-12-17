# template_utils.py
"""
Template utilities for AI Template Generator

Provides sample data generation and preview rendering for Liquid templates.
"""
from liquid import Template as LiquidTemplate, Environment
from typing import Dict, List
import random
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Sample data pools for realistic previews
SAMPLE_NAMES = [
    "Alex Rodriguez", "Jessica Kim", "Carlos Santos", "Sarah Johnson",
    "Michael Chen", "Emily Williams", "David Martinez", "Lisa Anderson"
]

SAMPLE_COMPANY_NAMES = [
    "FitZone Fitness", "CloudFlow", "ShopStyle", "TechStart Inc.",
    "Digital Boost Agency", "Wellness Hub", "Innovation Labs", "Urban Cafe"
]

SAMPLE_PRODUCT_NAMES = [
    "Premium Yoga Mat", "Smart Fitness Tracker", "Organic Protein Powder",
    "Wireless Headphones", "Designer Sneakers", "Laptop Stand Pro",
    "Coffee Maker Elite", "Winter Jacket Collection"
]

SAMPLE_COURSE_TITLES = [
    "Master Python Programming", "Digital Marketing Fundamentals",
    "UI/UX Design Bootcamp", "Business Analytics 101",
    "Creative Writing Workshop", "Photography Essentials"
]

SAMPLE_EVENT_TITLES = [
    "Annual Tech Summit 2025", "Startup Networking Mixer",
    "Product Launch Webinar", "Leadership Conference",
    "Industry Workshop Series", "Community Meetup"
]

SAMPLE_FEATURE_NAMES = [
    "Real-time Collaboration", "Advanced Analytics Dashboard",
    "AI-Powered Automation", "Cloud Backup & Sync",
    "Mobile App Integration", "Custom Reporting Tools"
]

SAMPLE_CLASS_NAMES = [
    "HIIT Cardio Blast", "Power Yoga Flow", "Strength Training 101",
    "Spin Class Advanced", "Pilates Core", "Boxing Bootcamp"
]

SAMPLE_DESCRIPTIONS = {
    "fitness": "Transform your body and mind with our high-intensity workout program. Designed by certified trainers to help you achieve your fitness goals faster.",
    "saas": "Streamline your workflow with cutting-edge automation tools. Boost productivity by 10x and save hours every week with our intelligent platform.",
    "ecommerce": "Premium quality meets unbeatable prices. Limited-time offer - don't miss out on this exclusive collection. Free shipping on orders over $50.",
    "education": "Learn from industry experts with hands-on projects and real-world examples. Lifetime access to course materials and community support.",
    "food": "Crafted with fresh, locally-sourced ingredients by our award-winning chef. A culinary experience that will delight your taste buds.",
    "event": "Join industry leaders and innovators for an unforgettable experience. Network, learn, and grow with like-minded professionals.",
    "testimonial": "This product completely changed how we work. The ROI was immediate and the support team is outstanding. Highly recommended!",
    "generic": "Experience excellence with our premium offering. Trusted by thousands of satisfied customers worldwide."
}

SAMPLE_BENEFITS = {
    "fitness": [
        "Burn up to 500 calories in 45 minutes",
        "Improve strength and endurance",
        "Expert guidance from certified trainers",
        "Flexible schedule - morning and evening classes"
    ],
    "saas": [
        "10x faster data processing",
        "99.9% uptime guarantee",
        "Seamless third-party integrations",
        "24/7 customer support"
    ],
    "ecommerce": [
        "Premium quality materials",
        "30-day money-back guarantee",
        "Free shipping on all orders",
        "Exclusive member discounts"
    ],
    "education": [
        "Self-paced learning",
        "Certification upon completion",
        "Lifetime access to materials",
        "Expert instructor support"
    ],
    "food": [
        "Made with fresh, organic ingredients",
        "Prepared by award-winning chef",
        "Locally sourced and sustainable",
        "Gluten-free and vegan options available"
    ],
    "consulting": [
        "Expert industry insights",
        "Customized solutions for your business",
        "Proven track record of success",
        "Ongoing support and guidance"
    ],
    "generic": [
        "High quality and reliability",
        "Excellent customer satisfaction",
        "Fast and efficient service",
        "Competitive pricing"
    ]
}


def generate_sample_data(field_schema: List[Dict], industry: str = "generic") -> Dict:
    """
    Generate realistic sample data for template preview.

    Args:
        field_schema: List of field definitions from AI generator
        industry: Industry context (fitness, saas, ecommerce, etc.)

    Returns:
        Dict with realistic sample values for each field
    """
    sample_data = {}

    for field in field_schema:
        field_name = field['name']
        field_type = field['type']
        field_label = field.get('label', field_name)

        # TEXT FIELDS
        if field_type == 'text':
            # Name fields
            if 'name' in field_name.lower():
                if 'instructor' in field_name.lower() or 'trainer' in field_name.lower():
                    sample_data[field_name] = random.choice(SAMPLE_NAMES)
                elif 'company' in field_name.lower() or 'business' in field_name.lower():
                    sample_data[field_name] = random.choice(SAMPLE_COMPANY_NAMES)
                elif 'customer' in field_name.lower() or 'client' in field_name.lower():
                    sample_data[field_name] = random.choice(SAMPLE_NAMES)
                elif 'speaker' in field_name.lower():
                    sample_data[field_name] = ", ".join(random.sample(SAMPLE_NAMES, 2))
                else:
                    sample_data[field_name] = random.choice(SAMPLE_NAMES)

            # Title/heading fields
            elif 'title' in field_name.lower() or 'heading' in field_name.lower():
                if industry == 'fitness':
                    sample_data[field_name] = random.choice(SAMPLE_CLASS_NAMES)
                elif industry == 'saas':
                    sample_data[field_name] = random.choice(SAMPLE_FEATURE_NAMES)
                elif industry == 'ecommerce':
                    sample_data[field_name] = random.choice(SAMPLE_PRODUCT_NAMES)
                elif industry == 'education':
                    sample_data[field_name] = random.choice(SAMPLE_COURSE_TITLES)
                elif 'event' in field_name.lower():
                    sample_data[field_name] = random.choice(SAMPLE_EVENT_TITLES)
                else:
                    sample_data[field_name] = f"Amazing {field_label}"

            # Class/course names
            elif 'class' in field_name.lower():
                sample_data[field_name] = random.choice(SAMPLE_CLASS_NAMES)
            elif 'course' in field_name.lower():
                sample_data[field_name] = random.choice(SAMPLE_COURSE_TITLES)
            elif 'product' in field_name.lower():
                sample_data[field_name] = random.choice(SAMPLE_PRODUCT_NAMES)
            elif 'feature' in field_name.lower():
                sample_data[field_name] = random.choice(SAMPLE_FEATURE_NAMES)
            elif 'event' in field_name.lower():
                sample_data[field_name] = random.choice(SAMPLE_EVENT_TITLES)

            # CTA buttons
            elif 'cta' in field_name.lower() or 'button' in field_name.lower():
                if 'register' in field_name.lower() or 'signup' in field_name.lower():
                    sample_data[field_name] = "Register Now"
                elif 'buy' in field_name.lower() or 'shop' in field_name.lower():
                    sample_data[field_name] = "Shop Now"
                elif 'learn' in field_name.lower():
                    sample_data[field_name] = "Learn More"
                elif 'contact' in field_name.lower():
                    sample_data[field_name] = "Contact Us"
                elif 'try' in field_name.lower():
                    sample_data[field_name] = "Try Free"
                elif 'rsvp' in field_name.lower():
                    sample_data[field_name] = "RSVP Now"
                else:
                    sample_data[field_name] = "Get Started"

            # Location fields
            elif 'location' in field_name.lower():
                sample_data[field_name] = "123 Main Street, Austin, TX 78701"

            # Tagline/subtitle
            elif 'tagline' in field_name.lower() or 'subtitle' in field_name.lower():
                sample_data[field_name] = "Transform Your Business Today"

            # Quote (for testimonials)
            elif 'quote' in field_name.lower():
                sample_data[field_name] = SAMPLE_DESCRIPTIONS.get('testimonial', "Amazing results!")

            # Generic text
            else:
                sample_data[field_name] = f"Sample {field_label}"

        # URL FIELDS (images, videos, links)
        elif field_type == 'url':
            if 'image' in field_name.lower() or 'photo' in field_name.lower() or 'picture' in field_name.lower():
                # Use different placeholder sizes based on context
                if 'logo' in field_name.lower():
                    sample_data[field_name] = "https://via.placeholder.com/200x100/FF6B35/FFFFFF?text=Logo"
                elif 'instructor' in field_name.lower() or 'person' in field_name.lower() or 'customer' in field_name.lower():
                    sample_data[field_name] = "https://via.placeholder.com/300x300/4A90E2/FFFFFF?text=Person"
                elif 'product' in field_name.lower():
                    sample_data[field_name] = "https://via.placeholder.com/600x400/50C878/FFFFFF?text=Product"
                else:
                    sample_data[field_name] = "https://via.placeholder.com/800x600/9370DB/FFFFFF?text=Image"

            elif 'video' in field_name.lower():
                sample_data[field_name] = "https://www.youtube.com/embed/dQw4w9WgXcQ"

            elif 'link' in field_name.lower():
                if 'registration' in field_name.lower():
                    sample_data[field_name] = "https://example.com/register"
                elif 'reservation' in field_name.lower():
                    sample_data[field_name] = "https://example.com/reserve"
                else:
                    sample_data[field_name] = "https://example.com"
            else:
                sample_data[field_name] = "https://via.placeholder.com/400x300"

        # NUMBER FIELDS
        elif field_type == 'number':
            if 'price' in field_name.lower():
                if 'original' in field_name.lower():
                    sample_data[field_name] = random.choice([99, 149, 199, 249])
                elif 'sale' in field_name.lower():
                    sample_data[field_name] = random.choice([49, 79, 99, 129])
                else:
                    sample_data[field_name] = random.choice([49, 79, 99, 149, 199])

            elif 'discount' in field_name.lower() or 'percent' in field_name.lower():
                sample_data[field_name] = random.choice([10, 20, 30, 40, 50])

            elif 'rating' in field_name.lower() or 'stars' in field_name.lower():
                sample_data[field_name] = random.choice([4, 4.5, 5])

            elif 'quantity' in field_name.lower() or 'count' in field_name.lower():
                sample_data[field_name] = random.randint(10, 100)

            elif 'duration' in field_name.lower():
                sample_data[field_name] = random.choice([30, 45, 60, 90])

            else:
                sample_data[field_name] = random.randint(1, 100)

        # DATETIME FIELDS
        elif field_type == 'datetime':
            if 'date' in field_name.lower() and 'time' not in field_name.lower():
                # Date only
                future_date = datetime.now() + timedelta(days=random.randint(1, 30))
                sample_data[field_name] = future_date.strftime("%B %d, %Y")  # "January 15, 2025"
            elif 'time' in field_name.lower() and 'date' not in field_name.lower():
                # Time only
                hour = random.choice([6, 7, 8, 9, 10, 17, 18, 19])
                minute = random.choice([0, 15, 30, 45])
                period = "AM" if hour < 12 else "PM"
                display_hour = hour if hour <= 12 else hour - 12
                sample_data[field_name] = f"{display_hour}:{minute:02d} {period}"
            else:
                # Full datetime
                future_date = datetime.now() + timedelta(days=random.randint(1, 14))
                sample_data[field_name] = future_date.strftime("%B %d, %Y at %I:%M %p")

        # RICH TEXT FIELDS
        elif field_type == 'rich_text':
            if 'benefit' in field_name.lower() or 'feature' in field_name.lower():
                # Bullet list
                benefits = SAMPLE_BENEFITS.get(industry, SAMPLE_BENEFITS['generic'])
                sample_data[field_name] = "<ul>" + "".join([f"<li>{b}</li>" for b in benefits[:3]]) + "</ul>"

            elif 'description' in field_name.lower() or 'body' in field_name.lower() or 'content' in field_name.lower():
                sample_data[field_name] = f"<p>{SAMPLE_DESCRIPTIONS.get(industry, SAMPLE_DESCRIPTIONS['generic'])}</p>"

            elif 'bio' in field_name.lower():
                sample_data[field_name] = "<p>Award-winning professional with 10+ years of experience. Passionate about helping others achieve their goals.</p>"

            elif 'ingredient' in field_name.lower():
                sample_data[field_name] = "<p>Fresh organic vegetables, premium olive oil, herbs, and spices</p>"

            else:
                sample_data[field_name] = f"<p>{SAMPLE_DESCRIPTIONS.get(industry, SAMPLE_DESCRIPTIONS['generic'])}</p>"

        # BOOLEAN FIELDS
        elif field_type == 'boolean':
            sample_data[field_name] = random.choice([True, False])

    return sample_data


def render_template_preview(liquid_template: str, field_schema: List[Dict], industry: str = "generic") -> str:
    """
    Render Liquid template with realistic sample data for preview.

    Args:
        liquid_template: Liquid template HTML string
        field_schema: List of field definitions
        industry: Industry context for sample data

    Returns:
        Rendered HTML string

    Raises:
        Exception: If template rendering fails
    """
    try:
        # Generate sample data
        sample_data = generate_sample_data(field_schema, industry)

        # Render template (pass fields directly, not nested in 'items')
        env = Environment()
        template = env.from_string(liquid_template)
        rendered = template.render(**sample_data)

        logger.info(f"Template preview rendered successfully ({len(rendered)} chars)")
        return rendered

    except Exception as e:
        logger.error(f"Error rendering template preview: {e}")
        raise Exception(f"Preview rendering failed: {str(e)}")
