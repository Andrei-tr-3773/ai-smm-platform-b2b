#!/usr/bin/env python3
"""
Test script for AI Template Generator Agent

Tests the agent with diverse descriptions across different industries.
"""
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents.template_generator_agent import TemplateGeneratorAgent

# Load environment variables
load_dotenv()

# Initialize OpenAI model
model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")
)

# Initialize agent
agent = TemplateGeneratorAgent(model=model)

# Test cases covering different industries and content types
test_cases = [
    {
        "name": "Fitness - Gym Class Announcement",
        "description": "I need template for gym class announcement with instructor photo, class name, date/time, and benefits. Include a registration button.",
        "expected_industry": "fitness",
        "expected_content_type": "announcement"
    },
    {
        "name": "SaaS - Product Update",
        "description": "Create a template for announcing new software features. Should have feature name, description, benefits, screenshot, and a 'Try Now' button.",
        "expected_industry": "saas",
        "expected_content_type": "update"
    },
    {
        "name": "E-commerce - Sale Announcement",
        "description": "Template for announcing a flash sale on dresses. Include product image, original price, sale price, discount percentage, and 'Shop Now' button.",
        "expected_industry": "ecommerce",
        "expected_content_type": "sale"
    },
    {
        "name": "Education - Course Promotion",
        "description": "Template for promoting online courses with course title, instructor bio, video thumbnail, price, and enrollment button.",
        "expected_industry": "education",
        "expected_content_type": "promotion"
    },
    {
        "name": "Food - Restaurant Special",
        "description": "Template for restaurant daily special with dish name, photo, ingredients, chef name, and reservation link.",
        "expected_industry": "food",
        "expected_content_type": "promotion"
    },
    {
        "name": "Generic - Testimonial",
        "description": "Customer testimonial template with customer name, photo, quote, rating stars, and company logo.",
        "expected_industry": "generic",
        "expected_content_type": "testimonial"
    },
    {
        "name": "Consulting - Event Invitation",
        "description": "Template for business event invitation with event title, speaker names, date/time, location, and RSVP button.",
        "expected_industry": "consulting",
        "expected_content_type": "event"
    },
]


def run_test(test_case):
    """Run a single test case and print results."""
    print(f"\n{'='*80}")
    print(f"TEST: {test_case['name']}")
    print(f"{'='*80}")
    print(f"Description: {test_case['description']}\n")

    try:
        # Generate template
        result = agent.generate_template_from_description(test_case['description'])

        # Check for errors
        if result.get('error'):
            print(f"❌ ERROR: {result['error']}")
            return False

        # Display results
        print("✅ RESULTS:")
        print(f"\n1. PARSED INTENT:")
        print(json.dumps(result['parsed_intent'], indent=2))

        print(f"\n2. FIELD SCHEMA ({len(result['field_schema'])} fields):")
        for field in result['field_schema']:
            required_mark = "* " if field.get('required') else "  "
            print(f"  {required_mark}{field['name']} ({field['type']}): {field['label']}")

        print(f"\n3. VALIDATION:")
        validation = result['validation_result']
        if validation['valid']:
            print(f"  ✅ Template is VALID")
            print(f"     - Syntax: {'✓' if validation['syntax_pass'] else '✗'}")
            print(f"     - Security: {'✓' if validation['security_pass'] else '✗'}")
            print(f"     - Consistency: {'✓' if validation['consistency_pass'] else '✗'}")
        else:
            print(f"  ❌ Template is INVALID")
            for error in validation['errors']:
                print(f"     - ERROR: {error}")

        if validation['warnings']:
            print(f"  ⚠️  WARNINGS:")
            for warning in validation['warnings']:
                print(f"     - {warning}")

        print(f"\n4. LIQUID TEMPLATE ({len(result['liquid_template'])} chars):")
        print("  " + result['liquid_template'][:200] + "..." if len(result['liquid_template']) > 200 else result['liquid_template'])

        print(f"\n5. PREVIEW HTML ({len(result['preview_html'])} chars):")
        print("  " + result['preview_html'][:200] + "..." if len(result['preview_html']) > 200 else result['preview_html'])

        # Verify expectations
        print(f"\n6. VERIFICATION:")
        parsed_intent = result['parsed_intent']
        checks = []

        # Check industry
        if parsed_intent.get('industry') == test_case['expected_industry']:
            checks.append("✓ Industry matched")
        else:
            checks.append(f"⚠️  Industry mismatch: expected {test_case['expected_industry']}, got {parsed_intent.get('industry')}")

        # Check content type
        if parsed_intent.get('content_type') == test_case['expected_content_type']:
            checks.append("✓ Content type matched")
        else:
            checks.append(f"⚠️  Content type mismatch: expected {test_case['expected_content_type']}, got {parsed_intent.get('content_type')}")

        # Check validation
        if validation['valid']:
            checks.append("✓ Template is valid")
        else:
            checks.append("✗ Template validation failed")

        # Check minimum fields
        if len(result['field_schema']) >= 4:
            checks.append(f"✓ Has {len(result['field_schema'])} fields (min 4)")
        else:
            checks.append(f"✗ Only {len(result['field_schema'])} fields (expected 4+)")

        for check in checks:
            print(f"  {check}")

        return validation['valid']

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all test cases."""
    print(f"\n{'='*80}")
    print(f"AI TEMPLATE GENERATOR AGENT - TEST SUITE")
    print(f"{'='*80}")
    print(f"Testing with {len(test_cases)} diverse descriptions\n")

    results = []
    for test_case in test_cases:
        success = run_test(test_case)
        results.append({
            'name': test_case['name'],
            'success': success
        })

    # Summary
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")

    passed = sum(1 for r in results if r['success'])
    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0

    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status}: {result['name']}")

    print(f"\n{'='*80}")
    print(f"TOTAL: {passed}/{total} tests passed ({pass_rate:.1f}%)")
    print(f"{'='*80}")

    # Check if we meet 95% validity requirement
    if pass_rate >= 95:
        print(f"\n🎉 SUCCESS! Agent meets 95%+ Liquid syntax validity requirement.")
        return 0
    else:
        print(f"\n⚠️  WARNING! Agent did not meet 95%+ validity requirement.")
        return 1


if __name__ == "__main__":
    exit(main())
