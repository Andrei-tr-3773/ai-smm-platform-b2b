"""User model for authentication and multi-tenancy."""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """User model for authentication."""

    name: str
    email: str
    password_hash: str
    workspace_id: str
    role: str = "owner"  # owner, admin, member

    # Optional fields
    id: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None

    # OAuth
    google_id: Optional[str] = None
    linkedin_id: Optional[str] = None

    # Email verification
    email_verified: bool = False
    verification_token: Optional[str] = None

    # Security
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def is_owner(self) -> bool:
        """Check if user is workspace owner."""
        return self.role == "owner"

    def is_admin(self) -> bool:
        """Check if user is admin or owner."""
        return self.role in ["owner", "admin"]

    def can_manage_team(self) -> bool:
        """Check if user can manage team members."""
        return self.is_owner()

    def can_edit_workspace(self) -> bool:
        """Check if user can edit workspace settings."""
        return self.is_admin()
