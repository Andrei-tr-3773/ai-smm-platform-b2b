"""
Campaign Analytics & Insights Dashboard.

This page shows the KILLER FEATURE - AI explains WHY content performed
well or poorly, providing actionable insights and recommendations.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta
from agents.analytics_agent import analyze_campaign
from analytics.mock_analytics_generator import MockAnalyticsGenerator
from analytics.analytics_models import CampaignMetrics

st.set_page_config(page_title="Campaign Analytics", page_icon="📊", layout="wide")

st.title("📊 Campaign Analytics & Insights")

st.markdown("""
Understand **WHAT** worked and **WHY**. Get actionable insights powered by AI.
""")

# Mock Data Transparency Check
# TODO: Replace with real campaign data check
campaign_days_old = 5  # Example: campaign is 5 days old (< 30 days)
has_real_data = campaign_days_old >= 30

if not has_real_data:
    # Show transparency disclaimer
    st.info(f"""
    📊 **Analytics will be available after 30 days of campaign data.**

    Your campaign has been running for {campaign_days_old} days. Analytics require at least 30 days
    of engagement data to provide accurate insights.

    **Want to see what analytics look like?**
    """)

    col1, col2 = st.columns([1, 3])
    with col1:
        show_demo = st.button("📈 Show Demo Analytics", type="primary")
    with col2:
        st.caption("Demo analytics use industry benchmarks to show you what insights look like.")

    if not show_demo and 'analytics_result' not in st.session_state:
        # Don't show analytics yet
        st.markdown("---")
        st.markdown("### 💡 Why 30 days?")
        st.markdown("""
        - Social media algorithms take 7-14 days to distribute content
        - Weekend vs weekday patterns need 4 weeks to detect
        - Viral spikes can occur up to 21 days after posting
        - Industry benchmarks are based on 30-day performance
        """)

        # NEW: Manual Metrics Entry Option
        st.markdown("---")
        st.markdown("### 📝 Already Posted? Enter Your Metrics")
        st.markdown("""
        If you've already posted this campaign to Instagram/Facebook and have engagement data,
        you can enter it manually to get AI-powered insights right now!
        """)

        with st.expander("➕ Enter Manual Metrics", expanded=False):
            st.markdown("**Enter your campaign's engagement metrics from Instagram/Facebook:**")

            col1, col2 = st.columns(2)
            with col1:
                manual_views = st.number_input("👁️ Views", min_value=0, value=0, step=100)
                manual_likes = st.number_input("❤️ Likes", min_value=0, value=0, step=10)
                manual_comments = st.number_input("💬 Comments", min_value=0, value=0, step=1)
            with col2:
                manual_shares = st.number_input("🔄 Shares", min_value=0, value=0, step=1)
                manual_saves = st.number_input("🔖 Saves", min_value=0, value=0, step=1)
                manual_clicks = st.number_input("🔗 Link Clicks", min_value=0, value=0, step=1)

            if st.button("🎯 Analyze My Metrics", type="primary"):
                if manual_views > 0:
                    st.session_state['manual_metrics'] = {
                        'views': manual_views,
                        'likes': manual_likes,
                        'comments': manual_comments,
                        'shares': manual_shares,
                        'saves': manual_saves,
                        'clicks': manual_clicks
                    }
                    st.session_state['use_manual_metrics'] = True
                    st.success("✅ Metrics saved! Generating insights...")
                    st.rerun()
                else:
                    st.error("Please enter at least your Views count")

        if not st.session_state.get('use_manual_metrics', False):
            st.markdown("---")
            st.info("In the meantime, focus on creating great content! 🚀")
            st.stop()  # Don't show analytics UI
    elif show_demo:
        # User clicked "Show Demo Analytics" - set flag
        st.session_state['show_demo_analytics'] = True
        st.warning("⚠️ **Demo Mode:** These analytics are based on industry benchmarks, not your actual campaign data.")

# Campaign selection
st.sidebar.subheader("Select Campaign")

# TODO: Get real campaigns from MongoDB
# For now, use mock data
campaign_options = {
    "Viral Fitness Class (Dec 2025)": {"id": "camp_001", "industry": "fitness", "platform": "instagram_reels", "viral": True},
    "SaaS Feature Launch (Nov 2025)": {"id": "camp_002", "industry": "saas", "platform": "linkedin", "viral": False},
    "E-commerce Flash Sale (Dec 2025)": {"id": "camp_003", "industry": "ecommerce", "platform": "tiktok", "viral": True}
}

selected_campaign_name = st.sidebar.selectbox(
    "Campaign:",
    options=list(campaign_options.keys())
)

campaign_config = campaign_options[selected_campaign_name]

# Generate analytics (mock OR manual metrics)
generate_trigger = st.sidebar.button("🔄 Generate Analytics") or st.session_state.get('use_manual_metrics', False)

if generate_trigger:
    with st.spinner("🤖 AI is analyzing your campaign... (15 seconds)"):
        try:
            generator = MockAnalyticsGenerator(
                industry=campaign_config["industry"],
                platform=campaign_config["platform"]
            )

            # Check if user provided manual metrics
            if st.session_state.get('use_manual_metrics', False):
                # Use manual metrics entered by user
                manual = st.session_state['manual_metrics']

                # Create single-day metric from manual data
                total_engagement = manual['likes'] + manual['comments'] + manual['shares']
                engagement_rate = total_engagement / manual['views'] if manual['views'] > 0 else 0

                metric = CampaignMetrics(
                    campaign_id=campaign_config["id"],
                    date=date.today(),
                    views=manual['views'],
                    likes=manual['likes'],
                    comments=manual['comments'],
                    shares=manual['shares'],
                    saves=manual['saves'],
                    clicks=manual['clicks'],
                    engagement_rate=engagement_rate,
                    save_rate=manual['saves'] / manual['views'] if manual['views'] > 0 else 0,
                    click_through_rate=manual['clicks'] / manual['views'] if manual['views'] > 0 else 0,
                    virality_score=(manual['shares'] / manual['views'] * 100) if manual['views'] > 0 else 0,
                    platform=campaign_config["platform"]
                )

                # Generate 30 days of projected metrics based on manual input
                start = date.today() - timedelta(days=29)
                base_virality = metric.virality_score / 10  # Scale to 1.0-3.0 range

                metrics = generator.generate_campaign_metrics(
                    campaign_id=campaign_config["id"],
                    start_date=start,
                    days=30,
                    virality_factor=max(1.0, base_virality)  # Use manual data to calibrate
                )

                # Replace last day with actual manual metrics
                metrics[-1] = metric

                st.info("📊 Using your manual metrics + AI-projected historical data for insights")

            else:
                # Generate mock data (demo mode)
                start = date.today() - timedelta(days=30)
                virality_factor = 2.5 if campaign_config["viral"] else 1.0

                metrics = generator.generate_campaign_metrics(
                    campaign_id=campaign_config["id"],
                    start_date=start,
                    days=30,
                    virality_factor=virality_factor
                )

                if campaign_config["viral"]:
                    metrics = generator.inject_viral_spike(metrics, spike_day=3, spike_magnitude=4.0)

            benchmark = generator.generate_benchmark_data()

            # Run analytics agent
            analysis = analyze_campaign(
                campaign_id=campaign_config["id"],
                metrics=metrics,
                benchmark=benchmark
            )

            # Store in session state
            st.session_state['analytics_metrics'] = metrics
            st.session_state['analytics_result'] = analysis

            # Clear manual metrics flag
            st.session_state['use_manual_metrics'] = False

            st.success("✅ Analysis complete!")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# Display analytics (if available)
if 'analytics_result' in st.session_state:
    metrics = st.session_state['analytics_metrics']
    analysis = st.session_state['analytics_result']

    # Performance Summary
    st.markdown("---")
    st.subheader("📈 Performance Summary")

    performance = analysis['performance_summary']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        rating = performance['overall_rating']
        emoji = {"excellent": "🟢", "good": "🟡", "average": "🟠", "below_average": "🔴"}
        st.metric(
            label="Overall Rating",
            value=rating.replace('_', ' ').title(),
            delta=emoji[rating]
        )

    with col2:
        st.metric(
            label="Total Views",
            value=f"{performance['total_views']:,}"
        )

    with col3:
        st.metric(
            label="Total Engagement",
            value=f"{performance['total_engagement']:,}",
            delta=f"{performance['avg_engagement_rate']*100:.1f}% rate"
        )

    with col4:
        st.metric(
            label="vs. Benchmark",
            value=performance['vs_benchmark']
        )

    # Engagement Chart
    st.markdown("---")
    st.subheader("📊 Engagement Over Time")

    # Prepare data for chart
    dates = [m.date for m in metrics]
    views = [m.views for m in metrics]
    engagement_rates = [m.engagement_rate * 100 for m in metrics]

    # Create dual-axis chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=dates,
        y=views,
        name="Views",
        marker_color='lightblue',
        yaxis='y'
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=engagement_rates,
        name="Engagement Rate (%)",
        mode='lines+markers',
        marker_color='orange',
        yaxis='y2'
    ))

    fig.update_layout(
        yaxis=dict(title="Views"),
        yaxis2=dict(title="Engagement Rate (%)", overlaying='y', side='right'),
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Patterns Detected
    st.markdown("---")
    st.subheader("🔍 Detected Patterns")

    patterns = analysis['detected_patterns']

    if patterns:
        for pattern in patterns:
            impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}

            with st.expander(f"{impact_emoji[pattern.impact]} {pattern.description}", expanded=(pattern.impact == "high")):
                st.markdown(f"**Type:** {pattern.pattern_type.replace('_', ' ').title()}")
                st.markdown(f"**Impact:** {pattern.impact.title()}")
                st.markdown(f"**Date Range:** {pattern.date_range[0]} to {pattern.date_range[1]}")
    else:
        st.info("No significant patterns detected in this campaign.")

    # Content Insights (WHY) - KILLER FEATURE
    st.markdown("---")
    st.subheader("💡 Why It Worked (or Didn't)")

    insights = analysis['content_insights']

    for insight in insights:
        confidence_color = "🟢" if insight.confidence >= 0.8 else "🟡" if insight.confidence >= 0.6 else "🟠"

        with st.expander(f"{confidence_color} {insight.explanation}", expanded=True):
            st.markdown(f"**Type:** {insight.insight_type.replace('_', ' ').title()}")
            st.markdown(f"**Confidence:** {insight.confidence*100:.0f}%")

            if insight.evidence:
                st.markdown("**Evidence:**")
                for evidence in insight.evidence:
                    st.markdown(f"- {evidence}")

    # Recommendations
    st.markdown("---")
    st.subheader("🎯 Recommendations for Next Campaign")

    recommendations = analysis['recommendations']

    for i, rec in enumerate(recommendations, 1):
        st.success(f"**{i}.** {rec}")

    # Next Month Strategy
    st.markdown("---")
    st.subheader("📅 Next Month Strategy")

    st.info(analysis['next_month_strategy'])

    # Demo Data Disclaimer (if showing demo analytics)
    if st.session_state.get('show_demo_analytics', False):
        st.markdown("---")
        st.warning("""
        **⚠️ Demo Analytics Notice**

        These analytics are generated using industry benchmarks and statistical patterns.
        They demonstrate what insights will look like once your campaign has 30 days of real data.

        **To get real analytics:**
        - Wait for 30 days after campaign launch
        - Real engagement data will automatically replace demo data
        - All insights will be based on your actual performance
        """)

    # Export Button
    st.markdown("---")

    if st.button("📄 Export Report as PDF"):
        st.info("💡 PDF export coming soon!")

else:
    st.info("👈 Select a campaign and click 'Generate Analytics' to see insights.")
