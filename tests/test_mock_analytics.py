"""
Tests for MockAnalyticsGenerator.

Verifies that mock data generation produces realistic engagement patterns.
"""

from datetime import date, timedelta
from analytics.mock_analytics_generator import MockAnalyticsGenerator


def test_generate_campaign_metrics():
    """Test basic campaign metrics generation."""
    generator = MockAnalyticsGenerator(industry="fitness", platform="instagram_reels")

    start = date.today() - timedelta(days=30)
    metrics = generator.generate_campaign_metrics(
        campaign_id="camp_001",
        start_date=start,
        days=30,
        virality_factor=1.0  # Average performance
    )

    assert len(metrics) == 30, "Should generate 30 days of metrics"
    assert metrics[0].campaign_id == "camp_001"
    assert metrics[0].platform == "instagram_reels"

    # Views should be higher on first day than day 7 (decay)
    print(f"Day 1 views: {metrics[0].views}")
    print(f"Day 7 views: {metrics[6].views}")
    assert metrics[0].views > metrics[6].views, "Views should decay over time"

    # Weekend views should be lower (Saturday = index 5 if start was Monday)
    print(f"First 7 days views: {[m.views for m in metrics[:7]]}")


def test_viral_campaign():
    """Test viral campaign with higher virality factor."""
    generator = MockAnalyticsGenerator(industry="fitness", platform="instagram_reels")

    start = date.today() - timedelta(days=30)
    viral_metrics = generator.generate_campaign_metrics(
        campaign_id="camp_002",
        start_date=start,
        days=30,
        virality_factor=2.5  # Viral performance!
    )

    # Viral campaign should have significantly higher engagement
    normal_generator = MockAnalyticsGenerator(industry="fitness", platform="instagram_reels")
    normal_metrics = normal_generator.generate_campaign_metrics(
        campaign_id="camp_003",
        start_date=start,
        days=30,
        virality_factor=1.0
    )

    viral_avg = sum(m.views for m in viral_metrics) / len(viral_metrics)
    normal_avg = sum(m.views for m in normal_metrics) / len(normal_metrics)

    print(f"Viral campaign avg views: {viral_avg:.0f}")
    print(f"Normal campaign avg views: {normal_avg:.0f}")
    print(f"Viral multiplier: {viral_avg / normal_avg:.2f}x")

    # Viral should be at least 2x higher
    assert viral_avg > normal_avg * 2, "Viral campaign should have 2x+ views"


def test_inject_viral_spike():
    """Test injecting viral spike on specific day."""
    generator = MockAnalyticsGenerator(industry="fitness", platform="instagram_reels")

    start = date.today() - timedelta(days=30)
    metrics = generator.generate_campaign_metrics(
        campaign_id="camp_004",
        start_date=start,
        days=30,
        virality_factor=1.0
    )

    # Record day 3 views before spike
    day_3_views_before = metrics[3].views

    # Inject trending spike on day 3
    metrics = generator.inject_viral_spike(metrics, spike_day=3, spike_magnitude=4.0)

    print(f"Day 3 views before spike: {day_3_views_before}")
    print(f"Day 3 views after spike: {metrics[3].views}")
    print(f"Virality score: {metrics[3].virality_score}")

    # Day 3 should have significantly more views
    assert metrics[3].views > day_3_views_before * 3, "Spike should increase views by 3x+"


def test_benchmark_data():
    """Test benchmark data generation."""
    generator = MockAnalyticsGenerator(industry="fitness", platform="instagram_reels")
    benchmark = generator.generate_benchmark_data()

    assert benchmark.industry == "fitness"
    assert benchmark.platform == "instagram_reels"
    assert benchmark.avg_views > 0
    assert benchmark.avg_engagement_rate > 0

    # Percentiles should be in correct order
    assert benchmark.p25_engagement < benchmark.p50_engagement
    assert benchmark.p50_engagement < benchmark.p75_engagement
    assert benchmark.p75_engagement < benchmark.p90_engagement

    print(f"Fitness Instagram Reels Benchmark:")
    print(f"  Avg views: {benchmark.avg_views}")
    print(f"  Avg engagement: {benchmark.avg_engagement_rate:.1%}")
    print(f"  P90 engagement: {benchmark.p90_engagement:.1%}")


def test_multiple_industries():
    """Test that different industries have different metrics."""
    fitness_gen = MockAnalyticsGenerator(industry="fitness", platform="instagram_reels")
    saas_gen = MockAnalyticsGenerator(industry="saas", platform="instagram_reels")

    start = date.today() - timedelta(days=30)

    fitness_metrics = fitness_gen.generate_campaign_metrics("f001", start, days=7)
    saas_metrics = saas_gen.generate_campaign_metrics("s001", start, days=7)

    fitness_avg = sum(m.views for m in fitness_metrics) / len(fitness_metrics)
    saas_avg = sum(m.views for m in saas_metrics) / len(saas_metrics)

    print(f"Fitness avg views: {fitness_avg:.0f}")
    print(f"SaaS avg views: {saas_avg:.0f}")

    # Fitness should have higher views than SaaS on Instagram
    assert fitness_avg > saas_avg, "Fitness should outperform SaaS on Instagram Reels"


if __name__ == "__main__":
    print("=== Test: Generate Campaign Metrics ===")
    test_generate_campaign_metrics()
    print("\n=== Test: Viral Campaign ===")
    test_viral_campaign()
    print("\n=== Test: Inject Viral Spike ===")
    test_inject_viral_spike()
    print("\n=== Test: Benchmark Data ===")
    test_benchmark_data()
    print("\n=== Test: Multiple Industries ===")
    test_multiple_industries()
    print("\n✅ All tests passed!")
