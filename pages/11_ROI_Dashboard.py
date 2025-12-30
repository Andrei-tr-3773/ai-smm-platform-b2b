"""
ROI Dashboard - Show return on investment for AI SMM Platform.

Week 8: Task 8.5.2 - Critical for Jessica persona (Marketing Manager).

Helps users justify subscription cost to executives by showing:
- Time saved (hours/week)
- Cost savings (vs agencies/freelancers)
- Total value generated
- ROI percentage

Use case: "I need to show my CEO that this $199/month subscription
saves us $2,000+/month and 15 hours/week."
"""

import streamlit as st
from utils.auth import require_auth
from utils.roi_calculator import get_roi_calculator, BENCHMARKS
from repositories.workspace_repository import WorkspaceRepository
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

st.set_page_config(page_title="ROI Dashboard", page_icon="💰", layout="wide")

# Require authentication
user = require_auth()

st.title("💰 ROI Dashboard")

st.markdown("""
**Show your executives the value of AI-powered content creation.**

This dashboard calculates your return on investment compared to agencies,
freelancers, or manual content creation.
""")

# Get workspace info
try:
    workspace_repo = WorkspaceRepository()
    workspace = workspace_repo.get_workspace(user.workspace_id)
    plan_tier = workspace.plan_tier
except Exception as e:
    logger.error(f"Error loading workspace: {e}")
    st.error("Could not load workspace data")
    st.stop()

st.markdown("---")

# ==========================================
# ROI Settings
# ==========================================

st.header("⚙️ ROI Settings")

col_settings1, col_settings2, col_settings3 = st.columns(3)

with col_settings1:
    period = st.selectbox(
        "Time Period",
        options=[7, 30, 90, 365],
        index=1,  # Default: 30 days
        format_func=lambda x: f"Last {x} days" if x < 365 else "Last year"
    )

with col_settings2:
    comparison = st.selectbox(
        "Compare To",
        options=["agency", "freelancer", "manual"],
        format_func=lambda x: {
            "agency": "Marketing Agency",
            "freelancer": "Freelancer",
            "manual": "Manual (In-house)"
        }[x],
        help="What would you use without this platform?"
    )

with col_settings3:
    hourly_rate = st.number_input(
        "Your Hourly Rate ($)",
        min_value=20,
        max_value=200,
        value=50,
        step=5,
        help="Your team's average hourly rate for content creation"
    )

st.markdown("---")

# ==========================================
# Calculate ROI
# ==========================================

try:
    roi_calc = get_roi_calculator()
    roi_data = roi_calc.calculate_user_roi(
        user_id=str(user.id),
        workspace_id=user.workspace_id,
        plan_tier=plan_tier,
        days=period,
        hourly_rate=hourly_rate,
        comparison=comparison
    )
except Exception as e:
    logger.error(f"Error calculating ROI: {e}")
    st.error("Could not calculate ROI. Please try again.")
    st.stop()

# Check if user has any usage
usage = roi_data.get("usage", {})
total_content = usage.get("campaigns", 0) + usage.get("blogs", 0) + usage.get("copy_variations", 0)

if total_content == 0:
    st.warning("⚠️ No content generated yet in this period")
    st.info("""
    **Get started:**
    1. Generate some campaigns, blogs, or copy variations
    2. Come back to see your ROI

    **Want to see a projection?** Use the ROI Calculator below.
    """)

# ==========================================
# Executive Summary (Top Priority)
# ==========================================

st.header("📊 Executive Summary")

st.markdown(f"""
**For period:** {period} days
**Your plan:** {plan_tier.title()}
**Compared to:** {comparison.title()}
""")

# ROI Metrics
roi_metrics = roi_data.get("roi", {})
value_metrics = roi_data.get("value", {})
cost_metrics = roi_data.get("costs", {})

col_exec1, col_exec2, col_exec3, col_exec4 = st.columns(4)

with col_exec1:
    roi_pct = roi_metrics.get("percentage", 0)
    roi_color = "🟢" if roi_pct > 100 else "🟡" if roi_pct > 0 else "🔴"

    st.metric(
        "ROI",
        f"{roi_color} {roi_pct:.0f}%",
        help="Return on Investment percentage"
    )
    if roi_pct > 100:
        st.caption("✅ Excellent ROI!")
    elif roi_pct > 0:
        st.caption("💡 Positive ROI")
    else:
        st.caption("⚠️ Generate more content")

with col_exec2:
    total_value = value_metrics.get("total_value", 0)
    st.metric(
        "Total Value",
        f"${total_value:,.0f}",
        help="Total value generated (time + cost savings)"
    )
    st.caption(f"vs ${cost_metrics.get('subscription_cost', 0):.0f} subscription")

with col_exec3:
    net_savings = roi_metrics.get("net_savings", 0)
    st.metric(
        "Net Savings",
        f"${net_savings:,.0f}",
        delta=f"{roi_metrics.get('multiplier', 0):.1f}x return",
        help="Value generated minus subscription cost"
    )
    st.caption("Money saved")

with col_exec4:
    time_saved = roi_data.get("time_saved", {})
    hours_saved = time_saved.get("total_hours", 0)
    st.metric(
        "Time Saved",
        f"{hours_saved:.0f} hrs",
        help="Hours saved vs alternative method"
    )
    st.caption(f"{time_saved.get('hours_per_week', 0):.1f} hrs/week")

# Quick wins box
if roi_pct > 100:
    st.success(f"""
    ✅ **Great ROI!** You're getting **{roi_metrics.get('multiplier', 0):.1f}x** return on your subscription.

    **Bottom line:** Spending ${cost_metrics.get('subscription_cost', 0):.0f} saves you ${net_savings:,.0f} in {period} days.
    """)
elif total_content > 0:
    st.info(f"""
    💡 **Good start!** Generate more content to increase ROI.

    **Current:** {total_content} pieces of content
    **Savings so far:** ${net_savings:,.0f}
    """)

st.markdown("---")

# ==========================================
# Time Savings Breakdown
# ==========================================

st.header("⏱️ Time Savings")

time_saved = roi_data.get("time_saved", {})

col_time1, col_time2 = st.columns([2, 1])

with col_time1:
    st.markdown("### Hours Saved by Content Type")

    if total_content > 0:
        import pandas as pd

        time_df = pd.DataFrame({
            "Content Type": ["Campaigns", "Blog Posts", "Copy Variations"],
            "Count": [
                usage.get("campaigns", 0),
                usage.get("blogs", 0),
                usage.get("copy_variations", 0)
            ],
            "Hours Saved": [
                time_saved.get("campaigns", 0),
                time_saved.get("blogs", 0),
                time_saved.get("copy_variations", 0)
            ]
        })

        # Filter out rows with 0 count
        time_df = time_df[time_df["Count"] > 0]

        if not time_df.empty:
            st.dataframe(time_df, hide_index=True, use_container_width=True)

            # Visualization
            for _, row in time_df.iterrows():
                if row["Hours Saved"] > 0:
                    pct = (row["Hours Saved"] / time_saved.get("total_hours", 1)) * 100
                    st.progress(
                        pct / 100,
                        text=f"{row['Content Type']}: {row['Hours Saved']:.1f} hrs ({pct:.0f}%)"
                    )
    else:
        st.info("No content generated yet")

with col_time2:
    st.markdown("### Time Breakdown")

    total_hours = time_saved.get("total_hours", 0)
    total_days = time_saved.get("total_days", 0)
    hours_per_week = time_saved.get("hours_per_week", 0)

    st.metric("Total Hours", f"{total_hours:.1f} hrs")
    st.metric("Equivalent Days", f"{total_days:.1f} days")
    st.metric("Per Week", f"{hours_per_week:.1f} hrs/week")

    if hours_per_week > 5:
        st.success("💡 That's more than half a work day per week!")
    elif hours_per_week > 2:
        st.info("💡 Significant time savings!")

st.markdown("---")

# ==========================================
# Cost Savings Breakdown
# ==========================================

st.header("💵 Cost Savings")

cost_savings = roi_data.get("cost_savings", {})

col_cost1, col_cost2 = st.columns([2, 1])

with col_cost1:
    st.markdown(f"### Savings vs {comparison.title()}")

    if total_content > 0:
        import pandas as pd

        cost_df = pd.DataFrame({
            "Content Type": ["Campaigns", "Blog Posts", "Copy Variations"],
            "Count": [
                usage.get("campaigns", 0),
                usage.get("blogs", 0),
                usage.get("copy_variations", 0)
            ],
            "Savings": [
                cost_savings.get("campaigns", 0),
                cost_savings.get("blogs", 0),
                cost_savings.get("copy_variations", 0)
            ]
        })

        cost_df = cost_df[cost_df["Count"] > 0]

        if not cost_df.empty:
            st.dataframe(cost_df, hide_index=True, use_container_width=True)

            # Visualization
            for _, row in cost_df.iterrows():
                if row["Savings"] > 0:
                    pct = (row["Savings"] / cost_savings.get("total_saved", 1)) * 100
                    st.progress(
                        pct / 100,
                        text=f"{row['Content Type']}: ${row['Savings']:,.0f} ({pct:.0f}%)"
                    )
    else:
        st.info("No content generated yet")

with col_cost2:
    st.markdown("### Cost Comparison")

    total_saved = cost_savings.get("total_saved", 0)
    subscription_cost = cost_metrics.get("subscription_cost", 0)
    alternative_cost = cost_metrics.get("alternative_cost", 0)

    st.metric("You Paid", f"${subscription_cost:.0f}")
    st.metric("Alternative Cost", f"${alternative_cost:,.0f}")
    st.metric("You Saved", f"${total_saved:,.0f}", delta="vs alternative")

    if total_saved > subscription_cost:
        multiplier = total_saved / subscription_cost if subscription_cost > 0 else 0
        st.success(f"💰 {multiplier:.1f}x cheaper than {comparison}!")

st.markdown("---")

# ==========================================
# Comparison Table
# ==========================================

st.header("📊 Cost Comparison: AI vs Alternatives")

st.markdown("""
See how AI compares to different content creation methods.
""")

# Get comparison data
try:
    monthly_usage = {
        "campaigns": usage.get("campaigns", 0) * (30 / period),  # Normalize to monthly
        "blogs": usage.get("blogs", 0) * (30 / period),
        "copy_variations": usage.get("copy_variations", 0) * (30 / period)
    }

    comparison_data = roi_calc.get_comparison_table(plan_tier, monthly_usage)

    import pandas as pd

    comparison_df = pd.DataFrame({
        "Method": ["AI Platform", "Manual (In-house)", "Freelancer", "Agency"],
        "Monthly Cost": [
            f"${comparison_data['ai_platform']['cost']:.0f}",
            f"${comparison_data['manual']['cost']:.0f}",
            f"${comparison_data['freelancer']['cost']:.0f}",
            f"${comparison_data['agency']['cost']:.0f}"
        ],
        "Time Required": [
            f"{comparison_data['ai_platform']['time_hours']:.0f} hrs",
            f"{comparison_data['manual']['time_hours']:.0f} hrs",
            "Outsourced",
            "Outsourced"
        ],
        "ROI vs AI": [
            "Baseline",
            f"{comparison_data['manual']['roi_multiplier']:.1f}x",
            f"{comparison_data['freelancer']['roi_multiplier']:.1f}x",
            f"{comparison_data['agency']['roi_multiplier']:.1f}x"
        ]
    })

    st.dataframe(comparison_df, hide_index=True, use_container_width=True)

    # Highlight
    ai_cost = comparison_data['ai_platform']['cost']
    manual_cost = comparison_data['manual']['cost']
    freelancer_cost = comparison_data['freelancer']['cost']
    agency_cost = comparison_data['agency']['cost']

    st.info(f"""
    **AI Platform is:**
    - **{(manual_cost / ai_cost):.0f}x cheaper** than manual (in-house)
    - **{(freelancer_cost / ai_cost):.0f}x cheaper** than freelancers
    - **{(agency_cost / ai_cost):.0f}x cheaper** than agencies
    """)

except Exception as e:
    logger.error(f"Error creating comparison table: {e}")
    st.error("Could not create comparison table")

st.markdown("---")

# ==========================================
# ROI Projection Calculator
# ==========================================

st.header("🔮 ROI Projection")

st.markdown("""
**Planning to increase content production?** See projected ROI.
""")

col_proj1, col_proj2, col_proj3 = st.columns(3)

with col_proj1:
    proj_campaigns = st.number_input(
        "Campaigns per Month",
        min_value=0,
        max_value=100,
        value=max(10, usage.get("campaigns", 0)),
        step=5
    )

with col_proj2:
    proj_blogs = st.number_input(
        "Blogs per Month",
        min_value=0,
        max_value=50,
        value=max(4, usage.get("blogs", 0)),
        step=2
    )

with col_proj3:
    proj_copy = st.number_input(
        "Copy Variations per Month",
        min_value=0,
        max_value=50,
        value=max(5, usage.get("copy_variations", 0)),
        step=5
    )

if st.button("📊 Calculate Projected ROI", type="primary"):
    try:
        projection = roi_calc.get_roi_projection(
            plan_tier=plan_tier,
            campaigns_per_month=int(proj_campaigns),
            blogs_per_month=int(proj_blogs),
            copy_per_month=int(proj_copy),
            hourly_rate=hourly_rate,
            comparison=comparison
        )

        col_proj_result1, col_proj_result2, col_proj_result3, col_proj_result4 = st.columns(4)

        with col_proj_result1:
            st.metric(
                "Projected ROI",
                f"{projection['roi']['percentage']:.0f}%"
            )

        with col_proj_result2:
            st.metric(
                "Monthly Value",
                f"${projection['value']['total_value']:,.0f}"
            )

        with col_proj_result3:
            st.metric(
                "Monthly Savings",
                f"${projection['roi']['net_savings']:,.0f}"
            )

        with col_proj_result4:
            st.metric(
                "Time Saved",
                f"{projection['time_saved']['hours_per_week']:.1f} hrs/wk"
            )

        st.success(f"""
        ✅ **Projected Results:**
        - **ROI:** {projection['roi']['percentage']:.0f}% ({projection['roi']['multiplier']:.1f}x return)
        - **Monthly Savings:** ${projection['roi']['net_savings']:,.0f}
        - **Annual Savings:** ${projection['roi']['net_savings'] * 12:,.0f}
        - **Time Freed Up:** {projection['time_saved']['hours_per_week']:.1f} hours/week
        """)

    except Exception as e:
        logger.error(f"Error projecting ROI: {e}")
        st.error("Could not calculate projection")

st.markdown("---")

# ==========================================
# Export / Actions
# ==========================================

st.header("📄 Export & Share")

col_export1, col_export2, col_export3 = st.columns(3)

with col_export1:
    if st.button("📥 Download PDF Report", use_container_width=True):
        st.info("PDF export coming in Week 9")

with col_export2:
    if st.button("📧 Email to Executive", use_container_width=True):
        st.info("Email feature coming in Week 9")

with col_export3:
    if st.button("📋 Copy Summary", use_container_width=True):
        # Create summary text
        summary = f"""
ROI Summary - {plan_tier.title()} Plan ({period} days)

Total Value Generated: ${value_metrics.get('total_value', 0):,.0f}
Subscription Cost: ${cost_metrics.get('subscription_cost', 0):.0f}
Net Savings: ${roi_metrics.get('net_savings', 0):,.0f}
ROI: {roi_metrics.get('percentage', 0):.0f}% ({roi_metrics.get('multiplier', 0):.1f}x return)

Time Saved: {time_saved.get('total_hours', 0):.0f} hours ({time_saved.get('hours_per_week', 0):.1f} hrs/week)
Cost Savings: ${cost_savings.get('total_saved', 0):,.0f} vs {comparison}

Content Generated:
- {usage.get('campaigns', 0)} campaigns
- {usage.get('blogs', 0)} blog posts
- {usage.get('copy_variations', 0)} copy variations

Bottom Line: Investing ${cost_metrics.get('subscription_cost', 0):.0f} generated ${value_metrics.get('total_value', 0):,.0f} in value.
        """
        st.code(summary)
        st.success("✅ Summary ready to copy!")

st.markdown("---")

# ==========================================
# Benchmarks & Methodology
# ==========================================

with st.expander("ℹ️ How ROI is Calculated", expanded=False):
    st.markdown("""
    ### Methodology

    **Time Saved:**
    - Campaign (manual): 2 hours → AI: 15 minutes = **1.75 hours saved**
    - Blog post (manual): 4 hours → AI: 30 minutes = **3.5 hours saved**
    - Copy variations (manual): 1.5 hours → AI: 10 minutes = **1.33 hours saved**

    **Cost Benchmarks:**
    - Agency campaign: $200 | Blog: $400 | Copy: $150
    - Freelancer campaign: $100 | Blog: $150 | Copy: $75
    - Manual: Hourly rate × time (+ 30% overhead)

    **ROI Formula:**
    ```
    Total Value = (Time Saved × Hourly Rate) + Cost Savings
    ROI % = ((Total Value - Subscription Cost) / Subscription Cost) × 100
    ```

    **Industry Rates:**
    - Marketing Manager: $50/hour (avg)
    - Freelancer: $40/hour
    - Agency: $100/hour
    """)

st.caption(f"""
**ROI Dashboard** - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

**Questions?** Contact support@example.com
""")
