#!/usr/bin/env python3
"""
Test script for Video Script Agent

Validates VideoScriptAgent functionality with diverse campaigns.
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents.video_script_agent import VideoScriptAgent

# Load environment
load_dotenv(override=True)

print("Testing Video Script Agent")
print("=" * 80)

# Initialize agent
print("\n[Setup] Initializing VideoScriptAgent...")
model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")
)
agent = VideoScriptAgent(model)
print("✅ Agent initialized\n")

# Test cases covering diverse industries and platforms
test_cases = [
    {
        "name": "Fitness - Instagram Reels",
        "campaign_content": """
🔥 NEW CLASS ALERT! 🔥

Join Sarah Martinez for our brand new HIIT Cardio Blast class!

📅 Every Saturday at 10:00 AM
⏱️ 45 minutes of high-energy cardio
💪 Burn up to 500 calories
🎯 All fitness levels welcome

First class FREE for new members!

Register now at FitZone.com or call (555) 123-4567
        """,
        "platform": "instagram_reels",
        "target_audience": "Fitness enthusiasts aged 25-40",
        "content_goal": "Drive class registrations for new HIIT class"
    },
    {
        "name": "SaaS - TikTok",
        "campaign_content": """
🚀 NEW FEATURE: Lightning-Fast API v3

We just launched our biggest update yet!

✨ What's New:
• 10x faster query processing
• Real-time data streaming
• Enhanced security protocols
• Zero downtime migration

Perfect for high-traffic applications that need speed + reliability.

Try it free for 30 days → CloudFlow.io/api-v3
        """,
        "platform": "tiktok",
        "target_audience": "Software developers and CTOs",
        "content_goal": "Drive API v3 trial signups"
    },
    {
        "name": "E-commerce - YouTube Shorts",
        "campaign_content": """
❄️ WINTER FLASH SALE ❄️

30% OFF All Winter Dresses!

This week only - while supplies last!

🛍️ 200+ styles available
📦 Free shipping over $50
💳 Easy returns within 30 days

Shop the collection at ShopStyle.com

Use code: WINTER30 at checkout
        """,
        "platform": "youtube_shorts",
        "target_audience": "Fashion-conscious women aged 25-45",
        "content_goal": "Drive flash sale purchases"
    },
    {
        "name": "Consulting - LinkedIn",
        "campaign_content": """
🎯 Ready to Scale Your B2B Sales?

Join our FREE webinar: "From $1M to $10M ARR in 18 Months"

Learn the exact framework we used with 50+ B2B companies:
✓ Inbound lead generation strategies
✓ Sales process optimization
✓ Account-based marketing tactics
✓ Revenue team alignment

Thursday, Jan 25th at 2:00 PM EST

Limited to 100 attendees. Register at GrowthConsulting.com/webinar
        """,
        "platform": "linkedin",
        "target_audience": "B2B sales leaders and founders",
        "content_goal": "Drive webinar registrations"
    }
]

# Run tests
results = []
for i, test in enumerate(test_cases, 1):
    print(f"\n{'=' * 80}")
    print(f"[Test {i}/{len(test_cases)}] {test['name']}")
    print("=" * 80)

    try:
        result = agent.generate_video_script_from_campaign(
            campaign_content=test['campaign_content'],
            platform=test['platform'],
            target_audience=test['target_audience'],
            content_goal=test['content_goal']
        )

        # Validate result structure
        assert 'campaign_analysis' in result, "Missing campaign_analysis"
        assert 'selected_pattern' in result, "Missing selected_pattern"
        assert 'script_sections' in result, "Missing script_sections"
        assert 'production_notes' in result, "Missing production_notes"
        assert 'virality_prediction' in result, "Missing virality_prediction"
        assert 'full_script' in result, "Missing full_script"

        analysis = result['campaign_analysis']
        pattern = result['selected_pattern']
        sections = result['script_sections']
        production = result['production_notes']
        prediction = result['virality_prediction']

        # Display analysis
        print(f"\n📊 Campaign Analysis:")
        print(f"   Content Type: {analysis.get('content_type', 'N/A')}")
        print(f"   Industry: {analysis.get('industry', 'N/A')}")
        print(f"   Key Message: {analysis.get('key_message', 'N/A')}")
        print(f"   Emotion: {analysis.get('emotion', 'N/A')}")

        # Display selected pattern
        print(f"\n🎯 Selected Pattern:")
        print(f"   Name: {pattern.get('name', 'N/A')}")
        print(f"   Success Rate: {pattern.get('success_rate', 0):.1%}")
        print(f"   Avg Views: {pattern.get('avg_views', 0):,}")

        # Display script sections
        print(f"\n🎬 Script Sections: {len(sections)} sections")
        for j, section in enumerate(sections[:3], 1):  # Show first 3
            print(f"   {j}. {section.get('section', 'N/A')} ({section.get('timing', 'N/A')})")
            print(f"      Shot: {section.get('shot', 'N/A')}")
            print(f"      Text: {section.get('text', 'N/A')[:60]}...")

        # Display production notes
        print(f"\n🎥 Production Notes:")
        if 'camera_setup' in production:
            print(f"   Camera: {production['camera_setup'][:80]}...")
        if 'lighting' in production:
            print(f"   Lighting: {production['lighting'][:80]}...")
        if 'smartphone_tips' in production:
            print(f"   Smartphone Tips: {production['smartphone_tips'][:80]}...")

        # Display virality prediction
        print(f"\n⚡ Virality Prediction:")
        print(f"   Score: {prediction.get('virality_score', 0)}/100")
        print(f"   Expected Views: {prediction.get('expected_views', 'N/A')}")
        if 'strengths' in prediction and prediction['strengths']:
            print(f"   Top Strength: {prediction['strengths'][0]}")

        # Validate virality score range
        virality_score = prediction.get('virality_score', 0)
        assert 0 <= virality_score <= 100, f"Virality score {virality_score} out of range"

        # Validate script sections have required fields
        for section in sections:
            assert 'section' in section, "Section missing 'section' field"
            assert 'timing' in section, "Section missing 'timing' field"
            assert 'text' in section, "Section missing 'text' field"
            assert 'shot' in section, "Section missing 'shot' field"

        # Validate production notes
        assert 'camera_setup' in production, "Missing camera_setup"
        assert 'lighting' in production, "Missing lighting"
        assert 'audio' in production, "Missing audio"

        print(f"\n✅ {test['name']} - PASSED")
        results.append({
            'test': test['name'],
            'status': 'PASSED',
            'virality_score': virality_score,
            'pattern': pattern.get('name', 'N/A'),
            'sections_count': len(sections)
        })

    except Exception as e:
        print(f"\n❌ {test['name']} - FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        results.append({
            'test': test['name'],
            'status': 'FAILED',
            'error': str(e)
        })

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

passed = sum(1 for r in results if r['status'] == 'PASSED')
failed = sum(1 for r in results if r['status'] == 'FAILED')

print(f"\n✅ Passed: {passed}/{len(test_cases)}")
print(f"❌ Failed: {failed}/{len(test_cases)}")

if passed == len(test_cases):
    print("\n🎉 All tests passed! VideoScriptAgent is ready for production!")

    # Display test results table
    print("\n📊 Test Results:")
    print(f"{'Test':<30} {'Pattern':<35} {'Score':<10} {'Sections':<10}")
    print("-" * 85)
    for r in results:
        if r['status'] == 'PASSED':
            print(f"{r['test']:<30} {r['pattern']:<35} {r['virality_score']:<10} {r['sections_count']:<10}")
else:
    print("\n⚠️  Some tests failed. Please review errors above.")
    exit(1)
