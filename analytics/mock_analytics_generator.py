"""
Mock analytics data generator for testing and demonstration.

This module generates realistic campaign metrics data for testing purposes,
simulating real-world engagement patterns including:
- Industry-specific baseline metrics
- Day-of-week engagement patterns
- Content decay over time
- Viral spikes
"""

import random
from datetime import datetime, date, timedelta
from typing import List, Dict
import logging

from analytics.analytics_models import CampaignMetrics, BenchmarkData

logger = logging.getLogger(__name__)


class MockAnalyticsGenerator:
    """Generate realistic mock analytics data for campaigns."""

    def __init__(self, industry: str = "fitness", platform: str = "instagram_reels"):
        """
        Initialize mock data generator.

        Args:
            industry: Industry category (fitness, ecommerce, saas)
            platform: Platform name (instagram_reels, tiktok, linkedin, etc.)
        """
        self.industry = industry
        self.platform = platform

        # Industry-specific base metrics
        self.base_metrics = {
            "fitness": {
                "instagram_reels": {"views": 5000, "engagement_rate": 0.045},
                "tiktok": {"views": 12000, "engagement_rate": 0.062},
                "youtube_shorts": {"views": 3500, "engagement_rate": 0.038},
                "facebook_video": {"views": 2000, "engagement_rate": 0.028},
                "linkedin": {"views": 800, "engagement_rate": 0.035}
            },
            "ecommerce": {
                "instagram_reels": {"views": 4200, "engagement_rate": 0.038},
                "tiktok": {"views": 15000, "engagement_rate": 0.055},
                "facebook_video": {"views": 3000, "engagement_rate": 0.025}
            },
            "saas": {
                "linkedin": {"views": 1200, "engagement_rate": 0.042},
                "youtube_shorts": {"views": 2500, "engagement_rate": 0.035},
                "instagram_reels": {"views": 2800, "engagement_rate": 0.032}
            }
        }

    def generate_campaign_metrics(
        self,
        campaign_id: str,
        start_date: date,
        days: int = 30,
        virality_factor: float = 1.0  # 1.0 = normal, 2.0 = viral content
    ) -> List[CampaignMetrics]:
        """
        Generate daily metrics for a campaign.

        Args:
            campaign_id: Campaign identifier
            start_date: First day of campaign
            days: Number of days to generate
            virality_factor: Multiplier for engagement (1.0-3.0)
                1.0 = average performance
                1.5 = good performance
                2.0+ = viral performance

        Returns:
            List of daily CampaignMetrics
        """
        metrics = []
        base = self._get_base_metrics()

        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)

            # Day-of-week patterns
            weekday_factor = self._get_weekday_factor(current_date.weekday())

            # Decay over time (content gets less views after first few days)
            decay_factor = self._get_decay_factor(day_offset)

            # Random variance (±20%)
            variance = random.uniform(0.8, 1.2)

            # Calculate views
            views = int(
                base["views"] *
                weekday_factor *
                decay_factor *
                virality_factor *
                variance
            )

            # Calculate engagement
            engagement_rate = base["engagement_rate"] * virality_factor * random.uniform(0.9, 1.1)

            # Generate engagement counts
            total_engagement = int(views * engagement_rate)
            likes = int(total_engagement * 0.70)  # 70% of engagement is likes
            comments = int(total_engagement * 0.15)  # 15% comments
            shares = int(total_engagement * 0.10)  # 10% shares
            saves = int(total_engagement * 0.05)  # 5% saves

            # Click-through rate (varies by platform)
            ctr_base = {"instagram_reels": 0.012, "tiktok": 0.008, "linkedin": 0.025}
            ctr = ctr_base.get(self.platform, 0.01)
            clicks = int(views * ctr * random.uniform(0.8, 1.2))

            metrics.append(CampaignMetrics(
                campaign_id=campaign_id,
                date=current_date,
                views=views,
                likes=likes,
                comments=comments,
                shares=shares,
                saves=saves,
                clicks=clicks,
                engagement_rate=engagement_rate,
                save_rate=saves / views if views > 0 else 0,
                click_through_rate=clicks / views if views > 0 else 0,
                virality_score=(shares / views * 100) if views > 0 else 0,
                platform=self.platform
            ))

        logger.info(f"Generated {len(metrics)} days of metrics for campaign {campaign_id}")
        return metrics

    def _get_base_metrics(self) -> Dict:
        """Get base metrics for industry/platform."""
        return self.base_metrics.get(self.industry, {}).get(
            self.platform,
            {"views": 3000, "engagement_rate": 0.035}
        )

    def _get_weekday_factor(self, weekday: int) -> float:
        """
        Get engagement multiplier based on day of week.

        0 = Monday, 6 = Sunday

        Patterns:
        - Weekend posts get 20-30% less engagement
        - Wednesday-Thursday peak
        - Monday recovering from weekend
        """
        factors = {
            0: 0.85,  # Monday (recovering)
            1: 0.95,  # Tuesday
            2: 1.10,  # Wednesday (peak)
            3: 1.05,  # Thursday (peak)
            4: 0.90,  # Friday (dropping)
            5: 0.70,  # Saturday (low)
            6: 0.75   # Sunday (low)
        }
        return factors.get(weekday, 1.0)

    def _get_decay_factor(self, day_offset: int) -> float:
        """
        Get decay factor based on days since posting.

        Social media content loses visibility over time:
        - Day 1-3: Peak visibility
        - Day 4-7: Moderate decay
        - Day 8+: Minimal ongoing engagement
        """
        if day_offset <= 1:
            return 1.0  # First 2 days = full visibility
        elif day_offset <= 3:
            return 0.6  # Days 2-3 = 60% visibility
        elif day_offset <= 7:
            return 0.2  # Days 4-7 = 20% visibility
        else:
            return 0.05  # Day 8+ = minimal residual engagement

    def inject_viral_spike(
        self,
        metrics: List[CampaignMetrics],
        spike_day: int,
        spike_magnitude: float = 3.0
    ) -> List[CampaignMetrics]:
        """
        Inject a viral spike into metrics (simulates trending audio, influencer share, etc.)

        Args:
            metrics: Existing metrics
            spike_day: Day index to inject spike
            spike_magnitude: Multiplier for spike (2.0-5.0)

        Returns:
            Modified metrics with spike
        """
        if spike_day >= len(metrics):
            return metrics

        # Spike affects the day and 2-3 days after
        for i in range(spike_day, min(spike_day + 3, len(metrics))):
            day_factor = spike_magnitude if i == spike_day else spike_magnitude * 0.4

            metrics[i].views = int(metrics[i].views * day_factor)
            metrics[i].likes = int(metrics[i].likes * day_factor * 1.2)  # Likes spike even more
            metrics[i].shares = int(metrics[i].shares * day_factor * 1.5)  # Shares spike most
            metrics[i].comments = int(metrics[i].comments * day_factor * 1.1)
            metrics[i].virality_score = (metrics[i].shares / metrics[i].views * 100)

        logger.info(f"Injected viral spike at day {spike_day} (magnitude: {spike_magnitude}x)")
        return metrics

    def generate_benchmark_data(self) -> BenchmarkData:
        """Generate benchmark data for industry/platform."""
        base = self._get_base_metrics()

        return BenchmarkData(
            industry=self.industry,
            platform=self.platform,
            avg_views=base["views"],
            avg_engagement_rate=base["engagement_rate"],
            avg_save_rate=0.008,  # 0.8% save rate
            avg_ctr=0.012,  # 1.2% CTR
            p25_engagement=base["engagement_rate"] * 0.6,
            p50_engagement=base["engagement_rate"],
            p75_engagement=base["engagement_rate"] * 1.4,
            p90_engagement=base["engagement_rate"] * 2.0
        )
