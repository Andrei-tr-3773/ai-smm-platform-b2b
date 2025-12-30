"""
Business Metrics Calculator - Track key SaaS metrics.

Week 8: Task 8.4.2 - Calculate MRR, CAC, churn, LTV, etc.

Metrics tracked:
- MRR (Monthly Recurring Revenue)
- Paying users count
- Churn rate
- CAC (Customer Acquisition Cost) by channel
- LTV (Lifetime Value)
- Conversion rate (free → paid)
- Activation rate
- Revenue by tier
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from utils.mongodb_utils import get_mongo_client
from utils.analytics_tracker import get_analytics_tracker
import logging

logger = logging.getLogger(__name__)


# Plan pricing (must match pricing page)
PLAN_PRICING = {
    "free": 0,
    "starter": 49,
    "professional": 99,
    "team": 199,
    "agency": 499,
    "enterprise": 999
}


class BusinessMetrics:
    """Calculate business metrics for SaaS analytics."""

    def __init__(self):
        """Initialize business metrics calculator."""
        self.db = get_mongo_client()
        self.workspaces = self.db["workspaces"]
        self.users = self.db["users"]
        self.analytics = get_analytics_tracker()

    def get_mrr(self) -> float:
        """
        Calculate Monthly Recurring Revenue (MRR).

        Returns:
            Total MRR in USD

        Formula:
            MRR = Σ(active_subscriptions * monthly_price)
        """
        try:
            # Get all paid workspaces
            paid_workspaces = self.workspaces.find({
                "plan_tier": {"$ne": "free"},
                "subscription_status": {"$in": ["active", "trialing"]}
            })

            mrr = 0
            for workspace in paid_workspaces:
                tier = workspace.get("plan_tier", "free")
                price = PLAN_PRICING.get(tier, 0)
                mrr += price

            return round(mrr, 2)

        except Exception as e:
            logger.error(f"Error calculating MRR: {e}")
            return 0.0

    def get_paying_users_count(self) -> int:
        """
        Count paying users (workspaces with active paid plans).

        Returns:
            Number of paying workspaces
        """
        try:
            return self.workspaces.count_documents({
                "plan_tier": {"$ne": "free"},
                "subscription_status": {"$in": ["active", "trialing"]}
            })
        except Exception as e:
            logger.error(f"Error counting paying users: {e}")
            return 0

    def get_total_users_count(self) -> int:
        """
        Count total users (all workspaces).

        Returns:
            Number of all workspaces
        """
        try:
            return self.workspaces.count_documents({})
        except Exception as e:
            logger.error(f"Error counting total users: {e}")
            return 0

    def get_churn_rate(self, days: int = 30) -> float:
        """
        Calculate churn rate over period.

        Args:
            days: Period to calculate over (default 30 days)

        Returns:
            Churn rate as percentage (0-100)

        Formula:
            Churn Rate = (churned_users / users_at_start) * 100
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Count users who churned in period
            churned = self.analytics.count_events(
                "churn",
                start_date=start_date
            )

            # Count paying users at start of period
            # (Approximation: use current paying users + churned)
            current_paying = self.get_paying_users_count()
            users_at_start = max(current_paying + churned, 1)  # Avoid division by zero

            churn_rate = (churned / users_at_start) * 100

            return round(churn_rate, 2)

        except Exception as e:
            logger.error(f"Error calculating churn rate: {e}")
            return 0.0

    def get_revenue_by_tier(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculate revenue breakdown by tier.

        Returns:
            Dict mapping tier → {count, mrr, percentage}

        Example:
            {
                "starter": {"count": 10, "mrr": 490, "percentage": 12.5},
                "professional": {"count": 25, "mrr": 2475, "percentage": 63.2},
                ...
            }
        """
        try:
            total_mrr = self.get_mrr()

            revenue_by_tier = {}

            for tier, price in PLAN_PRICING.items():
                if tier == "free":
                    continue  # Skip free tier for revenue calculation

                count = self.workspaces.count_documents({
                    "plan_tier": tier,
                    "subscription_status": {"$in": ["active", "trialing"]}
                })

                tier_mrr = count * price
                percentage = (tier_mrr / total_mrr * 100) if total_mrr > 0 else 0

                revenue_by_tier[tier] = {
                    "count": count,
                    "mrr": tier_mrr,
                    "percentage": round(percentage, 1)
                }

            return revenue_by_tier

        except Exception as e:
            logger.error(f"Error calculating revenue by tier: {e}")
            return {}

    def get_conversion_rate(self, days: int = 30) -> float:
        """
        Calculate free → paid conversion rate.

        Args:
            days: Period to calculate over (default 30 days)

        Returns:
            Conversion rate as percentage (0-100)

        Formula:
            Conversion Rate = (upgrades / signups) * 100
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            signups = self.analytics.count_events(
                "signup",
                start_date=start_date
            )

            upgrades = self.analytics.count_events(
                "upgrade",
                start_date=start_date
            )

            if signups == 0:
                return 0.0

            conversion_rate = (upgrades / signups) * 100

            return round(conversion_rate, 2)

        except Exception as e:
            logger.error(f"Error calculating conversion rate: {e}")
            return 0.0

    def get_cac_by_channel(self, days: int = 30) -> Dict[str, float]:
        """
        Calculate Customer Acquisition Cost by channel.

        Args:
            days: Period to calculate over (default 30 days)

        Returns:
            Dict mapping channel → CAC

        Example:
            {
                "product_hunt": 25.0,
                "google": 45.0,
                "facebook": 110.0,
                "referral": 0.0,
                "direct": 0.0
            }

        Note: Requires marketing spend data (hardcoded for Week 8, add tracking in Month 2)
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Get signups by source
            signups = self.analytics.get_events(
                event_name="signup",
                start_date=start_date,
                limit=10000
            )

            # Group by source
            signups_by_source = {}
            for signup in signups:
                source = signup.get("properties", {}).get("source", "direct")
                signups_by_source[source] = signups_by_source.get(source, 0) + 1

            # Marketing spend by channel (Week 8: hardcoded, Week 9+: track in DB)
            # These are estimates from FINANCIAL_MODEL.md
            marketing_spend = {
                "product_hunt": 500,    # $500 for Product Hunt launch
                "google": 1000,         # $1000/month Google Ads
                "facebook": 800,        # $800/month Facebook Ads
                "referral": 0,          # Referral program (no direct cost)
                "direct": 0,            # Direct traffic (no cost)
                "organic": 0            # Organic (SEO, no cost)
            }

            # Calculate CAC per channel
            cac_by_channel = {}
            for channel, spend in marketing_spend.items():
                users = signups_by_source.get(channel, 0)
                if users > 0:
                    cac_by_channel[channel] = round(spend / users, 2)
                else:
                    cac_by_channel[channel] = 0.0

            return cac_by_channel

        except Exception as e:
            logger.error(f"Error calculating CAC by channel: {e}")
            return {}

    def get_average_cac(self, days: int = 30) -> float:
        """
        Calculate overall average CAC.

        Args:
            days: Period to calculate over

        Returns:
            Average CAC in USD
        """
        try:
            cac_by_channel = self.get_cac_by_channel(days=days)

            if not cac_by_channel:
                return 0.0

            # Weighted average (based on signups per channel)
            start_date = datetime.utcnow() - timedelta(days=days)
            total_signups = self.analytics.count_events("signup", start_date=start_date)

            if total_signups == 0:
                return 0.0

            # Simplified: average of all CACs (more accurate would weight by channel usage)
            cacs = [cac for cac in cac_by_channel.values() if cac > 0]

            if not cacs:
                return 0.0

            return round(sum(cacs) / len(cacs), 2)

        except Exception as e:
            logger.error(f"Error calculating average CAC: {e}")
            return 0.0

    def get_ltv(self) -> float:
        """
        Calculate average Lifetime Value (LTV).

        Returns:
            Average LTV in USD

        Formula:
            LTV = ARPU / Churn Rate

        Note: Uses historical churn rate, requires at least 30 days of data
        """
        try:
            # Average Revenue Per User (ARPU)
            mrr = self.get_mrr()
            paying_users = self.get_paying_users_count()

            if paying_users == 0:
                return 0.0

            arpu = mrr / paying_users

            # Churn rate (as decimal, not percentage)
            churn_rate_pct = self.get_churn_rate(days=30)
            churn_rate = churn_rate_pct / 100

            if churn_rate == 0:
                # No churn yet, use industry average of 5%
                churn_rate = 0.05
                logger.info("Using default churn rate (5%) for LTV calculation")

            # LTV formula
            ltv = arpu / churn_rate

            return round(ltv, 2)

        except Exception as e:
            logger.error(f"Error calculating LTV: {e}")
            return 0.0

    def get_ltv_cac_ratio(self) -> float:
        """
        Calculate LTV/CAC ratio.

        Returns:
            LTV/CAC ratio

        Interpretation:
            - > 3:1 = Healthy (good unit economics)
            - 1-3:1 = Acceptable (can improve)
            - < 1:1 = Unsustainable (losing money per customer)

        Target: 27:1 (from FINANCIAL_MODEL.md)
        """
        try:
            ltv = self.get_ltv()
            cac = self.get_average_cac(days=30)

            if cac == 0:
                return 0.0

            ratio = ltv / cac

            return round(ratio, 1)

        except Exception as e:
            logger.error(f"Error calculating LTV/CAC ratio: {e}")
            return 0.0

    def get_month1_progress(self) -> Dict[str, Any]:
        """
        Track progress toward Month 1 targets.

        From FINANCIAL_MODEL.md:
        - Target: 50 paying users
        - Target: $7,500 MRR
        - Target: 55% conversion rate
        - Target: <10% churn

        Returns:
            Dict with current values and targets
        """
        try:
            current_users = self.get_paying_users_count()
            current_mrr = self.get_mrr()
            conversion_rate = self.get_conversion_rate(days=30)
            churn_rate = self.get_churn_rate(days=30)

            return {
                "paying_users": {
                    "current": current_users,
                    "target": 50,
                    "percentage": round((current_users / 50) * 100, 1)
                },
                "mrr": {
                    "current": current_mrr,
                    "target": 7500,
                    "percentage": round((current_mrr / 7500) * 100, 1)
                },
                "conversion_rate": {
                    "current": conversion_rate,
                    "target": 55.0,
                    "met": conversion_rate >= 55.0
                },
                "churn_rate": {
                    "current": churn_rate,
                    "target": 10.0,  # Below 10% is target
                    "met": churn_rate < 10.0
                }
            }

        except Exception as e:
            logger.error(f"Error calculating Month 1 progress: {e}")
            return {}

    def get_usage_metrics(self, days: int = 30) -> Dict[str, int]:
        """
        Get product usage metrics.

        Args:
            days: Period to analyze

        Returns:
            Dict with usage counts
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            return {
                "campaigns_generated": self.analytics.count_events(
                    "campaign_generated",
                    start_date=start_date
                ),
                "blogs_generated": self.analytics.count_events(
                    "blog_generated",
                    start_date=start_date
                ),
                "copy_variations_generated": self.analytics.count_events(
                    "copy_variations_generated",
                    start_date=start_date
                ),
                "total_content_generated": (
                    self.analytics.count_events("campaign_generated", start_date=start_date) +
                    self.analytics.count_events("blog_generated", start_date=start_date) +
                    self.analytics.count_events("copy_variations_generated", start_date=start_date)
                )
            }

        except Exception as e:
            logger.error(f"Error calculating usage metrics: {e}")
            return {}

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get complete dashboard summary.

        Returns:
            Dict with all key metrics
        """
        try:
            return {
                "revenue": {
                    "mrr": self.get_mrr(),
                    "revenue_by_tier": self.get_revenue_by_tier()
                },
                "users": {
                    "total": self.get_total_users_count(),
                    "paying": self.get_paying_users_count(),
                    "free": self.get_total_users_count() - self.get_paying_users_count()
                },
                "metrics": {
                    "conversion_rate": self.get_conversion_rate(days=30),
                    "churn_rate": self.get_churn_rate(days=30),
                    "cac": self.get_average_cac(days=30),
                    "ltv": self.get_ltv(),
                    "ltv_cac_ratio": self.get_ltv_cac_ratio()
                },
                "usage": self.get_usage_metrics(days=30),
                "month1_progress": self.get_month1_progress()
            }

        except Exception as e:
            logger.error(f"Error generating dashboard summary: {e}")
            return {}


# Global singleton
_business_metrics: Optional[BusinessMetrics] = None


def get_business_metrics() -> BusinessMetrics:
    """Get or create business metrics singleton."""
    global _business_metrics
    if _business_metrics is None:
        _business_metrics = BusinessMetrics()
    return _business_metrics
