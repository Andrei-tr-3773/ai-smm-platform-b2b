#!/usr/bin/env python3
"""
Test script for template_utils preview generation

Verifies that realistic sample data is generated for all field types.
"""
from utils.template_utils import generate_sample_data, render_template_preview

# Test field schema (fitness industry)
fitness_schema = [
    {"name": "class_name", "type": "text", "label": "Class Name"},
    {"name": "instructor_name", "type": "text", "label": "Instructor Name"},
    {"name": "instructor_photo", "type": "url", "label": "Instructor Photo"},
    {"name": "date", "type": "datetime", "label": "Class Date"},
    {"name": "time", "type": "datetime", "label": "Class Time"},
    {"name": "price", "type": "number", "label": "Price"},
    {"name": "benefits", "type": "rich_text", "label": "Benefits"},
    {"name": "cta_button", "type": "text", "label": "CTA Button"}
]

# Test Liquid template
fitness_template = """
<div class="campaign-card">
    <h1>{{ items.class_name }}</h1>
    <img src="{{ items.instructor_photo }}" alt="{{ items.instructor_name }}">
    <p class="instructor">Instructor: {{ items.instructor_name }}</p>
    <p class="schedule">{{ items.date }} at {{ items.time }}</p>
    <p class="price">${{ items.price }}</p>
    <div class="benefits">{{ items.benefits }}</div>
    <button>{{ items.cta_button }}</button>
</div>
"""

print("Testing Template Utils - Enhanced Preview\n")
print("=" * 80)

# Test 1: Generate sample data for fitness
print("\nTest 1: Generate Sample Data (Fitness)")
print("-" * 80)
sample_data = generate_sample_data(fitness_schema, industry="fitness")

for field in fitness_schema:
    field_name = field['name']
    value = sample_data.get(field_name, 'N/A')
    print(f"{field['label']:20} ({field['type']:10}): {str(value)[:60]}")

# Test 2: Render template with sample data
print("\n\nTest 2: Render Template with Sample Data")
print("-" * 80)
try:
    rendered = render_template_preview(fitness_template, fitness_schema, industry="fitness")
    print(f"✅ Template rendered successfully ({len(rendered)} chars)")
    print("\nRendered HTML (first 500 chars):")
    print(rendered[:500])
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Multiple industries
print("\n\nTest 3: Industry-Specific Sample Data")
print("-" * 80)

industries = ["fitness", "saas", "ecommerce", "education", "food", "generic"]

for industry in industries:
    sample = generate_sample_data(fitness_schema, industry=industry)
    class_name = sample.get('class_name', 'N/A')
    benefits = sample.get('benefits', 'N/A')[:60]
    print(f"\n{industry.upper():12} - Class: {class_name}")
    print(f"             Benefits: {benefits}...")

print("\n" + "=" * 80)
print("✅ All tests completed!\n")
