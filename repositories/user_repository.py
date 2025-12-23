"""User repository for CRUD operations."""
from typing import Optional, List
from models.user import User
from utils.mongodb_utils import get_mongo_client
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user CRUD operations."""

    def __init__(self):
        client = get_mongo_client()
        db = client.get_database("marketing_db")
        self.collection = db.get_collection("users")

        # Create indices for performance
        self._ensure_indices()

    def _ensure_indices(self):
        """Ensure database indices exist."""
        try:
            # Unique index on email
            self.collection.create_index("email", unique=True)
            # Index on workspace_id for queries
            self.collection.create_index("workspace_id")
            # Index on google_id and linkedin_id for OAuth
            self.collection.create_index("google_id", sparse=True)
            self.collection.create_index("linkedin_id", sparse=True)
        except Exception as e:
            logger.warning(f"Failed to create indices: {e}")

    def create_user(self, user: User) -> str:
        """Create new user."""
        user_dict = {
            "name": user.name,
            "email": user.email,
            "password_hash": user.password_hash,
            "workspace_id": user.workspace_id,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "phone": user.phone,
            "google_id": user.google_id,
            "linkedin_id": user.linkedin_id,
            "email_verified": user.email_verified,
            "verification_token": user.verification_token,
            "last_login": user.last_login,
            "failed_login_attempts": user.failed_login_attempts,
            "locked_until": user.locked_until,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        try:
            result = self.collection.insert_one(user_dict)
            logger.info(f"User created: {user.email}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            doc = self.collection.find_one({"_id": ObjectId(user_id)})

            if not doc:
                return None

            return self._doc_to_user(doc)
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            doc = self.collection.find_one({"email": email})

            if not doc:
                return None

            return self._doc_to_user(doc)
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None

    def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID (for OAuth)."""
        try:
            doc = self.collection.find_one({"google_id": google_id})

            if not doc:
                return None

            return self._doc_to_user(doc)
        except Exception as e:
            logger.error(f"Failed to get user by Google ID: {e}")
            return None

    def get_user_by_linkedin_id(self, linkedin_id: str) -> Optional[User]:
        """Get user by LinkedIn ID (for OAuth)."""
        try:
            doc = self.collection.find_one({"linkedin_id": linkedin_id})

            if not doc:
                return None

            return self._doc_to_user(doc)
        except Exception as e:
            logger.error(f"Failed to get user by LinkedIn ID: {e}")
            return None

    def get_workspace_users(self, workspace_id: str) -> List[User]:
        """Get all users in a workspace."""
        try:
            docs = self.collection.find({"workspace_id": workspace_id})
            return [self._doc_to_user(doc) for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get workspace users: {e}")
            return []

    def update_user(self, user_id: str, updates: dict):
        """Update user fields."""
        try:
            updates["updated_at"] = datetime.utcnow()

            self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": updates}
            )
            logger.info(f"User updated: {user_id}")
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            raise

    def update_last_login(self, user_id: str):
        """Update last login timestamp."""
        self.update_user(user_id, {"last_login": datetime.utcnow()})

    def increment_failed_login(self, email: str):
        """Increment failed login attempts counter."""
        try:
            self.collection.update_one(
                {"email": email},
                {
                    "$inc": {"failed_login_attempts": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        except Exception as e:
            logger.error(f"Failed to increment failed login: {e}")

    def reset_failed_login(self, user_id: str):
        """Reset failed login attempts counter."""
        self.update_user(user_id, {"failed_login_attempts": 0})

    def delete_user(self, user_id: str):
        """Delete user by ID."""
        try:
            self.collection.delete_one({"_id": ObjectId(user_id)})
            logger.info(f"User deleted: {user_id}")
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            raise

    def _doc_to_user(self, doc: dict) -> User:
        """Convert MongoDB document to User object."""
        return User(
            id=str(doc["_id"]),
            name=doc["name"],
            email=doc["email"],
            password_hash=doc["password_hash"],
            workspace_id=doc["workspace_id"],
            role=doc.get("role", "owner"),
            avatar_url=doc.get("avatar_url"),
            phone=doc.get("phone"),
            google_id=doc.get("google_id"),
            linkedin_id=doc.get("linkedin_id"),
            email_verified=doc.get("email_verified", False),
            verification_token=doc.get("verification_token"),
            last_login=doc.get("last_login"),
            failed_login_attempts=doc.get("failed_login_attempts", 0),
            locked_until=doc.get("locked_until"),
            created_at=doc.get("created_at", datetime.utcnow()),
            updated_at=doc.get("updated_at", datetime.utcnow())
        )
