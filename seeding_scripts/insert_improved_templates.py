# insert_improved_templates.py - Specialized B2B Templates
# Better templates based on B2B_TARGET_PERSONAS.md and EXAMPLE_BUSINESSES.md
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from urllib.parse import urlparse

# Load environment variables
load_dotenv(override=True)

connection_string = os.getenv("CONNECTION_STRING_MONGO")
parsed_url = urlparse(connection_string)
db_name = parsed_url.path.lstrip('/')
if '?' in db_name:
    db_name = db_name.split('?')[0]

client = MongoClient(connection_string)
db = client[db_name]
collection = db["content_templates"]

improved_templates = [
    # ===================
    # FITNESS TEMPLATES
    # ===================
    {
        "_id": ObjectId("65b8f3f1f1f1f1f1f1f1f201"),
        "name": "Fitness - New Class Announcement (Instagram/Facebook)",
        "liquid_template": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Arial Black', Arial, sans-serif; margin: 0; background: #FF6B35; }
        .container { max-width: 600px; margin: 0 auto; background: white; }
        .header { background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); color: white; padding: 40px 20px; text-align: center; }
        .header h1 { font-size: 36px; margin: 0; text-transform: uppercase; }
        .image-container { position: relative; width: 100%; height: 400px; overflow: hidden; }
        .image-container img { width: 100%; height: 100%; object-fit: cover; }
        .class-info { background: #2D3142; color: white; padding: 30px; }
        .class-detail { margin: 15px 0; font-size: 18px; }
        .class-detail strong { color: #FF6B35; }
        .benefits { background: #F4F4F4; padding: 30px; }
        .benefits h2 { color: #2D3142; margin-top: 0; }
        .benefit-list { list-style: none; padding: 0; }
        .benefit-list li { padding: 10px 0; padding-left: 30px; position: relative; }
        .benefit-list li:before { content: "🔥"; position: absolute; left: 0; }
        .cta { background: #FF6B35; text-align: center; padding: 40px 20px; }
        .cta-button { display: inline-block; background: white; color: #FF6B35; padding: 18px 50px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 20px; text-transform: uppercase; }
        .cta-button:hover { background: #2D3142; color: white; }
        .footer { background: #2D3142; color: white; text-align: center; padding: 20px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ClassName}}</h1>
            <p style="font-size: 18px; margin: 10px 0 0;">New Class Alert!</p>
        </div>

        <div class="image-container">
            <img src="{{ClassImageURL}}" alt="{{ClassName}} Class"/>
        </div>

        <div class="class-info">
            <div class="class-detail"><strong>INSTRUCTOR:</strong> {{InstructorName}}</div>
            <div class="class-detail"><strong>WHEN:</strong> {{ClassDate}} at {{ClassTime}}</div>
            <div class="class-detail"><strong>DURATION:</strong> {{Duration}} minutes</div>
            <div class="class-detail"><strong>LEVEL:</strong> {{Level}}</div>
        </div>

        <div class="benefits">
            <h2>What You'll Get:</h2>
            <ul class="benefit-list">
                <li>{{Benefit1}}</li>
                <li>{{Benefit2}}</li>
                <li>{{Benefit3}}</li>
            </ul>
        </div>

        <div class="cta">
            <p style="color: white; font-size: 20px; margin: 0 0 20px;">LIMITED SPOTS AVAILABLE</p>
            <a href="{{BookingLink}}" class="cta-button">Book Your Spot</a>
        </div>

        <div class="footer">
            <p><strong>FitZone Fitness</strong></p>
            <p>Your Zone. Your Strength.</p>
            <p>{{ContactEmail}} | {{ContactPhone}}</p>
        </div>
    </div>
</body>
</html>
        """,
        "items": [
            {"Type": "Text", "Name": "Class Name", "MaxLength": 50, "Id": "ClassName", "IsRequired": True},
            {"Type": "Text", "Name": "Class Image URL", "MaxLength": 200, "Id": "ClassImageURL", "IsRequired": True},
            {"Type": "Text", "Name": "Instructor Name", "MaxLength": 50, "Id": "InstructorName", "IsRequired": True},
            {"Type": "Text", "Name": "Class Date", "MaxLength": 50, "Id": "ClassDate", "IsRequired": True},
            {"Type": "Text", "Name": "Class Time", "MaxLength": 20, "Id": "ClassTime", "IsRequired": True},
            {"Type": "Text", "Name": "Duration (minutes)", "MaxLength": 10, "Id": "Duration", "IsRequired": True},
            {"Type": "Text", "Name": "Level (Beginner/Intermediate/Advanced)", "MaxLength": 30, "Id": "Level", "IsRequired": True},
            {"Type": "Text", "Name": "Benefit 1", "MaxLength": 100, "Id": "Benefit1", "IsRequired": True},
            {"Type": "Text", "Name": "Benefit 2", "MaxLength": 100, "Id": "Benefit2", "IsRequired": True},
            {"Type": "Text", "Name": "Benefit 3", "MaxLength": 100, "Id": "Benefit3", "IsRequired": True},
            {"Type": "Text", "Name": "Booking Link", "MaxLength": 200, "Id": "BookingLink", "IsRequired": True},
            {"Type": "Text", "Name": "Contact Email", "MaxLength": 100, "Id": "ContactEmail", "IsRequired": True},
            {"Type": "Text", "Name": "Contact Phone", "MaxLength": 50, "Id": "ContactPhone", "IsRequired": False},
        ],
        "example_query": "Announce Sarah's HIIT Blast class on Saturday at 10 AM. It's a 45-minute high-intensity class for all levels. Benefits: burn 500 calories, boost metabolism, build endurance. Use ClassImageURL=https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800, BookingLink=https://fitzone.com/book, ContactEmail=info@fitzone.com, ContactPhone=+1-555-FIT-ZONE"
    },

    # ===================
    # SaaS TEMPLATES
    # ===================
    {
        "_id": ObjectId("65b8f3f1f1f1f1f1f1f1f202"),
        "name": "SaaS - Feature Release Announcement (LinkedIn/Twitter)",
        "liquid_template": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: #f5f7fa; }
        .container { max-width: 700px; margin: 0 auto; background: white; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 50px 30px; text-align: center; }
        .header .badge { background: rgba(255,255,255,0.2); display: inline-block; padding: 8px 16px; border-radius: 20px; font-size: 14px; margin-bottom: 15px; }
        .header h1 { font-size: 42px; margin: 0; font-weight: 700; }
        .feature-visual { text-align: center; padding: 40px 20px; background: #f8f9fa; }
        .feature-visual img { max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .problem-solution { padding: 40px 30px; }
        .section { margin-bottom: 40px; }
        .section-title { color: #667eea; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
        .section-content { font-size: 18px; line-height: 1.8; color: #2C3E50; }
        .benefits-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; background: #f8f9fa; }
        .benefit-card { background: white; padding: 25px; border-radius: 8px; border-left: 4px solid #667eea; }
        .benefit-card h3 { margin: 0 0 10px; color: #2C3E50; font-size: 16px; }
        .benefit-card p { margin: 0; color: #666; font-size: 14px; }
        .cta-section { background: #2C3E50; color: white; padding: 50px 30px; text-align: center; }
        .cta-button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px 40px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 18px; }
        .footer { background: white; padding: 30px; text-align: center; border-top: 1px solid #e0e0e0; }
        .footer-logo { color: #667eea; font-size: 24px; font-weight: bold; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="badge">🚀 NEW FEATURE</div>
            <h1>{{FeatureName}}</h1>
            <p style="font-size: 20px; margin: 15px 0 0; opacity: 0.9;">{{TagLine}}</p>
        </div>

        <div class="feature-visual">
            <img src="{{ScreenshotURL}}" alt="{{FeatureName}} Screenshot"/>
        </div>

        <div class="problem-solution">
            <div class="section">
                <div class="section-title">THE PROBLEM</div>
                <div class="section-content">{{ProblemDescription}}</div>
            </div>

            <div class="section">
                <div class="section-title">OUR SOLUTION</div>
                <div class="section-content">{{SolutionDescription}}</div>
            </div>
        </div>

        <div class="benefits-grid">
            <div class="benefit-card">
                <h3>⚡ {{Benefit1Title}}</h3>
                <p>{{Benefit1Description}}</p>
            </div>
            <div class="benefit-card">
                <h3>💰 {{Benefit2Title}}</h3>
                <p>{{Benefit2Description}}</p>
            </div>
            <div class="benefit-card">
                <h3>🎯 {{Benefit3Title}}</h3>
                <p>{{Benefit3Description}}</p>
            </div>
        </div>

        <div class="cta-section">
            <h2 style="margin: 0 0 10px;">Ready to Experience the Difference?</h2>
            <p style="margin: 0 0 30px; font-size: 18px; opacity: 0.9;">Available now for all {{PlanTier}} users</p>
            <a href="{{CTALink}}" class="cta-button">{{CTAText}}</a>
        </div>

        <div class="footer">
            <div class="footer-logo">CloudFlow</div>
            <p style="color: #666; margin: 5px 0;">Work Flows Better in the Cloud</p>
            <p style="color: #999; font-size: 14px;">{{SupportEmail}} | Documentation: {{DocsLink}}</p>
        </div>
    </div>
</body>
</html>
        """,
        "items": [
            {"Type": "Text", "Name": "Feature Name", "MaxLength": 100, "Id": "FeatureName", "IsRequired": True},
            {"Type": "Text", "Name": "Tag Line", "MaxLength": 150, "Id": "TagLine", "IsRequired": True},
            {"Type": "Text", "Name": "Screenshot URL", "MaxLength": 200, "Id": "ScreenshotURL", "IsRequired": True},
            {"Type": "Text", "Name": "Problem Description", "MaxLength": 500, "Id": "ProblemDescription", "IsRequired": True},
            {"Type": "Text", "Name": "Solution Description", "MaxLength": 500, "Id": "SolutionDescription", "IsRequired": True},
            {"Type": "Text", "Name": "Benefit 1 Title", "MaxLength": 50, "Id": "Benefit1Title", "IsRequired": True},
            {"Type": "Text", "Name": "Benefit 1 Description", "MaxLength": 150, "Id": "Benefit1Description", "IsRequired": True},
            {"Type": "Text", "Name": "Benefit 2 Title", "MaxLength": 50, "Id": "Benefit2Title", "IsRequired": True},
            {"Type": "Text", "Name": "Benefit 2 Description", "MaxLength": 150, "Id": "Benefit2Description", "IsRequired": True},
            {"Type": "Text", "Name": "Benefit 3 Title", "MaxLength": 50, "Id": "Benefit3Title", "IsRequired": True},
            {"Type": "Text", "Name": "Benefit 3 Description", "MaxLength": 150, "Id": "Benefit3Description", "IsRequired": True},
            {"Type": "Text", "Name": "Plan Tier (Pro/Enterprise/All)", "MaxLength": 30, "Id": "PlanTier", "IsRequired": True},
            {"Type": "Text", "Name": "CTA Link", "MaxLength": 200, "Id": "CTALink", "IsRequired": True},
            {"Type": "Text", "Name": "CTA Text", "MaxLength": 50, "Id": "CTAText", "IsRequired": True},
            {"Type": "Text", "Name": "Support Email", "MaxLength": 100, "Id": "SupportEmail", "IsRequired": True},
            {"Type": "Text", "Name": "Docs Link", "MaxLength": 200, "Id": "DocsLink", "IsRequired": True},
        ],
        "example_query": "Announce our new Real-Time Collaboration API that makes database queries 10x faster. Problem: teams waste hours on slow data syncing. Solution: real-time updates with sub-100ms latency. Benefits: 10x faster queries, save $5k/month on infrastructure, zero downtime deployment. Available for Pro users. Use ScreenshotURL=https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800, CTALink=https://cloudflow.com/api-docs, CTAText=Try It Now, SupportEmail=support@cloudflow.com, DocsLink=https://docs.cloudflow.com"
    },

    # ===================
    # E-COMMERCE TEMPLATES
    # ===================
    {
        "_id": ObjectId("65b8f3f1f1f1f1f1f1f1f203"),
        "name": "E-commerce - Flash Sale Announcement (Instagram/Facebook)",
        "liquid_template": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; background: #FFE66D; }
        .container { max-width: 650px; margin: 0 auto; background: white; }
        .header { background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%); padding: 50px 20px; text-align: center; }
        .countdown { background: #2C3E50; color: white; padding: 15px; font-size: 24px; font-weight: bold; text-align: center; }
        .countdown .timer { color: #FFE66D; font-size: 36px; }
        .product-hero { position: relative; }
        .product-hero img { width: 100%; height: auto; display: block; }
        .discount-badge { position: absolute; top: 20px; right: 20px; background: #FF6B6B; color: white; font-size: 48px; font-weight: bold; padding: 30px; border-radius: 50%; box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
        .sale-details { padding: 40px 30px; text-align: center; }
        .sale-details h2 { font-size: 36px; color: #2C3E50; margin: 0 0 20px; }
        .price-comparison { margin: 30px 0; }
        .old-price { text-decoration: line-through; color: #999; font-size: 24px; }
        .new-price { color: #FF6B6B; font-size: 48px; font-weight: bold; margin-left: 20px; }
        .features-list { list-style: none; padding: 0; text-align: left; max-width: 400px; margin: 30px auto; }
        .features-list li { padding: 12px 0; padding-left: 40px; position: relative; font-size: 18px; }
        .features-list li:before { content: "✓"; position: absolute; left: 0; color: #FF6B6B; font-size: 24px; font-weight: bold; }
        .urgency { background: #FFF5E6; border-left: 4px solid #FF6B6B; padding: 20px; margin: 30px 0; }
        .urgency-title { color: #FF6B6B; font-weight: bold; margin-bottom: 10px; }
        .cta-section { background: #2C3E50; padding: 50px 20px; text-align: center; }
        .cta-button { display: inline-block; background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%); color: #2C3E50; padding: 20px 60px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 24px; text-transform: uppercase; }
        .footer { padding: 30px; text-align: center; background: #f4f4f4; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="font-size: 56px; margin: 0; color: #2C3E50;">⚡ FLASH SALE ⚡</h1>
            <p style="font-size: 24px; margin: 15px 0 0; color: #2C3E50;">{{SaleTitle}}</p>
        </div>

        <div class="countdown">
            <div>ENDS IN: <span class="timer">{{TimeRemaining}}</span></div>
        </div>

        <div class="product-hero">
            <img src="{{ProductImageURL}}" alt="{{ProductName}}"/>
            <div class="discount-badge">{{DiscountPercent}}%<br/>OFF</div>
        </div>

        <div class="sale-details">
            <h2>{{ProductName}}</h2>
            <p style="font-size: 18px; color: #666; line-height: 1.6;">{{ProductDescription}}</p>

            <div class="price-comparison">
                <span class="old-price">${{OriginalPrice}}</span>
                <span class="new-price">${{SalePrice}}</span>
            </div>

            <p style="color: #FF6B6B; font-size: 20px; font-weight: bold;">YOU SAVE ${{SavingsAmount}}!</p>

            <ul class="features-list">
                <li>{{Feature1}}</li>
                <li>{{Feature2}}</li>
                <li>{{Feature3}}</li>
            </ul>

            <div class="urgency">
                <div class="urgency-title">⏰ LIMITED TIME ONLY!</div>
                <div>{{UrgencyMessage}}</div>
            </div>
        </div>

        <div class="cta-section">
            <p style="color: white; font-size: 20px; margin: 0 0 30px;">Don't Miss Out!</p>
            <a href="{{ShopLink}}" class="cta-button">{{CTAText}}</a>
            <p style="color: #FFE66D; margin: 30px 0 0; font-size: 16px;">Free Shipping on Orders $50+</p>
        </div>

        <div class="footer">
            <p><strong>ShopStyle E-commerce</strong></p>
            <p>Your Style, Delivered</p>
            <p>{{ContactEmail}} | {{ContactPhone}}</p>
            <p style="font-size: 12px; color: #999; margin-top: 20px;">*Sale ends {{EndDate}}. While supplies last. Terms apply.</p>
        </div>
    </div>
</body>
</html>
        """,
        "items": [
            {"Type": "Text", "Name": "Sale Title", "MaxLength": 100, "Id": "SaleTitle", "IsRequired": True},
            {"Type": "Text", "Name": "Time Remaining (e.g., '6 HOURS')", "MaxLength": 30, "Id": "TimeRemaining", "IsRequired": True},
            {"Type": "Text", "Name": "Product Name", "MaxLength": 100, "Id": "ProductName", "IsRequired": True},
            {"Type": "Text", "Name": "Product Description", "MaxLength": 300, "Id": "ProductDescription", "IsRequired": True},
            {"Type": "Text", "Name": "Product Image URL", "MaxLength": 200, "Id": "ProductImageURL", "IsRequired": True},
            {"Type": "Text", "Name": "Discount Percent", "MaxLength": 3, "Id": "DiscountPercent", "IsRequired": True},
            {"Type": "Text", "Name": "Original Price", "MaxLength": 10, "Id": "OriginalPrice", "IsRequired": True},
            {"Type": "Text", "Name": "Sale Price", "MaxLength": 10, "Id": "SalePrice", "IsRequired": True},
            {"Type": "Text", "Name": "Savings Amount", "MaxLength": 10, "Id": "SavingsAmount", "IsRequired": True},
            {"Type": "Text", "Name": "Feature 1", "MaxLength": 100, "Id": "Feature1", "IsRequired": True},
            {"Type": "Text", "Name": "Feature 2", "MaxLength": 100, "Id": "Feature2", "IsRequired": True},
            {"Type": "Text", "Name": "Feature 3", "MaxLength": 100, "Id": "Feature3", "IsRequired": True},
            {"Type": "Text", "Name": "Urgency Message", "MaxLength": 200, "Id": "UrgencyMessage", "IsRequired": True},
            {"Type": "Text", "Name": "Shop Link", "MaxLength": 200, "Id": "ShopLink", "IsRequired": True},
            {"Type": "Text", "Name": "CTA Text", "MaxLength": 50, "Id": "CTAText", "IsRequired": True},
            {"Type": "Text", "Name": "End Date", "MaxLength": 50, "Id": "EndDate", "IsRequired": True},
            {"Type": "Text", "Name": "Contact Email", "MaxLength": 100, "Id": "ContactEmail", "IsRequired": True},
            {"Type": "Text", "Name": "Contact Phone", "MaxLength": 50, "Id": "ContactPhone", "IsRequired": False},
        ],
        "example_query": "Create a 24-hour flash sale for our Winter Dress Collection. Original price $129, now $79 (50% off, save $50). Features: premium cotton blend, machine washable, available in 5 colors. Only 50 items left in stock. Use ProductImageURL=https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800, ShopLink=https://shopstyle.com/flash-sale, CTAText=Shop Now, EndDate=Tonight at Midnight, TimeRemaining=6 HOURS, ContactEmail=support@shopstyle.com, ContactPhone=1-800-STYLE"
    },
]

# Add improved templates (don't delete existing ones)
print(f"Inserting {len(improved_templates)} improved specialized B2B templates...")

for template in improved_templates:
    # Check if template with this ID already exists
    existing = collection.find_one({"_id": template["_id"]})
    if existing:
        collection.replace_one({"_id": template["_id"]}, template)
        print(f"  ✓ Updated: {template['name']}")
    else:
        collection.insert_one(template)
        print(f"  ✓ Inserted: {template['name']}")

print(f"\n✅ Successfully added/updated {len(improved_templates)} improved templates!")
print("\nImproved template names:")
for template in improved_templates:
    print(f"  - {template['name']}")
