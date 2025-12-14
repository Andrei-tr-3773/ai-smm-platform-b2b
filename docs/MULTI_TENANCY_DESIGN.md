# Multi-Tenancy Architecture

## Overview

This document outlines the multi-tenant architecture for the AI SMM Platform for B2B. Each client (business) operates in an isolated **workspace** with their own templates, campaigns, team members, and usage limits.

## Core Concepts

- **Workspace**: A tenant environment for a single business/client
- **User**: An individual who belongs to one workspace
- **Role**: Permissions within a workspace (owner, admin, member)
- **Plan Tier**: Subscription level (free, professional, business, agency, enterprise)

---

## Database Schema

### workspaces

```json
{
  "_id": ObjectId,
  "name": "FitZone Fitness",
  "owner_user_id": ObjectId,
  "plan_tier": "professional", // free, professional, business, agency, enterprise
  "created_at": ISODate,
  "updated_at": ISODate,
  "settings": {
    "brand": {
      "logo_url": "https://example.com/logo.png",
      "colors": {
        "primary": "#FF6B35",
        "secondary": "#2D3142"
      },
      "fonts": {
        "heading": "Inter",
        "body": "Inter"
      }
    },
    "social_platforms": ["instagram", "facebook", "telegram"],
    "default_languages": ["en-US", "es-ES"]
  },
  "usage": {
    "campaigns_this_month": 45,
    "custom_templates_count": 8,
    "team_members_count": 3
  },
  "limits": {
    "max_campaigns_per_month": 100,  // based on plan
    "max_custom_templates": 5,        // based on plan
    "max_team_members": 1             // based on plan
  },
  "billing": {
    "stripe_customer_id": "cus_...",
    "stripe_subscription_id": "sub_...",
    "current_period_start": ISODate,
    "current_period_end": ISODate,
    "status": "active"  // active, past_due, canceled
  }
}
```

### users

```json
{
  "_id": ObjectId,
  "email": "alex@fitzone.com",
  "password_hash": "...",
  "name": "Alex Rodriguez",
  "workspace_id": ObjectId,  // belongs to workspace
  "role": "owner",  // owner, admin, member
  "created_at": ISODate,
  "last_login": ISODate,
  "avatar_url": "https://...",
  "preferences": {
    "language": "en-US",
    "timezone": "America/Chicago",
    "notifications": {
      "email": true,
      "push": false
    }
  }
}
```

### content_templates (per workspace)

```json
{
  "_id": ObjectId,
  "workspace_id": ObjectId,  // null = global template
  "name": "New Class Announcement",
  "description": "Announce new fitness classes",
  "liquid_template": "<div>...</div>",
  "items": {
    "class_name": {"type": "text", "required": true, "maxLength": 100},
    "instructor": {"type": "text", "required": true, "maxLength": 100},
    "date": {"type": "date", "required": true},
    "time": {"type": "time", "required": true},
    "benefits": {"type": "rich_text", "required": false, "maxLength": 500}
  },
  "example_query": "Announce Sarah's HIIT class on Saturday at 10 AM",
  "is_shared": false,  // global template or workspace-specific
  "created_by": ObjectId,
  "created_at": ISODate,
  "updated_at": ISODate,
  "category": "fitness",  // fitness, ecommerce, saas, generic
  "tags": ["fitness", "classes", "announcement"],
  "usage_count": 45  // how many times used
}
```

### campaigns

```json
{
  "_id": ObjectId,
  "workspace_id": ObjectId,  // belongs to workspace
  "template_id": ObjectId,
  "user_id": ObjectId,  // created by
  "name": "HIIT Class Saturday",
  "query": "Announce new HIIT class...",
  "content": {
    "class_name": "HIIT Blast",
    "instructor": "Sarah",
    "date": "2024-12-15",
    "time": "10:00 AM",
    "benefits": "Burn 500 calories in 45 minutes!"
  },
  "translations": {
    "es-ES": {
      "class_name": "HIIT Explosivo",
      "instructor": "Sarah",
      ...
    },
    "fr-FR": {...}
  },
  "platforms": ["instagram", "facebook"],
  "status": "draft",  // draft, published, archived
  "created_at": ISODate,
  "updated_at": ISODate,
  "published_at": ISODate,
  "analytics": {
    "instagram": {
      "reach": 5000,
      "engagement": 450,
      "likes": 320,
      "comments": 45,
      "shares": 85
    },
    "facebook": {
      "reach": 3200,
      "engagement": 280,
      ...
    }
  }
}
```

### audiences

```json
{
  "_id": ObjectId,
  "workspace_id": ObjectId,  // null = global audience
  "name": "Fitness Enthusiasts",
  "description": "People interested in fitness and healthy lifestyle",
  "demographics": {
    "age_range": "25-55",
    "gender": "all",
    "location": "Austin, TX"
  },
  "is_shared": false,
  "created_by": ObjectId,
  "created_at": ISODate
}
```

---

## Plan Tiers & Limits

| Feature | Free | Professional | Business | Agency | Enterprise |
|---------|------|--------------|----------|---------|------------|
| **Price/Month** | $0 | $99 | $199 | $499 | Custom |
| **Campaigns/Month** | 10 | 200 | Unlimited | Unlimited | Unlimited |
| **Custom Templates** | 1 | 5 | 20 | 50 | Unlimited |
| **Team Members** | 1 | 1 | 3 | 10 | Unlimited |
| **Languages** | 3 | 5 | 15 | 15 | 15 |
| **Analytics** | Basic | Advanced | Advanced | Advanced + API | Advanced + API |
| **White-label** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **API Access** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Dedicated Support** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **SLA** | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Access Control

### Roles & Permissions

#### Owner
- Full control over workspace
- Manage team members
- Change plan tier
- Delete workspace
- All admin permissions

#### Admin
- Create/edit/delete campaigns
- Create/edit/delete custom templates
- Invite team members (cannot remove owner)
- View analytics
- Cannot change plan tier or delete workspace

#### Member
- Create/edit own campaigns
- Use existing templates (cannot create custom)
- View analytics for own campaigns
- Cannot invite team members

### Permission Matrix

| Action | Owner | Admin | Member |
|--------|-------|-------|--------|
| Create campaign | ✅ | ✅ | ✅ |
| Edit own campaign | ✅ | ✅ | ✅ |
| Edit others' campaign | ✅ | ✅ | ❌ |
| Delete own campaign | ✅ | ✅ | ✅ |
| Delete others' campaign | ✅ | ✅ | ❌ |
| Create custom template | ✅ | ✅ | ❌ |
| Edit custom template | ✅ | ✅ | ❌ |
| Invite team member | ✅ | ✅ | ❌ |
| Remove team member | ✅ | ✅ (not owner) | ❌ |
| Change plan tier | ✅ | ❌ | ❌ |
| Delete workspace | ✅ | ❌ | ❌ |

---

## Authentication Flow

### Signup

```python
# POST /api/auth/signup
{
  "email": "alex@fitzone.com",
  "password": "...",
  "name": "Alex Rodriguez",
  "workspace_name": "FitZone Fitness"
}

# Response
{
  "user": {
    "_id": "...",
    "email": "alex@fitzone.com",
    "name": "Alex Rodriguez"
  },
  "workspace": {
    "_id": "...",
    "name": "FitZone Fitness",
    "plan_tier": "free"
  },
  "token": "jwt_token..."
}
```

**Flow:**
1. Create user
2. Create workspace (owner = user)
3. Set plan_tier = "free"
4. Generate JWT token
5. Return user + workspace + token

### Login

```python
# POST /api/auth/login
{
  "email": "alex@fitzone.com",
  "password": "..."
}

# Response
{
  "user": {...},
  "workspace": {...},
  "token": "jwt_token..."
}
```

### Session Management

```python
# JWT token contains:
{
  "user_id": "...",
  "workspace_id": "...",
  "role": "owner",
  "exp": 1234567890
}

# Middleware checks:
def get_current_user(token):
    payload = jwt.decode(token)
    user = User.get(payload['user_id'])
    workspace = Workspace.get(payload['workspace_id'])
    return user, workspace
```

---

## Data Isolation

### Query-level Isolation

All queries must include `workspace_id`:

```python
# ❌ BAD: No workspace filter
campaigns = db.campaigns.find({})

# ✅ GOOD: Workspace filter
workspace = get_current_workspace()
campaigns = db.campaigns.find({"workspace_id": workspace._id})
```

### Repository Pattern

```python
class CampaignRepository:
    def __init__(self, workspace_id):
        self.workspace_id = workspace_id

    def get_campaigns(self):
        return db.campaigns.find({"workspace_id": self.workspace_id})

    def create_campaign(self, data):
        data["workspace_id"] = self.workspace_id
        return db.campaigns.insert_one(data)
```

### Middleware

```python
# Flask/FastAPI middleware
@app.before_request
def load_workspace():
    user = get_current_user()
    request.workspace = Workspace.get(user.workspace_id)

    # Check plan limits
    if request.endpoint == "create_campaign":
        if request.workspace.usage.campaigns_this_month >= request.workspace.limits.max_campaigns_per_month:
            return {"error": "Campaign limit reached. Upgrade plan."}, 403
```

---

## Usage Tracking

### Monthly Reset

```python
# Cron job (runs 1st of each month)
def reset_monthly_usage():
    db.workspaces.update_many({}, {
        "$set": {
            "usage.campaigns_this_month": 0
        }
    })
```

### Increment on Create

```python
def create_campaign(workspace_id, campaign_data):
    # Create campaign
    campaign = db.campaigns.insert_one({
        "workspace_id": workspace_id,
        **campaign_data
    })

    # Increment usage
    db.workspaces.update_one(
        {"_id": workspace_id},
        {"$inc": {"usage.campaigns_this_month": 1}}
    )

    return campaign
```

### Limit Checks

```python
def can_create_campaign(workspace):
    if workspace.usage.campaigns_this_month >= workspace.limits.max_campaigns_per_month:
        return False, "Campaign limit reached. Upgrade to create more."
    return True, None

def can_create_custom_template(workspace):
    if workspace.custom_templates_count >= workspace.limits.max_custom_templates:
        return False, "Custom template limit reached. Upgrade to create more."
    return True, None
```

---

## Global vs Workspace Templates

### Global Templates (Platform-provided)

```python
{
  "_id": ObjectId,
  "workspace_id": null,  # Global!
  "name": "Fitness - New Class",
  "is_shared": true,
  "created_by": null,  # System template
  ...
}
```

**All workspaces can use global templates.**

### Workspace-Specific Templates (Custom)

```python
{
  "_id": ObjectId,
  "workspace_id": ObjectId("fitzone_workspace"),
  "name": "FitZone - HIIT Class",
  "is_shared": false,
  "created_by": ObjectId("alex_user"),
  ...
}
```

**Only users in FitZone workspace can see this template.**

### Query Logic

```python
def get_templates(workspace_id):
    # Get global templates + workspace templates
    return db.content_templates.find({
        "$or": [
            {"workspace_id": None},  # Global templates
            {"workspace_id": workspace_id}  # Workspace templates
        ]
    })
```

---

## Implementation Phases

### Phase 1: Foundation (Week 2)
- Add `workspace_id` to all collections
- Create Workspace model
- Update repositories to filter by workspace
- Add plan tier limits

**Deliverables:**
- `models/workspace.py`
- Updated repositories with workspace filtering
- Migration script to add workspace_id

### Phase 2: Authentication (Week 6)
- User signup/login
- JWT token generation
- Workspace creation on signup
- Session management

**Deliverables:**
- `/api/auth/signup`
- `/api/auth/login`
- Middleware for workspace loading

### Phase 3: Team Collaboration (Week 8)
- Invite team members
- Role-based access control
- Team member management UI

**Deliverables:**
- `/api/teams/invite`
- Permission checks
- Team settings page

### Phase 4: Billing (Week 10)
- Stripe integration
- Plan upgrades/downgrades
- Usage limit enforcement
- Subscription management

**Deliverables:**
- `/api/billing/subscribe`
- Usage tracking dashboard
- Upgrade prompts

---

## Migration Strategy

### Step 1: Add workspace_id (Week 2)

```python
# migrations/002_add_workspace_id.py
def migrate():
    # Create default workspace
    default_workspace = db.workspaces.insert_one({
        "name": "Default Workspace",
        "plan_tier": "professional",
        "created_at": datetime.now()
    })

    # Add workspace_id to all campaigns
    db.campaigns.update_many({}, {
        "$set": {"workspace_id": default_workspace.inserted_id}
    })

    # Add workspace_id to custom templates
    db.content_templates.update_many(
        {"is_shared": False},
        {"$set": {"workspace_id": default_workspace.inserted_id}}
    )

    # Global templates remain workspace_id = null
```

### Step 2: Create Workspace Model (Week 2)

```python
# models/workspace.py
from pydantic import BaseModel
from datetime import datetime

class Workspace(BaseModel):
    name: str
    owner_user_id: str
    plan_tier: str = "free"
    settings: dict = {}
    usage: dict = {
        "campaigns_this_month": 0,
        "custom_templates_count": 0
    }
    limits: dict = {
        "max_campaigns_per_month": 10,
        "max_custom_templates": 1,
        "max_team_members": 1
    }
```

### Step 3: Update Repositories (Week 2)

```python
# Before
class CampaignRepository:
    def get_campaigns(self):
        return db.campaigns.find({})

# After
class CampaignRepository:
    def __init__(self, workspace_id):
        self.workspace_id = workspace_id

    def get_campaigns(self):
        return db.campaigns.find({"workspace_id": self.workspace_id})
```

---

## Testing Strategy

### Unit Tests

```python
def test_workspace_isolation():
    workspace1 = create_workspace("Workspace 1")
    workspace2 = create_workspace("Workspace 2")

    repo1 = CampaignRepository(workspace1._id)
    repo2 = CampaignRepository(workspace2._id)

    campaign1 = repo1.create_campaign({...})

    # Workspace 2 should NOT see campaign1
    assert campaign1 not in repo2.get_campaigns()
```

### Integration Tests

```python
def test_plan_limits():
    workspace = create_workspace("Test Workspace", plan_tier="free")

    # Create 10 campaigns (free tier limit)
    for i in range(10):
        create_campaign(workspace._id, {...})

    # 11th should fail
    with pytest.raises(PlanLimitError):
        create_campaign(workspace._id, {...})
```

---

## Security Considerations

### Data Isolation
- ✅ All queries filter by `workspace_id`
- ✅ Repositories enforce workspace context
- ✅ Middleware validates workspace access

### Authorization
- ✅ JWT tokens include `workspace_id` and `role`
- ✅ Permission checks on all sensitive actions
- ✅ Owner cannot be removed by admins

### Rate Limiting
- ✅ Plan-based limits on campaigns/month
- ✅ API rate limiting per workspace
- ✅ Graceful degradation when limits reached

### Data Privacy
- ✅ Workspaces cannot see each other's data
- ✅ Soft deletes (archive) instead of hard deletes
- ✅ Audit logs for sensitive actions

---

## Future Enhancements

### Week 12+
- **Workspace Analytics**: Dashboard with usage trends, popular templates
- **White-label**: Custom domain, custom branding for agency tier
- **API Access**: REST API for programmatic campaign creation
- **SSO**: Single sign-on for enterprise tier
- **Audit Logs**: Track all actions (who created/edited/deleted what)
- **Export/Import**: Backup workspace data, migrate templates
- **Workspace Transfer**: Transfer ownership to another user

---

## Appendix: Plan Tier Details

### Free Tier ($0/month)
- 10 campaigns/month
- 1 custom template
- 1 team member
- 3 languages
- Basic analytics
- Community support

### Professional Tier ($99/month)
- 200 campaigns/month
- 5 custom templates
- 1 team member
- 5 languages
- Advanced analytics
- Email support

### Business Tier ($199/month)
- Unlimited campaigns
- 20 custom templates
- 3 team members
- 15 languages
- Advanced analytics
- Priority email support

### Agency Tier ($499/month)
- Unlimited campaigns
- 50 custom templates
- 10 team members
- 15 languages
- Advanced analytics + API
- White-label
- Priority support
- Multi-workspace management

### Enterprise Tier (Custom)
- Unlimited everything
- Dedicated support
- SLA
- Custom integrations
- SSO
- Audit logs
- On-premise option
