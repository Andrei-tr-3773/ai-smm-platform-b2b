import streamlit as st
import json

st.set_page_config(page_title="Getting Started", page_icon="🚀")

st.title("🚀 Getting Started")

# Welcome section - 30-second pitch
st.markdown("""
**Welcome!** Create your first viral marketing campaign in 3 minutes.

This platform generates professional social media content for **Instagram, Facebook, LinkedIn, and Telegram** using AI. Perfect for small businesses, agencies, and marketing teams.
""")

# Quick Start Guide - 5 steps
with st.expander("📖 Quick Start Guide", expanded=True):
    st.markdown("""
    **Step 1:** Choose your target audience from the **Audiences** tab (or use "General Audience")

    **Step 2:** Pick your platform: Instagram, Facebook, LinkedIn, or Telegram

    **Step 3:** Generate content using templates or 🔥 **Viral Patterns** for best results

    **Step 4:** Translate to 15+ languages (optional but recommended for international reach)

    **Step 5:** Export & Post - Download as PDF, DOCX, or HTML and publish!

    ⏱️ **Takes 3 minutes** (vs. 2+ hours manually)
    """)

# Demo Campaigns - Click to load
st.subheader("💡 Try Demo Campaigns")
st.markdown("Click any button below to load a ready-to-use campaign:")

demo_col1, demo_col2, demo_col3 = st.columns(3)

with demo_col1:
    st.markdown("### 🏋️ Fitness")
    st.caption("30-day transformation challenge")
    if st.button("Load Fitness Demo", key="fitness_demo", use_container_width=True, type="primary"):
        # Store demo data in session state
        st.session_state['demo_loaded'] = True
        st.session_state['demo_query'] = "Launch a 30-day transformation challenge starting January 15th. Results guaranteed: lose 10 pounds, gain muscle, boost energy. Includes meal plan, workout videos, and weekly coaching calls. Early bird special: $199 (regular $299). Limited to 20 participants."
        st.session_state['demo_template'] = "Sale Announcement"
        st.session_state['demo_platform'] = "Instagram"
        st.session_state['demo_industry'] = "fitness"
        st.success("✅ Demo loaded! Go to **Home** tab to generate content →")

with demo_col2:
    st.markdown("### 💼 SaaS")
    st.caption("Announce new AI feature")
    if st.button("Load SaaS Demo", key="saas_demo", use_container_width=True, type="primary"):
        st.session_state['demo_loaded'] = True
        st.session_state['demo_query'] = "Announce our new AI-powered analytics dashboard that automatically identifies trends and predicts customer churn with 95% accuracy. Save 10 hours per week on manual data analysis. Available now for Pro and Enterprise plans. Book a demo to see it in action."
        st.session_state['demo_template'] = "Product Update"
        st.session_state['demo_platform'] = "LinkedIn"
        st.session_state['demo_industry'] = "saas"
        st.success("✅ Demo loaded! Go to **Home** tab to generate content →")

with demo_col3:
    st.markdown("### 🛍️ E-commerce")
    st.caption("Promote Black Friday sale")
    if st.button("Load E-commerce Demo", key="ecommerce_demo", use_container_width=True, type="primary"):
        st.session_state['demo_loaded'] = True
        st.session_state['demo_query'] = "Black Friday MEGA SALE: Up to 70% off on all electronics! New iPhone 15 Pro - $899 (save $200), AirPods Pro - $179 (save $70), MacBook Air - $899 (save $300). Free shipping on orders over $50. Sale ends Sunday midnight. Shop now while supplies last!"
        st.session_state['demo_template'] = "Sale Announcement"
        st.session_state['demo_platform'] = "Facebook"
        st.session_state['demo_industry'] = "ecommerce"
        st.success("✅ Demo loaded! Go to **Home** tab to generate content →")

# Video Tutorial
st.markdown("---")
st.subheader("🎥 Video Tutorial (3 min)")
st.markdown("Watch how to create your first campaign:")

# Placeholder for video - user can replace with actual Loom URL later
video_placeholder = st.empty()
with video_placeholder.container():
    st.info("""
    📹 **Video tutorial coming soon!**

    For now, follow the Quick Start Guide above or try a demo campaign.
    """)
    # Uncomment and add real video URL when available:
    # st.video("https://www.loom.com/embed/your-video-id-here")

# Tips & Best Practices
st.markdown("---")
with st.expander("💡 Tips & Best Practices", expanded=False):
    st.markdown("""
    **For Best Results:**
    - ✅ Use **viral patterns** (generates content with 2-3x more engagement)
    - ✅ Post at optimal times:
        - Instagram: 9-11 AM, 7-9 PM
        - Facebook: 1-3 PM weekdays
        - LinkedIn: 7-8 AM, 12 PM, 5-6 PM
        - Telegram: 8-10 AM, 8-10 PM
    - ✅ Test different hooks (first 3 seconds matter!)
    - ✅ Use platform optimization for hashtags and formatting
    - ✅ Translate content for international audiences (15+ languages)

    **Avoid:**
    - ❌ Generic hooks like "Check this out!" or "You won't believe..."
    - ❌ Too many hashtags (max 11 for Instagram, 5 for LinkedIn)
    - ❌ Same exact content across all platforms (customize per platform)
    - ❌ Posting without reviewing AI-generated content first

    **Pro Tips:**
    - 📊 Use the **Analytics** page to track what content performs best
    - 🎯 Create specific audiences for better targeting
    - 🔄 Generate multiple variations and A/B test
    - 💰 Monitor API costs in the sidebar to stay on budget
    """)

# Success metrics
st.markdown("---")
st.subheader("🎯 What You'll Achieve")

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric(
        label="⏱️ Time Saved",
        value="2+ hours",
        delta="per campaign",
        help="Compared to manual content creation"
    )

with metric_col2:
    st.metric(
        label="🚀 Engagement Boost",
        value="2-3x",
        delta="with viral patterns",
        help="Using proven viral content templates"
    )

with metric_col3:
    st.metric(
        label="🌍 Languages",
        value="15+",
        delta="instant translation",
        help="Reach global audiences effortlessly"
    )

# Navigation CTA
st.markdown("---")
st.info("""
👉 **Ready to start?**

1. Try a demo campaign above, OR
2. Go to **Home** tab and create your own campaign from scratch
""")

# Footer
st.caption("""
**Note:** AI-generated content should always be reviewed before publishing. This tool helps you create drafts faster, not replace human creativity.
""")
