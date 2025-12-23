"""Workspace model for multi-tenancy."""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Workspace:
    """Workspace model for multi-tenancy."""

    name: str
    plan_tier: str = "free"  # free, starter, professional, team, agency, enterprise
    owner_email: str = ""

    # Usage tracking
    campaigns_this_month: int = 0
    custom_templates_count: int = 0

    # Team members
    team_member_ids: List[str] = field(default_factory=list)

    # Branding (for agencies)
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None

    # Stripe subscription
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    subscription_status: str = "free"  # free, active, canceled, past_due

    # Metadata
    id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def get_plan_limits(self):
        """Get limits based on plan tier."""
        plans = {
            "free": {
                "campaigns": 10,
                "custom_templates": 1,
                "team_members": 1,
                "languages": 3
            },
            "starter": {
                "campaigns": 50,
                "custom_templates": 3,
                "team_members": 1,
                "languages": 5
            },
            "professional": {
                "campaigns": 200,
                "custom_templates": 5,
                "team_members": 1,
                "languages": 15
            },
            "team": {
                "campaigns": -1,  # unlimited
                "custom_templates": 20,
                "team_members": 3,
                "languages": 15
            },
            "agency": {
                "campaigns": -1,
                "custom_templates": 50,
                "team_members": 10,
                "languages": 15
            },
            "enterprise": {
                "campaigns": -1,
                "custom_templates": -1,
                "team_members": -1,
                "languages": 15
            }
        }
        return plans.get(self.plan_tier, plans["free"])

    def can_create_campaign(self) -> bool:
        """Check if workspace can create more campaigns."""
        limits = self.get_plan_limits()
        if limits["campaigns"] == -1:
            return True
        return self.campaigns_this_month < limits["campaigns"]

    def can_create_template(self) -> bool:
        """Check if workspace can create more custom templates."""
        limits = self.get_plan_limits()
        if limits["custom_templates"] == -1:
            return True
        if limits["custom_templates"] == 0:
            return False
        return self.custom_templates_count < limits["custom_templates"]

    def can_add_team_member(self) -> bool:
        """Check if workspace can add more team members."""
        limits = self.get_plan_limits()
        if limits["team_members"] == -1:
            return True
        return len(self.team_member_ids) < limits["team_members"]

    def get_campaigns_remaining(self) -> int:
        """Get number of campaigns remaining this month."""
        limits = self.get_plan_limits()
        if limits["campaigns"] == -1:
            return -1  # unlimited
        return max(0, limits["campaigns"] - self.campaigns_this_month)

    def get_usage_percentage(self) -> float:
        """Get campaign usage percentage (0.0 to 1.0)."""
        limits = self.get_plan_limits()
        if limits["campaigns"] == -1:
            return 0.0  # unlimited
        if limits["campaigns"] == 0:
            return 1.0  # fully used
        return min(1.0, self.campaigns_this_month / limits["campaigns"])
