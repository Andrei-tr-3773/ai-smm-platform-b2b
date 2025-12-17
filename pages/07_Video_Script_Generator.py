# 07_Video_Script_Generator.py
import streamlit as st
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents.video_script_agent import VideoScriptAgent
from repositories.audience_repository import AudienceRepository
from utils.ui_components import init_page_settings, load_css
from utils.mongodb_utils import MongoDBClient
import logging
from weasyprint import HTML
from pdf2docx import Converter
import io

# Load environment variables
load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)

# Set page configuration
init_page_settings()
load_css("./static/ui/css/styles.css")

st.title("🎬 Video Script Generator")
st.markdown("""
Transform your marketing campaigns into **viral-ready video scripts** with shot-by-shot guidance.

**How it works:**
1. Paste your campaign content or write a new one
2. Select platform (Instagram Reels, TikTok, YouTube Shorts, etc.)
3. Choose target audience and content goal
4. AI selects best viral pattern and generates production-ready script
5. Get virality score + production notes for smartphone filming

**Based on 30 proven viral patterns!** 🚀
""")

# Initialize session state
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = None
if 'video_script_agent' not in st.session_state:
    # Initialize AI agent
    model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")
    )
    st.session_state.video_script_agent = VideoScriptAgent(model=model)

# Sidebar - Example Campaigns
with st.sidebar:
    st.header("📚 Example Campaigns")
    st.markdown("Click to use these examples:")

    examples = [
        {
            "name": "🏋️ Fitness Class Launch",
            "content": """🔥 NEW CLASS ALERT! 🔥

Join Sarah Martinez for our brand new HIIT Cardio Blast class!

📅 Every Saturday at 10:00 AM
⏱️ 45 minutes of high-energy cardio
💪 Burn up to 500 calories
🎯 All fitness levels welcome

First class FREE for new members!

Register now at FitZone.com or call (555) 123-4567""",
            "platform": "instagram_reels",
            "goal": "Drive class registrations"
        },
        {
            "name": "💻 SaaS Feature Launch",
            "content": """🚀 NEW FEATURE: Lightning-Fast API v3

We just launched our biggest update yet!

✨ What's New:
• 10x faster query processing
• Real-time data streaming
• Enhanced security protocols
• Zero downtime migration

Perfect for high-traffic applications that need speed + reliability.

Try it free for 30 days → CloudFlow.io/api-v3""",
            "platform": "tiktok",
            "goal": "Drive API v3 trial signups"
        },
        {
            "name": "🛍️ E-commerce Flash Sale",
            "content": """❄️ WINTER FLASH SALE ❄️

30% OFF All Winter Dresses!

This week only - while supplies last!

🛍️ 200+ styles available
📦 Free shipping over $50
💳 Easy returns within 30 days

Shop the collection at ShopStyle.com

Use code: WINTER30 at checkout""",
            "platform": "youtube_shorts",
            "goal": "Drive flash sale purchases"
        },
        {
            "name": "🎯 B2B Webinar",
            "content": """🎯 Ready to Scale Your B2B Sales?

Join our FREE webinar: "From $1M to $10M ARR in 18 Months"

Learn the exact framework we used with 50+ B2B companies:
✓ Inbound lead generation strategies
✓ Sales process optimization
✓ Account-based marketing tactics
✓ Revenue team alignment

Thursday, Jan 25th at 2:00 PM EST

Limited to 100 attendees. Register at GrowthConsulting.com/webinar""",
            "platform": "linkedin",
            "goal": "Drive webinar registrations"
        },
        {
            "name": "🍕 Restaurant Promotion",
            "content": """🍕 NEW MENU ALERT! 🍕

Introducing our Artisan Pizza Collection!

Hand-stretched dough, wood-fired perfection, premium ingredients from Italy.

Try our signature pizzas:
🔥 Truffle Mushroom Dream
🌶️ Spicy Calabrian
🧀 Four Cheese Heaven

Special Launch Price: Buy 1 Get 1 50% OFF
This weekend only!

Order at TasteOfRome.com or call (555) PIZZA-123""",
            "platform": "instagram_reels",
            "goal": "Drive weekend orders"
        },
        {
            "name": "📚 Online Course Launch",
            "content": """📚 Master Python in 30 Days! 📚

Join 10,000+ students who transformed their coding skills.

What you'll learn:
✅ Python fundamentals to advanced
✅ Build 12 real-world projects
✅ Web scraping, APIs, data analysis
✅ Career-ready portfolio

🎁 Early Bird Special: 50% OFF
💰 Only $49 (regular $99)
⏰ Offer ends in 48 hours!

Enroll now at CodeMastery.com/python""",
            "platform": "tiktok",
            "goal": "Drive course enrollments"
        },
        {
            "name": "🏡 Real Estate Open House",
            "content": """🏡 OPEN HOUSE THIS SUNDAY! 🏡

Stunning 4BR/3BA Modern Home in Riverside

Features:
🌟 Gourmet kitchen with marble counters
🌟 Spa-like master bathroom
🌟 Backyard oasis with pool
🌟 Smart home technology
🌟 Walking distance to top schools

📍 123 Maple Street, Riverside
🕐 Sunday 1-4 PM
💰 $799,000

Contact Lisa Chen: (555) 987-6543""",
            "platform": "facebook_video",
            "goal": "Drive open house attendance"
        }
    ]

    for example in examples:
        if st.button(example['name'], key=f"example_{example['name']}", use_container_width=True):
            st.session_state.example_campaign = example['content']
            st.session_state.example_platform = example['platform']
            st.session_state.example_goal = example['goal']
            st.rerun()

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📝 Campaign Input")

    # Campaign content input
    campaign_content = st.text_area(
        "Campaign Content",
        value=st.session_state.get('example_campaign', ''),
        height=300,
        placeholder="""Paste your existing campaign or write a new one here...

Example:
🔥 NEW PRODUCT LAUNCH! 🔥
Introducing our latest innovation...
""",
        help="Your marketing campaign text. Can be from an existing campaign or a new one."
    )

    # Platform selector
    platforms = {
        "Instagram Reels": "instagram_reels",
        "TikTok": "tiktok",
        "YouTube Shorts": "youtube_shorts",
        "Facebook Video": "facebook_video",
        "LinkedIn Video": "linkedin"
    }

    selected_platform_label = st.selectbox(
        "Target Platform",
        options=list(platforms.keys()),
        index=list(platforms.values()).index(st.session_state.get('example_platform', 'instagram_reels')) if 'example_platform' in st.session_state else 0,
        help="Video platform where you'll publish this content"
    )
    platform = platforms[selected_platform_label]

    # Platform info
    platform_info = {
        "instagram_reels": "⏱️ 15-30 seconds | 9:16 vertical | Trending audio crucial",
        "tiktok": "⏱️ 15-60 seconds | 9:16 vertical | Fast-paced, authentic",
        "youtube_shorts": "⏱️ 15-60 seconds | 9:16 vertical | Strong hook needed",
        "facebook_video": "⏱️ 30-90 seconds | Square or landscape | Story-driven",
        "linkedin": "⏱️ 30-60 seconds | Square or landscape | Professional tone"
    }
    st.caption(platform_info.get(platform, ""))

    # Audience selector
    st.markdown("### 👥 Target Audience")

    # Fetch audiences from database
    audience_repository = AudienceRepository("audiences")
    audiences = audience_repository.get_audiences()

    if audiences:
        audience_options = ["Custom audience..."] + [f"{aud.name} - {aud.description[:50]}..." for aud in audiences]
        selected_audience_option = st.selectbox(
            "Select Audience",
            options=audience_options,
            help="Choose from saved audiences or enter custom"
        )

        if selected_audience_option == "Custom audience...":
            target_audience = st.text_input(
                "Custom Audience",
                placeholder="e.g., Fitness enthusiasts aged 25-40",
                help="Describe your target audience"
            )
        else:
            # Extract audience from selected option
            selected_audience = next((aud for aud in audiences if selected_audience_option.startswith(aud.name)), None)
            target_audience = f"{selected_audience.name} - {selected_audience.description}" if selected_audience else ""
            st.caption(f"📋 {selected_audience.description}" if selected_audience else "")
    else:
        target_audience = st.text_input(
            "Target Audience",
            placeholder="e.g., Fitness enthusiasts aged 25-40",
            help="Describe your target audience"
        )

    # Content goal
    st.markdown("### 🎯 Content Goal")

    goal_presets = [
        "Custom goal...",
        "Drive product sales",
        "Increase brand awareness",
        "Generate leads",
        "Drive event registrations",
        "Boost engagement",
        "Promote limited-time offer",
        "Launch new feature/product",
        "Drive website traffic",
        "Build community"
    ]

    selected_goal = st.selectbox(
        "Select Goal",
        options=goal_presets,
        index=0,
        help="What action do you want viewers to take?"
    )

    if selected_goal == "Custom goal...":
        content_goal = st.text_input(
            "Custom Goal",
            value=st.session_state.get('example_goal', ''),
            placeholder="e.g., Drive class registrations for new HIIT class",
            help="What's the primary goal of this video?"
        )
    else:
        content_goal = selected_goal

    # Generate button
    st.markdown("---")
    generate_button = st.button("🎬 Generate Video Script", type="primary", use_container_width=True)

    if generate_button:
        if not campaign_content:
            st.error("⚠️ Please enter campaign content")
        elif not target_audience:
            st.error("⚠️ Please specify target audience")
        elif not content_goal:
            st.error("⚠️ Please specify content goal")
        else:
            with st.spinner("🎬 Generating viral video script..."):
                try:
                    result = st.session_state.video_script_agent.generate_video_script_from_campaign(
                        campaign_content=campaign_content,
                        platform=platform,
                        target_audience=target_audience,
                        content_goal=content_goal
                    )

                    st.session_state.generated_script = result
                    st.success("✅ Video script generated successfully!")

                except Exception as e:
                    st.error(f"❌ Error generating script: {str(e)}")
                    logging.error(f"Script generation error: {e}")
                    import traceback
                    traceback.print_exc()

# Right column - Display generated script
with col2:
    st.markdown("### 🎬 Generated Script")

    if st.session_state.generated_script:
        result = st.session_state.generated_script

        # Tabs for different sections
        script_tabs = st.tabs(["📜 Full Script", "🎥 Sections", "🎬 Production", "⚡ Virality", "🎯 Platform Tips"])

        with script_tabs[0]:  # Full Script
            st.markdown("#### Complete Video Script")

            # Display full script in markdown
            full_script = result.get('full_script', '')
            if full_script:
                st.markdown(full_script)
            else:
                st.info("Script will appear here after generation")

            # Export buttons
            if full_script:
                st.markdown("---")
                st.markdown("#### 📥 Export Script")

                col_exp1, col_exp2 = st.columns(2)

                with col_exp1:
                    # Download as markdown
                    st.download_button(
                        label="📄 Download Markdown",
                        data=full_script,
                        file_name="video_script.md",
                        mime="text/markdown",
                        use_container_width=True
                    )

                with col_exp2:
                    # Download as text
                    st.download_button(
                        label="📝 Download Text",
                        data=full_script,
                        file_name="video_script.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

        with script_tabs[1]:  # Sections
            st.markdown("#### 🎥 Shot-by-Shot Breakdown")

            sections = result.get('script_sections', [])
            if sections:
                for i, section in enumerate(sections, 1):
                    with st.expander(f"Shot {i}: {section.get('section', 'Unknown').upper()} ({section.get('timing', 'N/A')})", expanded=(i == 1)):
                        st.markdown(f"**⏱️ Timing:** {section.get('timing', 'N/A')}")
                        st.markdown(f"**📸 Shot Type:** {section.get('shot', 'N/A')}")
                        st.markdown(f"**🎭 Action:** {section.get('action', 'N/A')}")
                        st.markdown(f"**💬 Text/Narration:**")
                        st.info(section.get('text', 'N/A'))
            else:
                st.info("Shot breakdown will appear here")

        with script_tabs[2]:  # Production Notes
            st.markdown("#### 🎬 Production Guidance")

            production = result.get('production_notes', {})
            if production:
                # Camera setup
                st.markdown("##### 📹 Camera Setup")
                camera = production.get('camera_setup', [])
                if isinstance(camera, list):
                    for tip in camera:
                        st.markdown(f"• {tip}")
                else:
                    st.markdown(camera)

                # Lighting
                st.markdown("##### 💡 Lighting")
                lighting = production.get('lighting', '')
                st.markdown(lighting)

                # Audio
                st.markdown("##### 🎵 Audio")
                audio = production.get('audio', '')
                st.markdown(audio)

                # Editing
                if 'editing' in production:
                    st.markdown("##### ✂️ Editing Tips")
                    editing = production.get('editing', '')
                    st.markdown(editing)

                # Props/Location
                if 'props' in production or 'location' in production:
                    col_p1, col_p2 = st.columns(2)

                    with col_p1:
                        if 'props' in production:
                            st.markdown("##### 🎭 Props")
                            st.markdown(production.get('props', ''))

                    with col_p2:
                        if 'location' in production:
                            st.markdown("##### 📍 Location")
                            st.markdown(production.get('location', ''))

                # Smartphone tips
                st.markdown("---")
                st.markdown("##### 📱 Smartphone Filming Tips")
                smartphone_tips = production.get('smartphone_tips', [])
                if isinstance(smartphone_tips, list):
                    for tip in smartphone_tips:
                        st.markdown(f"• {tip}")
                else:
                    st.markdown(smartphone_tips)
            else:
                st.info("Production notes will appear here")

        with script_tabs[3]:  # Virality Prediction
            st.markdown("#### ⚡ Virality Prediction")

            prediction = result.get('virality_prediction', {})
            if prediction:
                # Virality score
                virality_score = prediction.get('virality_score', 0)

                # Color based on score
                if virality_score >= 80:
                    score_color = "🟢"
                    score_label = "Excellent"
                elif virality_score >= 60:
                    score_color = "🟡"
                    score_label = "Good"
                else:
                    score_color = "🔴"
                    score_label = "Needs Improvement"

                st.markdown(f"### {score_color} {virality_score}/100")
                st.caption(f"**{score_label}** viral potential")

                # Progress bar
                st.progress(virality_score / 100)

                # Expected views
                expected_views = prediction.get('expected_views', 'N/A')
                st.metric("📊 Expected Views", expected_views)

                st.markdown("---")

                # Factor scores
                st.markdown("##### 📈 Factor Breakdown")
                factors = prediction.get('factor_scores', {})
                if factors:
                    for factor, score in factors.items():
                        factor_name = factor.replace('_', ' ').title()
                        st.markdown(f"**{factor_name}:** {score}/100")
                        st.progress(score / 100)

                # Strengths
                st.markdown("---")
                st.markdown("##### ✅ Strengths")
                strengths = prediction.get('strengths', [])
                if strengths:
                    for strength in strengths:
                        st.markdown(f"• {strength}")
                else:
                    st.info("No specific strengths identified")

                # Improvements
                st.markdown("##### 💡 Suggested Improvements")
                improvements = prediction.get('improvements', [])
                if improvements:
                    for improvement in improvements:
                        st.markdown(f"• {improvement}")
                else:
                    st.success("Script is optimized!")
            else:
                st.info("Virality analysis will appear here")

        with script_tabs[4]:  # Platform Tips
            st.markdown("#### 🎯 Platform-Specific Optimization")

            platform_opt = result.get('platform_optimization', {})
            if platform_opt:
                # Duration check
                st.markdown("##### ⏱️ Duration Check")
                duration_status = platform_opt.get('duration_check', 'N/A')
                total_duration = platform_opt.get('total_duration', 0)

                if "✅" in duration_status:
                    st.success(f"{duration_status} - {total_duration} seconds")
                elif "⚠️" in duration_status:
                    st.warning(duration_status)
                else:
                    st.info(duration_status)

                # Platform specifications
                st.markdown("---")
                st.markdown("##### 📐 Platform Specifications")

                col_spec1, col_spec2 = st.columns(2)
                with col_spec1:
                    st.markdown(f"**Aspect Ratio:** {platform_opt.get('aspect_ratio', 'N/A')}")
                    st.markdown(f"**Tone:** {platform_opt.get('tone', 'N/A')}")

                with col_spec2:
                    best_times = platform_opt.get('best_times', [])
                    if best_times:
                        st.markdown(f"**Best Times:** {', '.join(best_times)}")

                # Critical platform notes
                st.markdown("---")
                st.markdown("##### ⚠️ Critical Platform Notes")

                platform_notes = platform_opt.get('platform_notes', [])
                if platform_notes:
                    for note in platform_notes:
                        if "CRITICAL" in note:
                            st.error(note)
                        elif "⚠️" in note:
                            st.warning(note)
                        else:
                            st.info(note)
                else:
                    st.info("No specific critical notes")

                # Optimization tips
                st.markdown("---")
                st.markdown("##### 💡 Optimization Tips")

                optimization_tips = platform_opt.get('optimization_tips', [])
                if optimization_tips:
                    for tip in optimization_tips:
                        st.markdown(f"• {tip}")
                else:
                    st.info("No specific optimization tips")

            else:
                st.info("Platform optimization tips will appear here")

        # Selected pattern info (below tabs)
        st.markdown("---")
        selected_pattern = result.get('selected_pattern', {})
        if selected_pattern:
            st.markdown("#### 🎯 Viral Pattern Used")

            col_pat1, col_pat2, col_pat3 = st.columns(3)
            with col_pat1:
                st.metric("Pattern", selected_pattern.get('name', 'N/A'))
            with col_pat2:
                success_rate = selected_pattern.get('success_rate', 0)
                st.metric("Success Rate", f"{success_rate:.1%}")
            with col_pat3:
                avg_views = selected_pattern.get('avg_views', 0)
                st.metric("Avg Views", f"{avg_views:,}")

    else:
        st.info("👈 Generate a video script to see results here")

# Footer
st.markdown("---")
st.caption("💡 **Tip:** Use Advanced Mode in AI Template Generator to customize your campaign templates, then generate video scripts here!")
