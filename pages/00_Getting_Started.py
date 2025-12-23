import streamlit as st

st.set_page_config(page_title="Getting Started", page_icon="🚀", layout="wide")

st.title("🚀 Getting Started with AI SMM Platform")

st.markdown("""
Create professional social media content for **Instagram, Facebook, Telegram, and LinkedIn** in minutes, not hours.

**Perfect for:**
- 🏋️ Fitness studios and gyms
- 🛍️ E-commerce stores
- 💻 SaaS companies
- 📊 Marketing agencies
- 🏢 Any B2B business
""")

# Quick Start
st.header("📚 Quick Start Guide")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1️⃣ Create Campaign")
    st.markdown("""
    1. Go to **Home** tab
    2. Select template
    3. Choose audience
    4. Enter campaign query
    5. Click **Generate Content**
    6. Review & download

    ⏱️ **Takes 15 minutes** (not 2.5 hours)
    """)

with col2:
    st.subheader("2️⃣ Translate Content")
    st.markdown("""
    - Select target languages
    - AI translates with cultural adaptation
    - Natural, not robotic
    - 15+ languages supported
    - Quality evaluation included

    🌍 **Instant multilingual content**
    """)

with col3:
    st.subheader("3️⃣ Export & Use")
    st.markdown("""
    - Export as HTML, PDF, DOCX
    - Copy to clipboard
    - Post to social media
    - Track what works
    - Iterate and improve

    📊 **Monitor API costs in sidebar**
    """)

# Demo Campaigns
st.header("🎬 Try Demo Campaigns")

st.markdown("Copy these example queries to get started quickly:")

demos = [
    {
        "business": "FitZone Fitness",
        "icon": "🏋️",
        "persona": "Small Business Owner",
        "name": "New HIIT Class Announcement",
        "query": "Announce Sarah's HIIT class on Saturday at 10 AM - burn 500 calories in 45 minutes!",
        "platform": "Instagram",
        "template": "New Class Announcement",
        "time_saved": "Saves 2 hours vs. Canva"
    },
    {
        "business": "CloudFlow SaaS",
        "icon": "💻",
        "persona": "Marketing Manager",
        "name": "Feature Release",
        "query": "Announce new API endpoint that makes database queries 10x faster, solving slow data retrieval",
        "platform": "LinkedIn",
        "template": "Product Update",
        "time_saved": "Saves 3 hours vs. manual writing"
    },
    {
        "business": "ShopStyle E-commerce",
        "icon": "🛍️",
        "persona": "E-commerce Owner",
        "name": "Product Launch",
        "query": "Launch new winter dress collection, prices starting at $79, 30% off this week only",
        "platform": "Facebook",
        "template": "Sale Announcement",
        "time_saved": "Saves 2.5 hours vs. DIY"
    }
]

for demo in demos:
    with st.expander(f"{demo['icon']} {demo['business']}: {demo['name']}", expanded=False):
        st.markdown(f"""
        **Platform:** {demo['platform']} | **Target:** {demo['persona']}

        **Template:** {demo['template']}

        **Query:**
        ```
        {demo['query']}
        ```

        💡 {demo['time_saved']}
        """)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.code(demo['query'], language=None)
        with col2:
            if st.button(f"Load Demo", key=f"load_{demo['name']}", type="primary"):
                # Store demo data in session state
                st.session_state['demo_loaded'] = True
                st.session_state['demo_query'] = demo['query']
                st.session_state['demo_template'] = demo['template']
                st.session_state['demo_platform'] = demo['platform']

                # Determine industry based on business type
                if "Fitness" in demo['business']:
                    st.session_state['demo_industry'] = "fitness"
                elif "SaaS" in demo['business'] or "CloudFlow" in demo['business']:
                    st.session_state['demo_industry'] = "saas"
                else:
                    st.session_state['demo_industry'] = "ecommerce"

                st.success("✅ Demo loaded! Go to **Home** tab to generate content →")

# Social Proof
st.header("🏆 What Our Users Say")

testimonial_cols = st.columns(3)

with testimonial_cols[0]:
    st.markdown("""
    > "We went from **2.5 hours per post to 15 minutes**. Our Instagram engagement increased **40%** with Spanish translations!"

    **Alex Rodriguez**
    Owner, FitZone Fitness (Austin, TX)
    🏋️ Fitness Studio • 3 locations
    """)

with testimonial_cols[1]:
    st.markdown("""
    > "Replaced Jasper + Canva. **Saved $1,344/year** and our B2B content quality improved significantly."

    **Jessica Kim**
    Marketing Manager, CloudFlow
    💻 SaaS Startup • $2M ARR
    """)

with testimonial_cols[2]:
    st.markdown("""
    > "Now we serve **50 clients** instead of 25, without hiring more staff. **Game changer** for our agency."

    **Carlos Santos**
    CEO, Digital Boost Agency
    📊 25 small business clients
    """)

# Pricing Comparison
st.header("💰 Why Switch to Our Platform?")

st.markdown("### Compare: DIY vs. Agency vs. Our Platform")

comparison_data = {
    "Method": ["🏢 Hire Agency", "🎨 DIY (Canva + Jasper)", "🚀 Our Platform"],
    "Time per Post": ["0 hours (outsourced)", "2.5 hours", "**15 minutes**"],
    "Cost per Month": ["$2,500", "$112", "**$49-199**"],
    "Quality": ["⭐⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐"],
    "Multilingual": ["✅ (expensive)", "❌ Manual", "✅ **Automatic**"],
    "Custom Templates": ["✅ (slow)", "❌ Generic", "✅ **Instant**"]
}

st.table(comparison_data)

savings_cols = st.columns(3)
with savings_cols[0]:
    st.metric("💰 Save vs. Agency", "$30k/year", delta="-92%", delta_color="normal")
with savings_cols[1]:
    st.metric("⏱️ Save vs. DIY", "10 hours/week", delta="10x faster", delta_color="normal")
with savings_cols[2]:
    st.metric("🔧 Replace Tools", "3 → 1", delta="Jasper + Canva + Translate", delta_color="normal")

# CTA Section
st.markdown("---")
st.header("🎯 Ready to Get Started?")

cta_cols = st.columns(3)

with cta_cols[0]:
    st.markdown("""
    ### 🏋️ Small Business?
    **Perfect for:** Fitness, local stores, services

    **Start with:**
    - Try FitZone demo (above)
    - Free tier: 10 posts/month
    - Upgrade to $49/mo as needed
    """)
    if st.button("Try FitZone Demo →", key="cta_small_business", type="primary", use_container_width=True):
        st.switch_page("Home.py")

with cta_cols[1]:
    st.markdown("""
    ### 💻 Marketing Manager?
    **Perfect for:** SaaS, B2B tech, agencies

    **Start with:**
    - Try CloudFlow demo (above)
    - 14-day Pro trial
    - Team plan: $199/mo
    """)
    if st.button("Try CloudFlow Demo →", key="cta_marketing", type="primary", use_container_width=True):
        st.switch_page("Home.py")

with cta_cols[2]:
    st.markdown("""
    ### 📊 Digital Agency?
    **Perfect for:** Multi-client agencies

    **Start with:**
    - Try ShopStyle demo (above)
    - White-label available
    - Agency plan: $499/mo
    """)
    if st.button("Try ShopStyle Demo →", key="cta_agency", type="primary", use_container_width=True):
        st.switch_page("Home.py")

# Platforms
st.markdown("---")
st.header("📱 Supported Platforms")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📸 Instagram
    - Feed posts
    - Visual content optimization
    - Hashtag suggestions (coming soon)
    - Stories (coming soon)

    **Best for:** Visual businesses (fitness, fashion, food)
    **Audience:** Young adults 18-35

    ### 📘 Facebook
    - Posts optimized for engagement
    - Community building
    - Local business reach
    - Groups (coming soon)

    **Best for:** Local businesses, community building
    **Audience:** Broader age range, local communities
    """)

with col2:
    st.markdown("""
    ### ✈️ Telegram
    - Channel posts with rich formatting
    - Group messages
    - Instant notifications
    - Bot integration (coming soon)

    **Best for:** Engaged communities, announcements
    **Audience:** Tech-savvy, international markets

    ### 💼 LinkedIn
    - Professional tone optimization
    - B2B thought leadership
    - Industry-specific content
    - Articles (coming soon)

    **Best for:** B2B, SaaS, professional services
    **Audience:** Professionals, decision-makers
    """)

# Industries
st.header("🏢 Industries We Serve")

industries = {
    "🏋️ Fitness & Wellness": "Gyms, yoga studios, personal trainers, nutrition coaches, wellness centers",
    "🛍️ E-commerce": "Fashion, electronics, handmade goods, dropshipping, online stores",
    "💻 SaaS & Tech": "Software companies, apps, developer tools, cloud services, B2B tech",
    "📊 Consulting": "Business consulting, coaching, training, advisory, professional services",
    "🏥 Local Services": "Dentists, lawyers, accountants, real estate, local professionals",
    "🎨 Digital Agencies": "Marketing agencies serving multiple clients, white-label solutions",
    "📚 Education": "Online courses, tutoring, schools, training programs, e-learning",
    "🍕 Food & Beverage": "Restaurants, cafes, catering, food delivery, culinary businesses"
}

cols = st.columns(2)
for i, (industry, description) in enumerate(industries.items()):
    with cols[i % 2]:
        st.markdown(f"""
        **{industry}**

        {description}
        """)

# Tips
st.header("💡 Tips for Best Results")

tip_cols = st.columns(2)

with tip_cols[0]:
    st.markdown("""
    **✍️ Be Specific**
    The more details, the better. Instead of "new product", say "new winter dress collection with 30% discount".

    **📱 Choose Right Platform**
    Instagram for visual, LinkedIn for professional, Telegram for community, Facebook for local.

    **✅ Review Before Publishing**
    AI content is a starting point. Always review and adapt to your brand voice.
    """)

with tip_cols[1]:
    st.markdown("""
    **🌍 Test Translations**
    Have native speakers review translated content for accuracy and cultural appropriateness.

    **🎨 Use Templates**
    Select templates that match your content type for better, faster results.

    **💰 Monitor API Usage**
    Check the sidebar to track your OpenAI API costs and stay within budget.
    """)

# Features
st.header("✨ Key Features")

feature_cols = st.columns(3)

with feature_cols[0]:
    st.markdown("""
    **🎯 Smart Content Generation**
    - Context-aware AI (GPT-4o-mini)
    - Platform-specific optimization
    - Audience targeting
    - Template-based generation
    - RAG-enhanced context
    """)

with feature_cols[1]:
    st.markdown("""
    **🌍 Multi-language Support**
    - 15+ languages supported
    - Cultural adaptation
    - Quality evaluation (G-Eval)
    - Professional translations
    - Reflection pattern for accuracy
    """)

with feature_cols[2]:
    st.markdown("""
    **📊 Cost Tracking & Monitoring**
    - Real-time API usage
    - Budget monitoring
    - Usage by model
    - Monthly reports
    - Cost per campaign
    """)

# Final CTA
st.markdown("---")
st.success("✨ **Ready to create your first campaign?** Choose a demo above or head to the **Home** tab!")

# Footer
st.markdown("---")
st.caption("""
**Note:** This platform uses AI to generate content. Always review and verify generated content before publishing.
See the disclaimer in the Home tab for more information.

📊 **Stats:** 500+ campaigns created • 15+ languages supported • 8 industries served
""")
