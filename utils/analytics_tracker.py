"""
Analytics Event Tracker - MongoDB-based event tracking.

Week 8: Task 8.4.1 - Track key business events for revenue analytics.

Events tracked:
- User lifecycle: signup, login, upgrade, churn
- Content generation: campaign_generated, blog_generated, copy_generated
- Payment: payment_successful, payment_failed
- Engagement: workspace_created, template_created, translation_used

Future: Migrate to Mixpanel/Amplitude for advanced analytics (Month 2+)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from utils.mongodb_utils import get_mongo_client
import logging

logger = logging.getLogger(__name__)


class AnalyticsTracker:
    """Track user events and business metrics."""

    def __init__(self):
        """Initialize analytics tracker with MongoDB."""
        self.db = get_mongo_client()
        self.events_collection = self.db["analytics_events"]

        # Create indexes for fast queries
        self.events_collection.create_index([
            ("user_id", 1),
            ("timestamp", -1)
        ])

        self.events_collection.create_index([
            ("event_name", 1),
            ("timestamp", -1)
        ])

        self.events_collection.create_index([
            ("workspace_id", 1),
            ("timestamp", -1)
        ])

        # TTL index: auto-delete events after 1 year (save storage)
        self.events_collection.create_index(
            "timestamp",
            expireAfterSeconds=31536000  # 365 days
        )

    def track_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track an event.

        Args:
            event_name: Name of event (e.g., "signup", "campaign_generated")
            user_id: User ID (optional for anonymous events)
            workspace_id: Workspace ID (optional)
            properties: Additional event properties

        Returns:
            True if tracked successfully, False otherwise

        Example:
            tracker.track_event(
                "campaign_generated",
                user_id="user_123",
                workspace_id="ws_456",
                properties={
                    "platform": "instagram",
                    "languages": ["en-US", "es-ES"],
                    "template_id": "template_789"
                }
            )
        """
        try:
            event = {
                "event_name": event_name,
                "user_id": user_id,
                "workspace_id": workspace_id,
                "properties": properties or {},
                "timestamp": datetime.utcnow(),
                "date": datetime.utcnow().strftime("%Y-%m-%d"),  # For daily aggregation
                "hour": datetime.utcnow().strftime("%Y-%m-%d %H:00")  # For hourly aggregation
            }

            self.events_collection.insert_one(event)

            logger.debug(f"Event tracked: {event_name} (user: {user_id})")
            return True

        except Exception as e:
            logger.error(f"Failed to track event {event_name}: {e}")
            return False

    # ==========================================
    # Convenience methods for common events
    # ==========================================

    def track_signup(
        self,
        user_id: str,
        email: str,
        source: Optional[str] = None,
        referrer: Optional[str] = None
    ):
        """
        Track user signup.

        Args:
            user_id: New user ID
            email: User email
            source: Acquisition source (e.g., "product_hunt", "google", "referral")
            referrer: Referring URL or user ID
        """
        self.track_event(
            "signup",
            user_id=user_id,
            properties={
                "email": email,
                "source": source,
                "referrer": referrer
            }
        )

    def track_login(self, user_id: str, workspace_id: str):
        """Track user login."""
        self.track_event(
            "login",
            user_id=user_id,
            workspace_id=workspace_id
        )

    def track_upgrade(
        self,
        user_id: str,
        workspace_id: str,
        from_tier: str,
        to_tier: str,
        price: float
    ):
        """
        Track plan upgrade.

        Args:
            user_id: User ID
            workspace_id: Workspace ID
            from_tier: Previous plan tier
            to_tier: New plan tier
            price: Monthly price
        """
        self.track_event(
            "upgrade",
            user_id=user_id,
            workspace_id=workspace_id,
            properties={
                "from_tier": from_tier,
                "to_tier": to_tier,
                "price": price,
                "currency": "USD"
            }
        )

    def track_campaign_generated(
        self,
        user_id: str,
        workspace_id: str,
        platform: str,
        languages: List[str],
        template_id: Optional[str] = None
    ):
        """
        Track campaign generation.

        Args:
            user_id: User ID
            workspace_id: Workspace ID
            platform: Platform (instagram, facebook, etc.)
            languages: List of language codes
            template_id: Template used (if any)
        """
        self.track_event(
            "campaign_generated",
            user_id=user_id,
            workspace_id=workspace_id,
            properties={
                "platform": platform,
                "languages": languages,
                "language_count": len(languages),
                "template_id": template_id
            }
        )

    def track_blog_generated(
        self,
        user_id: str,
        workspace_id: str,
        word_count: int,
        tone: str
    ):
        """Track blog post generation."""
        self.track_event(
            "blog_generated",
            user_id=user_id,
            workspace_id=workspace_id,
            properties={
                "word_count": word_count,
                "tone": tone
            }
        )

    def track_copy_variations_generated(
        self,
        user_id: str,
        workspace_id: str,
        variation_count: int = 5
    ):
        """Track copy variations generation."""
        self.track_event(
            "copy_variations_generated",
            user_id=user_id,
            workspace_id=workspace_id,
            properties={
                "variation_count": variation_count
            }
        )

    def track_payment_successful(
        self,
        user_id: str,
        workspace_id: str,
        amount: float,
        plan_tier: str,
        stripe_subscription_id: str
    ):
        """
        Track successful payment.

        Args:
            user_id: User ID
            workspace_id: Workspace ID
            amount: Payment amount (in dollars)
            plan_tier: Plan tier
            stripe_subscription_id: Stripe subscription ID
        """
        self.track_event(
            "payment_successful",
            user_id=user_id,
            workspace_id=workspace_id,
            properties={
                "amount": amount,
                "plan_tier": plan_tier,
                "stripe_subscription_id": stripe_subscription_id,
                "currency": "USD"
            }
        )

    def track_payment_failed(
        self,
        user_id: str,
        workspace_id: str,
        amount: float,
        reason: Optional[str] = None
    ):
        """Track failed payment."""
        self.track_event(
            "payment_failed",
            user_id=user_id,
            workspace_id=workspace_id,
            properties={
                "amount": amount,
                "reason": reason,
                "currency": "USD"
            }
        )

    def track_churn(
        self,
        user_id: str,
        workspace_id: str,
        plan_tier: str,
        reason: Optional[str] = None,
        lifetime_value: Optional[float] = None
    ):
        """
        Track user churn (subscription cancellation).

        Args:
            user_id: User ID
            workspace_id: Workspace ID
            plan_tier: Plan tier being cancelled
            reason: Cancellation reason (if provided)
            lifetime_value: Total revenue from this user
        """
        self.track_event(
            "churn",
            user_id=user_id,
            workspace_id=workspace_id,
            properties={
                "plan_tier": plan_tier,
                "reason": reason,
                "lifetime_value": lifetime_value
            }
        )

    # ==========================================
    # Query methods for analytics
    # ==========================================

    def get_events(
        self,
        event_name: Optional[str] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query events with filters.

        Args:
            event_name: Filter by event name
            user_id: Filter by user ID
            workspace_id: Filter by workspace ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            limit: Maximum number of results

        Returns:
            List of event dictionaries
        """
        query = {}

        if event_name:
            query["event_name"] = event_name

        if user_id:
            query["user_id"] = user_id

        if workspace_id:
            query["workspace_id"] = workspace_id

        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        return list(
            self.events_collection
            .find(query)
            .sort("timestamp", -1)
            .limit(limit)
        )

    def count_events(
        self,
        event_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> int:
        """
        Count events matching criteria.

        Args:
            event_name: Event name to count
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            user_id: Filter by user ID
            workspace_id: Filter by workspace ID

        Returns:
            Count of events
        """
        query = {"event_name": event_name}

        if user_id:
            query["user_id"] = user_id

        if workspace_id:
            query["workspace_id"] = workspace_id

        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        return self.events_collection.count_documents(query)

    def get_unique_users(
        self,
        event_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        Count unique users who triggered an event.

        Args:
            event_name: Event name (optional, counts all events if not specified)
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Count of unique user IDs
        """
        query = {}

        if event_name:
            query["event_name"] = event_name

        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        # MongoDB distinct operation
        unique_user_ids = self.events_collection.distinct("user_id", query)

        # Filter out None values
        return len([uid for uid in unique_user_ids if uid])

    def get_daily_event_counts(
        self,
        event_name: str,
        days: int = 30
    ) -> Dict[str, int]:
        """
        Get daily counts for an event over last N days.

        Args:
            event_name: Event name
            days: Number of days to look back

        Returns:
            Dict mapping date (YYYY-MM-DD) to count

        Example:
            {"2024-12-01": 5, "2024-12-02": 8, ...}
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        pipeline = [
            {
                "$match": {
                    "event_name": event_name,
                    "timestamp": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": "$date",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]

        results = self.events_collection.aggregate(pipeline)

        return {result["_id"]: result["count"] for result in results}


# Global singleton
_analytics_tracker: Optional[AnalyticsTracker] = None


def get_analytics_tracker() -> AnalyticsTracker:
    """Get or create analytics tracker singleton."""
    global _analytics_tracker
    if _analytics_tracker is None:
        _analytics_tracker = AnalyticsTracker()
    return _analytics_tracker


# Convenience functions for quick tracking
def track_event(event_name: str, user_id: Optional[str] = None, **properties):
    """
    Quick event tracking function.

    Example:
        track_event("campaign_generated", user_id="user_123", platform="instagram")
    """
    tracker = get_analytics_tracker()
    tracker.track_event(event_name, user_id=user_id, properties=properties)
