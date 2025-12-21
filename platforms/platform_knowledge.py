"""Platform algorithm knowledge base with rules for Instagram, Facebook, Telegram, LinkedIn.

Based on 2025 social media research and algorithm best practices.
Sources:
- Meta Creator Studio documentation
- Later.com social media research (2025)
- HubSpot social media benchmarks
- LinkedIn Marketing Solutions
- Telegram Best Practices Guide
"""

from datetime import time, datetime
from typing import Dict, Optional
from platforms.platform_models import PlatformRules, PlatformRulesVersion


# ============================================================================
# Instagram Rules
# ============================================================================

INSTAGRAM_RULES = PlatformRules(
    platform="instagram",

    # Content rules
    optimal_length={
        "feed_post": 150,  # characters (caption)
        "reel": 30,  # seconds
        "story": 15,  # seconds
        "carousel": 150  # characters per slide
    },
    max_hashtags=30,
    recommended_hashtags=11,  # Research shows 11 is optimal (not 30!)
    supports_carousels=True,
    supports_video=True,
    supports_stories=True,

    # Algorithm preferences
    video_boost=1.35,  # 35% more reach than static images
    carousel_boost=1.50,  # 50% more engagement than single image
    native_content_boost=1.20,  # vs external links

    # Best posting times (EST, based on engagement research)
    best_posting_times=[
        time(9, 0),   # 9 AM - morning scroll
        time(11, 0),  # 11 AM - mid-morning break
        time(14, 0),  # 2 PM - lunch break
        time(15, 0),  # 3 PM - afternoon energy dip
    ],
    worst_posting_days=["Saturday", "Sunday"],  # Lower B2B engagement

    # Penalties
    link_penalty=True,  # External links reduce reach by ~20%
    clickbait_penalty=True,

    # Best practices
    hook_importance="critical",  # First 3 seconds determine 90% of engagement
    first_3_seconds_critical=True,  # For Reels
    emoji_usage="encouraged",  # Emojis increase engagement 15-20%

    # Version info
    version_info=PlatformRulesVersion(
        version="2025-Q1",
        last_updated=datetime(2025, 12, 21),
        deprecated=False
    )
)


# ============================================================================
# Facebook Rules
# ============================================================================

FACEBOOK_RULES = PlatformRules(
    platform="facebook",

    # Content rules
    optimal_length={
        "post": 120,  # characters
        "video": 60,  # seconds
        "story": 15,  # seconds
    },
    max_hashtags=10,
    recommended_hashtags=3,  # Facebook doesn't need many hashtags
    supports_carousels=True,
    supports_video=True,
    supports_stories=True,

    # Algorithm preferences
    video_boost=1.35,  # 135% more reach than text-only posts
    carousel_boost=1.10,  # 10% more engagement
    native_content_boost=1.25,  # Strong preference for native content

    # Best posting times (EST)
    best_posting_times=[
        time(13, 0),  # 1 PM - lunch
        time(14, 0),  # 2 PM
        time(15, 0),  # 3 PM - highest engagement window
    ],
    worst_posting_days=["Saturday", "Sunday"],

    # Penalties
    link_penalty=True,  # Facebook penalizes external links
    clickbait_penalty=True,  # Meta fights clickbait aggressively

    # Best practices
    hook_importance="important",
    first_3_seconds_critical=True,
    emoji_usage="neutral",  # Use sparingly compared to Instagram

    # Version info
    version_info=PlatformRulesVersion(
        version="2025-Q1",
        last_updated=datetime(2025, 12, 21),
        deprecated=False
    )
)


# ============================================================================
# Telegram Rules
# ============================================================================

TELEGRAM_RULES = PlatformRules(
    platform="telegram",

    # Content rules
    optimal_length={
        "channel_post": 300,  # characters (longer than Instagram)
        "message": 200,  # characters
    },
    max_hashtags=5,
    recommended_hashtags=2,  # Telegram uses fewer hashtags
    supports_carousels=False,  # No carousel feature
    supports_video=True,
    supports_stories=False,  # No stories on Telegram

    # Algorithm preferences
    video_boost=1.15,  # 15% more engagement than text
    carousel_boost=1.0,  # N/A (no carousels)
    native_content_boost=1.10,  # Slight preference

    # Best posting times (EST) - different pattern from Instagram
    best_posting_times=[
        time(8, 0),   # 8 AM - morning commute
        time(18, 0),  # 6 PM - evening commute
        time(20, 0),  # 8 PM - evening browsing
    ],
    worst_posting_days=[],  # Telegram engagement consistent all week

    # Penalties
    link_penalty=False,  # Telegram doesn't penalize links!
    clickbait_penalty=False,  # More lenient than Meta platforms

    # Best practices
    hook_importance="moderate",
    first_3_seconds_critical=False,
    emoji_usage="encouraged",  # Very common on Telegram

    # Version info
    version_info=PlatformRulesVersion(
        version="2025-Q1",
        last_updated=datetime(2025, 12, 21),
        deprecated=False
    )
)


# ============================================================================
# LinkedIn Rules
# ============================================================================

LINKEDIN_RULES = PlatformRules(
    platform="linkedin",

    # Content rules
    optimal_length={
        "post": 1500,  # characters (much longer than other platforms)
        "article": 2000,  # characters
        "video": 90,  # seconds
    },
    max_hashtags=5,
    recommended_hashtags=3,  # LinkedIn uses strategic hashtags
    supports_carousels=True,
    supports_video=True,
    supports_stories=False,  # LinkedIn Stories deprecated

    # Algorithm preferences
    video_boost=1.20,  # 20% more reach
    carousel_boost=1.25,  # LinkedIn loves carousels (PDF carousels perform best)
    native_content_boost=1.40,  # HUGE penalty for external links

    # Best posting times (EST) - B2B professional hours
    best_posting_times=[
        time(7, 0),   # 7 AM - before work
        time(8, 0),   # 8 AM - morning
        time(12, 0),  # 12 PM - lunch break
        time(17, 0),  # 5 PM - end of workday
        time(18, 0),  # 6 PM - commute home
    ],
    worst_posting_days=["Saturday", "Sunday"],  # B2B platform

    # Penalties
    link_penalty=True,  # Put links in COMMENTS, not main post
    clickbait_penalty=True,  # Professional audience hates clickbait

    # Best practices
    hook_importance="important",
    first_3_seconds_critical=True,  # For video
    emoji_usage="discouraged",  # Keep it professional

    # Version info
    version_info=PlatformRulesVersion(
        version="2025-Q1",
        last_updated=datetime(2025, 12, 21),
        deprecated=False
    )
)


# ============================================================================
# Platform Rules Registry
# ============================================================================

PLATFORM_RULES_REGISTRY: Dict[str, PlatformRules] = {
    "instagram": INSTAGRAM_RULES,
    "facebook": FACEBOOK_RULES,
    "telegram": TELEGRAM_RULES,
    "linkedin": LINKEDIN_RULES,
}


def get_platform_rules(platform: str) -> Optional[PlatformRules]:
    """
    Get algorithm rules for a specific platform.

    Args:
        platform: Platform name (instagram, facebook, telegram, linkedin)

    Returns:
        PlatformRules object or None if platform not found

    Example:
        >>> rules = get_platform_rules("instagram")
        >>> print(rules.recommended_hashtags)
        11
    """
    platform_lower = platform.lower()
    rules = PLATFORM_RULES_REGISTRY.get(platform_lower)

    if rules:
        # Check freshness when rules are accessed
        rules.version_info.check_freshness()

    return rules


def get_supported_platforms() -> list[str]:
    """Get list of all supported platforms."""
    return list(PLATFORM_RULES_REGISTRY.keys())


def get_all_platform_rules() -> Dict[str, PlatformRules]:
    """Get all platform rules (for admin/debugging)."""
    return PLATFORM_RULES_REGISTRY.copy()
