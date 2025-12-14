# insert_templates.py - B2B Generic Templates
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv(override=True)

connection_string = os.getenv("CONNECTION_STRING_MONGO")

# Parse database name correctly (handle query parameters)
parsed_url = urlparse(connection_string)
db_name = parsed_url.path.lstrip('/')  # Remove leading slash
if '?' in db_name:
    db_name = db_name.split('?')[0]  # Remove query parameters

client = MongoClient(connection_string)
db = client[db_name]
collection = db["content_templates"]

templates = [
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f0"),
        "name": "B2B Email Template - FitZone Fitness",
        "liquid_template": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FitZone Fitness Campaign</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { text-align: center; background-color: #FF6B35; padding: 20px; color: white; }
        .brand-image-container {
            text-align: center;
            margin: 20px auto;
            width: 100%;
            max-width: 800px;
            background-color: #f4f4f4;
            height: 300px;
            position: relative;
        }
        .brand-image-container img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .content { margin: 30px auto; max-width: 800px; padding: 0 20px; }
        .user-info { background-color: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .footer { margin-top: 30px; padding: 20px; background-color: #f4f4f4; text-align: center; }
        .cta-button {
            display: inline-block;
            background-color: #FF6B35;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }
        .company-logo { width: 120px; height: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{HeaderText}}</h1>
    </div>

    <div class="brand-image-container">
        <img src="{{BrandImageURL}}" alt="Brand Image"/>
    </div>

    <div class="content">
        <div class="user-info">
            <p><strong>{{UserTitle}} {{UserName}}</strong></p>
            <p>Phone: {{UserPhone}}</p>
            <p>Email: <a href="mailto:{{UserEmail}}">{{UserEmail}}</a></p>
        </div>

        <h2>{{SubjectLine}}</h2>
        <p>{{BodyText}}</p>

        <div style="text-align: center;">
            <a href="{{Link}}" class="cta-button">{{CallToAction}}</a>
        </div>
    </div>

    <div class="footer">
        <img src="{{CompanyLogoURL}}" alt="Company Logo" class="company-logo"/>
        <p><strong>FitZone Fitness</strong></p>
        <p>Transform Your Business with Our Solutions</p>
        <p><a href="https://fitzone.example.com">www.fitzone.example.com</a></p>
        <p>For more information contact: <a href="mailto:contact@fitzone.example.com">contact@fitzone.example.com</a></p>
    </div>
</body>
</html>
        """,
        "items": [
            {"Type": "Text", "Name": "Header Text", "MaxLength": 100, "Id": "HeaderText", "IsRequired": True},
            {"Type": "Text", "Name": "Brand Image URL", "MaxLength": 200, "Id": "BrandImageURL", "IsRequired": True},
            {"Type": "Text", "Name": "User Title", "MaxLength": 10, "Id": "UserTitle", "IsRequired": False},
            {"Type": "Text", "Name": "User Name", "MaxLength": 100, "Id": "UserName", "IsRequired": True},
            {"Type": "Text", "Name": "User Phone", "MaxLength": 50, "Id": "UserPhone", "IsRequired": False},
            {"Type": "Text", "Name": "User Email", "MaxLength": 100, "Id": "UserEmail", "IsRequired": True},
            {"Type": "Text", "Name": "Subject Line", "MaxLength": 150, "Id": "SubjectLine", "IsRequired": True},
            {"Type": "Text", "Name": "Body Text", "MaxLength": 1000, "Id": "BodyText", "IsRequired": True},
            {"Type": "Text", "Name": "Link", "MaxLength": 200, "Id": "Link", "IsRequired": True},
            {"Type": "Text", "Name": "Call To Action", "MaxLength": 50, "Id": "CallToAction", "IsRequired": True},
            {"Type": "Text", "Name": "Company Logo URL", "MaxLength": 200, "Id": "CompanyLogoURL", "IsRequired": True},
        ],
        "example_query": "Promote our new FitZone Pro membership with 30% discount for businesses. Highlight corporate wellness programs, flexible scheduling, and team building benefits. Use BrandImageURL=https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800, UserTitle=Mr., UserName=John Smith, UserPhone=+1 555-123-4567, UserEmail=john.smith@business.com, CompanyLogoURL=https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=200"
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f1"),
        "name": "B2B Email Template - CloudFlow SaaS",
        "liquid_template": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudFlow SaaS Campaign</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #2C3E50; }
        .header { text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; color: white; }
        .brand-image-container {
            text-align: center;
            margin: 20px auto;
            width: 100%;
            max-width: 800px;
            background-color: #E8EAF6;
            height: 300px;
            position: relative;
            border-radius: 10px;
            overflow: hidden;
        }
        .brand-image-container img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .content { margin: 30px auto; max-width: 800px; padding: 0 20px; }
        .user-info {
            background: linear-gradient(to right, #f8f9fa, #e9ecef);
            padding: 20px;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
        }
        .footer { margin-top: 30px; padding: 30px; background-color: #2C3E50; color: white; text-align: center; }
        .footer a { color: #667eea; }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 35px;
            text-decoration: none;
            border-radius: 25px;
            margin: 20px 0;
            font-weight: bold;
        }
        .company-logo { width: 150px; height: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{HeaderText}}</h1>
    </div>

    <div class="brand-image-container">
        <img src="{{BrandImageURL}}" alt="CloudFlow Platform"/>
    </div>

    <div class="content">
        <div class="user-info">
            <p><strong>{{UserTitle}} {{UserName}}</strong></p>
            <p>Phone: {{UserPhone}}</p>
            <p>Email: <a href="mailto:{{UserEmail}}">{{UserEmail}}</a></p>
        </div>

        <h2>{{SubjectLine}}</h2>
        <p>{{BodyText}}</p>

        <div style="text-align: center;">
            <a href="{{Link}}" class="cta-button">{{CallToAction}}</a>
        </div>
    </div>

    <div class="footer">
        <img src="{{CompanyLogoURL}}" alt="CloudFlow Logo" class="company-logo"/>
        <p><strong>CloudFlow SaaS Solutions</strong></p>
        <p>Streamline Your Workflow, Scale Your Business</p>
        <p><a href="https://cloudflow.example.com">www.cloudflow.example.com</a></p>
        <p>Contact us: <a href="mailto:sales@cloudflow.example.com">sales@cloudflow.example.com</a></p>
    </div>
</body>
</html>
        """,
        "items": [
            {"Type": "Text", "Name": "Header Text", "MaxLength": 100, "Id": "HeaderText", "IsRequired": True},
            {"Type": "Text", "Name": "Brand Image URL", "MaxLength": 200, "Id": "BrandImageURL", "IsRequired": True},
            {"Type": "Text", "Name": "User Title", "MaxLength": 10, "Id": "UserTitle", "IsRequired": False},
            {"Type": "Text", "Name": "User Name", "MaxLength": 100, "Id": "UserName", "IsRequired": True},
            {"Type": "Text", "Name": "User Phone", "MaxLength": 50, "Id": "UserPhone", "IsRequired": False},
            {"Type": "Text", "Name": "User Email", "MaxLength": 100, "Id": "UserEmail", "IsRequired": True},
            {"Type": "Text", "Name": "Subject Line", "MaxLength": 150, "Id": "SubjectLine", "IsRequired": True},
            {"Type": "Text", "Name": "Body Text", "MaxLength": 1000, "Id": "BodyText", "IsRequired": True},
            {"Type": "Text", "Name": "Link", "MaxLength": 200, "Id": "Link", "IsRequired": True},
            {"Type": "Text", "Name": "Call To Action", "MaxLength": 50, "Id": "CallToAction", "IsRequired": True},
            {"Type": "Text", "Name": "Company Logo URL", "MaxLength": 200, "Id": "CompanyLogoURL", "IsRequired": True},
        ],
        "example_query": "Promote our CloudFlow Pro Plan with 50% discount for first 3 months. Highlight automated workflows, real-time collaboration, and enterprise security. Use BrandImageURL=https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800, UserTitle=Ms., UserName=Sarah Johnson, UserPhone=+1 555-987-6543, UserEmail=sarah.j@techcorp.com, CompanyLogoURL=https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=200"
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f2"),
        "name": "B2B Promotional Flyer - ShopStyle E-commerce",
        "liquid_template": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopStyle E-commerce Flyer</title>
    <style>
        body { font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; }
        .flyer-container { max-width: 800px; margin: 0 auto; background: white; }
        .header {
            background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%);
            padding: 40px 20px;
            text-align: center;
            color: #2C3E50;
        }
        .hero-image { width: 100%; height: 400px; object-fit: cover; }
        .content { padding: 40px 20px; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .feature-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #FFE66D;
        }
        .cta-section {
            background: #2C3E50;
            color: white;
            padding: 40px 20px;
            text-align: center;
        }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%);
            color: #2C3E50;
            padding: 18px 40px;
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
            font-size: 18px;
            margin-top: 20px;
        }
        .footer { background: #f4f4f4; padding: 30px 20px; text-align: center; }
        .company-logo { width: 130px; height: auto; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="flyer-container">
        <div class="header">
            <h1 style="font-size: 42px; margin: 0;">{{HeaderText}}</h1>
            <p style="font-size: 20px;">{{SubjectLine}}</p>
        </div>

        <img src="{{BrandImageURL}}" alt="Featured Product" class="hero-image"/>

        <div class="content">
            <h2>{{SubjectLine}}</h2>
            <p style="font-size: 18px; line-height: 1.8;">{{BodyText}}</p>

            <div class="features">
                <div class="feature-box">
                    <h3>🚀 Fast Delivery</h3>
                    <p>Get your orders within 24-48 hours</p>
                </div>
                <div class="feature-box">
                    <h3>💰 Best Prices</h3>
                    <p>Competitive pricing for businesses</p>
                </div>
                <div class="feature-box">
                    <h3>🎯 Bulk Discounts</h3>
                    <p>Save more on larger orders</p>
                </div>
            </div>
        </div>

        <div class="cta-section">
            <h2>Ready to Get Started?</h2>
            <a href="{{Link}}" class="cta-button">{{CallToAction}}</a>
            <p style="margin-top: 20px;">Contact: {{UserEmail}} | {{UserPhone}}</p>
        </div>

        <div class="footer">
            <img src="{{CompanyLogoURL}}" alt="ShopStyle Logo" class="company-logo"/>
            <p><strong>ShopStyle E-commerce Platform</strong></p>
            <p>Your One-Stop B2B Shopping Solution</p>
            <p><a href="https://shopstyle.example.com">www.shopstyle.example.com</a></p>
            <p>Business inquiries: <a href="mailto:b2b@shopstyle.example.com">b2b@shopstyle.example.com</a></p>
        </div>
    </div>
</body>
</html>
        """,
        "items": [
            {"Type": "Text", "Name": "Header Text", "MaxLength": 100, "Id": "HeaderText", "IsRequired": True},
            {"Type": "Text", "Name": "Brand Image URL", "MaxLength": 200, "Id": "BrandImageURL", "IsRequired": True},
            {"Type": "Text", "Name": "Subject Line", "MaxLength": 150, "Id": "SubjectLine", "IsRequired": True},
            {"Type": "Text", "Name": "Body Text", "MaxLength": 1000, "Id": "BodyText", "IsRequired": True},
            {"Type": "Text", "Name": "Link", "MaxLength": 200, "Id": "Link", "IsRequired": True},
            {"Type": "Text", "Name": "Call To Action", "MaxLength": 50, "Id": "CallToAction", "IsRequired": True},
            {"Type": "Text", "Name": "User Email", "MaxLength": 100, "Id": "UserEmail", "IsRequired": True},
            {"Type": "Text", "Name": "User Phone", "MaxLength": 50, "Id": "UserPhone", "IsRequired": False},
            {"Type": "Text", "Name": "Company Logo URL", "MaxLength": 200, "Id": "CompanyLogoURL", "IsRequired": True},
        ],
        "example_query": "Promote our ShopStyle B2B platform with exclusive wholesale prices. Highlight fast delivery, bulk discounts, and 24/7 customer support. Use BrandImageURL=https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800, UserEmail=partner@shopstyle.example.com, UserPhone=+1 555-222-3333, CompanyLogoURL=https://images.unsplash.com/photo-1599305445671-ac291c95aaa9?w=200"
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f3"),
        "name": "General B2B Email Template",
        "liquid_template": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Email</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px; }
        .header { background-color: #0066cc; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px 20px; background: white; }
        .footer { background-color: #f4f4f4; padding: 20px; text-align: center; margin-top: 30px; }
        .cta-button {
            display: inline-block;
            background-color: #0066cc;
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 4px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{HeaderText}}</h1>
    </div>

    <div class="content">
        <p>Dear {{RecipientName}},</p>
        <p>{{BodyText}}</p>
        <div style="text-align: center;">
            <a href="{{Link}}" class="cta-button">{{CallToAction}}</a>
        </div>
    </div>

    <div class="footer">
        <p><strong>{{CompanyName}}</strong></p>
        <p>{{ContactEmail}} | {{ContactPhone}}</p>
    </div>
</body>
</html>
        """,
        "items": [
            {"Type": "Text", "Name": "Header Text", "MaxLength": 100, "Id": "HeaderText", "IsRequired": True},
            {"Type": "Text", "Name": "Recipient Name", "MaxLength": 100, "Id": "RecipientName", "IsRequired": True},
            {"Type": "Text", "Name": "Body Text", "MaxLength": 1000, "Id": "BodyText", "IsRequired": True},
            {"Type": "Text", "Name": "Link", "MaxLength": 200, "Id": "Link", "IsRequired": True},
            {"Type": "Text", "Name": "Call To Action", "MaxLength": 50, "Id": "CallToAction", "IsRequired": True},
            {"Type": "Text", "Name": "Company Name", "MaxLength": 100, "Id": "CompanyName", "IsRequired": True},
            {"Type": "Text", "Name": "Contact Email", "MaxLength": 100, "Id": "ContactEmail", "IsRequired": True},
            {"Type": "Text", "Name": "Contact Phone", "MaxLength": 50, "Id": "ContactPhone", "IsRequired": False},
        ],
        "example_query": "Send a professional email to potential B2B clients introducing our consulting services. Highlight expertise, proven results, and free consultation offer."
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f4"),
        "name": "Simple Campaign",
        "liquid_template": """
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
            <h1 style="color: #333; text-align: center;">{{Title}}</h1>
            <p style="color: #666; line-height: 1.6;">{{Description}}</p>
            <div style="text-align: center; margin: 20px 0;">
                <a href="{{Link}}" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    {{CallToAction}}
                </a>
            </div>
        </div>
        """,
        "items": [
            {"Type": "Text", "Name": "Title", "MaxLength": 200, "Id": "Title", "IsRequired": True},
            {"Type": "Text", "Name": "Description", "MaxLength": 1000, "Id": "Description", "IsRequired": True},
            {"Type": "Text", "Name": "Link", "MaxLength": 200, "Id": "Link", "IsRequired": True},
            {"Type": "Text", "Name": "Call To Action", "MaxLength": 50, "Id": "CallToAction", "IsRequired": True},
        ],
        "example_query": "Create a simple promotional campaign for our new product launch with a clear call-to-action button."
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f5"),
        "name": "Call to Action (with Image)",
        "liquid_template": """
        <div style="max-width: 700px; margin: 0 auto; background: #f9f9f9; padding: 30px; font-family: Arial, sans-serif;">
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="{{ImageURL}}" alt="Campaign Image" style="max-width: 100%; height: auto; border-radius: 8px;"/>
            </div>
            <h2 style="color: #222; text-align: center;">{{HeaderText}}</h2>
            <p style="color: #555; line-height: 1.7; text-align: center;">{{BodyText}}</p>
            <div style="text-align: center; margin-top: 25px;">
                <a href="{{Link}}" style="background-color: #28a745; color: white; padding: 14px 35px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold;">
                    {{CallToAction}}
                </a>
            </div>
        </div>
        """,
        "items": [
            {"Type": "Text", "Name": "Header Text", "MaxLength": 150, "Id": "HeaderText", "IsRequired": True},
            {"Type": "Text", "Name": "Body Text", "MaxLength": 500, "Id": "BodyText", "IsRequired": True},
            {"Type": "Text", "Name": "Image URL", "MaxLength": 200, "Id": "ImageURL", "IsRequired": True},
            {"Type": "Text", "Name": "Link", "MaxLength": 200, "Id": "Link", "IsRequired": True},
            {"Type": "Text", "Name": "Call To Action", "MaxLength": 50, "Id": "CallToAction", "IsRequired": True},
        ],
        "example_query": "Promote our new service with an engaging image and strong call-to-action. Use ImageURL=https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800"
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f6"),
        "name": "Push Notification Preview",
        "liquid_template": """
        <div style="background-color: #fff; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); width: 350px; padding: 16px; display: flex; align-items: center; font-family: Arial, sans-serif;">
            <img src="https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=100" alt="App Icon" style="border-radius: 50%; width: 50px; height: 50px; margin-right: 16px;">
            <div style="flex: 1;">
                <div style="font-weight: bold; color: #333; margin-bottom: 4px;">{{AppName}}</div>
                <div style="color: #666; font-size: 14px;">{{NotificationText}}</div>
            </div>
        </div>
        """,
        "items": [
            {"Type": "Text", "Name": "App Name", "MaxLength": 50, "Id": "AppName", "IsRequired": True},
            {"Type": "Text", "Name": "Notification Text", "MaxLength": 200, "Id": "NotificationText", "IsRequired": True},
        ],
        "example_query": "Create a push notification for our mobile app alerting users about a flash sale."
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f7"),
        "name": "Message with Idioms",
        "liquid_template": """
        <div style="max-width: 600px; margin: 0 auto; padding: 25px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 10px; font-family: Georgia, serif;">
            <h2 style="color: #2c3e50; text-align: center; font-style: italic;">"{{Idiom}}"</h2>
            <p style="color: #34495e; line-height: 1.8; text-align: center; font-size: 16px;">{{Message}}</p>
            <div style="text-align: center; margin-top: 20px;">
                <a href="{{Link}}" style="background-color: #3498db; color: white; padding: 12px 28px; text-decoration: none; border-radius: 20px; display: inline-block;">
                    {{CallToAction}}
                </a>
            </div>
        </div>
        """,
        "items": [
            {"Type": "Text", "Name": "Idiom", "MaxLength": 150, "Id": "Idiom", "IsRequired": True},
            {"Type": "Text", "Name": "Message", "MaxLength": 500, "Id": "Message", "IsRequired": True},
            {"Type": "Text", "Name": "Link", "MaxLength": 200, "Id": "Link", "IsRequired": True},
            {"Type": "Text", "Name": "Call To Action", "MaxLength": 50, "Id": "CallToAction", "IsRequired": True},
        ],
        "example_query": "Create an inspirational message using the idiom 'Rome wasn't built in a day' to encourage business growth."
    },
    {
        "_id": ObjectId("64b8f3f1f1f1f1f1f1f1f1f8"),
        "name": "Header & Body Campaign",
        "liquid_template": """
        <div style="max-width: 650px; margin: 0 auto; font-family: 'Trebuchet MS', sans-serif;">
            <div style="background-color: #16a085; color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 32px;">{{HeaderText}}</h1>
            </div>
            <div style="background: white; padding: 40px 30px; border: 1px solid #e0e0e0;">
                <p style="color: #444; line-height: 1.7; font-size: 16px;">{{BodyText}}</p>
            </div>
            <div style="background-color: #ecf0f1; padding: 20px; text-align: center;">
                <a href="{{Link}}" style="background-color: #16a085; color: white; padding: 14px 32px; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: bold;">
                    {{CallToAction}}
                </a>
            </div>
        </div>
        """,
        "items": [
            {"Type": "Text", "Name": "Header Text", "MaxLength": 100, "Id": "HeaderText", "IsRequired": True},
            {"Type": "Text", "Name": "Body Text", "MaxLength": 1000, "Id": "BodyText", "IsRequired": True},
            {"Type": "Text", "Name": "Link", "MaxLength": 200, "Id": "Link", "IsRequired": True},
            {"Type": "Text", "Name": "Call To Action", "MaxLength": 50, "Id": "CallToAction", "IsRequired": True},
        ],
        "example_query": "Create a professional campaign announcement for our quarterly business review meeting."
    },
]

# Clear existing templates and insert new ones
collection.delete_many({})
collection.insert_many(templates)

print(f"Successfully inserted {len(templates)} B2B templates into {db_name}.content_templates")
print("Template names:")
for template in templates:
    print(f"  - {template['name']}")
