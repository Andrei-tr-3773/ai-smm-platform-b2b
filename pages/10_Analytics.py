"""
Analytics Dashboard - Business metrics and revenue tracking.

Week 8: Task 8.4.2 - Dashboard for workspace owner to track metrics.

Metrics:
- MRR (Monthly Recurring Revenue)
- Paying users
- Conversion rate
- Churn rate
- CAC by channel
- Month 1 progress
"""

import streamlit as st
from utils.auth import require_auth, check_user_role
from utils.business_metrics import get_business_metrics
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

# Require authentication
user = require_auth()

# Only workspace owner can view analytics
if not check_user_role(user, "owner"):
    st.error("🔒 Only workspace owners can access analytics")
    st.info("Contact your workspace owner for analytics insights")
    st.stop()

st.title("📊 Business Analytics")

st.markdown("""
Track your workspace performance, revenue metrics, and Month 1 targets.
""")

# Initialize business metrics
try:
    metrics = get_business_metrics()
    dashboard = metrics.get_dashboard_summary()
except Exception as e:
    logger.error(f"Error loading analytics: {e}")
    st.error("❌ Could not load analytics dashboard")
    st.info("Please refresh the page or contact support")
    st.stop()

st.markdown("---")

# ==========================================
# Month 1 Progress (top priority)
# ==========================================

st.header("🎯 Month 1 Target Progress")

month1 = dashboard.get("month1_progress", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    users_progress = month1.get("paying_users", {})
    current_users = users_progress.get("current", 0)
    target_users = users_progress.get("target", 50)
    user_pct = users_progress.get("percentage", 0)

    st.metric(
        "Paying Users",
        f"{current_users} / {target_users}",
        delta=f"{user_pct:.1f}% of target"
    )
    st.progress(min(user_pct / 100, 1.0))

with col2:
    mrr_progress = month1.get("mrr", {})
    current_mrr = mrr_progress.get("current", 0)
    target_mrr = mrr_progress.get("target", 7500)
    mrr_pct = mrr_progress.get("percentage", 0)

    st.metric(
        "MRR",
        f"${current_mrr:,.0f} / ${target_mrr:,.0f}",
        delta=f"{mrr_pct:.1f}% of target"
    )
    st.progress(min(mrr_pct / 100, 1.0))

with col3:
    conv_progress = month1.get("conversion_rate", {})
    current_conv = conv_progress.get("current", 0)
    target_conv = conv_progress.get("target", 55.0)
    conv_met = conv_progress.get("met", False)

    st.metric(
        "Conversion Rate",
        f"{current_conv:.1f}%",
        delta=f"Target: {target_conv}%",
        delta_color="normal" if conv_met else "off"
    )
    status = "✅" if conv_met else "⏳"
    st.caption(f"{status} {'Met target!' if conv_met else 'Working on it...'}")

with col4:
    churn_progress = month1.get("churn_rate", {})
    current_churn = churn_progress.get("current", 0)
    target_churn = churn_progress.get("target", 10.0)
    churn_met = churn_progress.get("met", False)

    st.metric(
        "Churn Rate",
        f"{current_churn:.1f}%",
        delta=f"Target: <{target_churn}%",
        delta_color="inverse" if churn_met else "off"
    )
    status = "✅" if churn_met else "⚠️"
    st.caption(f"{status} {'Great!' if churn_met else 'Monitor closely'}")

st.markdown("---")

# ==========================================
# Revenue Metrics
# ==========================================

st.header("💰 Revenue Metrics")

revenue = dashboard.get("revenue", {})
mrr = revenue.get("mrr", 0)
revenue_by_tier = revenue.get("revenue_by_tier", {})

col_rev1, col_rev2 = st.columns([1, 2])

with col_rev1:
    st.metric("Total MRR", f"${mrr:,.2f}")
    st.metric("Annual Run Rate", f"${(mrr * 12):,.0f}")

    # Average deal size
    users = dashboard.get("users", {})
    paying = users.get("paying", 1)
    avg_deal = mrr / paying if paying > 0 else 0
    st.metric("Avg Deal Size", f"${avg_deal:.0f}/mo")

with col_rev2:
    st.markdown("### Revenue by Tier")

    if revenue_by_tier:
        # Create bar chart data
        tiers = []
        mrrs = []
        counts = []

        for tier, data in revenue_by_tier.items():
            if data["count"] > 0:  # Only show tiers with customers
                tiers.append(tier.upper())
                mrrs.append(data["mrr"])
                counts.append(data["count"])

        if tiers:
            import pandas as pd

            df = pd.DataFrame({
                "Tier": tiers,
                "MRR": mrrs,
                "Customers": counts
            })

            st.dataframe(df, hide_index=True, use_container_width=True)

            # Show percentage breakdown
            for tier, data in revenue_by_tier.items():
                if data["count"] > 0:
                    st.progress(
                        data["percentage"] / 100,
                        text=f"{tier.upper()}: {data['percentage']:.1f}% (${data['mrr']:,.0f})"
                    )
    else:
        st.info("No paying customers yet")

st.markdown("---")

# ==========================================
# User Metrics
# ==========================================

st.header("👥 User Metrics")

users = dashboard.get("users", {})

col_user1, col_user2, col_user3 = st.columns(3)

with col_user1:
    st.metric("Total Workspaces", users.get("total", 0))

with col_user2:
    st.metric("Paying Users", users.get("paying", 0))

with col_user3:
    st.metric("Free Users", users.get("free", 0))

# Conversion funnel visualization
if users.get("total", 0) > 0:
    paying_pct = (users.get("paying", 0) / users.get("total", 1)) * 100

    st.markdown("### Conversion Funnel")
    st.progress(1.0, text=f"Total Signups: {users.get('total', 0)}")
    st.progress(
        paying_pct / 100,
        text=f"Paying: {users.get('paying', 0)} ({paying_pct:.1f}%)"
    )

st.markdown("---")

# ==========================================
# Unit Economics
# ==========================================

st.header("💵 Unit Economics")

unit_metrics = dashboard.get("metrics", {})

col_unit1, col_unit2, col_unit3, col_unit4 = st.columns(4)

with col_unit1:
    cac = unit_metrics.get("cac", 0)
    st.metric("CAC (Avg)", f"${cac:.2f}")
    st.caption("Customer Acquisition Cost")

with col_unit2:
    ltv = unit_metrics.get("ltv", 0)
    st.metric("LTV", f"${ltv:.2f}")
    st.caption("Lifetime Value")

with col_unit3:
    ltv_cac_ratio = unit_metrics.get("ltv_cac_ratio", 0)

    # Color code based on ratio
    if ltv_cac_ratio >= 3:
        ratio_color = "🟢"
        ratio_status = "Healthy"
    elif ltv_cac_ratio >= 1:
        ratio_color = "🟡"
        ratio_status = "Acceptable"
    else:
        ratio_color = "🔴"
        ratio_status = "Needs Work"

    st.metric("LTV/CAC Ratio", f"{ratio_color} {ltv_cac_ratio:.1f}:1")
    st.caption(ratio_status)

with col_unit4:
    conversion = unit_metrics.get("conversion_rate", 0)
    st.metric("Conversion Rate", f"{conversion:.1f}%")
    st.caption("Free → Paid (30 days)")

# Target comparison
st.markdown("### Target vs Actual")

col_target1, col_target2 = st.columns(2)

with col_target1:
    st.info(f"""
    **LTV/CAC Ratio**
    - Target: 27:1 (excellent)
    - Current: {ltv_cac_ratio:.1f}:1
    - Status: {"✅ Exceeds!" if ltv_cac_ratio >= 27 else "⏳ Work in progress"}
    """)

with col_target2:
    churn = unit_metrics.get("churn_rate", 0)
    st.info(f"""
    **Churn Rate**
    - Target: <10% per month
    - Current: {churn:.1f}%
    - Status: {"✅ On target!" if churn < 10 else "⚠️ Needs attention"}
    """)

st.markdown("---")

# ==========================================
# CAC by Channel
# ==========================================

st.header("📍 Acquisition Channels")

# Calculate CAC by channel
cac_by_channel = metrics.get_cac_by_channel(days=30)

if cac_by_channel:
    st.markdown("### CAC by Channel (Last 30 Days)")

    # Sort channels by CAC (lowest first)
    sorted_channels = sorted(
        cac_by_channel.items(),
        key=lambda x: x[1] if x[1] > 0 else 999
    )

    col_ch1, col_ch2 = st.columns([1, 1])

    with col_ch1:
        for channel, cac in sorted_channels:
            if cac > 0:
                # Color code: green if below average, red if above
                avg_cac = unit_metrics.get("cac", 0)
                color = "🟢" if cac < avg_cac else "🔴" if cac > avg_cac else "🟡"

                st.metric(
                    f"{color} {channel.upper()}",
                    f"${cac:.2f}",
                    delta=f"vs avg ${avg_cac:.2f}",
                    delta_color="inverse"
                )

    with col_ch2:
        st.info("""
        **Channel Optimization:**
        - 🟢 Green = Below average CAC (good!)
        - 🟡 Yellow = Average CAC
        - 🔴 Red = Above average CAC (optimize or reduce)

        **Recommended Actions:**
        - Focus spend on green channels
        - Test improvements on yellow channels
        - Consider pausing red channels
        """)
else:
    st.info("No acquisition data yet. Start tracking signups!")

st.markdown("---")

# ==========================================
# Product Usage
# ==========================================

st.header("🚀 Product Usage (Last 30 Days)")

usage = dashboard.get("usage", {})

col_usage1, col_usage2, col_usage3, col_usage4 = st.columns(4)

with col_usage1:
    st.metric("Campaigns Generated", usage.get("campaigns_generated", 0))

with col_usage2:
    st.metric("Blogs Written", usage.get("blogs_generated", 0))

with col_usage3:
    st.metric("Copy Variations", usage.get("copy_variations_generated", 0))

with col_usage4:
    st.metric("Total Content", usage.get("total_content_generated", 0))

# Usage insights
if usage.get("total_content_generated", 0) > 0 and users.get("paying", 0) > 0:
    avg_content_per_user = usage["total_content_generated"] / users["paying"]

    st.markdown("### Engagement Insights")
    st.success(f"📈 Average: {avg_content_per_user:.1f} pieces of content per paying user")

    if avg_content_per_user < 5:
        st.warning("⚠️ Low usage - consider onboarding improvements or engagement campaigns")
    elif avg_content_per_user > 20:
        st.info("💡 High usage - users are engaged! Consider upselling opportunities")

st.markdown("---")

# ==========================================
# Footer / Actions
# ==========================================

st.header("📋 Actions & Reports")

col_action1, col_action2, col_action3 = st.columns(3)

with col_action1:
    if st.button("📥 Export Data (CSV)", use_container_width=True):
        st.info("CSV export coming in Week 9")

with col_action2:
    if st.button("📊 Generate Report", use_container_width=True):
        st.info("PDF reports coming in Week 9")

with col_action3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

st.markdown("---")

# Help text
st.caption("""
**Analytics Dashboard** - Track your business performance in real-time.
Data updates automatically. Refresh page to see latest metrics.

**Need help?** Contact support@example.com
""")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
