# Week 6: Monetization & User Authentication

**Duration:** 24 hours
**Priority:** CRITICAL (Revenue enablement)
**Business Impact:** Enable paid plans → $500+ MRR by Month 6
**ROI:** Essential for business sustainability

---

## 📊 Business Case

**Current State:**
- No user accounts (anonymous usage)
- No payment collection
- No usage limits enforcement
- Cannot scale to multiple users per business

**Target State:**
- User signup with email/password + OAuth
- Workspace per company/team
- Usage tracking and enforcement
- Pricing page with clear tiers
- Ready for Stripe integration (Week 7)

**Financial Impact:**
```
Investment: $2,400 (24 hours × $100/hr)
Month 6 Target: $500+ MRR (10 paying customers)
Month 12 Target: $4,000+ MRR (50 paying customers)
Break-even: Month 2 after launch
```

---

## 📅 Week 6 Tasks

### Task 6.1: User Authentication (8 hours)

**Goal:** Enable users to sign up, log in, and manage their accounts

**Files to Create/Modify:**
- `pages/02_Login.py` - Login page
- `pages/03_Signup.py` - Signup page
- `pages/04_Account.py` - Account settings
- `utils/auth.py` - Authentication utilities
- `models/user.py` - User model
- `repositories/user_repository.py` - User CRUD operations

**Features:**

**6.1.1 Email/Password Authentication (3 hours)**
```python
# utils/auth.py
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from models.user import User
from repositories.user_repository import UserRepository

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, email: str) -> str:
    """Create JWT token for user session."""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user() -> Optional[User]:
    """Get current logged-in user from session."""
    if 'auth_token' not in st.session_state:
        return None

    token_data = verify_jwt_token(st.session_state['auth_token'])
    if not token_data:
        return None

    repo = UserRepository()
    return repo.get_user_by_id(token_data['user_id'])

def require_auth():
    """Decorator to require authentication for a page."""
    user = get_current_user()
    if not user:
        st.error("🔒 Please log in to access this page")
        st.switch_page("pages/02_Login.py")
        st.stop()
    return user
```

**6.1.2 Login Page (2 hours)**
```python
# pages/02_Login.py
import streamlit as st
from utils.auth import verify_password, create_jwt_token
from repositories.user_repository import UserRepository

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

st.title("🔐 Login to AI SMM Platform")

# Login form
with st.form("login_form"):
    email = st.text_input("Email", placeholder="your@email.com")
    password = st.text_input("Password", type="password")

    submit = st.form_submit_button("Login", type="primary", use_container_width=True)

    if submit:
        if not email or not password:
            st.error("Please enter both email and password")
        else:
            # Verify credentials
            repo = UserRepository()
            user = repo.get_user_by_email(email)

            if user and verify_password(password, user.password_hash):
                # Create session
                token = create_jwt_token(str(user.id), user.email)
                st.session_state['auth_token'] = token
                st.session_state['user_id'] = str(user.id)
                st.session_state['workspace_id'] = user.workspace_id

                st.success(f"✅ Welcome back, {user.name}!")
                st.switch_page("Home.py")
            else:
                st.error("❌ Invalid email or password")

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    if st.button("📝 Create Account", use_container_width=True):
        st.switch_page("pages/03_Signup.py")

with col2:
    if st.button("🔑 Forgot Password?", use_container_width=True):
        st.info("Password reset coming soon!")

# OAuth (Google, LinkedIn) - Optional
st.markdown("---")
st.markdown("### Or sign in with:")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔵 Continue with Google", use_container_width=True):
        st.info("Google OAuth coming in Week 7")

with col2:
    if st.button("💼 Continue with LinkedIn", use_container_width=True):
        st.info("LinkedIn OAuth coming in Week 7")
```

**6.1.3 Signup Page (2 hours)**
```python
# pages/03_Signup.py
import streamlit as st
from utils.auth import hash_password, create_jwt_token
from repositories.user_repository import UserRepository
from repositories.workspace_repository import WorkspaceRepository
from models.user import User
from models.workspace import Workspace
import re

st.set_page_config(page_title="Sign Up", page_icon="📝", layout="centered")

st.title("📝 Create Your Account")

with st.form("signup_form"):
    name = st.text_input("Full Name", placeholder="John Smith")
    email = st.text_input("Email", placeholder="your@email.com")
    password = st.text_input("Password", type="password",
                            help="At least 8 characters, 1 uppercase, 1 number")
    password_confirm = st.text_input("Confirm Password", type="password")

    company_name = st.text_input("Company Name (optional)",
                                 placeholder="Your Business Name")

    agree_terms = st.checkbox("I agree to Terms of Service and Privacy Policy")

    submit = st.form_submit_button("Create Account", type="primary",
                                   use_container_width=True)

    if submit:
        # Validation
        errors = []

        if not name or not email or not password:
            errors.append("Please fill in all required fields")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Invalid email format")

        if len(password) < 8:
            errors.append("Password must be at least 8 characters")

        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least 1 uppercase letter")

        if not re.search(r"\d", password):
            errors.append("Password must contain at least 1 number")

        if password != password_confirm:
            errors.append("Passwords do not match")

        if not agree_terms:
            errors.append("You must agree to Terms of Service")

        # Check if email exists
        user_repo = UserRepository()
        if user_repo.get_user_by_email(email):
            errors.append("Email already registered")

        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Create workspace first
            workspace_repo = WorkspaceRepository()
            workspace = Workspace(
                name=company_name or f"{name}'s Workspace",
                plan_tier="free",
                owner_email=email
            )
            workspace_id = workspace_repo.create_workspace(workspace)

            # Create user
            user = User(
                name=name,
                email=email,
                password_hash=hash_password(password),
                workspace_id=workspace_id,
                role="owner"
            )
            user_id = user_repo.create_user(user)

            # Create session
            token = create_jwt_token(str(user_id), email)
            st.session_state['auth_token'] = token
            st.session_state['user_id'] = str(user_id)
            st.session_state['workspace_id'] = workspace_id

            st.success(f"✅ Account created! Welcome, {name}!")
            st.balloons()

            # Redirect to Getting Started
            st.switch_page("pages/00_Getting_Started.py")

st.markdown("---")
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("Already have an account?")
with col2:
    if st.button("Login", use_container_width=True):
        st.switch_page("pages/02_Login.py")
```

**6.1.4 Session Management (1 hour)**
```python
# Add to Home.py and all protected pages
from utils.auth import get_current_user, require_auth

# At top of page
user = get_current_user()

if user:
    st.sidebar.markdown(f"👤 **{user.name}**")
    st.sidebar.markdown(f"📧 {user.email}")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        # Clear session
        st.session_state.clear()
        st.success("✅ Logged out successfully")
        st.switch_page("pages/02_Login.py")
else:
    st.sidebar.info("👋 Not logged in")
    if st.sidebar.button("🔐 Login", use_container_width=True):
        st.switch_page("pages/02_Login.py")
```

**Deliverables (Task 6.1):**
- ✅ Email/password signup working
- ✅ Login/logout functional
- ✅ Password hashing (bcrypt)
- ✅ JWT session management
- ✅ Protected pages (require auth)
- ✅ User profile in sidebar
- ⏳ OAuth (Google, LinkedIn) - deferred to Week 7
- ⏳ Email verification - deferred to Week 7
- ⏳ Password reset - deferred to Week 7

---

### Task 6.2: Workspace Management (6 hours)

**Goal:** Enable multi-user workspaces with team collaboration

**Files to Create/Modify:**
- `models/workspace.py` - Workspace model
- `repositories/workspace_repository.py` - Workspace CRUD
- `pages/05_Workspace_Settings.py` - Workspace settings page

**6.2.1 Workspace Model (1 hour)**
```python
# models/workspace.py
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Workspace:
    """Workspace model for multi-tenancy."""

    name: str
    plan_tier: str = "free"  # free, professional, business, agency
    owner_email: str = ""

    # Usage tracking
    campaigns_this_month: int = 0
    custom_templates_count: int = 0

    # Limits based on plan
    campaigns_limit: int = 10  # free tier
    custom_templates_limit: int = 0  # free tier

    # Team members
    team_member_ids: List[str] = field(default_factory=list)
    max_team_members: int = 1  # free tier

    # Branding (for agencies)
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def get_plan_limits(self):
        """Get limits based on plan tier."""
        plans = {
            "free": {
                "campaigns": 10,
                "custom_templates": 0,
                "team_members": 1,
                "languages": 3
            },
            "professional": {
                "campaigns": 100,
                "custom_templates": 5,
                "team_members": 1,
                "languages": 15
            },
            "business": {
                "campaigns": -1,  # unlimited
                "custom_templates": -1,
                "team_members": 3,
                "languages": 15
            },
            "agency": {
                "campaigns": -1,
                "custom_templates": -1,
                "team_members": 10,
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
        return self.custom_templates_count < limits["custom_templates"]
```

**6.2.2 Workspace Settings Page (3 hours)**
```python
# pages/05_Workspace_Settings.py
import streamlit as st
from utils.auth import require_auth
from repositories.workspace_repository import WorkspaceRepository

st.set_page_config(page_title="Workspace Settings", page_icon="⚙️", layout="wide")

# Require authentication
user = require_auth()

st.title("⚙️ Workspace Settings")

# Get workspace
workspace_repo = WorkspaceRepository()
workspace = workspace_repo.get_workspace(user.workspace_id)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["General", "Usage", "Team", "Billing"])

# Tab 1: General Settings
with tab1:
    st.header("General Settings")

    with st.form("workspace_settings"):
        workspace_name = st.text_input("Workspace Name", value=workspace.name)

        # Branding (Agency plan only)
        if workspace.plan_tier == "agency":
            st.subheader("🎨 Branding")
            logo_url = st.text_input("Logo URL (optional)", value=workspace.logo_url or "")
            primary_color = st.color_picker("Primary Color", value=workspace.primary_color or "#1f77b4")

        if st.form_submit_button("Save Changes", type="primary"):
            workspace.name = workspace_name
            if workspace.plan_tier == "agency":
                workspace.logo_url = logo_url
                workspace.primary_color = primary_color

            workspace_repo.update_workspace(user.workspace_id, workspace)
            st.success("✅ Workspace settings saved!")

# Tab 2: Usage & Limits
with tab2:
    st.header("📊 Usage & Limits")

    limits = workspace.get_plan_limits()

    # Current plan
    st.subheader(f"Current Plan: **{workspace.plan_tier.upper()}**")

    # Campaigns usage
    st.markdown("### Campaigns This Month")
    if limits["campaigns"] == -1:
        st.metric("Campaigns Created", workspace.campaigns_this_month, "Unlimited")
    else:
        progress = workspace.campaigns_this_month / limits["campaigns"]
        st.metric("Campaigns Created",
                 f"{workspace.campaigns_this_month} / {limits['campaigns']}")
        st.progress(progress)

        remaining = limits["campaigns"] - workspace.campaigns_this_month
        if remaining <= 2:
            st.warning(f"⚠️ Only {remaining} campaigns remaining this month")

    # Custom templates usage
    st.markdown("### Custom Templates")
    if limits["custom_templates"] == -1:
        st.metric("Custom Templates", workspace.custom_templates_count, "Unlimited")
    else:
        if limits["custom_templates"] == 0:
            st.info("🔒 Custom templates not available on Free plan. Upgrade to Professional!")
        else:
            st.metric("Custom Templates",
                     f"{workspace.custom_templates_count} / {limits['custom_templates']}")

    # Team members usage
    st.markdown("### Team Members")
    team_count = len(workspace.team_member_ids)
    st.metric("Team Members", f"{team_count} / {limits['team_members']}")

    # Upgrade CTA
    if workspace.plan_tier == "free":
        st.markdown("---")
        st.info("💎 Upgrade to unlock more features!")
        if st.button("View Plans", type="primary"):
            st.switch_page("pages/06_Pricing.py")

# Tab 3: Team Management
with tab3:
    st.header("👥 Team Management")

    if user.role != "owner":
        st.warning("⚠️ Only workspace owner can manage team members")
    else:
        # Current team
        st.subheader("Current Team Members")

        from repositories.user_repository import UserRepository
        user_repo = UserRepository()

        team_members = user_repo.get_workspace_users(user.workspace_id)

        for member in team_members:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{member.name}** ({member.email})")
            with col2:
                st.markdown(f"Role: {member.role}")
            with col3:
                if member.role != "owner":
                    if st.button("Remove", key=f"remove_{member.id}"):
                        # Remove member logic
                        st.success(f"✅ Removed {member.name}")

        # Invite new member
        st.markdown("---")
        st.subheader("Invite Team Member")

        if len(team_members) >= limits["team_members"]:
            st.warning(f"⚠️ Team limit reached ({limits['team_members']}). Upgrade to add more members.")
        else:
            with st.form("invite_member"):
                invite_email = st.text_input("Email")
                invite_role = st.selectbox("Role", ["member", "admin"])

                if st.form_submit_button("Send Invite"):
                    # TODO: Send email invite
                    st.success(f"✅ Invite sent to {invite_email}")

# Tab 4: Billing (placeholder)
with tab4:
    st.header("💳 Billing")

    st.subheader(f"Current Plan: **{workspace.plan_tier.upper()}**")

    if workspace.plan_tier == "free":
        st.info("You're on the Free plan. Upgrade to unlock premium features!")
        if st.button("Upgrade Now", type="primary"):
            st.switch_page("pages/06_Pricing.py")
    else:
        st.success(f"✅ Subscribed to {workspace.plan_tier.upper()} plan")

        # Placeholder for Stripe integration
        st.markdown("### Payment Method")
        st.info("💳 Stripe integration coming in Week 7")

        st.markdown("### Billing History")
        st.info("📄 Invoice history coming in Week 7")
```

**6.2.3 Workspace Repository (2 hours)**
```python
# repositories/workspace_repository.py
from typing import Optional
from models.workspace import Workspace
from utils.mongodb_utils import get_mongo_client
from bson import ObjectId
from datetime import datetime

class WorkspaceRepository:
    """Repository for workspace CRUD operations."""

    def __init__(self):
        client = get_mongo_client()
        db = client.get_database("marketing_db")
        self.collection = db.get_collection("workspaces")

    def create_workspace(self, workspace: Workspace) -> str:
        """Create new workspace."""
        workspace_dict = {
            "name": workspace.name,
            "plan_tier": workspace.plan_tier,
            "owner_email": workspace.owner_email,
            "campaigns_this_month": 0,
            "custom_templates_count": 0,
            "team_member_ids": [],
            "logo_url": workspace.logo_url,
            "primary_color": workspace.primary_color,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = self.collection.insert_one(workspace_dict)
        return str(result.inserted_id)

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID."""
        doc = self.collection.find_one({"_id": ObjectId(workspace_id)})

        if not doc:
            return None

        return Workspace(
            name=doc["name"],
            plan_tier=doc.get("plan_tier", "free"),
            owner_email=doc["owner_email"],
            campaigns_this_month=doc.get("campaigns_this_month", 0),
            custom_templates_count=doc.get("custom_templates_count", 0),
            team_member_ids=doc.get("team_member_ids", []),
            logo_url=doc.get("logo_url"),
            primary_color=doc.get("primary_color"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at")
        )

    def update_workspace(self, workspace_id: str, workspace: Workspace):
        """Update workspace."""
        self.collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$set": {
                "name": workspace.name,
                "logo_url": workspace.logo_url,
                "primary_color": workspace.primary_color,
                "updated_at": datetime.utcnow()
            }}
        )

    def increment_campaign_count(self, workspace_id: str):
        """Increment monthly campaign count."""
        self.collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$inc": {"campaigns_this_month": 1}}
        )

    def reset_monthly_limits(self, workspace_id: str):
        """Reset monthly usage (run via cron on 1st of month)."""
        self.collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$set": {"campaigns_this_month": 0}}
        )
```

**Deliverables (Task 6.2):**
- ✅ Workspace model with plan limits
- ✅ Workspace created on signup
- ✅ Workspace settings page
- ✅ Usage tracking (campaigns, templates)
- ✅ Team member management UI
- ⏳ Email invites - deferred to Week 7

---

### Task 6.3: Usage Tracking & Enforcement (6 hours)

**Goal:** Track and enforce usage limits based on plan tier

**6.3.1 Campaign Limit Enforcement (3 hours)**
```python
# Modify Home.py - Add usage check before generation

from utils.auth import get_current_user
from repositories.workspace_repository import WorkspaceRepository

# At top of Home.py
user = get_current_user()

if user:
    workspace_repo = WorkspaceRepository()
    workspace = workspace_repo.get_workspace(user.workspace_id)

    # Show usage in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Usage This Month")

    limits = workspace.get_plan_limits()

    if limits["campaigns"] == -1:
        st.sidebar.success(f"✅ {workspace.campaigns_this_month} campaigns (Unlimited)")
    else:
        remaining = limits["campaigns"] - workspace.campaigns_this_month
        st.sidebar.metric("Campaigns Remaining", remaining)

        progress = workspace.campaigns_this_month / limits["campaigns"]
        st.sidebar.progress(progress)

        if remaining <= 0:
            st.sidebar.error("⚠️ Limit reached!")
            st.sidebar.button("Upgrade Plan", type="primary")
        elif remaining <= 2:
            st.sidebar.warning(f"⚠️ Only {remaining} left")

# Before campaign generation
if st.button("Generate Content", type="primary"):
    if user and not workspace.can_create_campaign():
        st.error("❌ Monthly campaign limit reached!")
        st.info("💎 Upgrade to Professional plan for 100 campaigns/month or Business plan for unlimited.")

        if st.button("View Plans", type="primary"):
            st.switch_page("pages/06_Pricing.py")

        st.stop()

    # Generate campaign...
    # After successful generation:
    if user:
        workspace_repo.increment_campaign_count(user.workspace_id)
```

**6.3.2 Template Limit Enforcement (2 hours)**
```python
# Add to template creation flow (when implemented)

if st.button("Create Custom Template"):
    if user and not workspace.can_create_template():
        limits = workspace.get_plan_limits()

        if limits["custom_templates"] == 0:
            st.error("❌ Custom templates not available on Free plan")
            st.info("💎 Upgrade to Professional plan for 5 custom templates or Business plan for unlimited.")
        else:
            st.error(f"❌ Template limit reached ({limits['custom_templates']})")
            st.info("💎 Upgrade to Business plan for unlimited custom templates.")

        if st.button("View Plans", type="primary"):
            st.switch_page("pages/06_Pricing.py")

        st.stop()

    # Create template...
```

**6.3.3 Monthly Reset Cron Job (1 hour)**
```python
# utils/cron_jobs.py
from repositories.workspace_repository import WorkspaceRepository
from pymongo import MongoClient
import os

def reset_monthly_limits():
    """
    Reset monthly campaign counters for all workspaces.
    Run this on 1st of each month via cron.

    Cron setup:
    0 0 1 * * cd /path/to/project && python -c "from utils.cron_jobs import reset_monthly_limits; reset_monthly_limits()"
    """
    workspace_repo = WorkspaceRepository()

    # Get all workspaces
    client = MongoClient(os.getenv("CONNECTION_STRING_MONGO"))
    db = client.marketing_db
    workspaces = db.workspaces.find({})

    count = 0
    for ws in workspaces:
        workspace_repo.reset_monthly_limits(str(ws["_id"]))
        count += 1

    print(f"✅ Reset monthly limits for {count} workspaces")
    return count

if __name__ == "__main__":
    reset_monthly_limits()
```

**Deliverables (Task 6.3):**
- ✅ Campaign limits enforced
- ✅ Template limits enforced
- ✅ Usage displayed in sidebar
- ✅ Upgrade prompts when limit reached
- ✅ Monthly reset cron job

---

### Task 6.4: Pricing Page & Plan Upgrade (4 hours)

**Goal:** Beautiful pricing page with clear value proposition

**Files to Create:**
- `pages/06_Pricing.py` - Pricing page with tiers

**6.4.1 Pricing Page (4 hours)**
```python
# pages/06_Pricing.py
import streamlit as st
from utils.auth import get_current_user
from repositories.workspace_repository import WorkspaceRepository

st.set_page_config(page_title="Pricing", page_icon="💎", layout="wide")

st.title("💎 Choose Your Plan")

user = get_current_user()

# Current plan indicator
if user:
    workspace_repo = WorkspaceRepository()
    workspace = workspace_repo.get_workspace(user.workspace_id)
    current_plan = workspace.plan_tier

    st.info(f"📌 You're currently on the **{current_plan.upper()}** plan")
else:
    current_plan = None

# Pricing tiers
col1, col2, col3, col4 = st.columns(4)

# Free tier
with col1:
    st.markdown("### 🆓 STARTER")
    st.markdown("**Forever Free**")

    st.markdown("---")

    st.markdown("""
    **✅ Included:**
    - 10 campaigns/month
    - 3 languages
    - Basic templates (5)
    - Instagram + Facebook
    - PDF/DOCX export

    **❌ Not included:**
    - No custom templates
    - No analytics
    - Watermark on exports
    - No Telegram/LinkedIn
    """)

    st.markdown("---")

    if current_plan == "free":
        st.success("✅ Current Plan")
    elif current_plan:
        st.button("Downgrade", disabled=True, help="Contact support to downgrade")
    else:
        if st.button("Start Free", type="primary", use_container_width=True):
            st.switch_page("pages/03_Signup.py")

# Professional tier
with col2:
    st.markdown("### 💼 PROFESSIONAL")
    st.markdown("**$49/month**")

    st.markdown("---")

    st.markdown("""
    **✅ Everything in Starter, plus:**
    - **100 campaigns/month**
    - **All 15 languages**
    - **All platforms** (Instagram, Facebook, Telegram, LinkedIn)
    - **5 custom templates**
    - Basic analytics
    - No watermark
    - Email support

    **💡 Best for:** Small businesses
    """)

    st.markdown("---")

    if current_plan == "professional":
        st.success("✅ Current Plan")
    else:
        if st.button("Upgrade to Pro", type="primary", use_container_width=True):
            st.info("💳 Stripe integration coming in Week 7")

# Business tier (POPULAR)
with col3:
    st.markdown("### 🚀 BUSINESS")
    st.markdown("**$99/month**")
    st.markdown("⭐ **MOST POPULAR**")

    st.markdown("---")

    st.markdown("""
    **✅ Everything in Professional, plus:**
    - **Unlimited campaigns**
    - **Unlimited custom templates**
    - **Advanced analytics** (with WHY)
    - **Viral content generation**
    - **Video script generation**
    - **3 team members**
    - Priority support (24h)

    **💡 Best for:** Marketing managers
    """)

    st.markdown("---")

    if current_plan == "business":
        st.success("✅ Current Plan")
    else:
        if st.button("Upgrade to Business", type="primary", use_container_width=True):
            st.info("💳 Stripe integration coming in Week 7")

# Agency tier
with col4:
    st.markdown("### 🏢 AGENCY")
    st.markdown("**$299/month**")

    st.markdown("---")

    st.markdown("""
    **✅ Everything in Business, plus:**
    - **10 team members**
    - **25 client workspaces**
    - **White-label exports**
    - **API access** (coming soon)
    - Dedicated account manager
    - Monthly strategy call
    - Custom training

    **💡 Best for:** Digital agencies
    """)

    st.markdown("---")

    if current_plan == "agency":
        st.success("✅ Current Plan")
    else:
        if st.button("Upgrade to Agency", type="primary", use_container_width=True):
            st.info("💳 Stripe integration coming in Week 7")

# Comparison table
st.markdown("---")
st.markdown("## 📊 Feature Comparison")

comparison_data = {
    "Feature": [
        "Campaigns per month",
        "Languages",
        "Custom templates",
        "Platforms",
        "Analytics",
        "Viral content",
        "Video scripts",
        "Team members",
        "White-label",
        "Support"
    ],
    "Starter": [
        "10", "3", "0", "Instagram, Facebook", "❌", "❌", "❌", "1", "❌", "Email"
    ],
    "Professional": [
        "100", "15", "5", "All 4 platforms", "Basic", "❌", "❌", "1", "❌", "Email"
    ],
    "Business": [
        "Unlimited", "15", "Unlimited", "All 4 platforms", "Advanced", "✅", "✅", "3", "❌", "Priority"
    ],
    "Agency": [
        "Unlimited", "15", "Unlimited", "All 4 platforms", "Advanced", "✅", "✅", "10", "✅", "Dedicated"
    ]
}

st.table(comparison_data)

# FAQ
st.markdown("---")
st.markdown("## ❓ Frequently Asked Questions")

with st.expander("Can I change plans anytime?"):
    st.markdown("Yes! Upgrade or downgrade anytime. Upgrades are instant, downgrades take effect at the end of your billing cycle.")

with st.expander("What happens if I exceed my limit?"):
    st.markdown("You'll be prompted to upgrade. On the Free plan, you can't create more than 10 campaigns/month. Paid plans have higher limits.")

with st.expander("Do you offer refunds?"):
    st.markdown("Yes, we offer a 14-day money-back guarantee. If you're not satisfied, contact us for a full refund.")

with st.expander("Can I cancel anytime?"):
    st.markdown("Yes, cancel anytime from your Account Settings. No questions asked.")

with st.expander("Do you offer annual plans?"):
    st.markdown("Yes! Save 20% with annual billing. Contact sales@example.com for details.")

# Enterprise CTA
st.markdown("---")
st.info("""
### 🏆 Enterprise Plan

Need more than 10 team members or custom integrations?

**Contact us for custom pricing:**
- Unlimited everything
- Custom integrations
- On-premise deployment
- SLA guarantees
- Dedicated support team

📧 Email: enterprise@example.com
""")
```

**Deliverables (Task 6.4):**
- ✅ Pricing page with 4 tiers
- ✅ Feature comparison table
- ✅ FAQ section
- ✅ Upgrade buttons (Stripe placeholder)
- ✅ Current plan indicator

---

## 📦 Week 6 Summary

**Total Time:** 24 hours

**Breakdown:**
- Task 6.1: User Authentication (8h)
- Task 6.2: Workspace Management (6h)
- Task 6.3: Usage Tracking (6h)
- Task 6.4: Pricing Page (4h)

**Deliverables:**
- ✅ Email/password authentication
- ✅ Signup/login pages
- ✅ User sessions (JWT)
- ✅ Workspace per user
- ✅ Workspace settings page
- ✅ Team management UI
- ✅ Usage limits enforced
- ✅ Usage displayed in UI
- ✅ Pricing page with 4 tiers
- ✅ Upgrade prompts
- ⏳ Stripe integration (Week 7)
- ⏳ OAuth (Google, LinkedIn) (Week 7)
- ⏳ Email verification (Week 7)

**Success Criteria:**
1. Users can sign up with email/password
2. Each user gets a workspace
3. Usage limits enforced correctly
4. Pricing page clearly shows value
5. Free users see upgrade prompts
6. No breaking changes to existing features

**Testing Checklist:**
```bash
# 1. Test signup flow
# - Visit /pages/03_Signup.py
# - Create account
# - Verify workspace created
# - Verify redirected to Getting Started

# 2. Test login flow
# - Visit /pages/02_Login.py
# - Login with credentials
# - Verify session persists
# - Verify user info in sidebar

# 3. Test logout
# - Click logout button
# - Verify session cleared
# - Verify redirected to login

# 4. Test usage limits
# - Create 10 campaigns (Free plan)
# - Try to create 11th campaign
# - Verify error message
# - Verify upgrade prompt

# 5. Test workspace settings
# - Visit /pages/05_Workspace_Settings.py
# - Change workspace name
# - Verify saved

# 6. Test pricing page
# - Visit /pages/06_Pricing.py
# - Verify current plan highlighted
# - Click upgrade buttons
# - Verify Stripe placeholder shown

# 7. Test protected pages
# - Logout
# - Try to access Home.py
# - Verify redirected to login
```

---

## 🚀 Next Steps (Week 7)

After Week 6 completion:

1. **Stripe Integration** (6h)
   - Setup Stripe account
   - Create payment links
   - Handle webhooks
   - Upgrade/downgrade flow

2. **OAuth Integration** (4h)
   - Google OAuth
   - LinkedIn OAuth
   - Social signup flow

3. **Email Service** (4h)
   - SendGrid setup
   - Welcome email
   - Email verification
   - Password reset

4. **Blog & SEO Generator** (12h)
   - Content marketing tools
   - SEO optimization

**Total Week 7:** 26 hours

---

## 📝 Notes

**Security Considerations:**
- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens for sessions
- ✅ Input validation on signup
- ✅ Protected routes require auth
- ⚠️ TODO: Rate limiting (Week 7)
- ⚠️ TODO: Email verification (Week 7)
- ⚠️ TODO: 2FA (future)

**Database Collections Added:**
- `users` - User accounts
- `workspaces` - Multi-tenant workspaces

**Environment Variables Needed:**
```env
# Add to .env
JWT_SECRET_KEY=your-secret-key-here-change-in-production
SENDGRID_API_KEY=  # Week 7
STRIPE_SECRET_KEY=  # Week 7
STRIPE_WEBHOOK_SECRET=  # Week 7
```

**Deployment Notes:**
- JWT secret must be unique in production
- Use HTTPS for login/signup pages
- Setup monthly cron job for usage reset
- Monitor failed login attempts

---

**Week 6 Status:** Ready to start! 🚀
**Estimated Completion:** 3 working days (8h/day)
