"""Workspace Settings page for managing workspace and team."""
import streamlit as st
from utils.auth import require_auth
from repositories.workspace_repository import WorkspaceRepository
from repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Workspace Settings", page_icon="⚙️", layout="wide")

# Require authentication
user = require_auth()

st.title("⚙️ Workspace Settings")

st.markdown(f"Manage your workspace, team, and billing settings.")

st.markdown("---")

# Get workspace
workspace_repo = WorkspaceRepository()
workspace = workspace_repo.get_workspace(user.workspace_id)

if not workspace:
    st.error("❌ Workspace not found")
    st.stop()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["General", "Usage", "Team", "Billing"])

# Tab 1: General Settings
with tab1:
    st.header("General Settings")

    with st.form("workspace_settings"):
        workspace_name = st.text_input(
            "Workspace Name",
            value=workspace.name,
            help="Your workspace or company name"
        )

        # Branding (Agency plan only)
        if workspace.plan_tier == "agency":
            st.markdown("---")
            st.subheader("🎨 Branding (Agency Plan)")

            logo_url = st.text_input(
                "Logo URL (optional)",
                value=workspace.logo_url or "",
                help="URL to your company logo"
            )

            primary_color = st.color_picker(
                "Primary Brand Color",
                value=workspace.primary_color or "#1f77b4",
                help="Your brand's primary color"
            )
        else:
            logo_url = workspace.logo_url
            primary_color = workspace.primary_color

        st.markdown("---")

        if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
            try:
                workspace.name = workspace_name
                if workspace.plan_tier == "agency":
                    workspace.logo_url = logo_url
                    workspace.primary_color = primary_color

                workspace_repo.update_workspace(user.workspace_id, workspace)

                st.success("✅ Workspace settings saved!")
                logger.info(f"Workspace settings updated: {user.workspace_id}")
            except Exception as e:
                logger.error(f"Failed to update workspace: {e}")
                st.error(f"❌ Failed to save settings: {str(e)}")

# Tab 2: Usage & Limits
with tab2:
    st.header("📊 Usage & Limits")

    limits = workspace.get_plan_limits()

    # Current plan
    st.subheader(f"Current Plan: **{workspace.plan_tier.upper()}**")

    col1, col2 = st.columns(2)

    # Campaigns usage
    with col1:
        st.markdown("### Campaigns This Month")

        if limits["campaigns"] == -1:
            st.metric("Campaigns Created", workspace.campaigns_this_month)
            st.success("✅ Unlimited campaigns")
        else:
            remaining = limits["campaigns"] - workspace.campaigns_this_month
            st.metric(
                "Campaigns",
                f"{workspace.campaigns_this_month} / {limits['campaigns']}"
            )

            progress = workspace.campaigns_this_month / limits["campaigns"]
            st.progress(min(progress, 1.0))

            if remaining <= 0:
                st.error(f"❌ Limit reached! Upgrade to create more campaigns.")
            elif remaining <= 2:
                st.warning(f"⚠️ Only {remaining} campaigns remaining this month")
            else:
                st.info(f"✅ {remaining} campaigns remaining")

    # Custom templates usage
    with col2:
        st.markdown("### Custom Templates")

        if limits["custom_templates"] == -1:
            st.metric("Custom Templates", workspace.custom_templates_count)
            st.success("✅ Unlimited templates")
        elif limits["custom_templates"] == 0:
            st.metric("Custom Templates", "Not Available")
            st.info("🔒 Upgrade to Professional plan to create custom templates")
        else:
            st.metric(
                "Templates",
                f"{workspace.custom_templates_count} / {limits['custom_templates']}"
            )

            if workspace.custom_templates_count >= limits["custom_templates"]:
                st.error("❌ Template limit reached! Upgrade to create more.")
            else:
                remaining = limits["custom_templates"] - workspace.custom_templates_count
                st.info(f"✅ {remaining} templates remaining")

    st.markdown("---")

    col3, col4 = st.columns(2)

    # Team members usage
    with col3:
        st.markdown("### Team Members")

        team_count = len(workspace.team_member_ids)

        if limits["team_members"] == -1:
            st.metric("Team Members", team_count)
            st.success("✅ Unlimited team members")
        else:
            st.metric("Team Members", f"{team_count} / {limits['team_members']}")

            if team_count >= limits["team_members"]:
                st.error("❌ Team limit reached! Upgrade to add more members.")
            else:
                remaining = limits["team_members"] - team_count
                st.info(f"✅ {remaining} slots remaining")

    # Languages
    with col4:
        st.markdown("### Languages")

        if limits["languages"] == 15:
            st.metric("Languages", "All 15 languages")
            st.success("✅ Full language access")
        else:
            st.metric("Languages Available", limits["languages"])
            st.info(f"✅ {limits['languages']} languages included")

    # Upgrade CTA
    if workspace.plan_tier in ["free", "starter"]:
        st.markdown("---")
        st.info("💎 Upgrade to unlock more features and higher limits!")

        if st.button("View Pricing Plans", type="primary", use_container_width=True):
            st.switch_page("pages/06_Pricing.py")

# Tab 3: Team Management
with tab3:
    st.header("👥 Team Management")

    if user.role != "owner":
        st.warning("⚠️ Only workspace owner can manage team members")
        st.info(f"Your role: **{user.role}**")
    else:
        # Current team
        st.subheader("Current Team Members")

        user_repo = UserRepository()
        team_members = user_repo.get_workspace_users(user.workspace_id)

        if not team_members:
            st.info("No team members yet. Invite your first team member below!")
        else:
            for member in team_members:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

                with col1:
                    if member.role == "owner":
                        st.markdown(f"👑 **{member.name}** ({member.email})")
                    else:
                        st.markdown(f"**{member.name}** ({member.email})")

                with col2:
                    st.markdown(f"Role: `{member.role}`")

                with col3:
                    if member.last_login:
                        st.caption(f"Last login: {member.last_login.strftime('%Y-%m-%d')}")
                    else:
                        st.caption("Never logged in")

                with col4:
                    if member.role != "owner" and member.id != user.id:
                        if st.button("Remove", key=f"remove_{member.id}", type="secondary"):
                            try:
                                # Remove member logic
                                user_repo.delete_user(member.id)
                                workspace_repo.remove_team_member(user.workspace_id, member.id)

                                st.success(f"✅ Removed {member.name}")
                                st.rerun()
                            except Exception as e:
                                logger.error(f"Failed to remove team member: {e}")
                                st.error(f"❌ Failed to remove member: {str(e)}")

        # Invite new member
        st.markdown("---")
        st.subheader("Invite Team Member")

        limits = workspace.get_plan_limits()

        if len(team_members) >= limits["team_members"] and limits["team_members"] != -1:
            st.warning(f"⚠️ Team limit reached ({limits['team_members']} members). Upgrade to add more members.")

            if st.button("Upgrade Plan", type="primary"):
                st.switch_page("pages/06_Pricing.py")
        else:
            st.info("💡 **Email invites coming in Week 7!** For now, team members can sign up and you can add them manually.")

            with st.form("invite_member"):
                invite_email = st.text_input(
                    "Email",
                    placeholder="teammate@company.com",
                    help="Email address of the team member"
                )

                invite_role = st.selectbox(
                    "Role",
                    ["member", "admin"],
                    help="admin: can edit workspace settings, member: can only use the platform"
                )

                if st.form_submit_button("Send Invite (Coming Week 7)", type="primary"):
                    st.info(f"📧 Email invites coming in Week 7! Invite will be sent to {invite_email}")

# Tab 4: Billing
with tab4:
    st.header("💳 Billing & Subscription")

    st.subheader(f"Current Plan: **{workspace.plan_tier.upper()}**")

    # Plan details
    plan_details = {
        "free": {
            "price": "$0/month",
            "features": ["10 campaigns/month", "3 languages", "1 custom template", "Instagram + Facebook"]
        },
        "starter": {
            "price": "$49/month",
            "features": ["50 campaigns/month", "5 languages", "3 custom templates", "All 4 platforms"]
        },
        "professional": {
            "price": "$99/month",
            "features": ["200 campaigns/month", "15 languages", "5 custom templates", "Advanced analytics"]
        },
        "team": {
            "price": "$199/month",
            "features": ["Unlimited campaigns", "15 languages", "20 templates", "3 team members", "Viral content"]
        },
        "agency": {
            "price": "$499/month",
            "features": ["Unlimited campaigns", "10 team members", "50 templates", "White-label", "API access"]
        },
        "enterprise": {
            "price": "$999+/month",
            "features": ["Unlimited everything", "SSO & SAML", "SLA guarantees", "24/7 support"]
        }
    }

    current_plan = plan_details.get(workspace.plan_tier, plan_details["free"])

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"### {current_plan['price']}")

    with col2:
        st.markdown("**Included:**")
        for feature in current_plan["features"]:
            st.markdown(f"✅ {feature}")

    st.markdown("---")

    # Upgrade/Downgrade
    if workspace.plan_tier == "free":
        st.info("You're on the Free plan. Upgrade to unlock premium features!")

        if st.button("Upgrade Now", type="primary", use_container_width=True):
            st.switch_page("pages/06_Pricing.py")
    else:
        st.success(f"✅ Subscribed to {workspace.plan_tier.upper()} plan")

        # Placeholder for Stripe integration
        st.markdown("### Payment Method")
        st.info("💳 Stripe integration coming in Week 7")

        st.markdown("### Billing History")
        st.info("📄 Invoice history coming in Week 7")

        st.markdown("### Manage Subscription")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Change Plan", type="secondary", use_container_width=True):
                st.switch_page("pages/06_Pricing.py")

        with col2:
            if st.button("Cancel Subscription", type="secondary", use_container_width=True):
                st.warning("⚠️ Subscription management coming in Week 7")
                st.info("To cancel, please contact support@example.com")

# Footer
st.markdown("---")
st.caption("""
**Need help?** Contact support@example.com

**Workspace ID:** `{workspace_id}`
""".format(workspace_id=user.workspace_id))
