"""
ROI Calculator - Calculate return on investment for AI SMM Platform.

Week 8: Task 8.5.1 - Help users (especially Jessica persona) justify subscription cost.

Calculates:
- Time saved (vs manual content creation)
- Cost savings (vs agencies/freelancers)
- Total value generated
- ROI percentage

Use case: Marketing Manager needs to show CEO that $199/month subscription
saves $2,000+/month in agency costs + 15 hours/week.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from utils.mongodb_utils import get_mongo_client
from utils.analytics_tracker import get_analytics_tracker
import logging

logger = logging.getLogger(__name__)


# Industry benchmarks (from market research)
BENCHMARKS = {
    # Time benchmarks (hours)
    "time_manual_campaign": 2.0,        # Manual campaign creation: 2 hours
    "time_ai_campaign": 0.25,           # AI campaign creation: 15 minutes
    "time_manual_blog": 4.0,            # Manual blog writing: 4 hours
    "time_ai_blog": 0.5,                # AI blog writing: 30 minutes
    "time_manual_copy": 1.5,            # Manual copy variations: 1.5 hours
    "time_ai_copy": 0.17,               # AI copy variations: 10 minutes

    # Cost benchmarks (USD)
    "cost_agency_campaign": 200,        # Agency per campaign: $200
    "cost_freelance_campaign": 100,     # Freelancer per campaign: $100
    "cost_agency_blog": 400,            # Agency blog post: $400
    "cost_freelance_blog": 150,         # Freelancer blog post: $150
    "cost_agency_copy": 150,            # Agency copy variations: $150
    "cost_freelance_copy": 75,          # Freelancer copy variations: $75

    # Hourly rates (USD)
    "hourly_rate_marketing_manager": 50,  # Marketing Manager: $50/hour
    "hourly_rate_freelancer": 40,         # Freelancer: $40/hour
    "hourly_rate_agency": 100,            # Agency: $100/hour

    # Multipliers
    "overhead_multiplier": 1.3,         # 30% overhead on internal time
}


class ROICalculator:
    """Calculate ROI for AI SMM Platform usage."""

    def __init__(self):
        """Initialize ROI calculator."""
        self.db = get_mongo_client()
        self.analytics = get_analytics_tracker()

    def calculate_user_roi(
        self,
        user_id: str,
        workspace_id: str,
        plan_tier: str,
        days: int = 30,
        hourly_rate: Optional[float] = None,
        comparison: str = "agency"  # "agency", "freelancer", or "manual"
    ) -> Dict[str, Any]:
        """
        Calculate ROI for a user over a period.

        Args:
            user_id: User ID
            workspace_id: Workspace ID
            plan_tier: Plan tier (for pricing)
            days: Period to calculate (default 30 days)
            hourly_rate: User's hourly rate (defaults to Marketing Manager rate)
            comparison: What to compare against ("agency", "freelancer", "manual")

        Returns:
            Dict with ROI breakdown
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Get usage data
            usage = self._get_usage_data(user_id, workspace_id, start_date)

            # Calculate time saved
            time_saved = self._calculate_time_saved(usage)

            # Calculate cost savings
            cost_savings = self._calculate_cost_savings(usage, comparison)

            # Calculate total value
            if hourly_rate is None:
                hourly_rate = BENCHMARKS["hourly_rate_marketing_manager"]

            time_value = time_saved["total_hours"] * hourly_rate

            # Apply overhead multiplier (internal time has overhead costs)
            if comparison == "manual":
                time_value *= BENCHMARKS["overhead_multiplier"]

            total_value = time_value + cost_savings["total_saved"]

            # Get subscription cost
            subscription_cost = self._get_subscription_cost(plan_tier, days)

            # Calculate ROI
            if subscription_cost > 0:
                roi_percentage = ((total_value - subscription_cost) / subscription_cost) * 100
            else:
                roi_percentage = 0

            return {
                "period_days": days,
                "usage": usage,
                "time_saved": time_saved,
                "cost_savings": cost_savings,
                "value": {
                    "time_value": round(time_value, 2),
                    "cost_savings": round(cost_savings["total_saved"], 2),
                    "total_value": round(total_value, 2)
                },
                "costs": {
                    "subscription_cost": subscription_cost,
                    "alternative_cost": round(time_value + cost_savings["total_alternative_cost"], 2)
                },
                "roi": {
                    "percentage": round(roi_percentage, 1),
                    "multiplier": round(total_value / subscription_cost, 1) if subscription_cost > 0 else 0,
                    "net_savings": round(total_value - subscription_cost, 2)
                },
                "comparison": comparison,
                "hourly_rate": hourly_rate
            }

        except Exception as e:
            logger.error(f"Error calculating ROI: {e}")
            return {}

    def _get_usage_data(
        self,
        user_id: str,
        workspace_id: str,
        start_date: datetime
    ) -> Dict[str, int]:
        """Get usage counts for a user."""
        return {
            "campaigns": self.analytics.count_events(
                "campaign_generated",
                start_date=start_date,
                user_id=user_id
            ),
            "blogs": self.analytics.count_events(
                "blog_generated",
                start_date=start_date,
                user_id=user_id
            ),
            "copy_variations": self.analytics.count_events(
                "copy_variations_generated",
                start_date=start_date,
                user_id=user_id
            )
        }

    def _calculate_time_saved(self, usage: Dict[str, int]) -> Dict[str, Any]:
        """Calculate time saved using AI vs manual."""
        # Time saved per content type
        campaign_time_saved = usage["campaigns"] * (
            BENCHMARKS["time_manual_campaign"] - BENCHMARKS["time_ai_campaign"]
        )

        blog_time_saved = usage["blogs"] * (
            BENCHMARKS["time_manual_blog"] - BENCHMARKS["time_ai_blog"]
        )

        copy_time_saved = usage["copy_variations"] * (
            BENCHMARKS["time_manual_copy"] - BENCHMARKS["time_ai_copy"]
        )

        total_hours = campaign_time_saved + blog_time_saved + copy_time_saved

        return {
            "campaigns": round(campaign_time_saved, 2),
            "blogs": round(blog_time_saved, 2),
            "copy_variations": round(copy_time_saved, 2),
            "total_hours": round(total_hours, 2),
            "total_days": round(total_hours / 8, 1),  # Assuming 8-hour workday
            "hours_per_week": round(total_hours / 4.3, 1)  # Average weeks in month
        }

    def _calculate_cost_savings(
        self,
        usage: Dict[str, int],
        comparison: str
    ) -> Dict[str, Any]:
        """Calculate cost savings vs alternative (agency or freelancer)."""
        if comparison == "agency":
            campaign_cost = BENCHMARKS["cost_agency_campaign"]
            blog_cost = BENCHMARKS["cost_agency_blog"]
            copy_cost = BENCHMARKS["cost_agency_copy"]
        elif comparison == "freelancer":
            campaign_cost = BENCHMARKS["cost_freelance_campaign"]
            blog_cost = BENCHMARKS["cost_freelance_blog"]
            copy_cost = BENCHMARKS["cost_freelance_copy"]
        else:  # manual (no external cost, only time)
            return {
                "campaigns": 0,
                "blogs": 0,
                "copy_variations": 0,
                "total_saved": 0,
                "total_alternative_cost": 0
            }

        campaigns_saved = usage["campaigns"] * campaign_cost
        blogs_saved = usage["blogs"] * blog_cost
        copy_saved = usage["copy_variations"] * copy_cost

        total_saved = campaigns_saved + blogs_saved + copy_saved

        return {
            "campaigns": round(campaigns_saved, 2),
            "blogs": round(blogs_saved, 2),
            "copy_variations": round(copy_saved, 2),
            "total_saved": round(total_saved, 2),
            "total_alternative_cost": round(total_saved, 2)
        }

    def _get_subscription_cost(self, plan_tier: str, days: int) -> float:
        """Get subscription cost for period."""
        monthly_prices = {
            "free": 0,
            "starter": 49,
            "professional": 99,
            "team": 199,
            "agency": 499,
            "enterprise": 999
        }

        monthly_cost = monthly_prices.get(plan_tier, 0)

        # Prorate for period
        return round((monthly_cost / 30) * days, 2)

    def get_roi_projection(
        self,
        plan_tier: str,
        campaigns_per_month: int,
        blogs_per_month: int,
        copy_per_month: int,
        hourly_rate: Optional[float] = None,
        comparison: str = "agency"
    ) -> Dict[str, Any]:
        """
        Project ROI for future usage (for pricing page).

        Args:
            plan_tier: Plan tier to project
            campaigns_per_month: Expected campaigns per month
            blogs_per_month: Expected blogs per month
            copy_per_month: Expected copy variations per month
            hourly_rate: User's hourly rate
            comparison: Comparison type

        Returns:
            Projected ROI breakdown
        """
        try:
            # Simulate usage
            usage = {
                "campaigns": campaigns_per_month,
                "blogs": blogs_per_month,
                "copy_variations": copy_per_month
            }

            # Calculate time saved
            time_saved = self._calculate_time_saved(usage)

            # Calculate cost savings
            cost_savings = self._calculate_cost_savings(usage, comparison)

            # Calculate value
            if hourly_rate is None:
                hourly_rate = BENCHMARKS["hourly_rate_marketing_manager"]

            time_value = time_saved["total_hours"] * hourly_rate

            if comparison == "manual":
                time_value *= BENCHMARKS["overhead_multiplier"]

            total_value = time_value + cost_savings["total_saved"]

            # Get subscription cost (30 days)
            subscription_cost = self._get_subscription_cost(plan_tier, 30)

            # Calculate ROI
            if subscription_cost > 0:
                roi_percentage = ((total_value - subscription_cost) / subscription_cost) * 100
            else:
                roi_percentage = 0

            return {
                "plan_tier": plan_tier,
                "monthly_usage": usage,
                "time_saved": time_saved,
                "cost_savings": cost_savings,
                "value": {
                    "time_value": round(time_value, 2),
                    "cost_savings": round(cost_savings["total_saved"], 2),
                    "total_value": round(total_value, 2)
                },
                "costs": {
                    "subscription_cost": subscription_cost,
                    "alternative_cost": round(time_value + cost_savings["total_alternative_cost"], 2)
                },
                "roi": {
                    "percentage": round(roi_percentage, 1),
                    "multiplier": round(total_value / subscription_cost, 1) if subscription_cost > 0 else 0,
                    "net_savings": round(total_value - subscription_cost, 2)
                },
                "comparison": comparison,
                "hourly_rate": hourly_rate
            }

        except Exception as e:
            logger.error(f"Error projecting ROI: {e}")
            return {}

    def get_comparison_table(self, plan_tier: str, monthly_usage: Dict[str, int]) -> Dict[str, Any]:
        """
        Get comparison table: AI Platform vs Agency vs Freelancer vs Manual.

        Args:
            plan_tier: Plan tier
            monthly_usage: Expected monthly usage

        Returns:
            Comparison data
        """
        try:
            comparisons = {}

            for comparison_type in ["manual", "freelancer", "agency"]:
                roi = self.get_roi_projection(
                    plan_tier=plan_tier,
                    campaigns_per_month=monthly_usage.get("campaigns", 0),
                    blogs_per_month=monthly_usage.get("blogs", 0),
                    copy_per_month=monthly_usage.get("copy_variations", 0),
                    comparison=comparison_type
                )

                comparisons[comparison_type] = {
                    "cost": roi["costs"]["alternative_cost"],
                    "time_hours": roi["time_saved"]["total_hours"],
                    "savings": roi["value"]["total_value"],
                    "roi_multiplier": roi["roi"]["multiplier"]
                }

            # Add AI platform stats
            subscription_cost = self._get_subscription_cost(plan_tier, 30)
            time_saved = self._calculate_time_saved(monthly_usage)

            comparisons["ai_platform"] = {
                "cost": subscription_cost,
                "time_hours": time_saved["total_hours"],  # Time using AI
                "savings": 0,  # Baseline (comparing to itself)
                "roi_multiplier": 1.0
            }

            return comparisons

        except Exception as e:
            logger.error(f"Error creating comparison table: {e}")
            return {}


# Global singleton
_roi_calculator: Optional[ROICalculator] = None


def get_roi_calculator() -> ROICalculator:
    """Get or create ROI calculator singleton."""
    global _roi_calculator
    if _roi_calculator is None:
        _roi_calculator = ROICalculator()
    return _roi_calculator
