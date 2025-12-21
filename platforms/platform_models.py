"""Data models for platform-specific rules and optimization."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import time, datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PlatformRulesVersion:
    """Version tracking for platform rules to prevent outdated recommendations."""

    version: str  # "2025-Q1"
    last_updated: datetime
    deprecated: bool = False
    next_review_date: Optional[datetime] = None

    def __post_init__(self):
        """Auto-set review date to 90 days from last_updated."""
        if self.next_review_date is None:
            self.next_review_date = self.last_updated + timedelta(days=90)

    def is_outdated(self) -> bool:
        """Check if rules need review (>90 days old)."""
        return datetime.now() > self.next_review_date

    def check_freshness(self):
        """Log warning if rules may be outdated."""
        if self.is_outdated():
            logger.warning(
                f"Platform rules version {self.version} may be outdated. "
                f"Last updated: {self.last_updated.date()}. "
                f"Consider reviewing platform algorithm changes."
            )


@dataclass
class PlatformRules:
    """Algorithm rules for a social media platform."""

    platform: str  # instagram, facebook, telegram, linkedin

    # Content rules
    optimal_length: Dict[str, int]  # {text: 150, video: 30}
    max_hashtags: int
    recommended_hashtags: int
    supports_carousels: bool = True
    supports_video: bool = True
    supports_stories: bool = True

    # Algorithm preferences (boost multipliers)
    video_boost: float = 1.0  # 1.35 = 35% boost over images
    carousel_boost: float = 1.0
    native_content_boost: float = 1.0  # vs external links

    # Engagement patterns
    best_posting_times: List[time] = field(default_factory=list)
    worst_posting_days: List[str] = field(default_factory=list)

    # Penalties
    link_penalty: bool = False  # Does external link reduce reach?
    clickbait_penalty: bool = False

    # Best practices
    hook_importance: str = "moderate"  # "critical", "important", "moderate"
    first_3_seconds_critical: bool = False  # For video
    emoji_usage: str = "neutral"  # "encouraged", "neutral", "discouraged"

    # Version tracking
    version_info: Optional[PlatformRulesVersion] = None

    def __post_init__(self):
        """Initialize version tracking if not provided."""
        if self.version_info is None:
            self.version_info = PlatformRulesVersion(
                version="2025-Q1",
                last_updated=datetime(2025, 12, 21)
            )
        # Check freshness on load
        self.version_info.check_freshness()


@dataclass
class ContentFormat:
    """Content format specifications for a platform."""

    format_type: str  # feed_post, story, reel, carousel
    platform: str

    # Technical specs for video
    recommended_duration: Optional[int] = None  # seconds for video
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None

    # Image specs
    recommended_width: Optional[int] = None
    recommended_height: Optional[int] = None
    aspect_ratio: str = "1:1"  # "1:1", "9:16", "4:5"

    # Content specs
    min_text_length: Optional[int] = None
    max_text_length: Optional[int] = None
    ideal_text_length: Optional[int] = None

    # Best practices
    call_to_action_position: str = "end"  # "beginning", "middle", "end"
    hashtag_placement: str = "end"  # "inline", "end", "first_comment"


@dataclass
class ViralPattern:
    """Viral content pattern with templates and performance metrics."""

    pattern_id: str
    name: str  # "Curiosity Hook", "Problem-Solution", "Countdown"
    description: str

    # Pattern structure (Liquid-style templates)
    hook_template: str  # "Stop! You're making {{number}} mistakes..."
    body_template: str
    cta_template: str

    # Performance metrics
    avg_engagement_boost: float  # 2.5 = 250% of baseline
    success_rate: float  # 0.88 = 88% success rate
    avg_views: int  # Average views for posts using this pattern

    # Platform compatibility
    works_best_on: List[str] = field(default_factory=list)  # ["instagram", "tiktok"]

    # Industry fit
    industry_fit: List[str] = field(default_factory=list)  # ["fitness", "ecommerce", "saas"]
    example_campaigns: List[str] = field(default_factory=list)

    # Pattern metadata (for maintenance)
    trend_status: str = "active"  # "active", "declining", "deprecated"
    last_validated: Optional[str] = None  # "2025-12-21"
    success_rate_history: List[float] = field(default_factory=list)  # [88, 85, 82]
    deprecation_warning: Optional[str] = None

    def is_declining(self) -> bool:
        """Check if pattern success rate is declining (>20% drop)."""
        if len(self.success_rate_history) < 2:
            return False

        recent_avg = sum(self.success_rate_history[-3:]) / min(3, len(self.success_rate_history[-3:]))
        overall_avg = sum(self.success_rate_history) / len(self.success_rate_history)

        decline_pct = ((overall_avg - recent_avg) / overall_avg) if overall_avg > 0 else 0
        return decline_pct > 0.20  # 20% decline threshold

    def get_status_emoji(self) -> str:
        """Get visual indicator for pattern status."""
        if self.trend_status == "deprecated":
            return "❌"
        elif self.trend_status == "declining":
            return "⚠️"
        elif self.is_declining():
            return "📉"
        else:
            return "✅"
