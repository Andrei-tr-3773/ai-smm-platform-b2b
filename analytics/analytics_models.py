"""
Analytics data models for campaign performance tracking.

This module defines the core data structures for analytics:
- CampaignMetrics: Daily engagement metrics
- BenchmarkData: Industry benchmarks for comparison
- EngagementPattern: Detected patterns in engagement
- ContentInsight: AI-generated insights about content performance
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, date


@dataclass
class CampaignMetrics:
    """
    Daily engagement metrics for a campaign.

    Attributes:
        campaign_id: Unique identifier for the campaign
        date: Date of metrics
        views: Number of views/impressions
        likes: Number of likes/reactions
        comments: Number of comments
        shares: Number of shares/reposts
        saves: Number of saves (Instagram/Pinterest)
        clicks: Number of link clicks
        engagement_rate: (likes + comments + shares) / views
        save_rate: saves / views
        click_through_rate: clicks / views
        virality_score: shares / views * 100
        platform: Platform name (instagram, facebook, telegram, linkedin)
    """
    campaign_id: str
    date: date

    # Engagement metrics
    views: int
    likes: int
    comments: int
    shares: int
    saves: int  # Instagram/Pinterest
    clicks: int  # Link clicks

    # Calculated metrics
    engagement_rate: float  # (likes + comments + shares) / views
    save_rate: float  # saves / views
    click_through_rate: float  # clicks / views
    virality_score: float  # shares / views * 100

    # Platform
    platform: str  # instagram, facebook, telegram, linkedin


@dataclass
class BenchmarkData:
    """
    Industry benchmark data for comparison.

    Provides percentile-based benchmarks to compare campaign performance
    against industry standards.

    Attributes:
        industry: Industry category (fitness, ecommerce, saas, etc.)
        platform: Platform name
        avg_views: Average views for industry/platform
        avg_engagement_rate: Average engagement rate
        avg_save_rate: Average save rate
        avg_ctr: Average click-through rate
        p25_engagement: 25th percentile engagement rate
        p50_engagement: Median engagement rate
        p75_engagement: 75th percentile engagement rate
        p90_engagement: 90th percentile (top 10%) engagement rate
    """
    industry: str  # fitness, ecommerce, saas, etc.
    platform: str

    avg_views: int
    avg_engagement_rate: float
    avg_save_rate: float
    avg_ctr: float

    # Percentiles
    p25_engagement: float  # 25th percentile
    p50_engagement: float  # median
    p75_engagement: float  # 75th percentile
    p90_engagement: float  # top 10%


@dataclass
class EngagementPattern:
    """
    Detected pattern in engagement data.

    Identifies significant patterns in campaign performance such as
    spikes, declines, or consistent trends.

    Attributes:
        pattern_type: Type of pattern (spike, decline, weekend_drop,
                     consistent, trending)
        description: Human-readable description (e.g., "Spike on Dec 15
                    (+350% views)")
        date_range: Tuple of (start_date, end_date) for pattern
        impact: Impact level (high, medium, low)
    """
    pattern_type: str  # spike, decline, weekend_drop, consistent, trending
    description: str  # "Spike on Dec 15 (+350% views)"
    date_range: tuple[date, date]
    impact: str  # high, medium, low


@dataclass
class ContentInsight:
    """
    AI-generated insight about why content worked.

    Provides explainable AI insights about content performance,
    answering "WHY" the content succeeded or failed.

    Attributes:
        campaign_id: Campaign identifier
        insight_type: Type of insight (hook, timing, platform_fit,
                     audience_match, visual_appeal)
        explanation: Detailed explanation of the insight
        confidence: Confidence score (0.0-1.0)
        evidence: List of supporting data points
    """
    campaign_id: str
    insight_type: str  # hook, timing, platform_fit, audience_match, visual_appeal
    explanation: str  # "Strong hook in first 3 seconds grabbed attention"
    confidence: float  # 0.0-1.0
    evidence: List[str]  # Supporting data points


@dataclass
class CampaignAnalytics:
    """
    Complete analytics result for a campaign.

    Aggregates all analytics data for a campaign including metrics,
    benchmarks, patterns, and AI insights.

    Attributes:
        campaign_id: Campaign identifier
        campaign_name: Campaign name
        platform: Platform name
        industry: Industry category
        metrics: List of daily metrics
        benchmark: Industry benchmark data
        patterns: Detected engagement patterns
        insights: AI-generated insights
        recommendations: List of actionable recommendations
        performance_summary: Overall performance summary
        next_month_strategy: AI-generated strategy for next month
    """
    campaign_id: str
    campaign_name: str
    platform: str
    industry: str

    metrics: List[CampaignMetrics]
    benchmark: BenchmarkData
    patterns: List[EngagementPattern]
    insights: List[ContentInsight]

    recommendations: List[str]
    performance_summary: str
    next_month_strategy: Optional[str] = None
