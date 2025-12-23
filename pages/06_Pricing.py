"""Pricing page with plan tiers and upgrade options."""
import streamlit as st
from utils.auth import get_current_user
from repositories.workspace_repository import WorkspaceRepository
import logging

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Pricing", page_icon="💎", layout="wide")

st.title("💎 Choose Your Plan")

st.markdown("""
Simple, transparent pricing that grows with you. Start free, upgrade when you need more.

**All plans include:**
✅ AI-powered content generation
✅ Multi-language translation
✅ Professional templates
✅ Export to HTML, PDF, DOCX
✅ 24/7 platform access
""")

st.markdown("---")

# Get current user and plan
user = get_current_user()
current_plan = None

if user:
    workspace_repo = WorkspaceRepository()
    workspace = workspace_repo.get_workspace(user.workspace_id)
    if workspace:
        current_plan = workspace.plan_tier
        st.info(f"📌 You're currently on the **{current_plan.upper()}** plan")

# First Row: Free, Starter, Professional
st.markdown("## Choose Your Plan")
col1, col2, col3 = st.columns(3)

# FREE TIER
with col1:
    st.markdown("### 🆓 FREE")
    st.markdown("**$0/month**")
    st.caption("Forever Free")

    st.markdown("---")

    st.markdown("""
    **✅ Perfect for trying out:**
    - 10 campaigns/month
    - 1 custom template
    - 3 languages
    - Instagram + Facebook
    - Basic analytics

    **❌ Limitations:**
    - Watermark on exports
    - No Telegram/LinkedIn
    - Community support only
    """)

    st.markdown("---")

    if current_plan == "free":
        st.success("✅ Current Plan")
    elif current_plan:
        st.button("Downgrade", disabled=True, help="Contact support to downgrade")
    else:
        if st.button("Start Free", type="primary", use_container_width=True, key="free_signup"):
            st.switch_page("pages/03_Signup.py")

# STARTER TIER
with col2:
    st.markdown("### 🚀 STARTER")
    st.markdown("**$49/month**")
    st.caption("For solo entrepreneurs")

    st.markdown("---")

    st.markdown("""
    **✅ Everything in Free, plus:**
    - **50 campaigns/month** (5x more!)
    - **3 custom templates**
    - **5 languages**
    - **All 4 platforms**
      (Instagram, Facebook, Telegram, LinkedIn)
    - No watermark
    - Email support

    **💡 Best for:** Solo business owners
    """)

    st.markdown("---")

    if current_plan == "starter":
        st.success("✅ Current Plan")
    else:
        if st.button("Upgrade to Starter", type="primary", use_container_width=True, key="starter_upgrade"):
            st.info("💳 Stripe integration coming in Week 7")

# PROFESSIONAL TIER
with col3:
    st.markdown("### 💼 PROFESSIONAL")
    st.markdown("**$99/month**")
    st.caption("For growing businesses")

    st.markdown("---")

    st.markdown("""
    **✅ Everything in Starter, plus:**
    - **200 campaigns/month** (4x more!)
    - **All 15 languages**
    - **5 custom templates**
    - Advanced analytics
    - Priority email support (48h)
    - Quality scoring

    **💡 Best for:** Marketing teams
    """)

    st.markdown("---")

    if current_plan == "professional":
        st.success("✅ Current Plan")
    else:
        if st.button("Upgrade to Professional", type="primary", use_container_width=True, key="pro_upgrade"):
            st.info("💳 Stripe integration coming in Week 7")

# Second Row: Team, Agency, Enterprise
st.markdown("---")
col4, col5, col6 = st.columns(3)

# TEAM TIER (POPULAR)
with col4:
    st.markdown("### 👥 TEAM")
    st.markdown("**$199/month**")
    st.markdown("⭐ **MOST POPULAR**")

    st.markdown("---")

    st.markdown("""
    **✅ Everything in Professional, plus:**
    - **Unlimited campaigns**
    - **20 custom templates**
    - **3 team members**
    - Advanced analytics with WHY insights
    - Viral content generation
    - Video script generation
    - Priority support (24h)

    **💡 Best for:** Marketing teams & agencies
    """)

    st.markdown("---")

    if current_plan == "team":
        st.success("✅ Current Plan")
    else:
        if st.button("Upgrade to Team", type="primary", use_container_width=True, key="team_upgrade"):
            st.info("💳 Stripe integration coming in Week 7")

# AGENCY TIER
with col5:
    st.markdown("### 🏢 AGENCY")
    st.markdown("**$499/month**")
    st.caption("For digital agencies")

    st.markdown("---")

    st.markdown("""
    **✅ Everything in Team, plus:**
    - **10 team members** (vs 3)
    - **50 custom templates** (vs 20)
    - **White-label exports**
    - **API access** (coming soon)
    - Dedicated account manager
    - Monthly strategy call
    - Multi-workspace management

    **💡 Best for:** Agencies with 5-25 clients
    """)

    st.markdown("---")

    if current_plan == "agency":
        st.success("✅ Current Plan")
    else:
        if st.button("Upgrade to Agency", type="primary", use_container_width=True, key="agency_upgrade"):
            st.info("💳 Stripe integration coming in Week 7")

# ENTERPRISE TIER
with col6:
    st.markdown("### 🏆 ENTERPRISE")
    st.markdown("**$999+/month**")
    st.caption("Custom solutions")

    st.markdown("---")

    st.markdown("""
    **✅ Everything in Agency, plus:**
    - **Unlimited team members**
    - **Unlimited custom templates**
    - **SSO & SAML**
    - **Dedicated infrastructure**
    - **SLA guarantees (99.9% uptime)**
    - **Custom integrations**
    - **On-premise deployment option**
    - **24/7 priority support**

    **💡 Best for:** Large enterprises (100+ employees)
    """)

    st.markdown("---")

    if current_plan == "enterprise":
        st.success("✅ Current Plan")
    else:
        if st.button("Contact Sales", type="primary", use_container_width=True, key="enterprise_contact"):
            st.info("📧 Email: enterprise@example.com | Phone: +1 (555) 123-4567")

# Feature Comparison Table
st.markdown("---")
st.markdown("## 📊 Detailed Feature Comparison")

comparison_data = {
    "Feature": [
        "Campaigns per month",
        "Languages supported",
        "Custom templates",
        "Platforms",
        "Analytics",
        "Viral content AI",
        "Video scripts",
        "Team members",
        "White-label exports",
        "Support",
        "API access",
        "SLA guarantee"
    ],
    "Free": [
        "10", "3", "1", "Instagram, Facebook", "Basic", "❌", "❌", "1", "❌", "Community", "❌", "❌"
    ],
    "Starter": [
        "50", "5", "3", "All 4 platforms", "Basic", "❌", "❌", "1", "❌", "Email", "❌", "❌"
    ],
    "Professional": [
        "200", "15", "5", "All 4 platforms", "Advanced", "❌", "❌", "1", "❌", "Priority", "❌", "❌"
    ],
    "Team": [
        "Unlimited", "15", "20", "All 4 platforms", "Advanced + WHY", "✅", "✅", "3", "❌", "Priority (24h)", "❌", "❌"
    ],
    "Agency": [
        "Unlimited", "15", "50", "All 4 platforms", "Advanced + WHY", "✅", "✅", "10", "✅", "Dedicated", "✅", "❌"
    ],
    "Enterprise": [
        "Unlimited", "15", "Unlimited", "All 4 platforms", "Advanced + WHY", "✅", "✅", "Unlimited", "✅", "24/7 VIP", "✅", "99.9%"
    ]
}

st.table(comparison_data)

# FAQ Section
st.markdown("---")
st.markdown("## ❓ Frequently Asked Questions")

col1, col2 = st.columns(2)

with col1:
    with st.expander("Can I change plans anytime?"):
        st.markdown("""
        Yes! Upgrade or downgrade anytime.

        - **Upgrades:** Take effect immediately
        - **Downgrades:** Take effect at the end of your billing cycle
        - **No penalties:** Cancel anytime with no fees
        """)

    with st.expander("What happens if I exceed my limit?"):
        st.markdown("""
        On the **Free plan:** You'll be prompted to upgrade when you hit 10 campaigns/month.

        On **paid plans:** You'll get a notification when you're close to your limit. We'll never charge you extra without permission.

        **Team/Agency/Enterprise:** Unlimited campaigns means truly unlimited!
        """)

    with st.expander("Do you offer refunds?"):
        st.markdown("""
        **Yes!** We offer a **14-day money-back guarantee** on all paid plans.

        If you're not satisfied with our platform for any reason, contact us at support@example.com for a full refund.

        No questions asked.
        """)

with col2:
    with st.expander("Can I cancel anytime?"):
        st.markdown("""
        **Absolutely!** Cancel anytime from your Workspace Settings → Billing tab.

        - No cancellation fees
        - No questions asked
        - Keep access until end of billing cycle
        - Export all your data before canceling
        """)

    with st.expander("Do you offer annual plans?"):
        st.markdown("""
        **Yes!** Save **20% with annual billing.**

        Annual pricing:
        - Starter: $470/year (save $118)
        - Professional: $950/year (save $238)
        - Team: $1,910/year (save $478)
        - Agency: $4,790/year (save $1,198)

        Contact sales@example.com for annual billing.
        """)

    with st.expander("What payment methods do you accept?"):
        st.markdown("""
        We accept all major credit cards via Stripe:

        - Visa
        - Mastercard
        - American Express
        - Discover

        **Enterprise customers:** We also accept wire transfers and invoicing.
        """)

# Enterprise CTA
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.info("""
    ### 🏆 Need a Custom Enterprise Plan?

    For large enterprises with specific needs:

    **We offer:**
    - Custom pricing for high-volume usage
    - Dedicated infrastructure & VPC
    - On-premise deployment
    - Custom integrations & API development
    - White-glove onboarding & training
    - Dedicated success manager
    - SLA guarantees (up to 99.99%)

    **Contact us:** enterprise@example.com | +1 (555) 123-4567
    """)

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📧 Contact Sales", type="primary", use_container_width=True, key="contact_sales_footer"):
        st.info("Email: enterprise@example.com")

# Trust signals
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 🔒 Secure")
    st.caption("Bank-level encryption & SOC 2 compliant")

with col2:
    st.markdown("### 💳 No Hidden Fees")
    st.caption("Transparent pricing, cancel anytime")

with col3:
    st.markdown("### 🚀 Instant Setup")
    st.caption("Start creating content in under 2 minutes")

with col4:
    st.markdown("### 💬 Expert Support")
    st.caption("Real humans, fast responses")

# Footer
st.markdown("---")
st.caption("""
**All prices in USD.** Monthly billing unless otherwise specified.

**Need help choosing a plan?** Contact sales@example.com or book a demo: [calendly.com/example](https://calendly.com)

**Trusted by 500+ businesses** across fitness, SaaS, e-commerce, and agencies.
""")
