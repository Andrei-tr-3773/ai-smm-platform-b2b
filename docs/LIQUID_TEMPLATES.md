# Liquid Templates Documentation

## Overview

This platform uses [Liquid templating language](https://shopify.github.io/liquid/) (by Shopify) to generate dynamic HTML content for marketing campaigns. Liquid allows us to create flexible, reusable templates that can be populated with AI-generated content.

## Why Liquid?

- ✅ **Industry Standard**: Used by Shopify, Jekyll, and many CMS platforms
- ✅ **Simple Syntax**: Easy to learn and maintain
- ✅ **Safe**: Sandboxed execution, no arbitrary code execution
- ✅ **Flexible**: Supports conditionals, loops, filters
- ✅ **Python Support**: `python-liquid` package provides full Liquid support

## Liquid Syntax Basics

### Variables
```liquid
{{ HeaderText }}
{{ UserName }}
{{ BodyText }}
```

### Conditionals
```liquid
{% if discount %}
  <span class="discount">{{ discount }}% OFF</span>
{% endif %}

{% unless user_phone %}
  <p>Phone not provided</p>
{% endunless %}
```

### Loops
```liquid
{% for item in items %}
  <li>{{ item.name }}: {{ item.price }}</li>
{% endfor %}
```

### Filters
```liquid
{{ product_name | upcase }}
{{ price | times: 1.1 | round: 2 }}
{{ date | date: "%Y-%m-%d" }}
```

---

## Current B2B Templates

### 1. B2B Email Template - FitZone Fitness

**Use Case**: Fitness studios, gyms, wellness centers

**Fields Schema**:
```json
{
  "HeaderText": { "type": "Text", "maxLength": 100, "required": true },
  "BrandImageURL": { "type": "Text", "maxLength": 200, "required": true },
  "UserTitle": { "type": "Text", "maxLength": 10, "required": false },
  "UserName": { "type": "Text", "maxLength": 100, "required": true },
  "UserPhone": { "type": "Text", "maxLength": 50, "required": false },
  "UserEmail": { "type": "Text", "maxLength": 100, "required": true },
  "SubjectLine": { "type": "Text", "maxLength": 150, "required": true },
  "BodyText": { "type": "Text", "maxLength": 1000, "required": true },
  "Link": { "type": "Text", "maxLength": 200, "required": true },
  "CallToAction": { "type": "Text", "maxLength": 50, "required": true },
  "CompanyLogoURL": { "type": "Text", "maxLength": 200, "required": true }
}
```

**Example Query**:
```
Promote our new FitZone Pro membership with 30% discount for businesses.
Highlight corporate wellness programs, flexible scheduling, and team building benefits.
```

**Example JSON Output**:
```json
{
  "HeaderText": "FitZone Pro - Corporate Wellness",
  "BrandImageURL": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800",
  "UserTitle": "Mr.",
  "UserName": "John Smith",
  "UserPhone": "+1 555-123-4567",
  "UserEmail": "john.smith@business.com",
  "SubjectLine": "30% Off FitZone Pro Membership",
  "BodyText": "Transform your team's wellness with FitZone Pro...",
  "Link": "https://fitzone.example.com/corporate",
  "CallToAction": "Get Started Today",
  "CompanyLogoURL": "https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=200"
}
```

**Liquid Template**: See `seeding_scripts/insert_tempaltes.py` - Template ID: 64b8f3f1f1f1f1f1f1f1f1f0

---

### 2. B2B Email Template - CloudFlow SaaS

**Use Case**: SaaS companies, software products, tech platforms

**Fields Schema**:
```json
{
  "HeaderText": { "type": "Text", "maxLength": 100, "required": true },
  "BrandImageURL": { "type": "Text", "maxLength": 200, "required": true },
  "UserTitle": { "type": "Text", "maxLength": 10, "required": false },
  "UserName": { "type": "Text", "maxLength": 100, "required": true },
  "UserPhone": { "type": "Text", "maxLength": 50, "required": false },
  "UserEmail": { "type": "Text", "maxLength": 100, "required": true },
  "SubjectLine": { "type": "Text", "maxLength": 150, "required": true },
  "BodyText": { "type": "Text", "maxLength": 1000, "required": true },
  "Link": { "type": "Text", "maxLength": 200, "required": true },
  "CallToAction": { "type": "Text", "maxLength": 50, "required": true },
  "CompanyLogoURL": { "type": "Text", "maxLength": 200, "required": true }
}
```

**Design Features**:
- Modern gradient header (#667eea to #764ba2)
- Clean, professional layout
- Rounded brand image container
- Tech-focused color scheme

**Example Query**:
```
Promote our CloudFlow Pro Plan with 50% discount for first 3 months.
Highlight automated workflows, real-time collaboration, and enterprise security.
```

**Liquid Template**: See `seeding_scripts/insert_tempaltes.py` - Template ID: 64b8f3f1f1f1f1f1f1f1f1f1

---

### 3. B2B Promotional Flyer - ShopStyle E-commerce

**Use Case**: E-commerce platforms, online stores, retail businesses

**Fields Schema**:
```json
{
  "HeaderText": { "type": "Text", "maxLength": 100, "required": true },
  "BrandImageURL": { "type": "Text", "maxLength": 200, "required": true },
  "SubjectLine": { "type": "Text", "maxLength": 150, "required": true },
  "BodyText": { "type": "Text", "maxLength": 1000, "required": true },
  "Link": { "type": "Text", "maxLength": 200, "required": true },
  "CallToAction": { "type": "Text", "maxLength": 50, "required": true },
  "UserEmail": { "type": "Text", "maxLength": 100, "required": true },
  "UserPhone": { "type": "Text", "maxLength": 50, "required": false },
  "CompanyLogoURL": { "type": "Text", "maxLength": 200, "required": true }
}
```

**Design Features**:
- Vibrant gradient header (#FF6B6B to #FFE66D)
- Hero image section (400px height)
- Feature grid (3 columns)
- Dark CTA section for contrast

**Example Query**:
```
Promote our ShopStyle B2B platform with exclusive wholesale prices.
Highlight fast delivery, bulk discounts, and 24/7 customer support.
```

**Liquid Template**: See `seeding_scripts/insert_tempaltes.py` - Template ID: 64b8f3f1f1f1f1f1f1f1f1f2

---

### 4. General B2B Email Template

**Use Case**: Generic business communications, any B2B vertical

**Fields Schema**:
```json
{
  "HeaderText": { "type": "Text", "maxLength": 100, "required": true },
  "RecipientName": { "type": "Text", "maxLength": 100, "required": true },
  "BodyText": { "type": "Text", "maxLength": 1000, "required": true },
  "Link": { "type": "Text", "maxLength": 200, "required": true },
  "CallToAction": { "type": "Text", "maxLength": 50, "required": true },
  "CompanyName": { "type": "Text", "maxLength": 100, "required": true },
  "ContactEmail": { "type": "Text", "maxLength": 100, "required": true },
  "ContactPhone": { "type": "Text", "maxLength": 50, "required": false }
}
```

**Design Features**:
- Simple, professional layout
- Classic blue color scheme (#0066cc)
- Minimal distractions
- Formal business tone

**Example Query**:
```
Send a professional email to potential B2B clients introducing our consulting services.
Highlight expertise, proven results, and free consultation offer.
```

**Liquid Template**: See `seeding_scripts/insert_tempaltes.py` - Template ID: 64b8f3f1f1f1f1f1f1f1f1f3

---

### 5. Simple Campaign

**Use Case**: Quick announcements, basic promotions

**Fields Schema**:
```json
{
  "Title": { "type": "Text", "maxLength": 200, "required": true },
  "Description": { "type": "Text", "maxLength": 1000, "required": true },
  "Link": { "type": "Text", "maxLength": 200, "required": true },
  "CallToAction": { "type": "Text", "maxLength": 50, "required": true }
}
```

**Design Features**:
- Minimal fields (4 only)
- Clean, centered layout
- Bootstrap-style button (#007bff)
- Mobile-friendly

**Example Query**:
```
Create a simple promotional campaign for our new product launch with a clear call-to-action button.
```

**Liquid Template**: See `seeding_scripts/insert_tempaltes.py` - Template ID: 64b8f3f1f1f1f1f1f1f1f1f4

---

### 6. Call to Action (with Image)

**Use Case**: Image-driven campaigns, visual promotions

**Fields Schema**:
```json
{
  "HeaderText": { "type": "Text", "maxLength": 150, "required": true },
  "BodyText": { "type": "Text", "maxLength": 500, "required": true },
  "ImageURL": { "type": "Text", "maxLength": 200, "required": true },
  "Link": { "type": "Text", "maxLength": 200, "required": true },
  "CallToAction": { "type": "Text", "maxLength": 50, "required": true }
}
```

**Design Features**:
- Large hero image (rounded corners)
- Centered content
- Green CTA button (#28a745)
- Light gray background (#f9f9f9)

**Example Query**:
```
Promote our new service with an engaging image and strong call-to-action.
```

**Liquid Template**: See `seeding_scripts/insert_tempaltes.py` - Template ID: 64b8f3f1f1f1f1f1f1f1f1f5

---

### 7. Push Notification Preview

**Use Case**: Mobile app notifications, alerts

**Fields Schema**:
```json
{
  "AppName": { "type": "Text", "maxLength": 50, "required": true },
  "NotificationText": { "type": "Text", "maxLength": 200, "required": true }
}
```

**Design Features**:
- Mobile notification mockup (350px width)
- Circular app icon (50px)
- Compact layout
- Box shadow for depth

**Example Query**:
```
Create a push notification for our mobile app alerting users about a flash sale.
```

**Liquid Template**: See `seeding_scripts/insert_tempaltes.py` - Template ID: 64b8f3f1f1f1f1f1f1f1f1f6

---

### 8. Message with Idioms

**Use Case**: Inspirational content, motivational campaigns

**Fields Schema**:
```json
{
  "Idiom": { "type": "Text", "maxLength": 150, "required": true },
  "Message": { "type": "Text", "maxLength": 500, "required": true },
  "Link": { "type": "Text", "maxLength": 200, "required": true },
  "CallToAction": { "type": "Text", "maxLength": 50, "required": true }
}
```

**Design Features**:
- Gradient background (#f5f7fa to #c3cfe2)
- Italicized idiom (Georgia serif font)
- Elegant, literary style
- Rounded corners

**Example Query**:
```
Create an inspirational message using the idiom 'Rome wasn't built in a day' to encourage business growth.
```

**Liquid Template**: See `seeding_scripts/insert_tempaltes.py` - Template ID: 64b8f3f1f1f1f1f1f1f1f1f7

---

### 9. Header & Body Campaign

**Use Case**: General announcements, structured content

**Fields Schema**:
```json
{
  "HeaderText": { "type": "Text", "maxLength": 100, "required": true },
  "BodyText": { "type": "Text", "maxLength": 1000, "required": true },
  "Link": { "type": "Text", "maxLength": 200, "required": true },
  "CallToAction": { "type": "Text", "maxLength": 50, "required": true }
}
```

**Design Features**:
- Teal header (#16a085)
- Three-section layout (header, body, CTA)
- Professional borders
- Trebuchet MS font

**Example Query**:
```
Create a professional campaign announcement for our quarterly business review meeting.
```

**Liquid Template**: See `seeding_scripts/insert_tempaltes.py` - Template ID: 64b8f3f1f1f1f1f1f1f1f1f8

---

## Platform-Specific Considerations

### Instagram
- **Character Limit**: 2,200 characters (caption)
- **Image Dimensions**: 1080x1080px (square), 1080x1350px (portrait)
- **Best Practice**: Extract plain text from HTML, remove formatting
- **Hashtags**: Include relevant hashtags in BodyText

### Facebook
- **Character Limit**: No hard limit, but 63,206 recommended
- **Image Dimensions**: 1200x630px (link preview)
- **Best Practice**: First 3 lines visible before "See More"
- **Links**: Facebook auto-generates preview cards

### Telegram
- **Character Limit**: 4,096 characters per message
- **Formatting**: Supports HTML formatting
- **Image Support**: Can embed images via URL
- **Best Practice**: Use HTML version directly

### LinkedIn
- **Character Limit**: 3,000 characters
- **Image Dimensions**: 1200x627px
- **Best Practice**: Professional tone, B2B focus
- **Links**: Include UTM parameters for tracking

---

## Template Best Practices

### 1. Responsive Design
```html
<style>
  @media (max-width: 600px) {
    .content { padding: 10px !important; }
    .header h1 { font-size: 24px !important; }
  }
</style>
```

### 2. Fallback Images
```liquid
{% if BrandImageURL %}
  <img src="{{ BrandImageURL }}" alt="Brand Image"/>
{% else %}
  <div class="placeholder">No image available</div>
{% endif %}
```

### 3. Safe Email Client Rendering
- Use inline CSS (not `<style>` tags)
- Use tables for layout (older email clients)
- Avoid JavaScript
- Test in Litmus or Email on Acid

### 4. Accessibility
```html
<img src="..." alt="Descriptive text"/>
<a href="..." aria-label="Read more about our offer">Read More</a>
```

### 5. Variable Naming
- Use **PascalCase** for consistency: `HeaderText`, `BodyText`
- Descriptive names: `UserEmail` not `Email1`
- Avoid abbreviations: `CallToAction` not `CTA`

---

## Creating Custom Templates

### Step 1: Define Fields
```json
{
  "items": [
    {
      "Type": "Text",
      "Name": "Product Name",
      "MaxLength": 100,
      "Id": "ProductName",
      "IsRequired": true
    },
    {
      "Type": "Text",
      "Name": "Price",
      "MaxLength": 20,
      "Id": "Price",
      "IsRequired": true
    }
  ]
}
```

### Step 2: Create Liquid Template
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; }
    .product { padding: 20px; }
  </style>
</head>
<body>
  <div class="product">
    <h1>{{ ProductName }}</h1>
    <p class="price">${{ Price }}</p>
    {% if Discount %}
      <span class="discount">{{ Discount }}% OFF</span>
    {% endif %}
  </div>
</body>
</html>
```

### Step 3: Add Example Query
```python
"example_query": "Promote our new iPhone 15 Pro at $999 with 20% discount"
```

### Step 4: Insert to MongoDB
```python
from pymongo import MongoClient
from bson.objectid import ObjectId

template = {
    "_id": ObjectId(),
    "name": "Product Launch Template",
    "liquid_template": "...",  # Your HTML
    "items": [...],  # Your fields
    "example_query": "..."
}

db.content_templates.insert_one(template)
```

---

## Testing Templates

### Local Testing
```python
from liquid import Template

template_str = "{{ HeaderText }} - {{ BodyText }}"
template = Template(template_str)

data = {
    "HeaderText": "Welcome",
    "BodyText": "This is a test"
}

output = template.render(**data)
print(output)  # "Welcome - This is a test"
```

### Testing in Streamlit
1. Go to Home tab
2. Select your custom template
3. Enter test query
4. Generate content
5. Review rendered HTML

---

## Common Liquid Patterns

### Conditional Content
```liquid
{% if UserPhone %}
  <p>Phone: {{ UserPhone }}</p>
{% endif %}

{% if Discount > 20 %}
  <span class="big-discount">HUGE SAVINGS!</span>
{% elsif Discount > 10 %}
  <span class="discount">Save {{ Discount }}%</span>
{% endif %}
```

### Loops for Lists
```liquid
<ul>
  {% for feature in Features %}
    <li>{{ feature }}</li>
  {% endfor %}
</ul>
```

### Filters for Formatting
```liquid
{{ HeaderText | upcase }}
{{ Price | times: 1.1 | round: 2 }}
{{ Date | date: "%B %d, %Y" }}
```

### Default Values
```liquid
{{ UserTitle | default: "Mr./Ms." }}
{{ CompanyName | default: "Your Company" }}
```

---

## References

- **Liquid Docs**: https://shopify.github.io/liquid/
- **python-liquid**: https://github.com/jg-rp/liquid
- **HTML Email Best Practices**: https://www.campaignmonitor.com/css/
- **Email Client Support**: https://www.caniemail.com/
