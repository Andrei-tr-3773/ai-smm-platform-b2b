"""
Analytics package for campaign performance tracking and insights.

This package provides:
- Data models for analytics (analytics_models)
- Mock data generation for testing (mock_analytics_generator)
- Analytics agent for generating insights (analytics_agent)
"""

from analytics.analytics_models import (
    CampaignMetrics,
    BenchmarkData,
    EngagementPattern,
    ContentInsight,
    CampaignAnalytics,
)
from analytics.mock_analytics_generator import MockAnalyticsGenerator

__all__ = [
    "CampaignMetrics",
    "BenchmarkData",
    "EngagementPattern",
    "ContentInsight",
    "CampaignAnalytics",
    "MockAnalyticsGenerator",
]
