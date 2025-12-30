"""
Rate Limiter - Protect API costs and enforce fair usage.

Prevents API abuse that could spike COGS from $12/user → $30/user.
Protects 92% gross margin.
"""

from functools import wraps
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


# Rate limits per tier (per hour)
RATE_LIMITS = {
    "free": {
        "campaigns": 2,      # 2 campaigns per hour
        "blog_posts": 1,     # 1 blog post per hour
        "copy_variations": 2, # 2 copy variation sets per hour
        "translations": 10   # 10 translation batches per hour
    },
    "starter": {
        "campaigns": 10,
        "blog_posts": 5,
        "copy_variations": 10,
        "translations": 50
    },
    "professional": {
        "campaigns": 50,
        "blog_posts": 20,
        "copy_variations": 50,
        "translations": 200
    },
    "team": {
        "campaigns": 999,    # Effectively unlimited
        "blog_posts": 100,
        "copy_variations": 999,
        "translations": 999
    },
    "agency": {
        "campaigns": 999,
        "blog_posts": 999,
        "copy_variations": 999,
        "translations": 999
    },
    "enterprise": {
        "campaigns": 999,
        "blog_posts": 999,
        "copy_variations": 999,
        "translations": 999
    }
}


class RateLimitError(Exception):
    """Raised when user exceeds rate limit."""

    def __init__(self, message: str, reset_at: datetime, current: int, limit: int):
        self.message = message
        self.reset_at = reset_at
        self.current = current
        self.limit = limit
        super().__init__(self.message)


class RateLimiter:
    """Rate limiter using MongoDB for storage."""

    def __init__(self):
        from utils.mongodb_utils import get_mongo_client
        self.db = get_mongo_client()
        self.collection = self.db["rate_limits"]

        # Create index for automatic cleanup (TTL index)
        self.collection.create_index(
            "reset_at",
            expireAfterSeconds=0  # Documents expire at reset_at time
        )

        # Create compound index for fast lookups
        self.collection.create_index([
            ("user_id", 1),
            ("feature", 1),
            ("window_start", 1)
        ])

    def get_usage(
        self,
        user_id: str,
        feature: str,
        window_hours: int = 1
    ) -> Dict[str, Any]:
        """
        Get current usage for user and feature.

        Args:
            user_id: User ID
            feature: Feature name (campaigns, blog_posts, etc.)
            window_hours: Time window in hours (default 1)

        Returns:
            Dict with current usage, limit, and reset time
        """
        # Calculate window boundaries
        now = datetime.utcnow()
        window_start = now.replace(minute=0, second=0, microsecond=0)
        reset_at = window_start + timedelta(hours=window_hours)

        # Find or create usage record
        usage_doc = self.collection.find_one({
            "user_id": user_id,
            "feature": feature,
            "window_start": window_start
        })

        if not usage_doc:
            # Create new usage record
            usage_doc = {
                "user_id": user_id,
                "feature": feature,
                "window_start": window_start,
                "reset_at": reset_at,
                "count": 0,
                "created_at": now
            }
            self.collection.insert_one(usage_doc)

        return {
            "current": usage_doc.get("count", 0),
            "reset_at": usage_doc.get("reset_at", reset_at),
            "window_start": window_start
        }

    def increment_usage(
        self,
        user_id: str,
        feature: str,
        increment: int = 1
    ) -> int:
        """
        Increment usage counter.

        Args:
            user_id: User ID
            feature: Feature name
            increment: Amount to increment (default 1)

        Returns:
            New count after increment
        """
        now = datetime.utcnow()
        window_start = now.replace(minute=0, second=0, microsecond=0)
        reset_at = window_start + timedelta(hours=1)

        # Upsert with increment
        result = self.collection.find_one_and_update(
            {
                "user_id": user_id,
                "feature": feature,
                "window_start": window_start
            },
            {
                "$inc": {"count": increment},
                "$setOnInsert": {
                    "window_start": window_start,
                    "reset_at": reset_at,
                    "created_at": now
                },
                "$set": {
                    "updated_at": now
                }
            },
            upsert=True,
            return_document=True
        )

        return result["count"]

    def check_rate_limit(
        self,
        user_id: str,
        feature: str,
        tier: str
    ) -> bool:
        """
        Check if user is within rate limit.

        Args:
            user_id: User ID
            feature: Feature name
            tier: Plan tier (free, starter, etc.)

        Returns:
            True if within limit, raises RateLimitError otherwise
        """
        # Get tier limits
        tier_limits = RATE_LIMITS.get(tier, RATE_LIMITS["free"])
        limit = tier_limits.get(feature, 0)

        # Get current usage
        usage = self.get_usage(user_id, feature)
        current = usage["current"]
        reset_at = usage["reset_at"]

        # Check limit
        if current >= limit:
            logger.warning(
                f"Rate limit exceeded: user={user_id}, feature={feature}, "
                f"tier={tier}, current={current}, limit={limit}"
            )
            raise RateLimitError(
                f"Rate limit exceeded: {current}/{limit} {feature}/hour. "
                f"Resets at {reset_at.strftime('%H:%M UTC')}",
                reset_at=reset_at,
                current=current,
                limit=limit
            )

        return True

    def get_remaining(
        self,
        user_id: str,
        feature: str,
        tier: str
    ) -> Dict[str, Any]:
        """
        Get remaining quota for user.

        Args:
            user_id: User ID
            feature: Feature name
            tier: Plan tier

        Returns:
            Dict with remaining, limit, reset_at
        """
        tier_limits = RATE_LIMITS.get(tier, RATE_LIMITS["free"])
        limit = tier_limits.get(feature, 0)

        usage = self.get_usage(user_id, feature)
        current = usage["current"]

        return {
            "remaining": max(0, limit - current),
            "limit": limit,
            "current": current,
            "reset_at": usage["reset_at"],
            "percentage_used": round((current / limit * 100) if limit > 0 else 0, 1)
        }


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create rate limiter singleton."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def rate_limit(feature: str):
    """
    Decorator to enforce rate limits on functions.

    Usage:
        @rate_limit("campaigns")
        def generate_campaign(...):
            pass

    Args:
        feature: Feature name (must be in RATE_LIMITS)

    Raises:
        RateLimitError: If rate limit exceeded
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from utils.auth import get_current_user

            # Get current user
            user = get_current_user()
            if not user:
                # Guest users have free tier limits
                tier = "free"
                user_id = "guest"
            else:
                # Get user's workspace tier
                from repositories.workspace_repository import WorkspaceRepository
                workspace_repo = WorkspaceRepository()
                workspace = workspace_repo.get_workspace(user.workspace_id)
                tier = workspace.plan_tier if workspace else "free"
                user_id = user.id

            # Check rate limit
            limiter = get_rate_limiter()
            limiter.check_rate_limit(user_id, feature, tier)

            # Execute function
            result = func(*args, **kwargs)

            # Increment usage counter
            limiter.increment_usage(user_id, feature, increment=1)

            logger.info(
                f"Rate limit tracked: user={user_id}, feature={feature}, "
                f"tier={tier}"
            )

            return result

        return wrapper
    return decorator


def get_rate_limit_status(user_id: str, tier: str) -> Dict[str, Any]:
    """
    Get rate limit status for all features.

    Args:
        user_id: User ID
        tier: Plan tier

    Returns:
        Dict with status for each feature
    """
    limiter = get_rate_limiter()

    status = {}
    for feature in ["campaigns", "blog_posts", "copy_variations", "translations"]:
        status[feature] = limiter.get_remaining(user_id, feature, tier)

    return status
