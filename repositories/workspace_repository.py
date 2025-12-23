"""Workspace repository for CRUD operations."""
from typing import Optional
from models.workspace import Workspace
from utils.mongodb_utils import get_mongo_client
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WorkspaceRepository:
    """Repository for workspace CRUD operations."""

    def __init__(self):
        client = get_mongo_client()
        db = client.get_database("marketing_db")
        self.collection = db.get_collection("workspaces")

        # Create indices for performance
        self._ensure_indices()

    def _ensure_indices(self):
        """Ensure database indices exist."""
        try:
            # Index on owner_email
            self.collection.create_index("owner_email")
            # Index on stripe_customer_id for webhooks
            self.collection.create_index("stripe_customer_id", sparse=True)
        except Exception as e:
            logger.warning(f"Failed to create indices: {e}")

    def create_workspace(self, workspace: Workspace) -> str:
        """Create new workspace."""
        workspace_dict = {
            "name": workspace.name,
            "plan_tier": workspace.plan_tier,
            "owner_email": workspace.owner_email,
            "campaigns_this_month": workspace.campaigns_this_month,
            "custom_templates_count": workspace.custom_templates_count,
            "team_member_ids": workspace.team_member_ids,
            "logo_url": workspace.logo_url,
            "primary_color": workspace.primary_color,
            "stripe_customer_id": workspace.stripe_customer_id,
            "stripe_subscription_id": workspace.stripe_subscription_id,
            "subscription_status": workspace.subscription_status,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        try:
            result = self.collection.insert_one(workspace_dict)
            logger.info(f"Workspace created: {workspace.name}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create workspace: {e}")
            raise

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID."""
        try:
            doc = self.collection.find_one({"_id": ObjectId(workspace_id)})

            if not doc:
                return None

            return self._doc_to_workspace(doc)
        except Exception as e:
            logger.error(f"Failed to get workspace: {e}")
            return None

    def get_workspace_by_owner_email(self, email: str) -> Optional[Workspace]:
        """Get workspace by owner email."""
        try:
            doc = self.collection.find_one({"owner_email": email})

            if not doc:
                return None

            return self._doc_to_workspace(doc)
        except Exception as e:
            logger.error(f"Failed to get workspace by owner: {e}")
            return None

    def update_workspace(self, workspace_id: str, workspace: Workspace):
        """Update workspace."""
        try:
            self.collection.update_one(
                {"_id": ObjectId(workspace_id)},
                {"$set": {
                    "name": workspace.name,
                    "plan_tier": workspace.plan_tier,
                    "logo_url": workspace.logo_url,
                    "primary_color": workspace.primary_color,
                    "stripe_customer_id": workspace.stripe_customer_id,
                    "stripe_subscription_id": workspace.stripe_subscription_id,
                    "subscription_status": workspace.subscription_status,
                    "updated_at": datetime.utcnow()
                }}
            )
            logger.info(f"Workspace updated: {workspace_id}")
        except Exception as e:
            logger.error(f"Failed to update workspace: {e}")
            raise

    def increment_campaign_count(self, workspace_id: str):
        """Increment monthly campaign count."""
        try:
            self.collection.update_one(
                {"_id": ObjectId(workspace_id)},
                {
                    "$inc": {"campaigns_this_month": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            logger.debug(f"Campaign count incremented for workspace: {workspace_id}")
        except Exception as e:
            logger.error(f"Failed to increment campaign count: {e}")
            raise

    def increment_template_count(self, workspace_id: str):
        """Increment custom template count."""
        try:
            self.collection.update_one(
                {"_id": ObjectId(workspace_id)},
                {
                    "$inc": {"custom_templates_count": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            logger.debug(f"Template count incremented for workspace: {workspace_id}")
        except Exception as e:
            logger.error(f"Failed to increment template count: {e}")
            raise

    def reset_monthly_limits(self, workspace_id: str):
        """Reset monthly usage (run via cron on 1st of month)."""
        try:
            self.collection.update_one(
                {"_id": ObjectId(workspace_id)},
                {
                    "$set": {
                        "campaigns_this_month": 0,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            logger.info(f"Monthly limits reset for workspace: {workspace_id}")
        except Exception as e:
            logger.error(f"Failed to reset monthly limits: {e}")
            raise

    def add_team_member(self, workspace_id: str, user_id: str):
        """Add team member to workspace."""
        try:
            self.collection.update_one(
                {"_id": ObjectId(workspace_id)},
                {
                    "$addToSet": {"team_member_ids": user_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            logger.info(f"Team member added to workspace: {workspace_id}")
        except Exception as e:
            logger.error(f"Failed to add team member: {e}")
            raise

    def remove_team_member(self, workspace_id: str, user_id: str):
        """Remove team member from workspace."""
        try:
            self.collection.update_one(
                {"_id": ObjectId(workspace_id)},
                {
                    "$pull": {"team_member_ids": user_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            logger.info(f"Team member removed from workspace: {workspace_id}")
        except Exception as e:
            logger.error(f"Failed to remove team member: {e}")
            raise

    def upgrade_plan(self, workspace_id: str, new_tier: str, stripe_subscription_id: str = None):
        """Upgrade workspace plan."""
        try:
            update_fields = {
                "plan_tier": new_tier,
                "subscription_status": "active" if new_tier != "free" else "free",
                "updated_at": datetime.utcnow()
            }

            if stripe_subscription_id:
                update_fields["stripe_subscription_id"] = stripe_subscription_id

            self.collection.update_one(
                {"_id": ObjectId(workspace_id)},
                {"$set": update_fields}
            )
            logger.info(f"Workspace plan upgraded: {workspace_id} -> {new_tier}")
        except Exception as e:
            logger.error(f"Failed to upgrade plan: {e}")
            raise

    def delete_workspace(self, workspace_id: str):
        """Delete workspace by ID."""
        try:
            self.collection.delete_one({"_id": ObjectId(workspace_id)})
            logger.info(f"Workspace deleted: {workspace_id}")
        except Exception as e:
            logger.error(f"Failed to delete workspace: {e}")
            raise

    def _doc_to_workspace(self, doc: dict) -> Workspace:
        """Convert MongoDB document to Workspace object."""
        return Workspace(
            id=str(doc["_id"]),
            name=doc["name"],
            plan_tier=doc.get("plan_tier", "free"),
            owner_email=doc.get("owner_email", ""),
            campaigns_this_month=doc.get("campaigns_this_month", 0),
            custom_templates_count=doc.get("custom_templates_count", 0),
            team_member_ids=doc.get("team_member_ids", []),
            logo_url=doc.get("logo_url"),
            primary_color=doc.get("primary_color"),
            stripe_customer_id=doc.get("stripe_customer_id"),
            stripe_subscription_id=doc.get("stripe_subscription_id"),
            subscription_status=doc.get("subscription_status", "free"),
            created_at=doc.get("created_at", datetime.utcnow()),
            updated_at=doc.get("updated_at", datetime.utcnow())
        )
