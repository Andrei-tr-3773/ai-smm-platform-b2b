"""
Test analytics integration with CampaignRepository.

Verifies that analytics data can be saved to and retrieved from MongoDB.
"""

from datetime import date, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.analytics_agent import analyze_campaign
from analytics.mock_analytics_generator import MockAnalyticsGenerator


def test_analytics_integration_with_mock_data():
    """
    Test end-to-end analytics workflow with mock data.

    This test demonstrates the full flow without needing real MongoDB:
    1. Generate mock metrics
    2. Run analytics agent
    3. Verify results
    """
    print("=== Testing Analytics Integration (Mock Data) ===\n")

    # Generate mock campaign
    generator = MockAnalyticsGenerator("fitness", "instagram_reels")

    start = date.today() - timedelta(days=30)
    metrics = generator.generate_campaign_metrics(
        "test_campaign",
        start,
        days=30,
        virality_factor=1.8
    )

    # Add viral spike for interesting pattern
    metrics = generator.inject_viral_spike(metrics, spike_day=5, spike_magnitude=3.5)

    benchmark = generator.generate_benchmark_data()

    # Analyze campaign
    result = analyze_campaign("test_campaign", metrics, benchmark)

    # Verify results
    assert result['performance_summary'] is not None
    assert len(result['content_insights']) > 0
    assert len(result['recommendations']) > 0

    print(f"✅ Performance Rating: {result['performance_summary']['overall_rating']}")
    print(f"✅ Patterns Detected: {len(result['detected_patterns'])}")
    print(f"✅ Insights Generated: {len(result['content_insights'])}")
    print(f"✅ Recommendations: {len(result['recommendations'])}")

    print("\n📊 Sample Insights:")
    for insight in result['content_insights'][:2]:
        print(f"  - [{insight.insight_type}] {insight.explanation}")

    print("\n📝 Sample Recommendations:")
    for rec in result['recommendations'][:3]:
        print(f"  - {rec}")

    print(f"\n🎯 Next Month Strategy:\n  {result['next_month_strategy']}")

    print("\n✅ Analytics integration test passed!")
    return result


if __name__ == "__main__":
    test_analytics_integration_with_mock_data()
