# template_repository.py
"""
Template Repository for managing content templates in MongoDB.

Handles CRUD operations for both user-created and AI-generated templates.
"""
from pymongo import MongoClient
from datetime import datetime
from typing import Dict, List, Optional
import logging
import os
from dotenv import load_dotenv

load_dotenv(override=True)
logger = logging.getLogger(__name__)


class TemplateRepository:
    """Repository for managing content templates in MongoDB."""

    def __init__(self, connection_string: str = None):
        """
        Initialize template repository.

        Args:
            connection_string: MongoDB connection string (defaults to env var)
        """
        if connection_string is None:
            connection_string = os.getenv("CONNECTION_STRING_MONGO")

        self.client = MongoClient(connection_string)
        self.db = self.client.get_database()
        self.templates = self.db.content_templates
        logger.info("TemplateRepository initialized")

    def save_ai_generated_template(
        self,
        template_name: str,
        description: str,
        liquid_template: str,
        field_schema: List[Dict],
        parsed_intent: Dict,
        workspace_id: str = "default"
    ) -> str:
        """
        Save AI-generated template to database.

        Args:
            template_name: Unique name for the template
            description: Plain English description used to generate template
            liquid_template: Generated Liquid HTML template
            field_schema: List of field definitions
            parsed_intent: AI-parsed intent (industry, content_type, etc.)
            workspace_id: Workspace identifier (for future multi-tenancy)

        Returns:
            str: Inserted template ID

        Raises:
            ValueError: If template name already exists
        """
        try:
            # Check if template name already exists
            existing = self.templates.find_one({"name": template_name, "workspace_id": workspace_id})
            if existing:
                raise ValueError(f"Template '{template_name}' already exists in workspace '{workspace_id}'")

            # Prepare template document
            template_doc = {
                "workspace_id": workspace_id,
                "name": template_name,
                "description": description,
                "liquid_template": liquid_template,
                "items": field_schema,  # Use 'items' for compatibility with existing code
                "example_query": description,  # Use description as example query
                "metadata": {
                    "generated_by": "ai",
                    "model": "gpt-4o-mini",
                    "generated_at": datetime.now(),
                    "parsed_intent": parsed_intent,
                    "is_ai_generated": True,
                    "user_modified": False
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "usage_count": 0,
                "tags": [parsed_intent.get('industry', 'generic'), parsed_intent.get('content_type', 'custom')]
            }

            # Insert document
            result = self.templates.insert_one(template_doc)
            template_id = str(result.inserted_id)

            logger.info(f"✅ Saved AI template: '{template_name}' (id: {template_id})")
            return template_id

        except ValueError as e:
            logger.error(f"Template save failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving AI template: {e}")
            raise

    def update_template(
        self,
        template_name: str,
        liquid_template: str,
        field_schema: List[Dict] = None,
        workspace_id: str = "default"
    ) -> bool:
        """
        Update existing template (for Advanced Mode manual edits).

        Args:
            template_name: Name of template to update
            liquid_template: Updated Liquid template
            field_schema: Updated field schema (optional)
            workspace_id: Workspace identifier

        Returns:
            bool: True if updated successfully
        """
        try:
            update_doc = {
                "$set": {
                    "liquid_template": liquid_template,
                    "updated_at": datetime.now(),
                    "metadata.user_modified": True
                }
            }

            # Optionally update field schema
            if field_schema is not None:
                update_doc["$set"]["items"] = field_schema

            result = self.templates.update_one(
                {"name": template_name, "workspace_id": workspace_id},
                update_doc
            )

            if result.matched_count > 0:
                logger.info(f"✅ Updated template: '{template_name}'")
                return True
            else:
                logger.warning(f"Template '{template_name}' not found for update")
                return False

        except Exception as e:
            logger.error(f"Error updating template: {e}")
            return False

    def get_template_by_name(self, template_name: str, workspace_id: str = "default") -> Optional[Dict]:
        """
        Retrieve template by name.

        Args:
            template_name: Name of template to retrieve
            workspace_id: Workspace identifier

        Returns:
            Dict with template data or None if not found
        """
        try:
            template = self.templates.find_one({"name": template_name, "workspace_id": workspace_id})
            if template:
                logger.info(f"Retrieved template: '{template_name}'")
            return template
        except Exception as e:
            logger.error(f"Error retrieving template: {e}")
            return None

    def get_all_templates(self, workspace_id: str = "default", ai_generated_only: bool = False) -> List[Dict]:
        """
        Retrieve all templates for workspace.

        Args:
            workspace_id: Workspace identifier
            ai_generated_only: If True, only return AI-generated templates

        Returns:
            List of template documents
        """
        try:
            query = {"workspace_id": workspace_id}
            if ai_generated_only:
                query["metadata.is_ai_generated"] = True

            templates = list(self.templates.find(query).sort("created_at", -1))
            logger.info(f"Retrieved {len(templates)} templates from workspace '{workspace_id}'")
            return templates
        except Exception as e:
            logger.error(f"Error retrieving templates: {e}")
            return []

    def delete_template(self, template_name: str, workspace_id: str = "default") -> bool:
        """
        Delete template by name.

        Args:
            template_name: Name of template to delete
            workspace_id: Workspace identifier

        Returns:
            bool: True if deleted successfully
        """
        try:
            result = self.templates.delete_one({"name": template_name, "workspace_id": workspace_id})

            if result.deleted_count > 0:
                logger.info(f"✅ Deleted template: '{template_name}'")
                return True
            else:
                logger.warning(f"Template '{template_name}' not found for deletion")
                return False

        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            return False

    def increment_usage_count(self, template_name: str, workspace_id: str = "default") -> bool:
        """
        Increment usage counter when template is used in a campaign.

        Args:
            template_name: Name of template
            workspace_id: Workspace identifier

        Returns:
            bool: True if updated successfully
        """
        try:
            result = self.templates.update_one(
                {"name": template_name, "workspace_id": workspace_id},
                {"$inc": {"usage_count": 1}}
            )

            return result.matched_count > 0

        except Exception as e:
            logger.error(f"Error incrementing usage count: {e}")
            return False

    def get_template_stats(self, workspace_id: str = "default") -> Dict:
        """
        Get statistics about templates in workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            Dict with template statistics
        """
        try:
            total = self.templates.count_documents({"workspace_id": workspace_id})
            ai_generated = self.templates.count_documents({
                "workspace_id": workspace_id,
                "metadata.is_ai_generated": True
            })
            user_modified = self.templates.count_documents({
                "workspace_id": workspace_id,
                "metadata.user_modified": True
            })

            # Get most used template
            most_used = list(self.templates.find(
                {"workspace_id": workspace_id}
            ).sort("usage_count", -1).limit(1))

            stats = {
                "total_templates": total,
                "ai_generated": ai_generated,
                "user_modified": user_modified,
                "manual_created": total - ai_generated,
                "most_used_template": most_used[0]["name"] if most_used else None,
                "most_used_count": most_used[0]["usage_count"] if most_used else 0
            }

            logger.info(f"Template stats for workspace '{workspace_id}': {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting template stats: {e}")
            return {
                "total_templates": 0,
                "ai_generated": 0,
                "user_modified": 0,
                "manual_created": 0,
                "most_used_template": None,
                "most_used_count": 0
            }
